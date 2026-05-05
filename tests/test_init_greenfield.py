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
                ".aletheia/governance/CHARTER.md",
                ".aletheia/governance/INTAKE_POLICY.md",
                ".aletheia/state/FRONTIER_BOARD.md",
                ".aletheia/state/GLOSSARY.md",
                ".aletheia/state/DOMAIN_PROFILE.md",
                ".aletheia/evidence/INDEX.md",
                ".aletheia/contracts/INDEX.md",
                ".aletheia/hypotheses/.gitkeep",
                ".aletheia/nodes/ROOT.yaml",
                ".aletheia/playbooks/guided_bootstrap.md",
                ".aletheia/templates/HYPOTHESIS.md",
                ".aletheia/templates/NODE.yaml",
                ".aletheia/templates/TASK_CARD.md",
                ".aletheia/templates/AGENT_RUN.json",
                ".aletheia/templates/BOOTSTRAP_IMPORT_REPORT.md",
                ".aletheia/templates/BOOTSTRAP_INTAKE_MANIFEST.yaml",
                ".aletheia/bin/context_pack.py",
                ".aletheia/bin/intake_inventory.py",
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


if __name__ == "__main__":
    unittest.main()
