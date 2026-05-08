from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PluginManifestTests(unittest.TestCase):
    def test_codex_manifest_uses_complete_plugin_schema(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "aletheia-os")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["author"]["name"], "zynthium")
        self.assertEqual(manifest["repository"], "https://github.com/zynthium/aletheia-os")
        self.assertEqual(manifest["homepage"], "https://github.com/zynthium/aletheia-os")
        self.assertEqual(manifest["interface"]["developerName"], "zynthium")
        self.assertEqual(manifest["interface"]["websiteURL"], "https://github.com/zynthium/aletheia-os")
        self.assertIn("falsifiable truth tree", manifest["description"])
        self.assertIn("orphan incubator", manifest["description"])
        self.assertIn("falsifiable truth tree", manifest["interface"]["shortDescription"])
        self.assertIn("hierarchical, falsifiable, and evolvable", manifest["interface"]["longDescription"])
        self.assertIn("orphan incubator", manifest["interface"]["longDescription"])
        self.assertIn("evidence", manifest["interface"]["longDescription"])
        self.assertIn("truth-layer", manifest["keywords"])
        self.assertIn("truth-tree", manifest["keywords"])
        self.assertIn("falsifiable-truth", manifest["keywords"])
        self.assertIn("scientific-method", manifest["keywords"])
        self.assertIn("tree-governance", manifest["keywords"])
        self.assertIn("agent-governance", manifest["keywords"])
        self.assertIsInstance(manifest["interface"]["defaultPrompt"], list)
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        for prompt in manifest["interface"]["defaultPrompt"]:
            self.assertLessEqual(len(prompt), 128)
        self.assertIn("longDescription", manifest["interface"])
        self.assertIn("developerName", manifest["interface"])
        self.assertIn("category", manifest["interface"])
        self.assertIn("capabilities", manifest["interface"])

    def test_claude_manifest_uses_plugin_root_components(self) -> None:
        codex_manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude_manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertEqual(claude_manifest["name"], codex_manifest["name"])
        self.assertEqual(claude_manifest["description"], codex_manifest["description"])
        self.assertEqual(claude_manifest["version"], codex_manifest["version"])
        self.assertEqual(claude_manifest["author"], codex_manifest["author"])
        self.assertEqual(claude_manifest["skills"], "./skills/")
        self.assertTrue((ROOT / "skills" / "aletheia-bootstrap" / "SKILL.md").exists())
        self.assertFalse((ROOT / ".claude-plugin" / "skills").exists())

    def test_package_output_uses_manifest_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "scripts/package_plugin.py", "--output", tmp],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            release_root = Path(tmp) / "aletheia-os"
            self.assertEqual([path.name for path in Path(tmp).iterdir()], ["aletheia-os"])
            self.assertTrue((release_root / ".codex-plugin" / "plugin.json").exists())
            self.assertTrue((release_root / ".claude-plugin" / "plugin.json").exists())
            self.assertTrue((release_root / "skills" / "aletheia-promote" / "SKILL.md").exists())
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "CAPABILITY_MAP.md").exists())
            self.assertTrue(
                (release_root / "assets" / "scaffold" / ".aletheia" / "governance" / "TREE_GOVERNANCE.md").exists()
            )
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "state" / "ORPHANS.yaml").exists())
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "playbooks" / "drift_audit.md").exists())
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "playbooks" / "prompt_native_boundaries.md").exists())
            self.assertTrue(
                (
                    release_root
                    / "assets"
                    / "scaffold"
                    / ".aletheia"
                    / "playbooks"
                    / "tree_governed_truth_growth.md"
                ).exists()
            )
            self.assertTrue(
                (release_root / "assets" / "scaffold" / ".aletheia" / "playbooks" / "skeleton_review.md").exists()
            )
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "bin" / "help.py").exists())
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "bin" / "action.py").exists())
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "bin" / "capability_audit.py").exists())
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "bin" / "preflight.py").exists())
            self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "bin" / "truth_record.py").exists())
            self.assertTrue(
                (
                    release_root
                    / "assets"
                    / "scaffold"
                    / ".aletheia"
                    / "governance"
                    / "actions.json"
                ).exists()
            )
            self.assertFalse((release_root / "docs" / "superpowers").exists())
            self.assertFalse((release_root / "docs" / "plans").exists())
            self.assertFalse(any(release_root.rglob("__pycache__")))
            self.assertFalse(any(release_root.rglob("*.pyc")))

    def test_package_output_contains_readme_link_targets_and_host_smoke_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "scripts/package_plugin.py", "--output", tmp],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            release_root = Path(tmp) / "aletheia-os"
            self.assertTrue(
                (
                    release_root
                    / "docs"
                    / "articles"
                    / "aletheia-os-project-introduction.zh-CN.md"
                ).exists()
            )
            self.assertTrue((release_root / "docs" / "verification" / "host-smoke.zh-CN.md").exists())
            self.assertTrue((release_root / "README.md").exists())
            self.assertTrue((release_root / "README.zh-CN.md").exists())

    def test_host_smoke_checklist_requires_versions_commands_expected_results_and_failures(self) -> None:
        checklist = (ROOT / "docs" / "verification" / "host-smoke.zh-CN.md").read_text(encoding="utf-8")

        for required in [
            "版本记录",
            "claude --version",
            "codex --version",
            "执行命令",
            "期望结果",
            "实际结果",
            "失败记录",
            "不要把挂起结果标记为通过",
        ]:
            self.assertIn(required, checklist)

    def test_capability_map_covers_runtime_scripts_skills_and_review_agents(self) -> None:
        capability_map = (ROOT / "assets" / "scaffold" / ".aletheia" / "CAPABILITY_MAP.md").read_text(
            encoding="utf-8"
        )

        expected_terms = [
            "help.py",
            "action.py",
            "actions.json",
            "truth.validate",
            "truth.tree.review",
            "truth.tree.health",
            "truth.preflight",
            "truth.checkpoint.dry_run",
            "truth.bootstrap.guided.inspect",
            "truth.bootstrap.finalize.inspect",
            "--candidate-parent",
            "--source-ref",
            "--next-review",
            "--evidence-needed",
            "--disposition",
            "capability_audit.py",
            "orient.py",
            "context_pack.py",
            "system_context.py",
            "preflight.py",
            "status.py",
            "truth_record.py",
            "truth_record.py list/show/create/update/archive",
            "truth_record.py update",
            "model_gate.py",
            "runtime_policy.json",
            "USER_PREFERENCES.md",
            "source_inventory.py",
            "guided_bootstrap.py",
            "bootstrap_finalize.py",
            "validate.py",
            "overview.py",
            "checkpoint.py",
            "aletheia-bootstrap",
            "aletheia-orient",
            "aletheia-checkpoint",
            "aletheia-design-evidence",
            "aletheia-architecture-evolution",
            "aletheia-promote",
            "truth-auditor",
            "evidence-curator",
            "architecture-reviewer",
            "Codex enablement",
            "archive-only",
            "Delete means archive-by-default",
            "Agent Primitive Matrix",
            "Primitive-To-Workflow Map",
            "Primitive Wrappers",
            "host limitation",
            "ORPHANS.yaml",
            "tree refactor",
        ]
        for term in expected_terms:
            self.assertIn(term, capability_map)

        boundaries = (
            ROOT
            / "assets"
            / "scaffold"
            / ".aletheia"
            / "playbooks"
            / "prompt_native_boundaries.md"
        ).read_text(encoding="utf-8")
        for term in [
            "Delete Policy",
            "truth_record.py archive",
            "Permanent removal remains a",
            "Primitive-To-Workflow Map",
            "Primitive Wrappers",
            "system_context.py",
            "action.py",
            "Tree-governed truth growth",
        ]:
            self.assertIn(term, boundaries)

    def test_workflow_skills_declare_primitives_and_prompt_recipes(self) -> None:
        expected_primitives = {
            "aletheia-architecture-evolution": ["orient.py", "truth_record.py", "validate.py"],
            "aletheia-bootstrap": ["model_gate.py", "source_inventory.py", "guided_bootstrap.py"],
            "aletheia-checkpoint": ["preflight.py", "validate.py", "checkpoint.py"],
            "aletheia-design-evidence": ["truth_record.py", "validate.py"],
            "aletheia-orient": ["system_context.py", "orient.py", "context_pack.py"],
            "aletheia-promote": ["context_pack.py", "truth_record.py", "validate.py"],
        }

        for skill_name, primitives in expected_primitives.items():
            with self.subTest(skill=skill_name):
                text = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("## Primitive Capabilities", text)
                self.assertIn("## Prompt Recipe", text)
                self.assertIn("Do not add orchestration to runtime scripts", text)
                for primitive in primitives:
                    self.assertIn(primitive, text)

    def test_scaffold_docs_define_git_transition_protocol(self) -> None:
        protocol_paths = [
            "assets/scaffold/.aletheia/governance/GIT_POLICY.md",
            "assets/scaffold/.aletheia/governance/TREE_GOVERNANCE.md",
            "assets/scaffold/.aletheia/playbooks/tree_governed_truth_growth.md",
            "skills/aletheia-checkpoint/SKILL.md",
            "skills/aletheia-architecture-evolution/SKILL.md",
        ]
        protocol_text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in protocol_paths)

        for required in [
            "AIOS-Action",
            "AIOS-Tree-Op",
            "AIOS-Node-State: stable",
            "AIOS-Validation: pass",
            "AIOS-Review: human-confirmed",
            "Git commits are AletheiaOS truth-transition records",
        ]:
            self.assertIn(required, protocol_text)

        checkpoint = ROOT / "assets" / "scaffold" / ".aletheia" / "bin" / "checkpoint.py"
        self.assertTrue(checkpoint.exists())

        stable_node_docs = [
            "assets/scaffold/.aletheia/playbooks/tree_governed_truth_growth.md",
            "skills/aletheia-checkpoint/SKILL.md",
            "skills/aletheia-architecture-evolution/SKILL.md",
        ]
        for path in stable_node_docs:
            with self.subTest(stable_node_doc=path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("python3 .aletheia/bin/checkpoint.py --dry-run", text)
                self.assertIn("python3 .aletheia/bin/history_audit.py --json", text)
                self.assertRegex(text, r"(?i)once .*history audit runtime is installed")

        tree_governance = (
            ROOT / "assets" / "scaffold" / ".aletheia" / "governance" / "TREE_GOVERNANCE.md"
        ).read_text(encoding="utf-8")
        tree_growth = (
            ROOT / "assets" / "scaffold" / ".aletheia" / "playbooks" / "tree_governed_truth_growth.md"
        ).read_text(encoding="utf-8")
        tree_actions = re.findall(r"^- `([^`]+)`:", tree_growth, flags=re.MULTILINE)
        self.assertGreater(len(tree_actions), 0)
        for action in tree_actions:
            with self.subTest(tree_action=action):
                self.assertIn(f"`AIOS-Tree-Op: {action}`", tree_governance)

    def test_capability_audit_passes_for_scaffold_and_fails_when_map_drifts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scaffold = Path(tmp) / "scaffold"
            shutil.copytree(ROOT / "assets" / "scaffold", scaffold)

            result = subprocess.run(
                [sys.executable, ".aletheia/bin/capability_audit.py"],
                cwd=scaffold,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("capability audit passed", result.stdout)

            capability_map = scaffold / ".aletheia" / "CAPABILITY_MAP.md"
            capability_map.write_text("drifted\n", encoding="utf-8")
            drifted = subprocess.run(
                [sys.executable, ".aletheia/bin/capability_audit.py"],
                cwd=scaffold,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = drifted.stdout + drifted.stderr
            self.assertNotEqual(drifted.returncode, 0, output)
            self.assertIn("capability audit failed", output)

    def test_action_registry_defines_agent_native_contracts(self) -> None:
        actions_path = ROOT / "assets" / "scaffold" / ".aletheia" / "governance" / "actions.json"
        actions = json.loads(actions_path.read_text(encoding="utf-8"))

        self.assertIsInstance(actions.get("actions"), list)
        action_ids = {action["id"] for action in actions["actions"]}
        for required_id in [
            "capability.help",
            "truth.orient",
            "truth.validate",
            "truth.preflight",
            "truth.checkpoint.dry_run",
            "capability.audit",
            "truth.record.list",
            "truth.record.show",
            "truth.record.create",
            "truth.record.update",
            "truth.record.archive",
            "truth.system_context",
            "truth.system_context.runtime",
            "truth.source_inventory",
            "truth.bootstrap.guided",
            "truth.bootstrap.finalize",
            "truth.overview",
            "model.registry.list",
            "model.registry.register",
            "model.registry.show",
            "model.registry.enable",
            "model.registry.disable",
            "model.registry.deprecate",
            "model.registry.remove",
            "model.registry.deny",
            "model.registry.undeny",
        ]:
            self.assertIn(required_id, action_ids)

        for action in actions["actions"]:
            with self.subTest(action=action.get("id")):
                self.assertRegex(action["id"], r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_]*)+$")
                self.assertIn(action["risk"], {"read-only", "writes-state", "admin", "checkpoint"})
                self.assertIsInstance(action["command"], list)
                self.assertTrue(action["command"])
                self.assertIsInstance(action["verification"], dict)
                self.assertEqual(action["verification"].get("returncode"), 0)

    def test_capability_discovery_surfaces_core_truth_record_crud_consistently(self) -> None:
        capability_map = (ROOT / "assets" / "scaffold" / ".aletheia" / "CAPABILITY_MAP.md").read_text(
            encoding="utf-8"
        )
        help_text = (ROOT / "assets" / "scaffold" / ".aletheia" / "bin" / "help.py").read_text(
            encoding="utf-8"
        )

        for command in [
            "truth_record.py list",
            "truth_record.py create",
            "truth_record.py show",
            "truth_record.py update",
            "truth_record.py archive",
            "truth_record.py update orphan ORPH-0001 --candidate-parent",
        ]:
            self.assertIn(command, capability_map)
            self.assertIn(command, help_text)

        for entity in ["Evidence", "Decisions", "Contracts", "Hypotheses", "Risks", "Nodes", "Session notes"]:
            self.assertRegex(capability_map, rf"\| {re.escape(entity)} \| .*truth_record\.py create")
            self.assertRegex(capability_map, rf"\| {re.escape(entity)} \| .*truth_record\.py list/show")
            self.assertRegex(capability_map, rf"\| {re.escape(entity)} \| .*truth_record\.py update")
            self.assertRegex(capability_map, rf"\| {re.escape(entity)} \| .*truth_record\.py archive")

    def test_package_output_replaces_stale_release_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            release_root = Path(tmp) / "aletheia-os"
            stale = release_root / "stale.txt"
            stale.parent.mkdir(parents=True)
            stale.write_text("old package content\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/package_plugin.py", "--output", tmp],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(stale.exists())
            self.assertTrue((release_root / ".codex-plugin" / "plugin.json").exists())

    def test_package_output_rejects_existing_file_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "not-a-directory"
            output.write_text("occupied\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/package_plugin.py", "--output", str(output)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            combined = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, combined)
            self.assertIn("output path exists and is not a directory", combined)
            self.assertNotIn("Traceback", combined)

    def test_validate_scaffold_rejects_invalid_runtime_policy_before_packaging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scaffold = Path(tmp) / "scaffold"
            result = subprocess.run(
                [sys.executable, "scripts/package_plugin.py", "--output", tmp],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            packaged = Path(tmp) / "aletheia-os"
            source_scaffold = packaged / "assets" / "scaffold"
            shutil.copytree(source_scaffold, scaffold)
            policy = scaffold / ".aletheia" / "governance" / "runtime_policy.json"
            data = json.loads(policy.read_text(encoding="utf-8"))
            data["protected_path_patterns"].append("[bad")
            policy.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            validate = subprocess.run(
                [sys.executable, "scripts/validate_scaffold.py", str(scaffold)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = validate.stdout + validate.stderr
            self.assertNotEqual(validate.returncode, 0, output)
            self.assertIn("runtime policy protected_path_patterns invalid regex", output)
            self.assertNotIn("Traceback", output)

    def test_validate_scaffold_rejects_extra_tree_record_surfaces_before_packaging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scaffold = Path(tmp) / "scaffold"
            shutil.copytree(ROOT / "assets" / "scaffold", scaffold)
            (scaffold / ".aletheia" / "claims").mkdir()
            (scaffold / ".aletheia" / "bin" / "tree_record.py").write_text("# extra surface\n", encoding="utf-8")

            validate = subprocess.run(
                [sys.executable, "scripts/validate_scaffold.py", str(scaffold)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = validate.stdout + validate.stderr
            self.assertNotEqual(validate.returncode, 0, output)
            self.assertIn("extra tree-governance surface is not allowed: .aletheia/claims", output)
            self.assertIn("extra tree-governance surface is not allowed: .aletheia/bin/tree_record.py", output)
            self.assertNotIn("Traceback", output)

    def test_validate_scaffold_requires_tree_governance_core_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scaffold = Path(tmp) / "scaffold"
            shutil.copytree(ROOT / "assets" / "scaffold", scaffold)
            missing_paths = [
                ".aletheia/governance/TREE_GOVERNANCE.md",
                ".aletheia/state/ORPHANS.yaml",
                ".aletheia/playbooks/tree_governed_truth_growth.md",
                ".aletheia/playbooks/skeleton_review.md",
            ]
            for rel in missing_paths:
                (scaffold / rel).unlink()

            validate = subprocess.run(
                [sys.executable, "scripts/validate_scaffold.py", str(scaffold)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = validate.stdout + validate.stderr
            self.assertNotEqual(validate.returncode, 0, output)
            for rel in missing_paths:
                self.assertIn(f"missing required path: {rel}", output)

    def test_validate_scaffold_allows_common_technical_terms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scaffold = Path(tmp) / "scaffold"
            shutil.copytree(ROOT / "assets" / "scaffold", scaffold)
            note = scaffold / ".aletheia" / "playbooks" / "technical_terms.md"
            note.write_text(
                "Use import for source material, migration for old project notes, "
                "legacy support where needed, and compatibility notes for host APIs.\n",
                encoding="utf-8",
            )

            validate = subprocess.run(
                [sys.executable, "scripts/validate_scaffold.py", str(scaffold)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

    def test_package_checks_wiki_handoff_promotion_protocol(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/package_plugin.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((ROOT / "skills" / "aletheia-promote" / "SKILL.md").exists())
        self.assertTrue(
            (
                ROOT
                / "assets"
                / "scaffold"
                / ".aletheia"
                / "playbooks"
                / "wiki_handoff_promotion.md"
            ).exists()
        )

    def test_wiki_handoff_promotion_protocol_requires_dedup_and_conflict_resolution(self) -> None:
        playbook = (
            ROOT
            / "assets"
            / "scaffold"
            / ".aletheia"
            / "playbooks"
            / "wiki_handoff_promotion.md"
        ).read_text(encoding="utf-8")
        skill = (ROOT / "skills" / "aletheia-promote" / "SKILL.md").read_text(encoding="utf-8")
        combined = (playbook + "\n" + skill).lower()

        for required in [
            "deduplicate",
            "duplicate promotion",
            "conflicting claims",
            "do not promote both sides as accepted truth",
            "update the existing truth record",
        ]:
            self.assertIn(required, combined)

    def test_prompt_native_boundary_playbook_classifies_primitives_and_workflows(self) -> None:
        playbook = (
            ROOT
            / "assets"
            / "scaffold"
            / ".aletheia"
            / "playbooks"
            / "prompt_native_boundaries.md"
        ).read_text(encoding="utf-8")

        for required in [
            "Prompt-Native Boundary Assessment",
            "Primitive runtime scripts",
            "Workflow-coded scripts",
            "Keep in Python",
            "Move to skills or playbooks",
            "Primitive Wrappers",
            "truth_record.py",
            "capability_audit.py",
            "preflight.py",
            "runtime_policy.json",
            "guided_bootstrap.py",
            "guided_bootstrap.py --inspect --json",
            "bootstrap_finalize.py",
            "bootstrap_finalize.py --inspect --json",
            "checkpoint.py",
            "checkpoint.py --dry-run",
        ]:
            self.assertIn(required, playbook)

    def test_tree_growth_playbook_documents_lightweight_refactor_recipes(self) -> None:
        playbook = (
            ROOT
            / "assets"
            / "scaffold"
            / ".aletheia"
            / "playbooks"
            / "tree_governed_truth_growth.md"
        ).read_text(encoding="utf-8")

        for required in [
            "Minimal Tree Refactor Recipes",
            "Attach orphan",
            "Insert parent",
            "Split node",
            "Merge nodes",
            "SKELETON.yaml",
            "ORPHANS.yaml",
            "evidence",
            "decisions",
            "status.py",
            "orient.py",
            "overview.py",
            "validate.py",
            "No new command",
            "No new record family",
        ]:
            self.assertIn(required, playbook)

    def test_tree_governance_docs_define_skeleton_as_authoritative_truth_tree(self) -> None:
        governance = (
            ROOT
            / "assets"
            / "scaffold"
            / ".aletheia"
            / "governance"
            / "TREE_GOVERNANCE.md"
        ).read_text(encoding="utf-8")
        skeleton = (ROOT / "assets" / "scaffold" / ".aletheia" / "state" / "SKELETON.yaml").read_text(
            encoding="utf-8"
        )

        self.assertIn("SKELETON.yaml is the authoritative truth tree", governance)
        self.assertIn("SYSTEM_GRAPH.yaml is a coarse system map", governance)
        self.assertIn("authoritative_truth_tree", skeleton)
        self.assertIn("coarse_system_map", skeleton)

    def test_readme_documents_simple_installation(self) -> None:
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        english_readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("[English](README.md)", readme)
        self.assertIn("仓库原生事实层", readme)
        self.assertIn("仓库原生可证伪真理树层", readme)
        self.assertIn("One repo. One falsifiable truth tree. Many agents.", readme)
        self.assertIn("当前最可信、可审查、可证伪的项目事实", readme)
        self.assertIn("不是另一个 coding workflow", readme)
        self.assertIn("Global View Checksum", readme)
        self.assertIn("OpenSpec", readme)
        self.assertIn("Superpowers", readme)
        self.assertIn(".claude-plugin/plugin.json", readme)
        self.assertIn("python3 scripts/install_aletheia.py --host both --scope user", readme)
        self.assertIn("zynthium/aletheia-os", readme)
        self.assertIn("claude plugin marketplace add zynthium/aletheia-os --scope user", readme)
        self.assertIn("codex plugin marketplace add zynthium/aletheia-os", readme)
        self.assertIn("/plugin", readme)
        self.assertIn("/plugins", readme)
        self.assertIn("日常闭环", readme)
        self.assertIn("orient -> work -> update truth -> validate -> checkpoint", readme)
        self.assertIn("运行时参考", readme)
        self.assertIn("bootstrap finalize 会安装 AletheiaOS Git hooks", readme)
        self.assertIn("治理、归因和审计边界", readme)
        self.assertIn("不是安全沙箱", readme)
        self.assertIn("Claude Code 通过 hooks 自动执行门禁", readme)
        self.assertIn("Codex 当前以 skills、显式命令和可选 subagents 执行同一协议", readme)
        self.assertIn("### 新项目", readme)
        self.assertIn("### 已有项目", readme)
        self.assertIn("python3 /path/to/aletheia-os/scripts/init_aletheia.py .", readme)
        self.assertIn("git status --short", readme)
        self.assertIn("docs/verification/host-smoke.zh-CN.md", readme)
        self.assertIn("python3 .aletheia/bin/truth_record.py update evidence EV-0001 --status active", readme)
        self.assertIn("python3 .aletheia/bin/action.py next --json", readme)
        self.assertIn("python3 .aletheia/bin/truth_record.py create orphan --id ORPH-0001", readme)
        self.assertIn("python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --candidate-parent root", readme)
        self.assertIn("python3 .aletheia/bin/guided_bootstrap.py --inspect --json", readme)
        self.assertIn("python3 .aletheia/bin/bootstrap_finalize.py --inspect --json", readme)
        self.assertIn("truth_record.py 支持 `--json`", readme)
        self.assertIn("truth_record.py create/list/show/update/archive orphan", readme)
        self.assertIn("Codex 插件启用是宿主 UI 限制", readme)
        self.assertIn("`preflight.py` 是 Codex 等无自动 hook enforcement 宿主的显式检查入口", readme)
        self.assertIn("prompt_native_boundaries.md", readme)

        self.assertIn("[简体中文](README.zh-CN.md)", english_readme)
        self.assertIn("repo-native falsifiable truth tree layer", english_readme)
        self.assertIn("repo-native truth layer", english_readme)
        self.assertIn("current most trusted, reviewable, falsifiable project facts", english_readme)
        self.assertIn("not another coding workflow", english_readme)
        self.assertIn("Global View Checksum", english_readme)
        self.assertIn("OpenSpec", english_readme)
        self.assertIn("Superpowers", english_readme)
        self.assertIn(".claude-plugin/plugin.json", english_readme)
        self.assertIn("python3 scripts/install_aletheia.py --host both --scope user", english_readme)
        self.assertIn("zynthium/aletheia-os", english_readme)
        self.assertIn("claude plugin marketplace add zynthium/aletheia-os --scope user", english_readme)
        self.assertIn("codex plugin marketplace add zynthium/aletheia-os", english_readme)
        self.assertIn("/plugins", english_readme)
        self.assertIn("Daily Loop", english_readme)
        self.assertIn("orient -> work -> update truth -> validate -> checkpoint", english_readme)
        self.assertIn("Runtime Reference", english_readme)
        self.assertIn("bootstrap finalize installs AletheiaOS Git hooks", english_readme)
        self.assertIn("governance, attribution, and audit boundary", english_readme)
        self.assertIn("not a security sandbox", english_readme)
        self.assertIn("Claude Code enforces gates and audits through hooks", english_readme)
        self.assertIn("Codex currently uses skills, explicit commands, and optional subagents", english_readme)
        self.assertIn("### New Projects", english_readme)
        self.assertIn("### Existing Projects", english_readme)
        self.assertIn("python3 /path/to/aletheia-os/scripts/init_aletheia.py .", english_readme)
        self.assertIn("git status --short", english_readme)
        self.assertIn("docs/verification/host-smoke.zh-CN.md", english_readme)
        self.assertIn("python3 .aletheia/bin/truth_record.py update evidence EV-0001 --status active", english_readme)
        self.assertIn("python3 .aletheia/bin/action.py next --json", english_readme)
        self.assertIn("python3 .aletheia/bin/truth_record.py create orphan --id ORPH-0001", english_readme)
        self.assertIn("python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --candidate-parent root", english_readme)
        self.assertIn("python3 .aletheia/bin/guided_bootstrap.py --inspect --json", english_readme)
        self.assertIn("python3 .aletheia/bin/bootstrap_finalize.py --inspect --json", english_readme)
        self.assertIn("truth_record.py supports `--json`", english_readme)
        self.assertIn("truth_record.py create/list/show/update/archive orphan", english_readme)
        self.assertIn("Codex plugin enablement is a host UI limitation", english_readme)
        self.assertIn("without automatic hook enforcement", english_readme)
        self.assertIn("prompt_native_boundaries.md", english_readme)

        start_here = (ROOT / "assets" / "scaffold" / ".aletheia" / "START_HERE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Create, read, update, and archive truth records", start_here)

    def test_plugin_content_avoids_retired_identity_markers(self) -> None:
        banned_patterns = [
            r"\bold-project-name\b",
            r"\bold-plugin-name\b",
            r"https://github\.com/old-org/old-repo",
        ]
        checked_roots = [
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            ROOT / "skills",
            ROOT / "agents",
            ROOT / "codex-agents",
            ROOT / "assets" / "scaffold",
            ROOT / ".codex-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / ".agents" / "plugins" / "marketplace.json",
        ]
        offenders: list[str] = []
        for checked in checked_roots:
            paths = [checked] if checked.is_file() else [path for path in checked.rglob("*") if path.is_file()]
            for path in paths:
                if ".gitkeep" in path.name:
                    continue
                if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".txt"}:
                    continue
                text = path.read_text(encoding="utf-8")
                for pattern in banned_patterns:
                    if re.search(pattern, text):
                        offenders.append(f"{path.relative_to(ROOT)} contains {pattern}")

        self.assertEqual(offenders, [])

    def test_plugin_content_uses_zynthium_repository_identity(self) -> None:
        checked_roots = [
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            ROOT / ".codex-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / ".agents" / "plugins" / "marketplace.json",
        ]
        offenders: list[str] = []
        for checked in checked_roots:
            if not checked.exists():
                offenders.append(f"missing {checked.relative_to(ROOT)}")
                continue
            text = checked.read_text(encoding="utf-8")
            if "joeslee" in text or "github.com/joeslee" in text:
                offenders.append(str(checked.relative_to(ROOT)))

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
