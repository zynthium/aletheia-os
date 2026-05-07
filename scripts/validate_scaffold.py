#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "AGENTS.md",
    "START_HERE.md",
    "BOOTSTRAP.md",
    ".claude/settings.json",
    ".aletheia/START_HERE.md",
    ".aletheia/CAPABILITY_MAP.md",
    ".aletheia/.gitignore",
    ".aletheia/VERSION",
    ".aletheia/governance/CHARTER.md",
    ".aletheia/governance/ATTENTION_POLICY.md",
    ".aletheia/governance/MODEL_GOVERNANCE.md",
    ".aletheia/governance/GIT_POLICY.md",
    ".aletheia/governance/SOURCE_POLICY.md",
    ".aletheia/governance/runtime_policy.json",
    ".aletheia/governance/model_registry.json",
    ".aletheia/governance/actions.json",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/RISK_REGISTER.md",
    ".aletheia/state/FRONTIER_BOARD.md",
    ".aletheia/state/GLOSSARY.md",
    ".aletheia/state/DOMAIN_PROFILE.md",
    ".aletheia/state/USER_PREFERENCES.md",
    ".aletheia/contracts/INDEX.md",
    ".aletheia/evidence/INDEX.md",
    ".aletheia/hypotheses/.gitkeep",
    ".aletheia/nodes/ROOT.yaml",
    ".aletheia/playbooks/external_llm_wiki_handoff.md",
    ".aletheia/playbooks/guided_bootstrap.md",
    ".aletheia/playbooks/drift_audit.md",
    ".aletheia/playbooks/wiki_handoff_promotion.md",
    ".aletheia/bin/help.py",
    ".aletheia/bin/action.py",
    ".aletheia/bin/capability_audit.py",
    ".aletheia/bin/orient.py",
    ".aletheia/bin/context_pack.py",
    ".aletheia/bin/system_context.py",
    ".aletheia/bin/preflight.py",
    ".aletheia/bin/status.py",
    ".aletheia/bin/truth_record.py",
    ".aletheia/bin/model_gate.py",
    ".aletheia/bin/validate.py",
    ".aletheia/bin/checkpoint.py",
    ".aletheia/bin/overview.py",
    ".aletheia/bin/bootstrap_finalize.py",
    ".aletheia/bin/source_inventory.py",
    ".aletheia/bin/guided_bootstrap.py",
    ".aletheia/bin/change_hook.py",
    ".aletheia/bin/stop_hook.py",
    ".aletheia/templates/DECISION.md",
    ".aletheia/templates/EVIDENCE.md",
    ".aletheia/templates/RISK.md",
    ".aletheia/templates/CONTRACT.md",
    ".aletheia/templates/SESSION_NOTE.md",
    ".aletheia/templates/HYPOTHESIS.md",
    ".aletheia/templates/NODE.yaml",
    ".aletheia/templates/TASK_CARD.md",
    ".aletheia/templates/AGENT_RUN.json",
    ".aletheia/templates/TRUTH_INVENTORY_REPORT.md",
    ".aletheia/templates/SOURCE_INVENTORY_MANIFEST.yaml",
]

REQUIRED_SKELETON_ROOT_FIELDS = [
    "layer",
    "parent",
    "children",
    "purpose",
    "invariants",
    "interfaces",
    "owned_paths",
    "test_paths",
    "contract_refs",
    "decision_refs",
    "evidence_refs",
    "expand_when",
    "stop_when",
    "confidence",
    "last_reviewed",
]

BANNED_TEXT_PATTERNS = [
    re.compile(r"\bmigration\b", re.I),
    re.compile(r"\bmigrate\b", re.I),
    re.compile(r"\bimport\b", re.I),
    re.compile(r"\blegacy\b", re.I),
    re.compile(r"\bcompat\b", re.I),
    re.compile("迁移"),
    re.compile("导入"),
    re.compile("兼容"),
]
BANNED_EXTRA_TREE_SURFACES = [
    ".aletheia/claims",
    ".aletheia/theories",
    ".aletheia/tree",
    ".aletheia/bin/tree_record.py",
]


def validate_skeleton(root: Path) -> list[str]:
    skeleton_path = root / ".aletheia" / "state" / "SKELETON.yaml"
    text = skeleton_path.read_text(encoding="utf-8")
    if not re.search(r"(?m)^nodes:\s*$", text):
        return [".aletheia/state/SKELETON.yaml must contain nodes mapping"]

    root_match = re.search(r"(?m)^  root:\s*$", text)
    if not root_match:
        return [".aletheia/state/SKELETON.yaml must contain nodes.root mapping"]

    root_block_lines: list[str] = []
    for line in text[root_match.end() :].splitlines():
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", line):
            break
        root_block_lines.append(line)

    fields = set()
    for line in root_block_lines:
        field_match = re.match(r"^    ([A-Za-z_][A-Za-z0-9_]*):", line)
        if field_match:
            fields.add(field_match.group(1))

    missing = [field for field in REQUIRED_SKELETON_ROOT_FIELDS if field not in fields]
    return [f".aletheia/state/SKELETON.yaml nodes.root missing field: {field}" for field in missing]


def validate_no_retired_language(root: Path) -> list[str]:
    errors: list[str] = []
    checked_suffixes = {".md", ".json", ".yaml", ".yml", ".txt"}
    for path in root.rglob("*"):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        if path.suffix.lower() not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in BANNED_TEXT_PATTERNS:
            if pattern.search(text):
                errors.append(f"{path.relative_to(root).as_posix()} contains retired language: {pattern.pattern}")
    return errors


def validate_no_extra_tree_surfaces(root: Path) -> list[str]:
    return [
        f"extra tree-governance surface is not allowed: {rel}"
        for rel in BANNED_EXTRA_TREE_SURFACES
        if (root / rel).exists()
    ]


def validate_runtime_policy(root: Path) -> list[str]:
    path = root / ".aletheia" / "governance" / "runtime_policy.json"
    errors: list[str] = []
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"runtime policy JSON invalid: {exc}"]
    if not isinstance(policy, dict):
        return ["runtime policy JSON invalid: expected object"]

    required_sections = [
        "read_only_git_subcommands",
        "read_only_local_commands",
        "read_only_aletheia_scripts",
        "read_only_truth_record_actions",
        "checkpoint_state_patterns",
        "checkpoint_excluded_patterns",
        "protected_path_patterns",
        "source_inventory_excluded_dirs",
        "source_inventory_excluded_root_files",
        "source_inventory_sensitive_patterns",
        "source_inventory_kind_keywords",
        "source_inventory_suffix_kinds",
    ]
    for section in required_sections:
        values = policy.get(section)
        if section not in policy:
            errors.append(f"runtime policy missing section: {section}")
            continue
        if section in {"source_inventory_kind_keywords", "source_inventory_suffix_kinds"}:
            if not isinstance(values, dict) or not all(
                isinstance(key, str) and isinstance(value, str) for key, value in values.items()
            ):
                errors.append(f"runtime policy section must be an object of string values: {section}")
            continue
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            errors.append(f"runtime policy section must be a list of strings: {section}")

    for pattern in policy.get("protected_path_patterns", []):
        if not isinstance(pattern, str):
            continue
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"runtime policy protected_path_patterns invalid regex: {pattern}: {exc}")
    for pattern in policy.get("source_inventory_sensitive_patterns", []):
        if not isinstance(pattern, str):
            continue
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"runtime policy source_inventory_sensitive_patterns invalid regex: {pattern}: {exc}")
    large_bytes = policy.get("source_inventory_large_bytes")
    if not isinstance(large_bytes, int) or large_bytes <= 0:
        errors.append("runtime policy source_inventory_large_bytes must be a positive integer")
    return errors


def validate_actions(root: Path) -> list[str]:
    path = root / ".aletheia" / "governance" / "actions.json"
    errors: list[str] = []
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"actions registry JSON invalid: {exc}"]
    if not isinstance(registry, dict):
        return ["actions registry JSON invalid: expected object"]
    if registry.get("schema_version") != 1:
        errors.append("actions registry schema_version must be 1")
    actions = registry.get("actions")
    if not isinstance(actions, list) or not actions:
        errors.append("actions registry actions must be a non-empty list")
        return errors
    seen: set[str] = set()
    valid_risks = {"read-only", "writes-state", "admin", "checkpoint"}
    for action in actions:
        if not isinstance(action, dict):
            errors.append("actions registry action must be an object")
            continue
        action_id = action.get("id")
        if not isinstance(action_id, str) or not re.match(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_]*)+$", action_id):
            errors.append(f"actions registry invalid action id: {action_id}")
            continue
        if action_id in seen:
            errors.append(f"actions registry duplicate action id: {action_id}")
        seen.add(action_id)
        if action.get("risk") not in valid_risks:
            errors.append(f"actions registry invalid risk for {action_id}")
        command = action.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
            errors.append(f"actions registry invalid command for {action_id}")
        else:
            inputs = action.get("inputs")
            for part in command:
                if part.startswith("{{") and part.endswith("}}"):
                    key = part[2:-2]
                    if not isinstance(inputs, dict) or key not in inputs:
                        errors.append(f"actions registry command placeholder missing input for {action_id}: {key}")
        verification = action.get("verification")
        if not isinstance(verification, dict) or verification.get("returncode") != 0:
            errors.append(f"actions registry invalid verification for {action_id}")
    recommended = registry.get("recommended_actions", [])
    if not isinstance(recommended, list) or not all(isinstance(item, str) for item in recommended):
        errors.append("actions registry recommended_actions must be a list of strings")
    else:
        for action_id in recommended:
            if action_id not in seen:
                errors.append(f"actions registry recommended action is missing: {action_id}")
    return errors


def validate_capability_map(root: Path) -> list[str]:
    path = root / ".aletheia" / "CAPABILITY_MAP.md"
    if not path.exists():
        return ["missing capability map: .aletheia/CAPABILITY_MAP.md"]
    text = path.read_text(encoding="utf-8")
    required_terms = [
        "help.py",
        "action.py",
        "actions.json",
        "truth.validate",
        "truth.preflight",
        "truth.checkpoint.dry_run",
        "capability_audit.py",
        "truth_record.py list",
        "truth_record.py create",
        "truth_record.py show",
        "truth_record.py update",
        "truth_record.py archive",
        "model_gate.py --registry register",
        "model_gate.py --registry remove",
    ]
    return [f"capability map missing term: {term}" for term in required_terms if term not in text]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an AletheiaOS scaffold directory.")
    parser.add_argument("scaffold", type=Path)
    args = parser.parse_args()

    root = args.scaffold.resolve()
    missing = [rel for rel in REQUIRED_PATHS if not (root / rel).exists()]
    if missing:
        for rel in missing:
            print(f"missing required path: {rel}", file=sys.stderr)
        return 1

    skeleton_errors = (
        validate_skeleton(root)
        + validate_runtime_policy(root)
        + validate_actions(root)
        + validate_capability_map(root)
        + validate_no_retired_language(root)
        + validate_no_extra_tree_surfaces(root)
    )
    if skeleton_errors:
        for error in skeleton_errors:
            print(error, file=sys.stderr)
        return 1

    print("scaffold validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
