from __future__ import annotations

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


def init_target(target: Path) -> None:
    result = run_script("scripts/init_aletheia.py", str(target))
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def validate_target(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, ".aletheia/bin/validate.py"],
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class RuntimeValidateTests(unittest.TestCase):
    def test_overview_defaults_to_aletheia_generated_output_and_can_export_public_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/overview.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertTrue((target / ".aletheia" / "overview" / "status.json").exists())
            self.assertTrue((target / ".aletheia" / "overview" / "index.html").exists())
            self.assertFalse((target / "docs" / "overview" / "status.json").exists())

            public = subprocess.run(
                [sys.executable, ".aletheia/bin/overview.py", "--public-docs"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            public_output = public.stdout + public.stderr
            self.assertEqual(public.returncode, 0, public_output)
            self.assertTrue((target / "docs" / "overview" / "status.json").exists())

    def test_scaffold_gitignore_marks_generated_aletheia_outputs(self) -> None:
        ignore = (ROOT / "assets" / "scaffold" / ".aletheia" / ".gitignore").read_text(encoding="utf-8")

        for pattern in ["/runtime/", "/overview/", "/source_inventory/"]:
            self.assertIn(pattern, ignore)

    def test_validate_rejects_missing_claude_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".claude" / "settings.json").unlink()

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("missing required path: .claude/settings.json", output)

    def test_validate_rejects_graph_skeleton_root_child_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8").replace("      - risk_safety\n", "      - obsolete_branch\n"),
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("skeleton root children do not match system graph root children", output)

    def test_validate_rejects_missing_contract_decision_and_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                .replace("    contract_refs: []", "    contract_refs:\n      - contracts/missing.md")
                .replace("    decision_refs: []", "    decision_refs:\n      - decisions/missing.md")
                .replace("    evidence_refs: []", "    evidence_refs:\n      - evidence/missing.md"),
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("skeleton reference target missing: .aletheia/contracts/missing.md", output)
            self.assertIn("skeleton reference target missing: .aletheia/decisions/missing.md", output)
            self.assertIn("skeleton reference target missing: .aletheia/evidence/missing.md", output)

    def test_orient_outputs_truth_layer_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/orient.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("# AletheiaOS Project Truth Orientation", output)
            self.assertIn("## Project Truth", output)
            self.assertIn("## Active Frontier", output)
            self.assertIn("## Linked Evidence", output)
            self.assertIn("## Missing Or Stale Truth Warnings", output)
            self.assertIn("## Global View Checksum", output)
            for field in [
                "Root mission:",
                "Active frontier:",
                "Active node:",
                "Parent constraints:",
                "Success criteria:",
                "Invalidation criteria:",
                "Required truth updates:",
                "Verification path:",
                "Model gate status:",
                "Checkpoint plan:",
            ]:
                self.assertIn(field, output)

    def test_scaffold_attention_policy_contains_minimal_context_protocol(self) -> None:
        policy = (ROOT / "assets" / "scaffold" / ".aletheia" / "governance" / "ATTENTION_POLICY.md").read_text(
            encoding="utf-8"
        )

        for phrase in [
            "## Context tiers",
            "Tier 0",
            "Tier 4",
            "## Stop signs",
            "## Context reset protocol",
        ]:
            self.assertIn(phrase, policy)

    def test_truth_templates_keep_traceability_fields(self) -> None:
        template_root = ROOT / "assets" / "scaffold" / ".aletheia" / "templates"
        expectations = {
            "EVIDENCE.md": ["Linked node", "Limitations", "Confidence impact"],
            "DECISION.md": ["Affected nodes", "Affected contracts", "Evidence links", "Review trigger"],
            "CONTRACT.md": ["Serves nodes", "Upstream assumptions", "Invariants", "Validation"],
            "SESSION_NOTE.md": ["Active node", "Files changed", "Truth records updated", "Checkpoint"],
        }

        for filename, phrases in expectations.items():
            text = (template_root / filename).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
