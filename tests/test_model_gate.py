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


class ModelGateTests(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
