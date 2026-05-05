from __future__ import annotations

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


def init_target(target: Path) -> None:
    result = run_script("scripts/init_aletheia.py", str(target))
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def validate_target(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, ".aletheia/bin/validate.py"],
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class RuntimeValidateTests(unittest.TestCase):
    def test_validate_rejects_missing_claude_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".claude" / "settings.json").unlink()

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("missing required path: .claude/settings.json", output)

    def test_validate_rejects_graph_skeleton_root_child_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8").replace("      - risk_safety\n", "      - obsolete_branch\n"),
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("skeleton root children do not match system graph root children", output)


if __name__ == "__main__":
    unittest.main()
