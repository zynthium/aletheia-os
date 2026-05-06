from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def init_target(target: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "init_aletheia.py"), str(target)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def run_intake(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, ".aletheia/bin/truth_intake.py", *args],
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TruthIntakeTests(unittest.TestCase):
    def test_scaffold_contains_git_native_intake_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            expected = [
                ".aletheia/truth_intake/inbox/.gitkeep",
                ".aletheia/truth_intake/runs/.gitkeep",
                ".aletheia/truth_intake/registry.json",
                ".aletheia/truth_intake/PROMOTION_LOG.md",
                ".aletheia/bin/truth_intake.py",
                ".aletheia/templates/CONVERSATION_DIGEST.md",
                ".aletheia/templates/BOOTSTRAP_SYNTHESIS_PACKET.md",
                ".aletheia/templates/FUSION_PACKET.md",
                ".aletheia/templates/PROMOTION_LOG.md",
            ]
            for rel in expected:
                self.assertTrue((target / rel).exists(), rel)

    def test_stage_dedupes_renames_and_whitespace_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            inbox = target / ".aletheia" / "truth_intake" / "inbox"
            (inbox / "research-a.md").write_text("Alpha   claim\n\nBeta observation\n", encoding="utf-8")
            (inbox / "renamed.txt").write_text("Alpha claim\nBeta   observation\n", encoding="utf-8")

            begin = run_intake(target, "begin", "--objective", "Design project")
            self.assertEqual(begin.returncode, 0, begin.stdout + begin.stderr)
            run_id = begin.stdout.strip().splitlines()[-1].split()[-1]
            stage = run_intake(target, "stage", "--run", run_id)
            self.assertEqual(stage.returncode, 0, stage.stdout + stage.stderr)

            registry = json.loads((target / ".aletheia" / "truth_intake" / "registry.json").read_text(encoding="utf-8"))
            sources = registry["sources"]
            self.assertEqual(len(sources), 1)
            source = next(iter(sources.values()))
            self.assertEqual(source["status"], "pending_digest")
            self.assertEqual(len(source["aliases"]), 2)

    def test_packet_uses_bootstrap_then_fusion_after_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            inbox = target / ".aletheia" / "truth_intake" / "inbox"
            (inbox / "initial.md").write_text("Initial objective\nArchitecture option\n", encoding="utf-8")

            begin = run_intake(target, "begin", "--objective", "Design project")
            run_id = begin.stdout.strip().splitlines()[-1].split()[-1]
            self.assertEqual(run_intake(target, "stage", "--run", run_id).returncode, 0)
            packet = run_intake(target, "packet", "--run", run_id)
            self.assertEqual(packet.returncode, 0, packet.stdout + packet.stderr)
            self.assertTrue(
                (target / ".aletheia" / "truth_intake" / "runs" / run_id / "BOOTSTRAP_SYNTHESIS_PACKET.md").exists()
            )

            promotion_log = target / ".aletheia" / "truth_intake" / "PROMOTION_LOG.md"
            promotion_log.write_text(promotion_log.read_text(encoding="utf-8") + "\nBaseline established.\n")
            (inbox / "next.md").write_text("New experiment idea\n", encoding="utf-8")
            next_begin = run_intake(target, "begin", "--objective", "Add new research")
            next_run = next_begin.stdout.strip().splitlines()[-1].split()[-1]
            self.assertEqual(run_intake(target, "stage", "--run", next_run).returncode, 0)
            fusion = run_intake(target, "packet", "--run", next_run)
            self.assertEqual(fusion.returncode, 0, fusion.stdout + fusion.stderr)
            self.assertTrue((target / ".aletheia" / "truth_intake" / "runs" / next_run / "FUSION_PACKET.md").exists())

    def test_finish_cleans_run_workspace_after_explicit_completion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            inbox = target / ".aletheia" / "truth_intake" / "inbox"
            (inbox / "research.md").write_text("Claim\n", encoding="utf-8")
            begin = run_intake(target, "begin", "--objective", "Design project")
            run_id = begin.stdout.strip().splitlines()[-1].split()[-1]
            self.assertEqual(run_intake(target, "stage", "--run", run_id).returncode, 0)
            self.assertEqual(run_intake(target, "packet", "--run", run_id).returncode, 0)

            finish = run_intake(target, "finish", "--run", run_id)
            self.assertEqual(finish.returncode, 0, finish.stdout + finish.stderr)
            self.assertFalse((target / ".aletheia" / "truth_intake" / "runs" / run_id).exists())
            self.assertFalse((inbox / "research.md").exists())
            self.assertTrue((target / ".aletheia" / "truth_intake" / "registry.json").exists())

    def test_validate_rejects_packet_claims_without_source_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            run_dir = target / ".aletheia" / "truth_intake" / "runs" / "RUN-bad"
            run_dir.mkdir(parents=True)
            (run_dir / "BOOTSTRAP_SYNTHESIS_PACKET.md").write_text(
                "# Bootstrap Synthesis Packet\n\n## Candidate Claims\n\n- Missing source ref.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/validate.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate claim missing source ref", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
