from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
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
            status = json.loads((target / ".aletheia" / "overview" / "status.json").read_text(encoding="utf-8"))
            self.assertIn("Generated/runtime outputs", status["durability_note"])
            self.assertIn("truth.preflight", status["recommended_actions"])
            self.assertIn("truth.history_audit", status["recommended_actions"])
            self.assertIn("python3 .aletheia/bin/status.py --json", status["next_actions"])
            self.assertIn("python3 .aletheia/bin/history_audit.py --json", status["next_actions"])
            self.assertIn("history_audit", status)
            self.assertIn("returncode", status["history_audit"])
            self.assertTrue(any(item["path"] == ".aletheia/overview/" for item in status["generated_outputs"]))
            html = (target / ".aletheia" / "overview" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Git Truth History", html)

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

    def test_overview_reports_output_path_conflict_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "overview").write_text("occupied\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/overview.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("overview output path exists and is not a directory", output)
            self.assertNotIn("Traceback", output)

    def test_status_refresh_reports_active_state_validation_records_and_runtime_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "runtime").mkdir()
            (target / ".aletheia" / "runtime" / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-status",
                        "provider": "openai",
                        "model_id": "gpt-test",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                        "objective": "Refresh status",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "evidence" / "EV-001.md").write_text(
                "# Evidence: sample\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead docs.\n\n"
                "## Result\n\nResult.\n\n"
                "## Limitations\n\nSingle source.\n\n"
                "## Invalidation criteria\n\nContradiction.\n\n"
                "## Confidence impact\n\nRaises confidence.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("# AletheiaOS Status Refresh", output)
            self.assertIn("## Durability", output)
            self.assertIn("## Active State", output)
            self.assertIn("- active nodes: root", output)
            self.assertIn("- current phase: bootstrap", output)
            self.assertIn("## Validation", output)
            self.assertIn("- returncode: 0", output)
            self.assertIn("## Git Truth History", output)
            self.assertIn("- returncode: 0", output)
            self.assertIn("## Records", output)
            self.assertIn("- evidence: 1", output)
            self.assertIn("## Tree Health", output)
            self.assertIn("- skeleton nodes:", output)
            self.assertIn("- orphan count: 0", output)
            self.assertIn("- stale orphan count: 0", output)
            self.assertIn("- tree warning count: 0", output)
            self.assertIn("- tree error count: 0", output)
            self.assertIn("- review needed: False", output)
            self.assertIn("## Runtime Gate", output)
            self.assertIn("- run_id: RUN-status", output)
            self.assertIn("- gate_status: allowed", output)
            self.assertIn("## Generated Outputs", output)
            self.assertIn(".aletheia/overview/", output)
            self.assertIn("## Next Actions", output)
            self.assertIn("truth.checkpoint.dry_run", output)
            self.assertNotIn("Traceback", output)

    def test_status_refresh_surfaces_recent_runtime_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir()
            (runtime / "change_log.jsonl").write_text(
                json.dumps(
                    {
                        "ts": "2026-05-08T00:00:00+00:00",
                        "event": "PostToolUse",
                        "tool": "Write",
                        "file_path": ".aletheia/evidence/EV-001.md",
                        "model_id": "gpt-test",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("## Recent Changes", output)
            self.assertIn(".aletheia/evidence/EV-001.md", output)
            self.assertIn("model=gpt-test", output)

            as_json = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(as_json.returncode, 0, as_json.stdout + as_json.stderr)
            payload = json.loads(as_json.stdout)
            self.assertEqual(payload["recent_changes"][0]["file_path"], ".aletheia/evidence/EV-001.md")

    def test_status_refresh_can_emit_json_for_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["active_state"]["active_nodes"], ["root"])
            self.assertEqual(payload["active_state"]["current_phase"], "bootstrap")
            self.assertEqual(payload["validation"]["returncode"], 0)
            self.assertIn("decisions", payload["records"])
            self.assertIn("Generated/runtime outputs", payload["durability_note"])
            self.assertIn("truth.preflight", payload["recommended_actions"])
            self.assertIn("python3 .aletheia/bin/checkpoint.py --dry-run", payload["next_actions"])
            self.assertIn("python3 .aletheia/bin/history_audit.py --json", payload["next_actions"])
            self.assertTrue(any(item["path"] == ".aletheia/runtime/" for item in payload["generated_outputs"]))
            self.assertIn("history_audit", payload)
            self.assertIn("returncode", payload["history_audit"])
            self.assertEqual(payload["history_audit"]["error_count"], 0)
            self.assertEqual(payload["history_audit"]["warning_count"], 0)
            self.assertEqual(payload["tree_health"]["stale_orphan_count"], 0)
            self.assertEqual(payload["tree_health"]["warning_count"], 0)
            self.assertEqual(payload["tree_health"]["error_count"], 0)
            self.assertFalse(payload["tree_health"]["review_needed"])
            self.assertIsNone(payload["runtime_gate"])

    def test_validate_json_reports_structured_errors_and_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans:\n"
                "  - id: OR-json\n"
                "    status: incubating\n"
                "    summary: JSON validation warning\n"
                "    candidate_parent: root\n"
                f"    next_review: {yesterday}\n",
                encoding="utf-8",
            )
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  detached_json_leaf:\n"
                "    layer: leaf\n"
                "    parent: root\n"
                "    children: []\n"
                "    purpose: \"Detached leaf for JSON validation.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.1\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/validate.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["returncode"], 1)
            self.assertTrue(any("orphan review is stale: OR-json" == warning for warning in payload["warnings"]))
            self.assertTrue(
                any("skeleton parent missing child link: detached_json_leaf parent=root" == error for error in payload["errors"])
            )

    def test_status_tree_health_uses_structured_validation_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans:\n"
                "  - id: OR-json-health\n"
                "    status: incubating\n"
                "    summary: Structured status warning\n"
                "    candidate_parent: root\n"
                f"    next_review: {yesterday}\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["validation"]["returncode"], 0)
            self.assertIn("warnings", payload["validation"])
            self.assertIn("errors", payload["validation"])
            self.assertEqual(payload["validation"]["stderr"], "")
            self.assertEqual(payload["tree_health"]["stale_orphan_count"], 1)
            self.assertIn("orphan review is stale: OR-json-health", payload["tree_health"]["semantic_review_signals"])
            self.assertEqual(payload["tree_health"]["structural_error_signals"], [])

    def test_preflight_reports_validation_gate_and_checkpoint_candidate_for_no_hooks_hosts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-preflight",
                        "provider": "openai",
                        "model_id": "gpt-test",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nPreflight state note.\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/preflight.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["runtime_gate"]["run_id"], "RUN-preflight")
            self.assertEqual(payload["validation"]["returncode"], 0)
            self.assertIn("warnings", payload["validation"])
            self.assertIn("errors", payload["validation"])
            self.assertTrue(payload["checkpoint"]["has_candidate"])
            self.assertIn(".aletheia/state/ACTIVE_STATE.md", payload["checkpoint"]["candidate_files"])
            self.assertIn("context", payload)
            self.assertEqual(payload["context"]["active_nodes"], ["root"])
            self.assertIn("python3 .aletheia/bin/orient.py --with-runtime", payload["next_actions"])
            self.assertIn("python3 .aletheia/bin/status.py --json", payload["next_actions"])
            self.assertIn("python3 .aletheia/bin/history_audit.py --json", payload["next_actions"])
            self.assertIn("python3 .aletheia/bin/checkpoint.py --dry-run", payload["next_actions"])
            self.assertIn("truth.orient.runtime", payload["recommended_actions"])
            self.assertIn("truth.status", payload["recommended_actions"])
            self.assertIn("truth.history_audit", payload["recommended_actions"])
            self.assertIn("truth.checkpoint.dry_run", payload["recommended_actions"])
            self.assertIn("history_audit", payload)
            self.assertIn("returncode", payload["history_audit"])
            self.assertIn("Generated/runtime outputs", payload["durability_note"])
            self.assertTrue(any(item["path"] == ".aletheia/source_inventory/" for item in payload["generated_outputs"]))

    def test_preflight_validation_uses_structured_json_warnings_and_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans:\n"
                "  - id: OR-preflight-json\n"
                "    status: incubating\n"
                "    summary: Structured preflight warning\n"
                "    candidate_parent: root\n"
                f"    next_review: {yesterday}\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/preflight.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["validation"]["returncode"], 0)
            self.assertIn("orphan review is stale: OR-preflight-json", payload["validation"]["warnings"])
            self.assertEqual(payload["validation"]["errors"], [])
            self.assertEqual(payload["validation"]["stderr"], "")

    def test_action_layer_lists_explains_runs_and_recommends_agent_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            listed = subprocess.run(
                [sys.executable, ".aletheia/bin/action.py", "list", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(listed.returncode, 0, listed.stdout + listed.stderr)
            list_payload = json.loads(listed.stdout)
            self.assertEqual(list_payload["schema_version"], 1)
            action_ids = {action["id"] for action in list_payload["actions"]}
            self.assertIn("truth.validate", action_ids)
            self.assertIn("truth.preflight", action_ids)
            self.assertIn("truth.history_audit", action_ids)
            self.assertIn("truth.checkpoint.dry_run", action_ids)
            self.assertIn("truth.bootstrap.guided.inspect", action_ids)
            self.assertIn("truth.bootstrap.finalize.inspect", action_ids)

            explained = subprocess.run(
                [sys.executable, ".aletheia/bin/action.py", "explain", "truth.validate", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(explained.returncode, 0, explained.stdout + explained.stderr)
            explain_payload = json.loads(explained.stdout)
            self.assertEqual(explain_payload["action"]["id"], "truth.validate")
            self.assertEqual(explain_payload["action"]["risk"], "read-only")
            self.assertEqual(explain_payload["action"]["verification"]["returncode"], 0)

            ran = subprocess.run(
                [sys.executable, ".aletheia/bin/action.py", "run", "truth.validate", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
            run_payload = json.loads(ran.stdout)
            self.assertEqual(run_payload["action_id"], "truth.validate")
            self.assertEqual(run_payload["result"]["returncode"], 0)
            self.assertTrue(run_payload["verification"]["passed"])

            listed_records = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/action.py",
                    "run",
                    "truth.record.list",
                    "--arg",
                    "entity=decisions",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(listed_records.returncode, 0, listed_records.stdout + listed_records.stderr)
            record_payload = json.loads(listed_records.stdout)
            self.assertEqual(record_payload["action_id"], "truth.record.list")
            self.assertIn("decisions", record_payload["command"])
            self.assertTrue(record_payload["verification"]["passed"])

            bootstrap_inspect = subprocess.run(
                [sys.executable, ".aletheia/bin/action.py", "run", "truth.bootstrap.guided.inspect", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(bootstrap_inspect.returncode, 0, bootstrap_inspect.stdout + bootstrap_inspect.stderr)
            inspect_payload = json.loads(bootstrap_inspect.stdout)
            self.assertEqual(inspect_payload["action_id"], "truth.bootstrap.guided.inspect")
            self.assertTrue(inspect_payload["verification"]["passed"])
            self.assertIn('"ready": false', inspect_payload["result"]["stdout"])

            blocked_write = subprocess.run(
                [sys.executable, ".aletheia/bin/action.py", "run", "truth.checkpoint.create"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertNotEqual(blocked_write.returncode, 0, blocked_write.stdout + blocked_write.stderr)
            self.assertIn("requires --confirm-risk", blocked_write.stderr)

            next_result = subprocess.run(
                [sys.executable, ".aletheia/bin/action.py", "next", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(next_result.returncode, 0, next_result.stdout + next_result.stderr)
            next_payload = json.loads(next_result.stdout)
            self.assertIn("truth.orient.runtime", next_payload["recommended_actions"])
            self.assertIn("truth.status", next_payload["recommended_actions"])
            self.assertIn("truth.preflight", next_payload["recommended_actions"])
            self.assertIn("truth.validate", next_payload["recommended_actions"])
            self.assertIn("truth.history_audit", next_payload["recommended_actions"])
            self.assertIn("truth.checkpoint.dry_run", next_payload["recommended_actions"])

    def test_preflight_markdown_names_codex_no_hooks_use_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/preflight.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("# AletheiaOS Preflight", output)
            self.assertIn("Use this on hosts without automatic hook enforcement", output)
            self.assertIn("## Durability", output)
            self.assertIn("## Validation", output)
            self.assertIn("## Git Truth History", output)
            self.assertIn("## Checkpoint Candidate", output)
            self.assertIn("## Generated Outputs", output)
            self.assertIn("## Next Actions", output)

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

    def test_help_outputs_outcome_level_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/help.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("# AletheiaOS Capabilities", output)
            self.assertIn("## What you can ask", output)
            for phrase in [
                "Initialize project truth",
                "Orient on current truth",
                "Refresh context",
                "Create truth records",
                "Validate and checkpoint",
                "Audit Git truth history",
                "Review truth alignment",
            ]:
                self.assertIn(phrase, output)
            self.assertIn("## Runtime commands", output)
            self.assertIn("python3 .aletheia/bin/orient.py", output)
            self.assertIn("python3 .aletheia/bin/history_audit.py --json", output)
            self.assertIn("python3 .aletheia/bin/truth_record.py update evidence EV-0001", output)
            self.assertIn("python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --candidate-parent", output)
            self.assertIn("archive-only", output)

    def test_context_pack_defaults_to_stable_capabilities_source_summary_and_record_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / "src").mkdir()
            (target / "src" / "main.py").write_text("print('project code')\n", encoding="utf-8")
            (target / ".env.local").write_text("TOKEN=secret\n", encoding="utf-8")
            (target / "reports").mkdir()
            (target / "reports" / "big.csv").write_text("x" * 1_000_001, encoding="utf-8")
            (target / ".aletheia" / "runtime").mkdir()
            (target / ".aletheia" / "runtime" / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-test",
                        "provider": "openai",
                        "model_id": "gpt-test",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "session_notes" / "2026-05-07-note.md").write_text(
                "# Session Note: recent work\n\nSummary.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "evidence" / "EV-001.md").write_text(
                "# Evidence: sample\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead docs.\n\n"
                "## Result\n\nResult.\n\n"
                "## Limitations\n\nSingle source.\n\n"
                "## Invalidation criteria\n\nContradiction.\n\n"
                "## Confidence impact\n\nRaises confidence.\n",
                encoding="utf-8",
            )
            inventory = subprocess.run(
                [sys.executable, ".aletheia/bin/source_inventory.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(inventory.returncode, 0, inventory.stdout + inventory.stderr)

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
            self.assertIn("## .aletheia/CAPABILITY_MAP.md", output)
            self.assertIn("Initialize AletheiaOS scaffold", output)
            self.assertIn("## Source Inventory Summary", output)
            self.assertIn("- total items: 3", output)
            self.assertIn("- implementation_code: 1", output)
            self.assertIn("- data_or_report: 1", output)
            self.assertIn("- unsafe_or_sensitive: 1", output)
            self.assertIn("- deferred_due_to_size: 1", output)
            self.assertIn("- full content candidates: 1", output)
            self.assertNotIn("## Current Agent Run", output)
            self.assertNotIn("RUN-test", output)
            self.assertNotIn("## Recent Session Notes", output)
            self.assertNotIn("Summary.", output)
            self.assertIn("## Truth Record Inventory", output)
            self.assertIn(".aletheia/evidence/EV-001.md", output)
            self.assertLess(output.index("## Source Inventory Summary"), output.index("## Truth Record Inventory"))

    def test_context_pack_can_append_runtime_context_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "runtime").mkdir()
            (target / ".aletheia" / "runtime" / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-test",
                        "provider": "openai",
                        "model_id": "gpt-test",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "session_notes" / "2026-05-07-note.md").write_text(
                "# Session Note: recent work\n\nSummary.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/context_pack.py", "--with-runtime"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("## Source Inventory Summary", output)
            self.assertIn("## Truth Record Inventory", output)
            self.assertIn("## Current Agent Run", output)
            self.assertIn("RUN-test", output)
            self.assertIn("## Recent Session Notes", output)
            self.assertIn(".aletheia/session_notes/2026-05-07-note.md", output)
            self.assertLess(output.index("## Truth Record Inventory"), output.index("## Current Agent Run"))

    def test_system_context_outputs_prompt_ready_context_with_preferences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            preferences = target / ".aletheia" / "state" / "USER_PREFERENCES.md"
            preferences.write_text(
                "# User Preferences\n\n## Communication\n\n- Keep updates concise.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/system_context.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("# AletheiaOS Prompt Context", output)
            self.assertIn("## User Preferences", output)
            self.assertIn("Keep updates concise.", output)
            self.assertIn("## Project Context Pack", output)
            self.assertIn("# AletheiaOS Project Truth Context Pack", output)
            self.assertNotIn("## Current Agent Run", output)

    def test_system_context_can_emit_json_with_runtime_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "runtime").mkdir()
            (target / ".aletheia" / "runtime" / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-system-context",
                        "provider": "openai",
                        "model_id": "gpt-test",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/system_context.py", "--with-runtime", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["with_runtime"])
            self.assertIn("RUN-system-context", payload["prompt"])

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
            self.assertIn("missing required path: .claude/settings.json", status["validation"]["errors"])
            self.assertIn(".aletheia/evidence/EV-001.md", status["records"]["evidence"])
            self.assertIn(".aletheia/decisions/DEC-001.md", status["records"]["decisions"])
            self.assertIn(".aletheia/contracts/CON-001.md", status["records"]["contracts"])
            self.assertIn(".aletheia/hypotheses/HYP-001.md", status["records"]["hypotheses"])
            self.assertIn(".aletheia/nodes/feature.yaml", status["records"]["nodes"])
            self.assertIn(".aletheia/risks/RISK-001.md", status["records"]["risks"])
            self.assertIn(".aletheia/agent_runs/RUN-test.json", status["records"]["agent_runs"])
            self.assertIn("tree_health", status)
            self.assertIn("skeleton_nodes", status["tree_health"])
            self.assertIn("orphan_count", status["tree_health"])
            self.assertIn("stale_orphan_count", status["tree_health"])
            self.assertIn("warning_count", status["tree_health"])
            self.assertIn("error_count", status["tree_health"])
            self.assertIn("review_needed", status["tree_health"])

    def test_overview_surfaces_recent_runtime_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir()
            (runtime / "change_log.jsonl").write_text(
                json.dumps(
                    {
                        "ts": "2026-05-08T00:00:00+00:00",
                        "event": "PostToolUse",
                        "tool": "Bash",
                        "command": "python3 .aletheia/bin/validate.py",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

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
            self.assertEqual(status["recent_changes"][0]["command"], "python3 .aletheia/bin/validate.py")
            html = (target / ".aletheia" / "overview" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Recent changes", html)
            self.assertIn("python3 .aletheia/bin/validate.py", html)
            self.assertIn("Tree health", html)
            self.assertIn("Generated outputs", html)
            self.assertIn("Next actions", html)

    def test_tree_governance_context_surfaces_orphans_and_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans:\n"
                "  - id: OR-001\n"
                "    status: incubating\n"
                "    summary: Candidate unmounted claim\n"
                "    candidate_parent: root\n"
                "    source_refs: []\n"
                f"    next_review: {yesterday}\n",
                encoding="utf-8",
            )

            orient = subprocess.run(
                [sys.executable, ".aletheia/bin/orient.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(orient.returncode, 0, orient.stdout + orient.stderr)
            self.assertIn("## Tree Governance", orient.stdout)
            self.assertIn("## Tree Health Lens", orient.stdout)
            self.assertIn("Semantic review signals", orient.stdout)
            self.assertIn("Structural errors", orient.stdout)
            self.assertIn("## Incubator Orphans", orient.stdout)
            self.assertIn("OR-001", orient.stdout)

            status = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            payload = json.loads(status.stdout)
            self.assertEqual(payload["tree_health"]["orphan_count"], 1)
            self.assertEqual(payload["tree_health"]["stale_orphan_count"], 1)
            self.assertEqual(payload["tree_health"]["semantic_review_count"], payload["tree_health"]["warning_count"])
            self.assertEqual(payload["tree_health"]["structural_error_count"], 0)
            self.assertTrue(payload["tree_health"]["human_review_needed"])
            self.assertTrue(
                any("orphan review is stale" in signal.lower() for signal in payload["tree_health"]["semantic_review_signals"])
            )
            self.assertEqual(payload["tree_health"]["structural_error_signals"], [])
            self.assertGreaterEqual(payload["tree_health"]["warning_count"], 1)
            self.assertEqual(payload["tree_health"]["error_count"], 0)
            self.assertTrue(payload["tree_health"]["review_needed"])
            self.assertTrue(any("orphan" in signal.lower() for signal in payload["tree_health"]["signals"]))

            overview = subprocess.run(
                [sys.executable, ".aletheia/bin/overview.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(overview.returncode, 0, overview.stdout + overview.stderr)
            overview_status = json.loads((target / ".aletheia" / "overview" / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(overview_status["tree_health"]["orphan_count"], 1)
            self.assertEqual(overview_status["tree_health"]["stale_orphan_count"], 1)
            self.assertEqual(overview_status["tree_health"]["semantic_review_count"], overview_status["tree_health"]["warning_count"])
            self.assertEqual(overview_status["tree_health"]["structural_error_count"], 0)
            self.assertTrue(overview_status["tree_health"]["human_review_needed"])
            self.assertGreaterEqual(overview_status["tree_health"]["warning_count"], 1)
            self.assertEqual(overview_status["tree_health"]["error_count"], 0)
            self.assertTrue(overview_status["tree_health"]["review_needed"])
            self.assertIn("warnings", overview_status["validation"])
            self.assertIn("errors", overview_status["validation"])
            self.assertIn("orphan review is stale: OR-001", overview_status["validation"]["warnings"])

            validate = validate_target(target)
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            self.assertIn("orphan review is stale: OR-001", validate.stdout)

    def test_orphan_stale_review_uses_current_date_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            today = date.today().isoformat()
            tomorrow = (date.today() + timedelta(days=1)).isoformat()
            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans:\n"
                "  - id: OR-stale\n"
                "    status: incubating\n"
                "    summary: Stale review\n"
                "    candidate_parent: root\n"
                f"    next_review: {yesterday}\n"
                "  - id: OR-today\n"
                "    status: incubating\n"
                "    summary: Review today\n"
                "    candidate_parent: root\n"
                f"    next_review: {today}\n"
                "  - id: OR-future\n"
                "    status: incubating\n"
                "    summary: Future review\n"
                "    candidate_parent: root\n"
                f"    next_review: {tomorrow}\n",
                encoding="utf-8",
            )

            status = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            payload = json.loads(status.stdout)
            signals = "\n".join(payload["tree_health"]["signals"])
            self.assertEqual(payload["tree_health"]["stale_orphan_count"], 1)
            self.assertIn("OR-stale", signals)
            self.assertNotIn("OR-today", signals)
            self.assertNotIn("OR-future", signals)

    def test_status_separates_tree_semantic_review_from_structural_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  detached_leaf:\n"
                "    layer: leaf\n"
                "    parent: root\n"
                "    children: []\n"
                "    purpose: \"Intentionally detached leaf for structural health classification.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.1\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )

            status = subprocess.run(
                [sys.executable, ".aletheia/bin/status.py", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            payload = json.loads(status.stdout)
            self.assertEqual(payload["validation"]["returncode"], 1)
            self.assertEqual(payload["tree_health"]["semantic_review_count"], 0)
            self.assertGreaterEqual(payload["tree_health"]["structural_error_count"], 1)
            self.assertFalse(payload["tree_health"]["human_review_needed"])
            self.assertTrue(payload["tree_health"]["structural_fix_needed"])
            self.assertTrue(
                any("skeleton parent missing child link" in signal for signal in payload["tree_health"]["structural_error_signals"])
            )

    def test_overview_tree_health_uses_structured_validation_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  detached_overview_leaf:\n"
                "    layer: leaf\n"
                "    parent: root\n"
                "    children: []\n"
                "    purpose: \"Detached leaf for structured overview health.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.1\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/overview.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads((target / ".aletheia" / "overview" / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["validation"]["returncode"], 1)
            self.assertIn("warnings", payload["validation"])
            self.assertIn("errors", payload["validation"])
            self.assertEqual(payload["tree_health"]["semantic_review_count"], 0)
            self.assertGreaterEqual(payload["tree_health"]["structural_error_count"], 1)
            self.assertFalse(payload["tree_health"]["human_review_needed"])
            self.assertTrue(payload["tree_health"]["structural_fix_needed"])
            self.assertTrue(
                any(
                    "skeleton parent missing child link" in signal
                    for signal in payload["tree_health"]["structural_error_signals"]
                )
            )

    def test_overview_can_watch_for_refresh_iterations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/overview.py", "--watch", "--interval", "0", "--iterations", "2"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertGreaterEqual(output.count("overview written:"), 2)
            status = json.loads((target / ".aletheia" / "overview" / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["refresh"]["mode"], "watch")
            self.assertEqual(status["refresh"]["iteration"], 2)

    def test_truth_record_script_creates_lists_shows_and_archives_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            create = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "evidence",
                    "--id",
                    "EV-0001",
                    "--title",
                    "Source-backed claim",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            create_output = create.stdout + create.stderr
            self.assertEqual(create.returncode, 0, create_output)
            record = target / ".aletheia" / "evidence" / "EV-0001.md"
            self.assertTrue(record.exists())
            text = record.read_text(encoding="utf-8")
            self.assertIn("# Evidence: Source-backed claim", text)
            self.assertIn("Claim tested: Source-backed claim", text)

            listing = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "list", "evidence"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            listing_output = listing.stdout + listing.stderr
            self.assertEqual(listing.returncode, 0, listing_output)
            self.assertIn(".aletheia/evidence/EV-0001.md", listing_output)

            show = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "show", "evidence", "EV-0001"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            show_output = show.stdout + show.stderr
            self.assertEqual(show.returncode, 0, show_output)
            self.assertIn("# Evidence: Source-backed claim", show_output)

            archive = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "archive",
                    "evidence",
                    "EV-0001",
                    "--reason",
                    "Superseded by later evidence.",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            archive_output = archive.stdout + archive.stderr
            self.assertEqual(archive.returncode, 0, archive_output)
            archived = record.read_text(encoding="utf-8")
            self.assertIn("Status: archived", archived)
            self.assertIn("Archive reason: Superseded by later evidence.", archived)

    def test_truth_record_script_updates_records_and_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            create = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "evidence",
                    "--id",
                    "EV-0001",
                    "--title",
                    "Initial claim",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

            update = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "update",
                    "evidence",
                    "EV-0001",
                    "--title",
                    "Updated claim",
                    "--status",
                    "active",
                    "--section",
                    "Result",
                    "--content",
                    "Observed project behavior supports the updated claim.",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            update_output = update.stdout + update.stderr
            self.assertEqual(update.returncode, 0, update_output)
            payload = json.loads(update.stdout)
            self.assertEqual(payload["action"], "update")
            self.assertEqual(payload["entity"], "evidence")
            self.assertEqual(payload["path"], ".aletheia/evidence/EV-0001.md")
            self.assertEqual(payload["updated"], ["title", "status", "section:Result"])

            text = (target / ".aletheia" / "evidence" / "EV-0001.md").read_text(encoding="utf-8")
            self.assertIn("# Evidence: Updated claim", text)
            self.assertIn("Status: active", text)
            self.assertIn("## Result\n\nObserved project behavior supports the updated claim.", text)

            show = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "show", "evidence", "EV-0001", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(show.returncode, 0, show.stdout + show.stderr)
            show_payload = json.loads(show.stdout)
            self.assertEqual(show_payload["path"], ".aletheia/evidence/EV-0001.md")
            self.assertIn("# Evidence: Updated claim", show_payload["content"])

    def test_truth_record_script_updates_yaml_records_and_lists_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            create = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "node",
                    "--id",
                    "feature_node",
                    "--title",
                    "Feature Node",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

            update = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "update",
                    "node",
                    "feature_node",
                    "--title",
                    "Updated Feature Node",
                    "--status",
                    "active",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            payload = json.loads(update.stdout)
            self.assertEqual(payload["updated"], ["title", "status"])

            node_text = (target / ".aletheia" / "nodes" / "feature_node.yaml").read_text(encoding="utf-8")
            self.assertIn("title: Updated Feature Node", node_text)
            self.assertIn("status: active", node_text)

            listing = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "list", "nodes", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(listing.returncode, 0, listing.stdout + listing.stderr)
            listing_payload = json.loads(listing.stdout)
            self.assertEqual(listing_payload["entity"], "nodes")
            self.assertIn(".aletheia/nodes/feature_node.yaml", listing_payload["records"])

    def test_truth_record_script_rejects_unknown_entity_and_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            unknown = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "list", "unknown"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            unknown_output = unknown.stdout + unknown.stderr
            self.assertNotEqual(unknown.returncode, 0, unknown_output)
            self.assertIn("unknown truth record entity", unknown_output)
            self.assertNotIn("Traceback", unknown_output)

            traversal = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "evidence",
                    "--id",
                    "../outside",
                    "--title",
                    "Invalid",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            traversal_output = traversal.stdout + traversal.stderr
            self.assertNotEqual(traversal.returncode, 0, traversal_output)
            self.assertIn("record id must contain only", traversal_output)
            self.assertFalse((target / ".aletheia" / "outside.md").exists())
            self.assertNotIn("Traceback", traversal_output)

    def test_truth_record_script_handles_runtime_and_yaml_records_safely(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "agent_runs" / "RUN-0001.json").write_text(
                json.dumps({"run_id": "RUN-0001"}) + "\n",
                encoding="utf-8",
            )

            agent_runs = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "list", "agent-runs"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            agent_runs_output = agent_runs.stdout + agent_runs.stderr
            self.assertEqual(agent_runs.returncode, 0, agent_runs_output)
            self.assertIn(".aletheia/agent_runs/RUN-0001.json", agent_runs_output)

            create_node = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "node",
                    "--id",
                    "feature_node",
                    "--title",
                    "Feature Node",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(create_node.returncode, 0, create_node.stdout + create_node.stderr)

            archive_node = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "archive",
                    "node",
                    "feature_node",
                    "--reason",
                    "No longer active.",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(archive_node.returncode, 0, archive_node.stdout + archive_node.stderr)
            node_text = (target / ".aletheia" / "nodes" / "feature_node.yaml").read_text(encoding="utf-8")
            self.assertIn("status: archived", node_text)
            self.assertNotIn("Status: archived", node_text)

    def test_truth_record_script_admin_crud_for_governance_and_state_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            show = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "show", "capability-map", "current", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(show.returncode, 0, show.stdout + show.stderr)
            show_payload = json.loads(show.stdout)
            self.assertEqual(show_payload["path"], ".aletheia/CAPABILITY_MAP.md")

            fixed_entities = {
                "charter": ".aletheia/governance/CHARTER.md",
                "attention-policy": ".aletheia/governance/ATTENTION_POLICY.md",
                "model-governance": ".aletheia/governance/MODEL_GOVERNANCE.md",
                "tree-governance": ".aletheia/governance/TREE_GOVERNANCE.md",
                "git-policy": ".aletheia/governance/GIT_POLICY.md",
                "source-policy": ".aletheia/governance/SOURCE_POLICY.md",
                "user-preferences": ".aletheia/state/USER_PREFERENCES.md",
                "domain-profile": ".aletheia/state/DOMAIN_PROFILE.md",
                "frontier-board": ".aletheia/state/FRONTIER_BOARD.md",
                "risk-register": ".aletheia/state/RISK_REGISTER.md",
                "glossary": ".aletheia/state/GLOSSARY.md",
                "skeleton": ".aletheia/state/SKELETON.yaml",
                "actions-registry": ".aletheia/governance/actions.json",
            }
            for entity, rel_path in fixed_entities.items():
                fixed_show = subprocess.run(
                    [sys.executable, ".aletheia/bin/truth_record.py", "show", entity, "current", "--json"],
                    cwd=target,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(fixed_show.returncode, 0, fixed_show.stdout + fixed_show.stderr)
                self.assertEqual(json.loads(fixed_show.stdout)["path"], rel_path)

            update = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "update",
                    "active-state",
                    "current",
                    "--section",
                    "Active frontier",
                    "--content",
                    "Policy-driven frontier.",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            active_text = (target / ".aletheia" / "state" / "ACTIVE_STATE.md").read_text(encoding="utf-8")
            self.assertIn("Policy-driven frontier.", active_text)

            charter_update = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "update",
                    "charter",
                    "current",
                    "--section",
                    "Mission",
                    "--content",
                    "Maintain explicit project truth.",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(charter_update.returncode, 0, charter_update.stdout + charter_update.stderr)
            charter_text = (target / ".aletheia" / "governance" / "CHARTER.md").read_text(encoding="utf-8")
            self.assertIn("## Mission\n\nMaintain explicit project truth.", charter_text)

            json_update = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "update",
                    "runtime-policy",
                    "current",
                    "--status",
                    "active",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(json_update.returncode, 0, json_update.stdout + json_update.stderr)
            self.assertIn("JSON fixed truth files can be shown or archived", json_update.stdout + json_update.stderr)
            json.loads((target / ".aletheia" / "governance" / "runtime_policy.json").read_text(encoding="utf-8"))

            archive = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "archive",
                    "runtime-policy",
                    "current",
                    "--reason",
                    "Keep as historical policy.",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(archive.returncode, 0, archive.stdout + archive.stderr)
            archive_path = target / ".aletheia" / "archive" / "governance" / "runtime_policy.json"
            self.assertTrue(archive_path.exists())
            self.assertFalse((target / ".aletheia" / "governance" / "runtime_policy.json").exists())

    def test_truth_record_script_manages_orphan_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            create = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "orphan",
                    "--id",
                    "ORPH-0001",
                    "--title",
                    "Unattached claim",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stdout + create.stderr)
            self.assertEqual(json.loads(create.stdout)["path"], ".aletheia/state/ORPHANS.yaml#ORPH-0001")
            expected_review = (date.today() + timedelta(days=30)).isoformat()
            self.assertIn(
                f"    next_review: {expected_review}",
                (target / ".aletheia" / "state" / "ORPHANS.yaml").read_text(encoding="utf-8"),
            )

            duplicate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "orphan",
                    "--id",
                    "ORPH-0001",
                    "--title",
                    "Duplicate",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(duplicate.returncode, 0, duplicate.stdout + duplicate.stderr)
            self.assertIn("orphan already exists", duplicate.stdout + duplicate.stderr)

            listing = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "list", "orphan", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(listing.returncode, 0, listing.stdout + listing.stderr)
            self.assertIn(".aletheia/state/ORPHANS.yaml#ORPH-0001", json.loads(listing.stdout)["records"])

            show = subprocess.run(
                [sys.executable, ".aletheia/bin/truth_record.py", "show", "orphan", "ORPH-0001", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(show.returncode, 0, show.stdout + show.stderr)
            self.assertIn("summary: \"Unattached claim\"", json.loads(show.stdout)["content"])

            update = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "update",
                    "orphan",
                    "ORPH-0001",
                    "--title",
                    "Reviewed unattached claim",
                    "--status",
                    "reviewed",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            self.assertEqual(json.loads(update.stdout)["updated"], ["summary", "status"])

            field_update = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "update",
                    "orphan",
                    "ORPH-0001",
                    "--candidate-parent",
                    "root",
                    "--source-ref",
                    ".aletheia/evidence/EV-0001.md",
                    "--next-review",
                    "2099-01-01",
                    "--evidence-needed",
                    "Confirm with source inventory.",
                    "--disposition",
                    "attach",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(field_update.returncode, 0, field_update.stdout + field_update.stderr)
            self.assertEqual(
                json.loads(field_update.stdout)["updated"],
                ["candidate_parent", "source_refs", "next_review", "evidence_needed", "disposition"],
            )
            updated_orphans = (target / ".aletheia" / "state" / "ORPHANS.yaml").read_text(encoding="utf-8")
            self.assertIn("    candidate_parent: root", updated_orphans)
            self.assertIn("    source_refs:", updated_orphans)
            self.assertIn("      - .aletheia/evidence/EV-0001.md", updated_orphans)
            self.assertIn("    next_review: 2099-01-01", updated_orphans)
            self.assertIn("    evidence_needed: \"Confirm with source inventory.\"", updated_orphans)
            self.assertIn("    disposition: attach", updated_orphans)

            action_explain = subprocess.run(
                [sys.executable, ".aletheia/bin/action.py", "explain", "truth.orphan.update", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(action_explain.returncode, 0, action_explain.stdout + action_explain.stderr)
            action_payload = json.loads(action_explain.stdout)["action"]
            self.assertEqual(action_payload["id"], "truth.orphan.update")
            self.assertIn("lifecycle status", action_payload["intent"])
            self.assertIn("selected review fields", action_payload["notes"])
            self.assertIn("candidate_parent", action_payload["notes"])
            self.assertIn("next_review", action_payload["notes"])

            archive = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "archive",
                    "orphan",
                    "ORPH-0001",
                    "--reason",
                    "Disposition resolved.",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(archive.returncode, 0, archive.stdout + archive.stderr)
            orphans = (target / ".aletheia" / "state" / "ORPHANS.yaml").read_text(encoding="utf-8")
            self.assertIn("status: archived", orphans)
            self.assertIn("archive_reason: \"Disposition resolved.\"", orphans)

            validation = validate_target(target)
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_truth_record_orphan_create_uses_review_policy_days_with_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            orphans_path = target / ".aletheia" / "state" / "ORPHANS.yaml"
            orphans_path.write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 7\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans: []\n",
                encoding="utf-8",
            )

            create_custom = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "orphan",
                    "--id",
                    "ORPH-custom",
                    "--title",
                    "Custom policy",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(create_custom.returncode, 0, create_custom.stdout + create_custom.stderr)
            self.assertIn(
                f"    next_review: {(date.today() + timedelta(days=7)).isoformat()}",
                orphans_path.read_text(encoding="utf-8"),
            )

            orphans_path.write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "orphans: []\n",
                encoding="utf-8",
            )

            create_fallback = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/truth_record.py",
                    "create",
                    "orphan",
                    "--id",
                    "ORPH-fallback",
                    "--title",
                    "Fallback policy",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(create_fallback.returncode, 0, create_fallback.stdout + create_fallback.stderr)
            self.assertIn(
                f"    next_review: {(date.today() + timedelta(days=30)).isoformat()}",
                orphans_path.read_text(encoding="utf-8"),
            )

    def test_orphan_validation_rejects_duplicates_and_missing_candidate_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n"
                "\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n"
                "\n"
                "orphans:\n"
                "  - id: ORPH-duplicate\n"
                "    status: incubating\n"
                "    summary: first\n"
                "    candidate_parent: missing-node\n"
                "  - id: ORPH-duplicate\n"
                "    status: incubating\n"
                "    summary: second\n",
                encoding="utf-8",
            )

            validation = validate_target(target)
            output = validation.stdout + validation.stderr
            self.assertNotEqual(validation.returncode, 0, output)
            self.assertIn("orphan entry duplicate id: ORPH-duplicate", output)
            self.assertIn("orphan entry candidate parent missing", output)
            self.assertIn("orphan entry missing field: ORPH-duplicate candidate_parent", output)

    def test_truth_record_script_replaces_template_placeholders_for_supported_entities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            cases = [
                ("evidence", "EV-template", "Template Evidence", ".aletheia/evidence/EV-template.md"),
                ("decision", "DEC-template", "Template Decision", ".aletheia/decisions/DEC-template.md"),
                ("contract", "CON-template", "Template Contract", ".aletheia/contracts/CON-template.md"),
                ("hypothesis", "HYP-template", "Template Hypothesis", ".aletheia/hypotheses/HYP-template.md"),
                ("risk", "RISK-template", "Template Risk", ".aletheia/risks/RISK-template.md"),
                ("session-note", "2026-05-07-template", "Template Session", ".aletheia/session_notes/2026-05-07-template.md"),
                ("node", "template_node", "Template Node", ".aletheia/nodes/template_node.yaml"),
            ]

            for entity, record_id, title, rel in cases:
                result = subprocess.run(
                    [
                        sys.executable,
                        ".aletheia/bin/truth_record.py",
                        "create",
                        entity,
                        "--id",
                        record_id,
                        "--title",
                        title,
                    ],
                    cwd=target,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                text = (target / rel).read_text(encoding="utf-8")
                for placeholder in ["<title>", "<boundary name>", "TITLE", "YYYY-MM-DD", "HYP-0001", "node_id", "Node title"]:
                    self.assertNotIn(placeholder, text, f"{placeholder} remained in {rel}")

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

    def test_source_inventory_uses_runtime_policy_classification_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            policy_path = target / ".aletheia" / "governance" / "runtime_policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["source_inventory_excluded_dirs"].append("generated")
            policy["source_inventory_excluded_root_files"].append("PROJECT_ONLY.md")
            policy["source_inventory_sensitive_patterns"].append("customer-list")
            policy["source_inventory_large_bytes"] = 12
            policy["source_inventory_kind_keywords"]["roadmap"] = "planning_material"
            policy["source_inventory_suffix_kinds"][".plan"] = "planning_file"
            policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")

            (target / "generated").mkdir()
            (target / "generated" / "ignored.md").write_text("# generated\n", encoding="utf-8")
            (target / "PROJECT_ONLY.md").write_text("# ignored root file\n", encoding="utf-8")
            (target / "customer-list.md").write_text("# names\n", encoding="utf-8")
            (target / "tiny.txt").write_text("0123456789013", encoding="utf-8")
            (target / "product-roadmap.md").write_text("# roadmap\n", encoding="utf-8")
            (target / "launch.plan").write_text("plan\n", encoding="utf-8")

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
            self.assertNotIn("generated/ignored.md", by_path)
            self.assertNotIn("PROJECT_ONLY.md", by_path)
            self.assertEqual(by_path["customer-list.md"]["initial_classification"], "unsafe_or_sensitive")
            self.assertEqual(by_path["tiny.txt"]["initial_classification"], "deferred_due_to_size")
            self.assertEqual(by_path["product-roadmap.md"]["kind"], "planning_material")
            self.assertEqual(by_path["launch.plan"]["kind"], "planning_file")

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

    def test_source_inventory_handles_unicode_paths_and_skips_external_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target with space"
            target.mkdir()
            init_target(target)
            notes = target / "研究 资料"
            notes.mkdir()
            (notes / "市场 建模.md").write_text("# Market modeling\n", encoding="utf-8")
            outside = Path(tmp) / "outside-secret.md"
            outside.write_text("# outside\n", encoding="utf-8")
            os.symlink(outside, target / "outside-link.md")

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
            self.assertNotIn("Traceback", output)
            inventory = json.loads((target / ".aletheia" / "source_inventory" / "inventory.json").read_text(encoding="utf-8"))
            paths = {item["path"] for item in inventory["items"]}
            self.assertIn("研究 资料/市场 建模.md", paths)
            self.assertNotIn("outside-link.md", paths)

    def test_source_inventory_skips_nested_git_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            nested = target / "examples" / "external-repo"
            nested.mkdir(parents=True)
            (nested / ".git").mkdir()
            (nested / "README.md").write_text("# External repo\n", encoding="utf-8")
            (target / "examples" / "local-note.md").write_text("# Local note\n", encoding="utf-8")

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
            self.assertIn("examples/local-note.md", paths)
            self.assertNotIn("examples/external-repo/README.md", paths)

    def test_source_inventory_reports_output_path_conflict_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            conflict = target / ".aletheia" / "source_inventory"
            conflict.write_text("not a directory\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/source_inventory.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("source inventory failed:", output)
            self.assertIn(".aletheia/source_inventory exists and is not a directory", output)
            self.assertNotIn("Traceback", output)

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

    def test_validate_rejects_invalid_runtime_policy_with_clear_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            policy = target / ".aletheia" / "governance" / "runtime_policy.json"

            policy.write_text("{invalid json", encoding="utf-8")
            invalid_json = validate_target(target)
            invalid_json_output = invalid_json.stdout + invalid_json.stderr
            self.assertNotEqual(invalid_json.returncode, 0, invalid_json_output)
            self.assertIn("runtime policy JSON invalid", invalid_json_output)
            self.assertNotIn("Traceback", invalid_json_output)

            policy.write_text(json.dumps({"read_only_git_subcommands": ["status"]}) + "\n", encoding="utf-8")
            missing = validate_target(target)
            missing_output = missing.stdout + missing.stderr
            self.assertNotEqual(missing.returncode, 0, missing_output)
            self.assertIn("runtime policy missing section: protected_path_patterns", missing_output)
            self.assertIn("runtime policy missing section: checkpoint_state_patterns", missing_output)
            self.assertNotIn("Traceback", missing_output)

            good_policy = json.loads((ROOT / "assets" / "scaffold" / ".aletheia" / "governance" / "runtime_policy.json").read_text(encoding="utf-8"))
            good_policy["protected_path_patterns"].append("[bad")
            policy.write_text(json.dumps(good_policy, indent=2) + "\n", encoding="utf-8")
            bad_regex = validate_target(target)
            bad_regex_output = bad_regex.stdout + bad_regex.stderr
            self.assertNotEqual(bad_regex.returncode, 0, bad_regex_output)
            self.assertIn("runtime policy protected_path_patterns invalid regex", bad_regex_output)
            self.assertIn("[bad", bad_regex_output)
            self.assertNotIn("Traceback", bad_regex_output)

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

    def test_validate_accepts_active_nodes_from_skeleton_and_rejects_unknown_active_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  reproducibility_checks:\n"
                "    layer: leaf\n"
                "    parent: engineering_execution\n"
                "    children: []\n"
                "    purpose: \"Keep project checks reproducible.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(
                active_state.read_text(encoding="utf-8").replace("- `root`", "- `reproducibility_checks`"),
                encoding="utf-8",
            )

            accepted = validate_target(target)
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)

            active_state.write_text(
                active_state.read_text(encoding="utf-8").replace("`reproducibility_checks`", "`missing_branch`"),
                encoding="utf-8",
            )
            rejected = validate_target(target)
            output = rejected.stdout + rejected.stderr
            self.assertNotEqual(rejected.returncode, 0, output)
            self.assertIn("active state references unknown graph or skeleton nodes: missing_branch", output)

    def test_validate_rejects_active_node_that_points_to_archived_skeleton_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  obsolete_branch:\n"
                "    layer: leaf\n"
                "    status: archived\n"
                "    parent: engineering_execution\n"
                "    children: []\n"
                "    purpose: \"Retired execution branch.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.1\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(
                active_state.read_text(encoding="utf-8").replace("- `root`", "- `obsolete_branch`"),
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("active state references archived skeleton node: obsolete_branch", output)

    def test_validate_rejects_skeleton_parent_child_link_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  reproducibility_checks:\n"
                "    layer: branch\n"
                "    parent: engineering_execution\n"
                "    children:\n"
                "      - deterministic_fixtures\n"
                "    purpose: \"Keep project checks reproducible.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n"
                "  deterministic_fixtures:\n"
                "    layer: leaf\n"
                "    parent: system_design\n"
                "    children: []\n"
                "    purpose: \"Keep fixture generation deterministic.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(
                "skeleton child parent mismatch: reproducibility_checks child=deterministic_fixtures parent=system_design",
                output,
            )

    def test_validate_rejects_skeleton_parent_missing_child_backlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  reproducibility_checks:\n"
                "    layer: branch\n"
                "    parent: engineering_execution\n"
                "    children: []\n"
                "    purpose: \"Keep project checks reproducible.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n"
                "  deterministic_fixtures:\n"
                "    layer: leaf\n"
                "    parent: reproducibility_checks\n"
                "    children: []\n"
                "    purpose: \"Keep fixture generation deterministic.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(
                "skeleton parent missing child link: deterministic_fixtures parent=reproducibility_checks",
                output,
            )

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

    def test_validate_rejects_accepted_hypothesis_without_supporting_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            hypothesis = target / ".aletheia" / "hypotheses" / "HYP-accepted.md"
            hypothesis.write_text(
                "# Hypothesis: unsupported acceptance\n\n"
                "- Lifecycle: accepted\n\n"
                "## Claim\n\nA possible explanation.\n\n"
                "## Invalidation criteria\n\nContradicting evidence.\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(
                "hypothesis lifecycle requires supporting evidence: .aletheia/hypotheses/HYP-accepted.md",
                output,
            )

    def test_validate_rejects_accepted_decision_linking_falsified_hypothesis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "evidence" / "EV-0001.md").write_text(
                "# Evidence: falsifies hypothesis\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead source.\n\n"
                "## Result\n\nContradiction.\n\n"
                "## Limitations\n\nSingle source.\n\n"
                "## Invalidation criteria\n\nNew evidence.\n\n"
                "## Confidence impact\n\nLowers confidence.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "hypotheses" / "HYP-falsified.md").write_text(
                "# Hypothesis: falsified support\n\n"
                "- Lifecycle: falsified\n\n"
                "## Claim\n\nA disproven explanation.\n\n"
                "## Invalidation criteria\n\nContradiction.\n\n"
                "## Review Note\n\nTBD.\n",
                encoding="utf-8",
            )
            decision = target / ".aletheia" / "decisions" / "DEC-0001.md"
            decision.write_text(
                "# Decision: depends on falsified hypothesis\n\n"
                "Status: accepted\n\n"
                "## Context\n\nContext.\n\n"
                "## Decision\n\nChosen path.\n\n"
                "## Evidence links\n\n- `.aletheia/evidence/EV-0001.md`\n\n"
                "## Hypothesis links\n\n- `.aletheia/hypotheses/HYP-falsified.md`\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(
                "accepted decision references falsified hypothesis: .aletheia/decisions/DEC-0001.md -> .aletheia/hypotheses/HYP-falsified.md",
                output,
            )

    def test_validate_allows_weakened_hypothesis_when_review_note_explains_decision_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "evidence" / "EV-0001.md").write_text(
                "# Evidence: weakens hypothesis\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead source.\n\n"
                "## Result\n\nPartial contradiction.\n\n"
                "## Limitations\n\nSingle source.\n\n"
                "## Invalidation criteria\n\nNew evidence.\n\n"
                "## Confidence impact\n\nLowers confidence.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "hypotheses" / "HYP-weakened.md").write_text(
                "# Hypothesis: weakened support\n\n"
                "- Lifecycle: weakened\n\n"
                "## Claim\n\nA partially weakened explanation.\n\n"
                "## Invalidation criteria\n\nContradiction.\n\n"
                "## Review Note\n\n"
                "Decision DEC-0001 keeps this hypothesis as a historical constraint only; it no longer serves as primary support.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "decisions" / "DEC-0001.md").write_text(
                "# Decision: keeps weakened hypothesis under review\n\n"
                "Status: accepted\n\n"
                "## Context\n\nContext.\n\n"
                "## Decision\n\nChosen path with explicit review boundary.\n\n"
                "## Evidence links\n\n- `.aletheia/evidence/EV-0001.md`\n\n"
                "## Hypothesis links\n\n- `.aletheia/hypotheses/HYP-weakened.md`\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_validate_rejects_accepted_decision_links_to_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            decision = target / ".aletheia" / "decisions" / "DEC-missing-evidence.md"
            decision.write_text(
                "# Decision: missing evidence link\n\n"
                "Status: accepted\n\n"
                "## Context\n\nA decision with a stale evidence reference.\n\n"
                "## Decision\n\nAccept the stale link for testing.\n\n"
                "## Evidence links\n\n- `.aletheia/evidence/EV-does-not-exist.md`\n",
                encoding="utf-8",
            )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn(
                "accepted decision evidence link target missing: .aletheia/evidence/EV-does-not-exist.md",
                output,
            )

    def test_validate_rejects_duplicate_accepted_decision_titles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            evidence = target / ".aletheia" / "evidence" / "EV-dup-decision.md"
            evidence.write_text(
                "# Evidence: duplicate decision support\n\n"
                "## Source refs\n\n- `README.md`\n\n"
                "## Method\n\nRead project docs.\n\n"
                "## Result\n\nThe same decision should not be accepted twice.\n\n"
                "## Limitations\n\nSingle sample.\n\n"
                "## Invalidation criteria\n\nContradicting evidence appears.\n\n"
                "## Confidence impact\n\nRaises confidence.\n",
                encoding="utf-8",
            )
            for name in ["DEC-first.md", "DEC-second.md"]:
                (target / ".aletheia" / "decisions" / name).write_text(
                    "# Decision: use market-structure-gated factors\n\n"
                    "Status: accepted\n\n"
                    "## Context\n\nDuplicate decision title.\n\n"
                    "## Decision\n\nAccept the same architectural choice.\n\n"
                    "## Evidence links\n\n- `.aletheia/evidence/EV-dup-decision.md`\n",
                    encoding="utf-8",
                )

            result = validate_target(target)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("duplicate accepted decision title: use market-structure-gated factors", output)

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

    def test_orient_defaults_to_cache_friendly_context_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "runtime").mkdir()
            (target / ".aletheia" / "runtime" / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-orient",
                        "provider": "openai",
                        "model_id": "gpt-test",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "session_notes" / "2026-05-07-orient.md").write_text(
                "# Session Note: orient context\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "decisions" / "DEC-001.md").write_text(
                "# Decision: sample\n\nStatus: proposed\n",
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
            self.assertIn("## Capability Map", output)
            self.assertIn("truth_record.py create", output)
            self.assertIn("## Truth Record Inventory", output)
            self.assertIn(".aletheia/decisions/DEC-001.md", output)
            self.assertNotIn("## Current Agent Run", output)
            self.assertNotIn("RUN-orient", output)
            self.assertNotIn("## Recent Session Notes", output)
            self.assertNotIn(".aletheia/session_notes/2026-05-07-orient.md", output)

    def test_orient_can_include_runtime_context_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "runtime").mkdir()
            (target / ".aletheia" / "runtime" / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-orient",
                        "provider": "openai",
                        "model_id": "gpt-test",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "session_notes" / "2026-05-07-orient.md").write_text(
                "# Session Note: orient context\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/orient.py", "--with-runtime"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("## Current Agent Run", output)
            self.assertIn("RUN-orient", output)
            self.assertIn("## Recent Session Notes", output)
            self.assertIn(".aletheia/session_notes/2026-05-07-orient.md", output)

    def test_orient_static_mode_omits_record_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            (target / ".aletheia" / "decisions" / "DEC-001.md").write_text(
                "# Decision: sample\n\nStatus: proposed\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/orient.py", "--static"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("## Capability Map", output)
            self.assertNotIn("## Truth Record Inventory", output)
            self.assertNotIn(".aletheia/decisions/DEC-001.md", output)

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
            "EVIDENCE.md": ["Linked node", "Claim lifecycle impact", "Source refs", "Limitations", "Confidence impact"],
            "HYPOTHESIS.md": ["Lifecycle", "Supporting Evidence", "Dependent Decisions", "Review Note"],
            "DECISION.md": ["Decision type", "Affected nodes", "Affected contracts", "Evidence links", "Hypothesis links", "Review trigger"],
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

    def test_change_hook_records_invalid_current_agent_run_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text("{bad json", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/change_hook.py"],
                cwd=target,
                input=json.dumps(
                    {
                        "hook_event_name": "PostToolUse",
                        "tool_name": "Write",
                        "tool_input": {"file_path": ".aletheia/state/ACTIVE_STATE.md"},
                    }
                ),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            log_path = target / ".aletheia" / "runtime" / "change_log.jsonl"
            record = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(record["file_path"], ".aletheia/state/ACTIVE_STATE.md")
            self.assertIsNone(record["agent_run_id"])
            self.assertIn("current_agent_run.json", record["agent_run_error"])

    def test_model_registry_can_deprecate_and_remove_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)

            register = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--registry",
                    "register",
                    "codex",
                    "--provider",
                    "openai",
                    "--model-id",
                    "gpt-test",
                    "--tier",
                    "C3",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(register.returncode, 0, register.stdout + register.stderr)

            deprecate = subprocess.run(
                [
                    sys.executable,
                    ".aletheia/bin/model_gate.py",
                    "--registry",
                    "deprecate",
                    "codex",
                    "--reason",
                    "Superseded.",
                    "--json",
                ],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(deprecate.returncode, 0, deprecate.stdout + deprecate.stderr)
            registry = json.loads((target / ".aletheia" / "governance" / "model_registry.json").read_text(encoding="utf-8"))
            self.assertFalse(registry["registered_models"]["codex"]["enabled"])
            self.assertEqual(registry["registered_models"]["codex"]["status"], "deprecated")
            self.assertEqual(registry["registered_models"]["codex"]["deprecation_reason"], "Superseded.")

            remove = subprocess.run(
                [sys.executable, ".aletheia/bin/model_gate.py", "--registry", "remove", "codex", "--json"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(remove.returncode, 0, remove.stdout + remove.stderr)
            registry = json.loads((target / ".aletheia" / "governance" / "model_registry.json").read_text(encoding="utf-8"))
            self.assertNotIn("codex", registry["registered_models"])

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

    def test_stop_hook_reports_missing_git_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_target(target)
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(active_state.read_text(encoding="utf-8") + "\nStop hook missing git note.\n", encoding="utf-8")
            empty_bin = Path(tmp) / "empty-bin"
            empty_bin.mkdir()
            env = os.environ.copy()
            env["PATH"] = str(empty_bin)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/stop_hook.py"],
                cwd=target,
                env=env,
                input=json.dumps({"hook_event_name": "Stop"}),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("AletheiaOS stop hook: required command is not available on PATH", output)
            self.assertNotIn("Traceback", output)
            self.assertNotIn("Recommended next command", output)


if __name__ == "__main__":
    unittest.main()
