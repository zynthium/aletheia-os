from __future__ import annotations

import json
import os
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

    def test_sessionstart_records_payload_model_and_env_task_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            env = os.environ.copy()
            env["AIOS_TASK_CLASS"] = "orientation"
            env["AIOS_OBJECTIVE"] = "Open Claude Code session"

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/model_gate.py", "--hook-mode", "sessionstart"],
                cwd=target,
                env=env,
                input=json.dumps({"session_id": "claude-session", "model": "claude-sonnet-4-5"}),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("Detected model: anthropic/claude-sonnet-4-5", output)
            run_data = json.loads((target / ".aletheia" / "runtime" / "current_agent_run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_data["provider"], "anthropic")
            self.assertEqual(run_data["model_id"], "claude-sonnet-4-5")
            self.assertEqual(run_data["agent_tool"], "claude-code")
            self.assertEqual(run_data["task_class"], "orientation")
            self.assertEqual(run_data["objective"], "Open Claude Code session")

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

    def test_pretooluse_rejects_bash_commands_that_only_look_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            for command in [
                "git status && touch should-not-run",
                "git status > status.txt",
                "lsbad",
                "python3 .aletheia/bin/validate.py && touch should-not-run",
            ]:
                result = self.run_pretooluse_hook(
                    target,
                    {"tool_name": "Bash", "tool_input": {"command": command}},
                )

                output = result.stdout + result.stderr
                self.assertEqual(result.returncode, 0, output)
                self.assertIn("permissionDecision", output, command)
                self.assertIn("no current agent run", output, command)

    def test_pretooluse_allows_strict_read_only_bash_commands_without_agent_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            for command in [
                "git status --short",
                "git diff -- .aletheia/state/ACTIVE_STATE.md",
                "ls .aletheia",
                "pwd",
                "sed -n 1,80p .aletheia/START_HERE.md",
                "rg AletheiaOS .aletheia/START_HERE.md",
                "find .aletheia -maxdepth 1 -type f",
                "python3 .aletheia/bin/orient.py",
                "python3 .aletheia/bin/context_pack.py",
                "python3 .aletheia/bin/validate.py",
                "python3 .aletheia/bin/truth_record.py list evidence",
                "python3 .aletheia/bin/truth_record.py show evidence EV-0001",
            ]:
                result = self.run_pretooluse_hook(
                    target,
                    {"tool_name": "Bash", "tool_input": {"command": command}},
                )

                output = result.stdout + result.stderr
                self.assertEqual(result.returncode, 0, output)
                self.assertNotIn("permissionDecision", output, command)

    def test_pretooluse_treats_truth_record_create_and_archive_as_write_capable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            for command in [
                "python3 .aletheia/bin/truth_record.py create evidence --id EV-0001 --title Claim",
                "python3 .aletheia/bin/truth_record.py archive evidence EV-0001 --reason stale",
            ]:
                result = self.run_pretooluse_hook(
                    target,
                    {"tool_name": "Bash", "tool_input": {"command": command}},
                )

                output = result.stdout + result.stderr
                self.assertEqual(result.returncode, 0, output)
                self.assertIn("permissionDecision", output, command)
                self.assertIn("no current agent run", output, command)

    def test_registered_model_alias_denied_model_and_self_attested_policy_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            registry_path = target / ".aletheia" / "governance" / "model_registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["registered_models"] = {
                "openai/codex-e2e": {
                    "tier": "C3",
                    "aliases": ["codex-e2e", "openai/codex-alias"],
                    "notes": "test model",
                }
            }
            registry["denylist"] = ["blocked-model"]
            registry.setdefault("default_policy", {})["allow_self_attested_tier"] = False
            registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

            alias = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "research_design",
                    "--provider",
                    "openai",
                    "--model-id",
                    "codex-alias",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(alias.returncode, 0, alias.stdout + alias.stderr)
            alias_gate = json.loads(alias.stdout)
            self.assertEqual(alias_gate["gate_status"], "allowed")
            self.assertEqual(alias_gate["registry_status"], "registered:openai/codex-e2e")

            denied = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "orientation",
                    "--provider",
                    "test",
                    "--model-id",
                    "blocked-model",
                    "--tier",
                    "C4",
                    "--operator-approved",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(denied.returncode, 0, denied.stdout + denied.stderr)
            denied_gate = json.loads(denied.stdout)
            self.assertEqual(denied_gate["gate_status"], "rejected")
            self.assertIn("denied", denied_gate["reason"])

            self_attested = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "research_design",
                    "--provider",
                    "test",
                    "--model-id",
                    "self-model",
                    "--tier",
                    "C3",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(self_attested.returncode, 0, self_attested.stdout + self_attested.stderr)
            self_attested_gate = json.loads(self_attested.stdout)
            self.assertEqual(self_attested_gate["registry_status"], "self_attested_rejected")

            registry["default_policy"]["allow_self_attested_tier"] = True
            registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
            allowed_self_attested = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "research_design",
                    "--provider",
                    "test",
                    "--model-id",
                    "self-model",
                    "--tier",
                    "C3",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(allowed_self_attested.returncode, 0, allowed_self_attested.stdout + allowed_self_attested.stderr)
            allowed_self_attested_gate = json.loads(allowed_self_attested.stdout)
            self.assertEqual(allowed_self_attested_gate["gate_status"], "allowed")
            self.assertEqual(allowed_self_attested_gate["registry_status"], "self_attested")

    def test_unknown_task_class_has_clear_cli_and_hook_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            cli = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "unknown_task",
                    "--provider",
                    "test",
                    "--model-id",
                    "test-model",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(cli.returncode, 2, cli.stdout + cli.stderr)
            self.assertIn("unknown task class: unknown_task", cli.stderr)

            hook = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--hook-mode",
                    "pretooluse",
                    "--task-class",
                    "unknown_task",
                ],
                cwd=target,
                input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": "x.txt"}}),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            output = hook.stdout + hook.stderr
            self.assertEqual(hook.returncode, 0, output)
            self.assertIn("permissionDecision", output)
            self.assertIn("unknown task class: unknown_task", output)

    def test_invalid_model_registry_object_falls_back_to_default_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            registry_path = target / ".aletheia" / "governance" / "model_registry.json"
            registry_path.write_text("[]\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "orientation",
                    "--provider",
                    "test",
                    "--model-id",
                    "test-model",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            gate = json.loads(result.stdout)
            self.assertEqual(gate["task_class"], "orientation")
            self.assertEqual(gate["registry_status"], "unknown")
            self.assertEqual(gate["gate_status"], "rejected")

if __name__ == "__main__":
    unittest.main()
