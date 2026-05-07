from __future__ import annotations

import json
import os
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
    def test_checkpoint_does_not_treat_public_overview_as_durable_state(self) -> None:
        text = (ROOT / "assets" / "scaffold" / ".aletheia" / "bin" / "checkpoint.py").read_text(encoding="utf-8")

        self.assertNotIn('"docs/overview/"', text)

    def test_checkpoint_cli_does_not_expose_dead_state_only_argument(self) -> None:
        result = subprocess.run(
            [sys.executable, "assets/scaffold/.aletheia/bin/checkpoint.py", "--help"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn("--state-only", output)

    def test_checkpoint_reports_missing_git_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nMissing git checkpoint note.\n", encoding="utf-8")
            empty_bin = Path(tmp) / "empty-bin"
            empty_bin.mkdir()
            env = os.environ.copy()
            env["PATH"] = str(empty_bin)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--no-model-gate"],
                cwd=target,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("checkpoint blocked: git is not available on PATH", output)
            self.assertNotIn("Traceback", output)

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

    def test_checkpoint_rejects_env_only_unrecorded_agent_attribution_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nEnv-only checkpoint note.\n", encoding="utf-8")

            env = os.environ.copy()
            env.update(
                {
                    "AIOS_AGENT_PROVIDER": "test",
                    "AIOS_MODEL_ID": "test-model",
                    "AIOS_MODEL_TIER": "C3",
                    "AIOS_TASK_CLASS": "research_design",
                }
            )
            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run"],
                cwd=target,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("no current AI agent run attribution found", output)

    def test_checkpoint_reports_invalid_current_agent_run_without_treating_it_as_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text("{bad json", encoding="utf-8")
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nInvalid run checkpoint note.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("checkpoint blocked: current AI agent run record is invalid", output)
            self.assertIn("current_agent_run.json", output)
            self.assertNotIn("no current AI agent run attribution found", output)
            self.assertNotIn("Traceback", output)

    def test_checkpoint_explicit_no_model_gate_allows_unattributed_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nExplicitly unattributed checkpoint note.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--no-model-gate"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("checkpoint candidate:", output)

    def test_checkpoint_blocks_protected_files_even_with_full_worktree(self) -> None:
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
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nProtected file checkpoint note.\n", encoding="utf-8")
            (target / ".env.local").write_text("TOKEN=secret\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--include-worktree"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 2, output)
            self.assertIn("checkpoint blocked: protected-looking files are present", output)
            self.assertIn(".env.local", output)

    def test_checkpoint_uses_runtime_policy_for_state_and_protected_paths(self) -> None:
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
                        "run_id": "RUN-policy",
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
            policy_path = target / ".aletheia" / "governance" / "runtime_policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["checkpoint_state_patterns"].append("docs/truth/")
            policy["protected_path_patterns"].append("(^|/)private_notes/")
            policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")

            doc = target / "docs" / "truth" / "note.md"
            doc.parent.mkdir(parents=True)
            doc.write_text("# Truth note\n", encoding="utf-8")
            blocked_file = target / "private_notes" / "secret.txt"
            blocked_file.parent.mkdir()
            blocked_file.write_text("blocked\n", encoding="utf-8")

            blocked = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--include-worktree"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            blocked_output = blocked.stdout + blocked.stderr
            self.assertEqual(blocked.returncode, 2, blocked_output)
            self.assertIn("private_notes/secret.txt", blocked_output)

            blocked_file.unlink()
            allowed = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--no-validate"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            allowed_output = allowed.stdout + allowed.stderr
            self.assertEqual(allowed.returncode, 0, allowed_output)
            self.assertIn("docs/truth/note.md", allowed_output)
            self.assertNotIn("changes do not include durable project-state update", allowed_output)

    def test_checkpoint_allow_code_only_env_and_no_validate_paths_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
            subprocess.run(["git", "add", "-A"], cwd=target, check=False)
            baseline = subprocess.run(
                ["git", "commit", "-m", "test: initial scaffold"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-test",
                        "provider": "test",
                        "model_id": "test-model",
                        "capability_tier": "C3",
                        "task_class": "mechanical_implementation",
                        "gate_status": "allowed",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            src = target / "src"
            src.mkdir()
            (src / "only_code.py").write_text("print('code only')\n", encoding="utf-8")

            blocked = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--include-worktree", "--no-validate"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            blocked_output = blocked.stdout + blocked.stderr
            self.assertEqual(blocked.returncode, 3, blocked_output)
            self.assertIn("changes do not include durable project-state update", blocked_output)

            env = os.environ.copy()
            env["AIOS_ALLOW_CODE_ONLY_COMMIT"] = "1"
            allowed = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--include-worktree", "--no-validate"],
                cwd=target,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            allowed_output = allowed.stdout + allowed.stderr
            self.assertEqual(allowed.returncode, 0, allowed_output)
            self.assertIn("checkpoint candidate:", allowed_output)
            self.assertIn("src/", allowed_output)
            self.assertNotIn("missing required path: .claude/settings.json", allowed_output)

            (target / ".claude" / "settings.json").unlink()
            no_validate = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--include-worktree", "--no-validate"],
                cwd=target,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            no_validate_output = no_validate.stdout + no_validate.stderr
            self.assertEqual(no_validate.returncode, 0, no_validate_output)
            self.assertNotIn("missing required path: .claude/settings.json", no_validate_output)

    def test_checkpoint_default_commit_stages_only_state_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)

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
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nState checkpoint note.\n", encoding="utf-8")
            src = target / "src"
            src.mkdir()
            (src / "unrelated.py").write_text("print('not part of truth checkpoint')\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/checkpoint.py",
                    "--auto",
                    "--message",
                    "state: checkpoint only truth layer",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            committed = subprocess.run(
                ["git", "show", "--name-only", "--format=", "HEAD"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            committed_paths = set(committed.stdout.splitlines())
            self.assertIn(".aletheia/state/ACTIVE_STATE.md", committed_paths)
            self.assertNotIn("src/unrelated.py", committed_paths)
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertIn("?? src/", status.stdout)

    def test_checkpoint_default_commit_does_not_include_pre_staged_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)

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
            src = target / "src"
            src.mkdir()
            (src / "pre_staged.py").write_text("print('user staged work')\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/pre_staged.py"], cwd=target, check=False)

            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nState checkpoint note.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/checkpoint.py",
                    "--auto",
                    "--message",
                    "state: checkpoint only truth layer",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            committed = subprocess.run(
                ["git", "show", "--name-only", "--format=", "HEAD"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            committed_paths = set(committed.stdout.splitlines())
            self.assertIn(".aletheia/state/ACTIVE_STATE.md", committed_paths)
            self.assertNotIn("src/pre_staged.py", committed_paths)
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertIn("A  src/pre_staged.py", status.stdout)

    def test_checkpoint_blocks_during_interrupted_git_operation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
            (target / ".git" / "MERGE_HEAD").write_text("pending merge\n", encoding="utf-8")

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
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nState checkpoint note.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("checkpoint blocked: git operation in progress", output)
            self.assertIn("finish or abort the current merge/rebase/cherry-pick before checkpointing", output)
            self.assertNotIn("checkpoint failed: git commit returned non-zero status", output)

    def test_checkpoint_default_output_reports_only_state_candidates(self) -> None:
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
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nState checkpoint note.\n", encoding="utf-8")
            (target / "__pycache__").mkdir()
            (target / "__pycache__" / "sample.pyc").write_bytes(b"cache")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--message", "state: dry run"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            candidate_block = output.split("checkpoint candidate:", 1)[1].split(
                "non-checkpoint worktree changes remain:",
                1,
            )[0]
            self.assertIn(".aletheia/", candidate_block)
            self.assertIn(".claude/settings.json", candidate_block)
            self.assertNotIn("__pycache__/", candidate_block)
            self.assertIn("non-checkpoint worktree changes remain", output)
            self.assertIn("__pycache__/", output)

    def test_checkpoint_default_output_excludes_generated_and_runtime_paths_from_candidates(self) -> None:
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
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nState checkpoint note.\n", encoding="utf-8")
            overview = target / ".aletheia" / "overview"
            overview.mkdir()
            (overview / "status.json").write_text("{}\n", encoding="utf-8")
            source_inventory = target / ".aletheia" / "source_inventory"
            source_inventory.mkdir()
            (source_inventory / "inventory.json").write_text("{}\n", encoding="utf-8")
            (runtime / "change_log.jsonl").write_text("{}\n", encoding="utf-8")
            subprocess.run(
                [
                    "git",
                    "add",
                    "-f",
                    ".aletheia/overview/status.json",
                    ".aletheia/source_inventory/inventory.json",
                    ".aletheia/runtime/change_log.jsonl",
                ],
                cwd=target,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run", "--message", "state: dry run"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            candidate_block = output.split("checkpoint candidate:", 1)[1].split(
                "non-checkpoint worktree changes remain:",
                1,
            )[0]
            self.assertIn(".aletheia/state/ACTIVE_STATE.md", candidate_block)
            self.assertNotIn(".aletheia/overview/status.json", candidate_block)
            self.assertNotIn(".aletheia/source_inventory/inventory.json", candidate_block)
            self.assertNotIn(".aletheia/runtime/change_log.jsonl", candidate_block)
            self.assertIn(".aletheia/overview/status.json", output)
            self.assertIn(".aletheia/source_inventory/inventory.json", output)
            self.assertIn(".aletheia/runtime/change_log.jsonl", output)

    def test_checkpoint_include_worktree_stages_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)

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
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nState plus project file checkpoint.\n", encoding="utf-8")
            src = target / "src"
            src.mkdir()
            (src / "included.py").write_text("print('included by explicit flag')\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/checkpoint.py",
                    "--auto",
                    "--include-worktree",
                    "--message",
                    "engineering: checkpoint explicit worktree",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            committed = subprocess.run(
                ["git", "show", "--name-only", "--format=", "HEAD"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            committed_paths = set(committed.stdout.splitlines())
            self.assertIn(".aletheia/state/ACTIVE_STATE.md", committed_paths)
            self.assertIn("src/included.py", committed_paths)

    def test_checkpoint_commit_excludes_forced_generated_and_runtime_paths_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)

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
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nState checkpoint note.\n", encoding="utf-8")
            overview = target / ".aletheia" / "overview"
            overview.mkdir()
            (overview / "status.json").write_text("{}\n", encoding="utf-8")
            source_inventory = target / ".aletheia" / "source_inventory"
            source_inventory.mkdir()
            (source_inventory / "inventory.json").write_text("{}\n", encoding="utf-8")
            (runtime / "change_log.jsonl").write_text("{}\n", encoding="utf-8")
            subprocess.run(
                [
                    "git",
                    "add",
                    "-f",
                    ".aletheia/overview/status.json",
                    ".aletheia/source_inventory/inventory.json",
                    ".aletheia/runtime/change_log.jsonl",
                ],
                cwd=target,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--message", "state: checkpoint"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            committed = subprocess.run(
                ["git", "show", "--name-only", "--format=", "HEAD"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            committed_paths = set(committed.stdout.splitlines())
            self.assertIn(".aletheia/state/ACTIVE_STATE.md", committed_paths)
            self.assertNotIn(".aletheia/overview/status.json", committed_paths)
            self.assertNotIn(".aletheia/source_inventory/inventory.json", committed_paths)
            self.assertNotIn(".aletheia/runtime/change_log.jsonl", committed_paths)

    def test_checkpoint_default_output_reports_truth_record_rename_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
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
            evidence = target / ".aletheia" / "evidence" / "old-name.md"
            evidence.write_text(
                "# Evidence: old name\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead docs.\n\n"
                "## Result\n\nObserved behavior.\n\n"
                "## Limitations\n\nSingle sample.\n\n"
                "## Invalidation criteria\n\nContradicting evidence.\n\n"
                "## Confidence impact\n\nRaises confidence.\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "-A"], cwd=target, check=False)
            baseline = subprocess.run(
                ["git", "commit", "-m", "test: baseline evidence"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            new_evidence = target / ".aletheia" / "evidence" / "new-name.md"
            evidence.rename(new_evidence)

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
            self.assertIn(".aletheia/evidence/new-name.md", output)
            self.assertNotIn("non-checkpoint worktree changes remain", output)


if __name__ == "__main__":
    unittest.main()
