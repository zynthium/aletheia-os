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


class CheckpointTests(unittest.TestCase):
    def test_checkpoint_dry_run_reports_agent_attribution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-test",
                        "provider": "test",
                        "model_id": "test-model",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nDry-run checkpoint note.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("checkpoint candidate:", output)
            self.assertIn("agent_run: RUN-test test/test-model", output)


if __name__ == "__main__":
    unittest.main()
