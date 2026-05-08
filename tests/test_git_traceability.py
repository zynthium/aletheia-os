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


def init_git_repo(target: Path) -> None:
    subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)


def scaffold_git_repo(target: Path) -> None:
    init = run_script("scripts/init_aletheia.py", str(target))
    if init.returncode != 0:
        raise AssertionError(init.stderr)
    init_git_repo(target)
    subprocess.run(["git", "add", "-A"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    baseline = subprocess.run(
        ["git", "commit", "-m", "test: baseline scaffold"],
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if baseline.returncode != 0:
        raise AssertionError(baseline.stdout + baseline.stderr)


def run_commit_msg_hook(target: Path, message: str) -> subprocess.CompletedProcess[str]:
    message_file = target / ".git" / "COMMIT_EDITMSG"
    message_file.write_text(message, encoding="utf-8")
    return subprocess.run(
        [sys.executable, ".aletheia/bin/commit_msg_hook.py", str(message_file)],
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


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

    def test_commit_msg_hook_allows_normal_readme_commit_without_aios_trailers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            scaffold_git_repo(target)
            (target / "README.md").write_text("# Project\n\nUpdated overview.\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=target, check=False)

            result = run_commit_msg_hook(target, "docs: update readme\n")

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertNotIn("AletheiaOS commit message blocked:", output)

    def test_commit_msg_hook_rejects_skeleton_change_without_tree_traceability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            scaffold_git_repo(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(skeleton.read_text(encoding="utf-8") + "\n# staged tree change\n", encoding="utf-8")
            subprocess.run(["git", "add", ".aletheia/state/SKELETON.yaml"], cwd=target, check=False)

            result = run_commit_msg_hook(target, "truth: update skeleton\n")

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("AletheiaOS commit message blocked:", output)
            self.assertIn("tree-sensitive changes require AIOS-Action", output)
            self.assertIn("tree-sensitive changes require AIOS-Tree-Op or AIOS-Node-State", output)

    def test_commit_msg_hook_rejects_stable_marker_without_required_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            scaffold_git_repo(target)

            result = run_commit_msg_hook(
                target,
                "truth: stabilize theory\n\n"
                "AIOS-Action: truth.node.stabilize\n"
                "AIOS-Node-State: stable\n",
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("AletheiaOS commit message blocked:", output)
            self.assertIn("stable node marker requires AIOS-Node", output)
            self.assertIn("stable node marker requires AIOS-Evidence", output)
            self.assertIn("stable node marker requires AIOS-Decision", output)
            self.assertIn("stable node marker requires AIOS-Validation: pass", output)
            self.assertIn("stable node marker requires AIOS-Review: human-confirmed", output)

    def test_commit_msg_hook_accepts_valid_stable_marker_with_existing_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            scaffold_git_repo(target)
            evidence = target / ".aletheia" / "evidence" / "EV-001-factor-baseline.md"
            evidence.write_text("# Evidence: factor baseline\n", encoding="utf-8")
            decision = target / ".aletheia" / "decisions" / "DEC-001-modeling-lens-policy.md"
            decision.write_text("# Decision: modeling lens policy\n\nStatus: accepted\n", encoding="utf-8")
            subprocess.run(
                [
                    "git",
                    "add",
                    ".aletheia/evidence/EV-001-factor-baseline.md",
                    ".aletheia/decisions/DEC-001-modeling-lens-policy.md",
                ],
                cwd=target,
                check=False,
            )

            result = run_commit_msg_hook(
                target,
                "truth: stabilize theory\n\n"
                "AIOS-Action: truth.node.stabilize\n"
                "AIOS-Node: theory_model\n"
                "AIOS-Node-State: stable\n"
                "AIOS-Evidence: .aletheia/evidence/EV-001-factor-baseline.md\n"
                "AIOS-Decision: .aletheia/decisions/DEC-001-modeling-lens-policy.md\n"
                "AIOS-Validation: pass\n"
                "AIOS-Review: human-confirmed\n",
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertNotIn("AletheiaOS commit message blocked:", output)


if __name__ == "__main__":
    unittest.main()
