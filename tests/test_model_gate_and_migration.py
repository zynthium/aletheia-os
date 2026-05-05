from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        cwd=cwd or ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class ModelGateAndMigrationTests(unittest.TestCase):
    def test_model_gate_blocks_unregistered_write_and_allows_operator_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            registry_path = target / ".aletheia" / "governance" / "model_registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["registered_models"] = {}
            registry["denylist"] = []
            registry.setdefault("default_policy", {})["allow_self_attested_tier"] = False
            registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

            blocked = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "root_theory_revision",
                    "--provider",
                    "test",
                    "--model-id",
                    "arbitrary-small-model",
                    "--capability-tier",
                    "C4",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0, blocked.stdout + blocked.stderr)
            self.assertIn("rejected", blocked.stdout)

            allowed = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "root_theory_revision",
                    "--provider",
                    "test",
                    "--model-id",
                    "arbitrary-small-model",
                    "--tier",
                    "C4",
                    "--operator-approved",
                    "--record",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
            self.assertTrue((target / ".aletheia" / "runtime" / "current_agent_run.json").exists())
            self.assertTrue(any((target / ".aletheia" / "agent_runs").glob("*.json")))

    def test_migrate_legacy_rewrites_paths_preserves_legacy_tree_and_writes_claude_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            legacy = target / "aletheia_os"
            legacy.mkdir()
            (legacy / "00_CHARTER.md").write_text(
                "See aletheia_os/02_ACTIVE_STATE.md and aletheia_os/01_SYSTEM_GRAPH.yaml.\n",
                encoding="utf-8",
            )
            (legacy / "01_SYSTEM_GRAPH.yaml").write_text(
                "version: 0.1\nschema: AIOS_SYSTEM_GRAPH\nupdated: 2026-05-05\n",
                encoding="utf-8",
            )
            (legacy / "02_ACTIVE_STATE.md").write_text("# Active State\n", encoding="utf-8")
            (legacy / "10_ATTENTION_POLICY.md").write_text("Use aletheia_os/00_CHARTER.md.\n", encoding="utf-8")
            (legacy / "11_MODEL_GOVERNANCE.md").write_text("Gate via aletheia_os/model_registry.json.\n", encoding="utf-8")
            (legacy / "model_registry.json").write_text(
                json.dumps({"capability_tiers": {"C0": {"rank": 0}}, "task_classes": {}, "registered_models": {}, "denylist": []}, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (legacy / "decisions").mkdir()
            (legacy / "decisions" / "ADR-0000.md").write_text("Decision references aletheia_os/07_EVIDENCE_INDEX.md.\n", encoding="utf-8")

            result = run_script("scripts/migrate_aletheia.py", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)

            self.assertTrue((target / ".aletheia" / "governance" / "INTAKE_POLICY.md").exists())
            self.assertTrue((target / ".claude" / "settings.json").exists())
            self.assertTrue((target / "aletheia_os").exists())
            self.assertTrue((target / ".aletheia" / "bootstrap_intake" / "IMPORT_REPORT.md").exists())

            charter = (target / ".aletheia" / "governance" / "CHARTER.md").read_text(encoding="utf-8")
            self.assertNotIn("aletheia_os/", charter)
            attention = (target / ".aletheia" / "governance" / "ATTENTION_POLICY.md").read_text(encoding="utf-8")
            self.assertNotIn("aletheia_os/", attention)
            self.assertIn(".aletheia/", attention)


if __name__ == "__main__":
    unittest.main()
