from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "assets" / "scaffold"


def run_script(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        cwd=cwd or ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def init_target(target: Path) -> None:
    result = run_script("scripts/init_aletheia.py", str(target))
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def load_truth_record_module():
    path = SCAFFOLD / ".aletheia" / "bin" / "truth_record.py"
    spec = importlib.util.spec_from_file_location("truth_record_for_agent_native_coverage", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AgentNativeCoverageTests(unittest.TestCase):
    def test_action_contracts_recommend_safe_documented_actions(self) -> None:
        registry = json.loads((SCAFFOLD / ".aletheia" / "governance" / "actions.json").read_text(encoding="utf-8"))
        actions = {action["id"]: action for action in registry["actions"]}
        self.assertEqual(len(actions), len(registry["actions"]))

        for action_id in registry["recommended_actions"]:
            with self.subTest(action_id=action_id):
                self.assertIn(action_id, actions)
                self.assertEqual(actions[action_id]["risk"], "read-only")

        for action_id, action in actions.items():
            inputs = action.get("inputs", {})
            for part in action["command"]:
                match = re.fullmatch(r"\{\{([A-Za-z0-9_]+)\}\}", part)
                if match:
                    self.assertIn(match.group(1), inputs, action_id)

        capability_map = (SCAFFOLD / ".aletheia" / "CAPABILITY_MAP.md").read_text(encoding="utf-8")
        help_output = subprocess.run(
            [sys.executable, "assets/scaffold/.aletheia/bin/help.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(help_output.returncode, 0, help_output.stdout + help_output.stderr)
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        discovery_text = "\n".join([capability_map, help_output.stdout, readme])

        for required in [
            "truth.orient.runtime",
            "truth.status",
            "truth.preflight",
            "truth.validate",
            "truth.checkpoint.dry_run",
            "truth.orphan.create",
            "truth.orphan.archive",
            "truth.bootstrap.guided.inspect",
            "truth.bootstrap.finalize.inspect",
            "truth_record.py create orphan",
            "truth_record.py show charter current",
            "guided_bootstrap.py --inspect --json",
            "bootstrap_finalize.py --inspect --json",
            "generated-output boundaries",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, discovery_text)

    def test_fixed_truth_aliases_documented_in_crud_matrix_exist_in_truth_record_script(self) -> None:
        truth_record = load_truth_record_module()
        capability_map = (SCAFFOLD / ".aletheia" / "CAPABILITY_MAP.md").read_text(encoding="utf-8")
        aliases = [
            "charter",
            "attention-policy",
            "model-governance",
            "tree-governance",
            "git-policy",
            "source-policy",
            "user-preferences",
            "domain-profile",
            "frontier-board",
            "risk-register",
            "glossary",
            "skeleton",
            "actions-registry",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                self.assertIn(alias, truth_record.ENTITY_CONFIG)
                self.assertIn(f"truth_record.py show {alias} current", capability_map)

    def test_status_preflight_and_overview_share_hook_free_refresh_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

            status = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            preflight = subprocess.run(
                [sys.executable, ".aletheia/bin/preflight.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            overview = subprocess.run(
                [sys.executable, ".aletheia/bin/overview.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            self.assertEqual(preflight.returncode, 0, preflight.stdout + preflight.stderr)
            self.assertEqual(overview.returncode, 0, overview.stdout + overview.stderr)
            status_payload = json.loads(status.stdout)
            preflight_payload = json.loads(preflight.stdout)
            overview_payload = json.loads((target / ".aletheia" / "overview" / "status.json").read_text(encoding="utf-8"))

            for payload in [status_payload, preflight_payload, overview_payload]:
                with self.subTest(payload=payload["repo"]):
                    self.assertIn("Generated/runtime outputs", payload["durability_note"])
                    self.assertTrue(any(item["path"] == ".aletheia/overview/" for item in payload["generated_outputs"]))
                    self.assertTrue(any("checkpoint.py --dry-run" in action for action in payload["next_actions"]))

            self.assertIn("truth.checkpoint.dry_run", status_payload["recommended_actions"])
            self.assertIn("truth.checkpoint.dry_run", preflight_payload["recommended_actions"])
            self.assertIn("truth.checkpoint.dry_run", overview_payload["recommended_actions"])

    def test_scaffold_validation_catches_agent_native_capability_map_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scaffold = Path(tmp) / "scaffold"
            shutil.copytree(SCAFFOLD, scaffold)
            capability_map = scaffold / ".aletheia" / "CAPABILITY_MAP.md"
            capability_map.write_text(
                capability_map.read_text(encoding="utf-8").replace("truth.orphan.create", "truth.orphan.missing"),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate_scaffold.py", str(scaffold)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("capability map missing term: truth.orphan.create", result.stderr)


if __name__ == "__main__":
    unittest.main()
