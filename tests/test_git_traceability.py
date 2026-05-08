from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def import_scaffold_module(target: Path, name: str):
    script = target / ".aletheia" / "bin" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GitTraceabilityTests(unittest.TestCase):
    def test_parse_trailers_collects_aios_trailer_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            git_trailers = import_scaffold_module(target, "git_trailers")

            message = (
                "subject\n\n"
                "body\n\n"
                "AIOS-Action: truth.node.stabilize\n"
                "AIOS-Node: theory_model\n"
            )

            trailers = git_trailers.parse_trailers(message)

            self.assertEqual(trailers["AIOS-Action"], ["truth.node.stabilize"])
            self.assertEqual(trailers["AIOS-Node"], ["theory_model"])

    def test_build_aios_trailers_formats_stable_node_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            git_trailers = import_scaffold_module(target, "git_trailers")

            trailers = git_trailers.build_aios_trailers(
                action="truth.node.stabilize",
                tree_op=None,
                node="theory_model",
                parent="root",
                node_state="stable",
                evidence=[".aletheia/evidence/EV-001-factor-baseline.md"],
                decision=[".aletheia/decisions/DEC-001-modeling-lens-policy.md"],
                implements=[],
                supersedes=[],
                validation="pass",
                review="human-confirmed",
            )

            self.assertIn("AIOS-Action: truth.node.stabilize", trailers)
            self.assertIn("AIOS-Node-State: stable", trailers)
            self.assertIn("AIOS-Review: human-confirmed", trailers)

    def test_validate_trailer_values_rejects_unknown_enums(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            git_trailers = import_scaffold_module(target, "git_trailers")

            errors = git_trailers.validate_trailer_values(
                {
                    "AIOS-Action": ["truth.node.stabilize", "invalid.action"],
                    "AIOS-Tree-Op": ["attach_orphan", "teleport"],
                    "AIOS-Node-State": ["stable", "unknown"],
                    "AIOS-Validation": ["pass", "skip"],
                    "AIOS-Review": ["human-confirmed", "rubber-stamped"],
                }
            )

            self.assertIn("AIOS-Action has unsupported value: invalid.action", errors)
            self.assertIn("AIOS-Tree-Op has unsupported value: teleport", errors)
            self.assertIn("AIOS-Node-State has unsupported value: unknown", errors)
            self.assertIn("AIOS-Validation has unsupported value: skip", errors)
            self.assertIn("AIOS-Review has unsupported value: rubber-stamped", errors)


if __name__ == "__main__":
    unittest.main()
