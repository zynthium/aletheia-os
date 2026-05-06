from __future__ import annotations

import json
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


class BootstrapFinalizeTests(unittest.TestCase):
    def test_guided_bootstrap_stops_without_recorded_bootstrap_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/guided_bootstrap.py", "--objective", "Initialize AletheiaOS"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("no bootstrap model gate run recorded", output)
            self.assertFalse((target / ".aletheia" / "source_inventory" / "TRUTH_INVENTORY_REPORT.md").exists())

    def test_guided_bootstrap_succeeds_with_recorded_operator_approved_bootstrap_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            gate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "bootstrap_finalize",
                    "--provider",
                    "test",
                    "--model-id",
                    "test-model",
                    "--tier",
                    "C3",
                    "--operator-approved",
                    "--record",
                    "--objective",
                    "Initialize AletheiaOS",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/guided_bootstrap.py", "--objective", "Initialize AletheiaOS"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            report = target / ".aletheia" / "source_inventory" / "TRUTH_INVENTORY_REPORT.md"
            self.assertTrue(report.exists())
            self.assertIn("Initialization mode: new repository", report.read_text(encoding="utf-8"))

    def test_guided_bootstrap_rejects_read_only_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-test",
                        "provider": "test",
                        "model_id": "test-model",
                        "capability_tier": "C3",
                        "task_class": "bootstrap_finalize",
                        "gate_status": "allowed",
                        "write_allowed": False,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/guided_bootstrap.py", "--objective", "Initialize AletheiaOS"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("does not allow bootstrap writes", output)
            self.assertFalse((target / ".aletheia" / "source_inventory" / "TRUTH_INVENTORY_REPORT.md").exists())

    def test_bootstrap_finalize_blocks_without_allowed_agent_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/bootstrap_finalize.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("no AI model gate run recorded", output)
            self.assertTrue((target / "BOOTSTRAP.md").exists())

    def test_bootstrap_finalize_blocks_when_critical_state_still_has_tbd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-test",
                        "provider": "test",
                        "model_id": "test-model",
                        "capability_tier": "C3",
                        "task_class": "bootstrap_finalize",
                        "gate_status": "allowed",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/bootstrap_finalize.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("critical files still contain TBD markers", output)
            self.assertTrue((target / "BOOTSTRAP.md").exists())


if __name__ == "__main__":
    unittest.main()
