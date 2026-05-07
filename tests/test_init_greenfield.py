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


class GreenfieldInitTests(unittest.TestCase):
    def test_greenfield_init_writes_complete_control_plane_and_claude_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()

            result = run_script("scripts/init_aletheia.py", str(target))

            self.assertEqual(result.returncode, 0, result.stderr)
            expected_paths = [
                "AGENTS.md",
                "START_HERE.md",
                "BOOTSTRAP.md",
                ".claude/settings.json",
                ".aletheia/START_HERE.md",
                ".aletheia/CAPABILITY_MAP.md",
                ".aletheia/governance/CHARTER.md",
                ".aletheia/governance/SOURCE_POLICY.md",
                ".aletheia/governance/runtime_policy.json",
                ".aletheia/state/FRONTIER_BOARD.md",
                ".aletheia/state/GLOSSARY.md",
                ".aletheia/state/DOMAIN_PROFILE.md",
                ".aletheia/evidence/INDEX.md",
                ".aletheia/contracts/INDEX.md",
                ".aletheia/hypotheses/.gitkeep",
                ".aletheia/nodes/ROOT.yaml",
                ".aletheia/playbooks/external_llm_wiki_handoff.md",
                ".aletheia/playbooks/guided_bootstrap.md",
                ".aletheia/playbooks/drift_audit.md",
                ".aletheia/playbooks/wiki_handoff_promotion.md",
                ".aletheia/templates/HYPOTHESIS.md",
                ".aletheia/templates/NODE.yaml",
                ".aletheia/templates/TASK_CARD.md",
                ".aletheia/templates/AGENT_RUN.json",
                ".aletheia/templates/TRUTH_INVENTORY_REPORT.md",
                ".aletheia/templates/SOURCE_INVENTORY_MANIFEST.yaml",
                ".aletheia/bin/help.py",
                ".aletheia/bin/context_pack.py",
                ".aletheia/bin/status.py",
                ".aletheia/bin/truth_record.py",
                ".aletheia/bin/source_inventory.py",
                ".aletheia/bin/guided_bootstrap.py",
                ".aletheia/bin/change_hook.py",
                ".aletheia/bin/stop_hook.py",
            ]
            for rel in expected_paths:
                self.assertTrue((target / rel).exists(), rel)

            settings = json.loads((target / ".claude/settings.json").read_text(encoding="utf-8"))
            self.assertEqual(
                settings["hooks"]["SessionStart"][0]["hooks"][0]["command"],
                "python3 .aletheia/bin/model_gate.py --hook-mode sessionstart",
            )
            self.assertEqual(
                settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"],
                "python3 .aletheia/bin/model_gate.py --hook-mode pretooluse",
            )
            self.assertEqual(
                settings["hooks"]["PostToolUse"][0]["hooks"][0]["command"],
                "python3 .aletheia/bin/change_hook.py",
            )
            self.assertEqual(settings["hooks"]["Stop"][0]["hooks"][0]["command"], "python3 .aletheia/bin/stop_hook.py")

            validate = subprocess.run(
                [sys.executable, ".aletheia/bin/validate.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

    def test_init_merges_existing_claude_hooks_without_overwriting_root_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text("# Existing Agents\n", encoding="utf-8")
            (target / "START_HERE.md").write_text("# Existing Start\n", encoding="utf-8")
            claude = target / ".claude"
            claude.mkdir()
            settings = claude / "settings.json"
            settings.write_text(
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                {
                                    "matcher": "Bash",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": "python3 custom_pretool.py",
                                        }
                                    ],
                                }
                            ]
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_script("scripts/init_aletheia.py", str(target))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "# Existing Agents\n")
            self.assertEqual((target / "START_HERE.md").read_text(encoding="utf-8"), "# Existing Start\n")
            merged = json.loads(settings.read_text(encoding="utf-8"))
            pretool_commands = [
                hook["command"]
                for entry in merged["hooks"]["PreToolUse"]
                for hook in entry["hooks"]
            ]
            self.assertIn("python3 custom_pretool.py", pretool_commands)
            self.assertIn("python3 .aletheia/bin/model_gate.py --hook-mode pretooluse", pretool_commands)
            self.assertIn("SessionStart", merged["hooks"])
            self.assertIn("PostToolUse", merged["hooks"])
            self.assertIn("Stop", merged["hooks"])

    def test_init_fails_clearly_for_invalid_existing_claude_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            claude = target / ".claude"
            claude.mkdir()
            (claude / "settings.json").write_text("{invalid json", encoding="utf-8")

            result = run_script("scripts/init_aletheia.py", str(target))

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("Claude settings JSON invalid", output)

    def test_init_fails_clearly_for_invalid_existing_claude_hooks_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            claude = target / ".claude"
            claude.mkdir()
            (claude / "settings.json").write_text(json.dumps({"hooks": []}) + "\n", encoding="utf-8")

            result = run_script("scripts/init_aletheia.py", str(target))

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("Claude settings JSON invalid", output)
            self.assertIn("hooks must be object", output)
            self.assertNotIn("Traceback", output)

    def test_init_fails_clearly_when_scaffold_directory_path_is_occupied_by_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".aletheia").write_text("not a directory\n", encoding="utf-8")

            result = run_script("scripts/init_aletheia.py", str(target))

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("cannot create scaffold path", output)
            self.assertIn(".aletheia", output)
            self.assertNotIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
