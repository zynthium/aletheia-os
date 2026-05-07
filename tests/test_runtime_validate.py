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

    def test_context_pack_includes_core_truth_files_missing_markers_and_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            charter = target / ".aletheia" / "governance" / "CHARTER.md"
            charter.write_text(
                charter.read_text(encoding="utf-8") + "\n" + ("Long charter context.\n" * 400),
                encoding="utf-8",
            )
            (target / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml").unlink()

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/context_pack.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("# AletheiaOS Project Truth Context Pack", output)
            self.assertIn("## .aletheia/governance/CHARTER.md", output)
            self.assertIn("## .aletheia/state/SYSTEM_GRAPH.yaml", output)
            self.assertIn("MISSING", output)
            self.assertIn("...[truncated]", output)

    def test_overview_records_validation_failure_and_truth_record_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "evidence" / "EV-001.md").write_text(
                "# Evidence: sample\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead project docs.\n\n"
                "## Result\n\nObserved a project fact.\n\n"
                "## Limitations\n\nSingle source.\n\n"
                "## Invalidation criteria\n\nContradicting source.\n\n"
                "## Confidence impact\n\nRaises confidence.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "decisions" / "DEC-001.md").write_text(
                "# Decision: sample\n\n"
                "Status: proposed\n\n"
                "## Context\n\nContext.\n\n"
                "## Decision\n\nDecision.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "contracts" / "CON-001.md").write_text("# Contract: sample\n", encoding="utf-8")
            (target / ".aletheia" / "hypotheses" / "HYP-001.md").write_text(
                "# Hypothesis: sample\n\n## Invalidation criteria\n\nA failed test.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "nodes" / "feature.yaml").write_text("id: feature\n", encoding="utf-8")
            (target / ".aletheia" / "risks" / "RISK-001.md").write_text("# Risk: sample\n", encoding="utf-8")
            (target / ".aletheia" / "agent_runs" / "RUN-test.json").write_text("{}\n", encoding="utf-8")
            (target / ".claude" / "settings.json").unlink()

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
            status = json.loads((target / ".aletheia" / "overview" / "status.json").read_text(encoding="utf-8"))
            self.assertNotEqual(status["validation"]["returncode"], 0)
            self.assertIn("missing required path: .claude/settings.json", status["validation"]["stderr"])
            self.assertIn(".aletheia/evidence/EV-001.md", status["records"]["evidence"])
            self.assertIn(".aletheia/decisions/DEC-001.md", status["records"]["decisions"])
            self.assertIn(".aletheia/contracts/CON-001.md", status["records"]["contracts"])
            self.assertIn(".aletheia/hypotheses/HYP-001.md", status["records"]["hypotheses"])
            self.assertIn(".aletheia/nodes/feature.yaml", status["records"]["nodes"])
            self.assertIn(".aletheia/risks/RISK-001.md", status["records"]["risks"])
            self.assertIn(".aletheia/agent_runs/RUN-test.json", status["records"]["agent_runs"])

    def test_scaffold_gitignore_marks_generated_aletheia_outputs(self) -> None:
        ignore = (ROOT / "assets" / "scaffold" / ".aletheia" / ".gitignore").read_text(encoding="utf-8")

        for pattern in ["/runtime/", "/overview/", "/source_inventory/"]:
            self.assertIn(pattern, ignore)

    def test_source_inventory_excludes_aletheia_control_plane_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/source_inventory.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            inventory = json.loads((target / ".aletheia" / "source_inventory" / "inventory.json").read_text(encoding="utf-8"))
            paths = {item["path"] for item in inventory["items"]}
            self.assertNotIn("AGENTS.md", paths)
            self.assertNotIn("START_HERE.md", paths)
            self.assertNotIn("BOOTSTRAP.md", paths)
            self.assertFalse(any(path.startswith(".aletheia/") for path in paths))
            self.assertFalse(any(path.startswith(".claude/") for path in paths))

    def test_source_inventory_classifies_sensitive_large_and_historical_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".env.local").write_text("TOKEN=secret\n", encoding="utf-8")
            reports = target / "reports"
            reports.mkdir()
            (reports / "big.csv").write_text("x" * 1_000_001, encoding="utf-8")
            archive = target / "docs" / "archive"
            archive.mkdir(parents=True)
            (archive / "old-design.md").write_text("# Old design\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/source_inventory.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            inventory = json.loads((target / ".aletheia" / "source_inventory" / "inventory.json").read_text(encoding="utf-8"))
            by_path = {item["path"]: item for item in inventory["items"]}
            self.assertEqual(by_path[".env.local"]["initial_classification"], "unsafe_or_sensitive")
            self.assertFalse(by_path[".env.local"]["should_read_full_content"])
            self.assertEqual(by_path["reports/big.csv"]["initial_classification"], "deferred_due_to_size")
            self.assertFalse(by_path["reports/big.csv"]["should_read_full_content"])
            self.assertEqual(by_path["docs/archive/old-design.md"]["initial_classification"], "historical_context")

    def test_source_inventory_skips_heavy_generated_dependency_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            for rel in [
                "node_modules/package/index.js",
                ".venv/lib/python/site-packages/lib.py",
                "target/debug/build.log",
                "vendor/library/source.c",
                ".pytest_cache/v/cache/nodeids",
            ]:
                path = target / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("generated dependency content\n", encoding="utf-8")
            (target / "src" / "main.py").parent.mkdir()
            (target / "src" / "main.py").write_text("print('project source')\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/source_inventory.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            inventory = json.loads((target / ".aletheia" / "source_inventory" / "inventory.json").read_text(encoding="utf-8"))
            paths = {item["path"] for item in inventory["items"]}
            self.assertIn("src/main.py", paths)
            self.assertFalse(any(path.startswith("node_modules/") for path in paths))
            self.assertFalse(any(path.startswith(".venv/") for path in paths))
            self.assertFalse(any(path.startswith("target/") for path in paths))
            self.assertFalse(any(path.startswith("vendor/") for path in paths))
            self.assertFalse(any(path.startswith(".pytest_cache/") for path in paths))

    def test_guided_bootstrap_detects_existing_repository_from_real_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            src = target / "src"
            src.mkdir()
            for name in ["alpha.py", "beta.py", "gamma.py"]:
                (src / name).write_text("print('project code')\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/guided_bootstrap.py", "--skip-gate", "--objective", "Initialize AletheiaOS"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            report = (target / ".aletheia" / "source_inventory" / "TRUTH_INVENTORY_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("Initialization mode: existing repository", report)

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

    def test_validate_rejects_invalid_claude_settings_json_with_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".claude" / "settings.json").write_text("{invalid json", encoding="utf-8")

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("Claude settings JSON invalid", output)
            self.assertNotIn("Traceback", output)

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

    def test_validate_rejects_evidence_record_missing_source_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            evidence = target / ".aletheia" / "evidence" / "EV-0001.md"
            evidence.write_text(
                "# Evidence: missing source refs\n\n"
                "## Method\n\nObserved behavior.\n\n"
                "## Result\n\nResult.\n\n"
                "## Limitations\n\nLimited sample.\n\n"
                "## Invalidation criteria\n\nContradicting run.\n\n"
                "## Confidence impact\n\nRaises confidence.\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("evidence record missing required section: .aletheia/evidence/EV-0001.md Source refs", output)

    def test_validate_rejects_hypothesis_missing_invalidation_criteria(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            hypothesis = target / ".aletheia" / "hypotheses" / "HYP-0001.md"
            hypothesis.write_text(
                "# Hypothesis: missing invalidation\n\n"
                "## Claim\n\nA possible explanation.\n\n"
                "## Evidence Needed\n\nA test.\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(
                "hypothesis record missing required section: .aletheia/hypotheses/HYP-0001.md Invalidation criteria",
                output,
            )

    def test_validate_rejects_accepted_decision_without_evidence_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            decision = target / ".aletheia" / "decisions" / "DEC-0001.md"
            decision.write_text(
                "# Decision: missing evidence\n\n"
                "Status: accepted\n\n"
                "## Context\n\nContext.\n\n"
                "## Decision\n\nChosen path.\n\n"
                "## Evidence links\n\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(
                "accepted decision missing evidence links: .aletheia/decisions/DEC-0001.md",
                output,
            )

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

    def test_orient_does_not_treat_following_skeleton_lists_as_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            evidence = target / ".aletheia" / "evidence" / "behavior.md"
            evidence.write_text(
                "# Evidence: behavior\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead docs.\n\n"
                "## Result\n\nObserved behavior.\n\n"
                "## Limitations\n\nSingle sample.\n\n"
                "## Invalidation criteria\n\nContradicting evidence.\n\n"
                "## Confidence impact\n\nRaises confidence.\n",
                encoding="utf-8",
            )
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8").replace(
                    "    evidence_refs: []",
                    '    evidence_refs:\n      - ".aletheia/evidence/behavior.md"',
                ),
                encoding="utf-8",
            )

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
            linked_evidence = output.split("## Linked Evidence", 1)[1].split("## Linked Contracts", 1)[0]
            self.assertIn(".aletheia/evidence/behavior.md", linked_evidence)
            self.assertNotIn("The task changes project objectives", linked_evidence)
            self.assertNotIn("The active task can be answered", linked_evidence)

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
            "EVIDENCE.md": ["Linked node", "Source refs", "Limitations", "Confidence impact"],
            "DECISION.md": ["Affected nodes", "Affected contracts", "Evidence links", "Review trigger"],
            "CONTRACT.md": ["Serves nodes", "Upstream assumptions", "Invariants", "Validation"],
            "SESSION_NOTE.md": ["Active node", "Files changed", "Truth records updated", "Checkpoint"],
        }

        for filename, phrases in expectations.items():
            text = (template_root / filename).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_change_hook_records_real_payload_with_current_agent_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            gate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "research_design",
                    "--provider",
                    "openai",
                    "--model-id",
                    "codex-e2e",
                    "--tier",
                    "C3",
                    "--operator-approved",
                    "--record",
                    "--objective",
                    "Record hook payload",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            payload = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": ".aletheia/evidence/EV-test.md"},
                "cwd": str(target),
            }

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/change_hook.py"],
                cwd=target,
                input=json.dumps(payload),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            log_path = target / ".aletheia" / "runtime" / "change_log.jsonl"
            record = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(record["event"], "PostToolUse")
            self.assertEqual(record["tool"], "Write")
            self.assertEqual(record["file_path"], ".aletheia/evidence/EV-test.md")
            self.assertEqual(record["model_id"], "codex-e2e")
            self.assertEqual(record["task_class"], "research_design")

    def test_change_hook_records_bash_command_when_file_path_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            gate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "research_design",
                    "--provider",
                    "openai",
                    "--model-id",
                    "codex-e2e",
                    "--tier",
                    "C3",
                    "--operator-approved",
                    "--record",
                    "--objective",
                    "Record bash hook payload",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            payload = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 .aletheia/bin/validate.py"},
                "cwd": str(target),
            }

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/change_hook.py"],
                cwd=target,
                input=json.dumps(payload),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            log_path = target / ".aletheia" / "runtime" / "change_log.jsonl"
            record = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(record["tool"], "Bash")
            self.assertEqual(record["command"], "python3 .aletheia/bin/validate.py")
            self.assertIsNone(record["file_path"])

    def test_stop_hook_reports_checkpoint_recommendation_and_autocommit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
            gate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--task-class",
                    "research_design",
                    "--provider",
                    "openai",
                    "--model-id",
                    "codex-e2e",
                    "--tier",
                    "C3",
                    "--operator-approved",
                    "--record",
                    "--objective",
                    "Stop hook checkpoint",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nStop hook state note.\n", encoding="utf-8")

            recommend = subprocess.run(
                [sys.executable, ".aletheia/bin/stop_hook.py"],
                cwd=target,
                input=json.dumps({"hook_event_name": "Stop"}),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            recommend_output = recommend.stdout + recommend.stderr
            self.assertEqual(recommend.returncode, 0, recommend_output)
            self.assertIn("current agent run", recommend_output)
            self.assertIn("changes detected. Recommended next command", recommend_output)

            env = os.environ.copy()
            env["AIOS_AUTOCOMMIT"] = "1"
            autocommit = subprocess.run(
                [sys.executable, ".aletheia/bin/stop_hook.py"],
                cwd=target,
                env=env,
                input=json.dumps({"hook_event_name": "Stop"}),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            autocommit_output = autocommit.stdout + autocommit.stderr
            self.assertEqual(autocommit.returncode, 0, autocommit_output)
            self.assertIn("checkpoint candidate:", autocommit_output)
            committed = subprocess.run(
                ["git", "show", "--name-only", "--format=%B", "HEAD"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertIn("AIOS-Agent-Model: codex-e2e", committed.stdout)
            self.assertIn(".aletheia/state/ACTIVE_STATE.md", committed.stdout)

    def test_stop_hook_validation_failure_does_not_recommend_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".claude" / "settings.json").unlink()

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/stop_hook.py"],
                cwd=target,
                input=json.dumps({"hook_event_name": "Stop"}),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("validation failed", output)
            self.assertIn("Do not finalize this task", output)
            self.assertNotIn("Recommended next command", output)
            self.assertNotIn("checkpoint candidate:", output)


if __name__ == "__main__":
    unittest.main()
