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


if __name__ == "__main__":
    unittest.main()
