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
    def run_pretooluse_hook(self, target: Path, payload: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, ".aletheia/bin/model_gate.py", "--hook-mode", "pretooluse"],
            cwd=target,
            input=json.dumps(payload),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

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

    def test_pretooluse_allows_standalone_bootstrap_model_gate_before_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            result = self.run_pretooluse_hook(
                target,
                {
                    "tool_name": "Bash",
                    "tool_input": {
                        "command": (
                            "python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize "
                            "--provider test --model-id test-model --tier C3 --operator-approved "
                            '--record --objective "Initialize AletheiaOS"'
                        )
                    },
                },
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertNotIn("permissionDecision", output)

    def test_pretooluse_rejects_chained_model_gate_command_before_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            result = self.run_pretooluse_hook(
                target,
                {
                    "tool_name": "Bash",
                    "tool_input": {
                        "command": (
                            "python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize "
                            "--provider test --model-id test-model --tier C3 --operator-approved "
                            '--record --objective "Initialize AletheiaOS" && touch should-not-run'
                        )
                    },
                },
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("permissionDecision", output)
            self.assertIn("standalone model gate record command", output)

    def test_pretooluse_rejects_allowed_read_only_task_for_write_tool(self) -> None:
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
                    "orientation",
                    "--provider",
                    "test",
                    "--model-id",
                    "test-model",
                    "--tier",
                    "C0",
                    "--operator-approved",
                    "--record",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)

            result = self.run_pretooluse_hook(
                target,
                {"tool_name": "Write", "tool_input": {"file_path": "x.txt", "content": "blocked"}},
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("permissionDecision", output)
            self.assertIn("does not allow write-capable tool calls", output)

if __name__ == "__main__":
    unittest.main()
