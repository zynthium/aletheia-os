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


def replace_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(old, new), encoding="utf-8")


def customize_minimal_project_truth(target: Path) -> None:
    replace_text(
        target / ".aletheia" / "governance" / "CHARTER.md",
        "TBD. Define the durable project mission in one paragraph.",
        "Maintain a deterministic local utility with reviewable project truth in git.",
    )
    replace_text(
        target / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml",
        'title: "TBD Project Root"',
        'title: "Local Utility"',
    )
    replace_text(
        target / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml",
        'thesis: "TBD: define the governing project thesis."',
        'thesis: "A small local utility can remain understandable through explicit truth records."',
    )
    replace_text(
        target / ".aletheia" / "state" / "ACTIVE_STATE.md",
        "- Domain: TBD\n- Mission: TBD",
        "- Domain: local developer tooling\n- Mission: Maintain a deterministic local utility.",
    )
    replace_text(
        target / ".aletheia" / "state" / "ACTIVE_STATE.md",
        "Bootstrap AletheiaOS | root | active | project owner + AI | TBD",
        "Bootstrap AletheiaOS | root | active | project owner + Codex | `.aletheia/source_inventory/TRUTH_INVENTORY_REPORT.md`",
    )
    (target / ".aletheia" / "state" / "DOMAIN_PROFILE.md").write_text(
        "# Domain Profile\n\n"
        "## Domain\n\n"
        "Local developer tooling.\n\n"
        "## Objective Function\n\n"
        "Optimize for deterministic behavior, simple review, and explicit project truth.\n\n"
        "## Evidence Standards\n\n"
        "Behavioral claims should be backed by tests, source inspection, or explicit observations.\n\n"
        "## Failure Modes\n\n"
        "The project fails if local behavior becomes unclear or project facts drift from source behavior.\n",
        encoding="utf-8",
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

    def test_guided_bootstrap_skip_inventory_uses_existing_inventory_without_rescanning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            inventory_dir = target / ".aletheia" / "source_inventory"
            inventory_dir.mkdir(parents=True)
            inventory = {
                "items": [
                    {
                        "path": "docs/design.md",
                        "kind": "document",
                        "initial_classification": "useful_but_unverified",
                    },
                    {
                        "path": "experiments/result.md",
                        "kind": "evidence_experiment_or_simulation",
                        "initial_classification": "useful_but_unverified",
                    },
                    {
                        "path": "src/a.py",
                        "kind": "implementation_code",
                        "initial_classification": "useful_but_unverified",
                    },
                    {
                        "path": "src/b.py",
                        "kind": "implementation_code",
                        "initial_classification": "useful_but_unverified",
                    },
                    {
                        "path": "src/c.py",
                        "kind": "implementation_code",
                        "initial_classification": "useful_but_unverified",
                    },
                ]
            }
            (inventory_dir / "inventory.json").write_text(
                json.dumps(inventory, indent=2) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/guided_bootstrap.py",
                    "--skip-gate",
                    "--skip-inventory",
                    "--objective",
                    "Use existing inventory",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertNotIn("$ python3 .aletheia/bin/source_inventory.py", output)
            report = (inventory_dir / "TRUTH_INVENTORY_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("Objective: Use existing inventory", report)
            self.assertIn("Total items: 5", report)
            self.assertIn("Initialization mode: existing repository", report)

    def test_guided_bootstrap_skip_inventory_requires_existing_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/guided_bootstrap.py", "--skip-gate", "--skip-inventory"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("source inventory missing", output)
            self.assertIn("source_inventory.py", output)

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

    def test_existing_project_bootstrap_finalize_creates_truth_checkpoint_without_touching_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
            (target / "README.md").write_text("# Existing Utility\n\nA local utility.\n", encoding="utf-8")
            (target / "utility.py").write_text("def run():\n    return 'ok'\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md", "utility.py"], cwd=target, check=False)
            initial = subprocess.run(
                ["git", "commit", "-m", "initial utility"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
            original_readme = (target / "README.md").read_text(encoding="utf-8")
            original_source = (target / "utility.py").read_text(encoding="utf-8")

            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            gate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "bootstrap_finalize",
                    "--provider",
                    "openai",
                    "--model-id",
                    "codex-e2e",
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
            inventory = subprocess.run(
                [sys.executable, ".aletheia/bin/source_inventory.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(inventory.returncode, 0, inventory.stdout + inventory.stderr)
            customize_minimal_project_truth(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/bootstrap_finalize.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertFalse((target / "BOOTSTRAP.md").exists())
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), original_readme)
            self.assertEqual((target / "utility.py").read_text(encoding="utf-8"), original_source)
            hooks_path = subprocess.run(
                ["git", "config", "core.hooksPath"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(hooks_path.stdout.strip(), ".aletheia/hooks")
            committed = subprocess.run(
                ["git", "show", "--name-only", "--format=%B", "HEAD"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertIn("bootstrap: initialize AletheiaOS", committed.stdout)
            self.assertIn("AIOS-Agent-Model: codex-e2e", committed.stdout)
            self.assertIn(".aletheia/governance/CHARTER.md", committed.stdout)
            self.assertNotIn("utility.py", committed.stdout)

    def test_bootstrap_finalize_keep_bootstrap_no_checkpoint_installs_hooks_without_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            gate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "bootstrap_finalize",
                    "--provider",
                    "openai",
                    "--model-id",
                    "codex-e2e",
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
            customize_minimal_project_truth(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/bootstrap_finalize.py", "--keep-bootstrap", "--no-checkpoint"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("bootstrap finalized", output)
            self.assertTrue((target / "BOOTSTRAP.md").exists())
            self.assertTrue((target / ".aletheia" / "hooks" / "pre-commit").exists())
            hooks_path = subprocess.run(
                ["git", "config", "core.hooksPath"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(hooks_path.stdout.strip(), ".aletheia/hooks")
            log = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(log.stdout.strip(), "")

    def test_installed_pre_commit_hook_blocks_invalid_truth_layer_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            gate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "bootstrap_finalize",
                    "--provider",
                    "openai",
                    "--model-id",
                    "codex-e2e",
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
            customize_minimal_project_truth(target)
            finalize = subprocess.run(
                [sys.executable, ".aletheia/bin/bootstrap_finalize.py", "--no-checkpoint"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)
            (target / ".claude" / "settings.json").unlink()
            subprocess.run(["git", "add", "-A"], cwd=target, check=False)

            commit = subprocess.run(
                ["git", "commit", "-m", "test: invalid truth layer"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = commit.stdout + commit.stderr
            self.assertNotEqual(commit.returncode, 0, output)
            self.assertIn("AletheiaOS validation failed", output)
            self.assertIn("missing required path: .claude/settings.json", output)


if __name__ == "__main__":
    unittest.main()
