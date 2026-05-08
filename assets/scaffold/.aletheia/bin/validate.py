#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path


REQUIRED_PATHS = [
    "AGENTS.md",
    "START_HERE.md",
    ".claude/settings.json",
    ".aletheia/START_HERE.md",
    ".aletheia/CAPABILITY_MAP.md",
    ".aletheia/VERSION",
    ".aletheia/governance/CHARTER.md",
    ".aletheia/governance/ATTENTION_POLICY.md",
    ".aletheia/governance/MODEL_GOVERNANCE.md",
    ".aletheia/governance/GIT_POLICY.md",
    ".aletheia/governance/SOURCE_POLICY.md",
    ".aletheia/governance/TREE_GOVERNANCE.md",
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
    ".aletheia/state/ORPHANS.yaml",
    ".aletheia/contracts/INDEX.md",
    ".aletheia/evidence/INDEX.md",
    ".aletheia/nodes/ROOT.yaml",
    ".aletheia/playbooks/drift_audit.md",
    ".aletheia/playbooks/external_llm_wiki_handoff.md",
    ".aletheia/playbooks/wiki_handoff_promotion.md",
    ".aletheia/bin/help.py",
    ".aletheia/bin/action.py",
    ".aletheia/bin/capability_audit.py",
    ".aletheia/bin/orient.py",
    ".aletheia/bin/context_pack.py",
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

REQUIRED_DIRS = [
    ".aletheia/agent_runs",
    ".aletheia/contracts",
    ".aletheia/decisions",
    ".aletheia/evidence",
    ".aletheia/hypotheses",
    ".aletheia/nodes",
    ".aletheia/playbooks",
    ".aletheia/risks",
    ".aletheia/session_notes",
    ".aletheia/templates",
]

REQUIRED_CLAUDE_COMMANDS = {
    "SessionStart": "python3 .aletheia/bin/model_gate.py --hook-mode sessionstart",
    "PreToolUse": "python3 .aletheia/bin/model_gate.py --hook-mode pretooluse",
    "PostToolUse": "python3 .aletheia/bin/change_hook.py",
    "Stop": "python3 .aletheia/bin/stop_hook.py",
}

CRITICAL_TBD_FILES = [
    ".aletheia/governance/CHARTER.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/DOMAIN_PROFILE.md",
    ".aletheia/governance/model_registry.json",
]

PROTECTED_PATTERNS = [
    re.compile(r"(^|/|\\)\.env(\.|$)"),
    re.compile(r"(^|/|\\)secrets(/|\\)"),
    re.compile(r"\.(pem|key|crt|credentials|secret)$", re.IGNORECASE),
]

def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def extract_root_children_yaml(text: str) -> list[str]:
    lines = text.splitlines()
    in_root = False
    in_children = False
    children: list[str] = []
    for line in lines:
        if line == "root:":
            in_root = True
            continue
        if in_root and line and not line.startswith(" "):
            break
        if in_root and line == "  children:":
            in_children = True
            continue
        if in_children:
            if line.startswith("    - "):
                children.append(line.split("-", 1)[1].strip())
                continue
            if line.startswith("  ") and not line.startswith("    "):
                break
    return children


def extract_skeleton_root_children(text: str) -> list[str]:
    root_match = re.search(r"(?m)^  root:\s*$", text)
    if not root_match:
        return []
    root_block = []
    for line in text[root_match.end() :].splitlines():
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", line):
            break
        root_block.append(line)
    block = "\n".join(root_block)
    match = re.search(r"(?m)^    children:\s*\n((?:      - .+\n)+)", block)
    if not match:
        return []
    return [line.split("-", 1)[1].strip() for line in match.group(1).splitlines() if line.strip().startswith("-")]


def extract_active_nodes(active_text: str) -> set[str]:
    nodes: set[str] = set()
    in_section = False
    for line in active_text.splitlines():
        if line.strip() == "## Active nodes":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            nodes.update(re.findall(r"`([A-Za-z0-9_.-]+)`", line))
            match = re.match(r"^\s*-\s*([A-Za-z0-9_.-]+)\s*$", line)
            if match:
                nodes.add(match.group(1))
    return nodes


def extract_graph_node_ids(graph_text: str) -> set[str]:
    ids = {"root"}
    in_nodes = False
    for line in graph_text.splitlines():
        if line.startswith("nodes:"):
            in_nodes = True
            continue
        if in_nodes:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                break
            match = re.match(r"^\s{2}([A-Za-z0-9_.-]+):\s*$", line)
            if match:
                ids.add(match.group(1))
    return ids


def extract_skeleton_nodes(skeleton_text: str) -> dict[str, dict[str, object]]:
    nodes: dict[str, dict[str, object]] = {}
    in_nodes = False
    current_id: str | None = None
    current_list: str | None = None
    for line in skeleton_text.splitlines():
        if line.startswith("nodes:"):
            in_nodes = True
            continue
        if not in_nodes:
            continue
        node_match = re.match(r"^\s{2}([A-Za-z0-9_.-]+):\s*$", line)
        if node_match:
            current_id = node_match.group(1)
            nodes[current_id] = {}
            current_list = None
            continue
        if current_id is None:
            continue
        field_match = re.match(r"^\s{4}([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if field_match:
            key = field_match.group(1)
            value = field_match.group(2).strip()
            current_list = None
            if value == "[]":
                nodes[current_id][key] = []
            elif value == "":
                nodes[current_id][key] = []
                current_list = key
            elif value == "null":
                nodes[current_id][key] = None
            else:
                nodes[current_id][key] = value.strip("\"'")
            continue
        if current_list:
            item_match = re.match(r"^\s{6}-\s+(.+?)\s*$", line)
            if item_match:
                value = item_match.group(1).strip().strip("\"'")
                existing = nodes[current_id].setdefault(current_list, [])
                if isinstance(existing, list):
                    existing.append(value)
    return nodes


def detect_cycles(nodes: dict[str, dict[str, object]]) -> list[str]:
    cycles: list[str] = []
    for node_id in nodes:
        seen: set[str] = set()
        current = node_id
        while current in nodes:
            if current in seen:
                cycles.append(node_id)
                break
            seen.add(current)
            parent = nodes[current].get("parent")
            if not isinstance(parent, str) or parent == current:
                if parent == current:
                    cycles.append(node_id)
                break
            current = parent
    return sorted(set(cycles))


def extract_orphan_count(orphan_text: str) -> int:
    in_orphans = False
    count = 0
    for line in orphan_text.splitlines():
        if line.strip() == "orphans: []":
            return 0
        if line.startswith("orphans:"):
            in_orphans = True
            continue
        if in_orphans and re.match(r"^\s{2}-\s+id:\s*\S+", line):
            count += 1
    return count


def extract_stale_orphan_ids(orphan_text: str) -> list[str]:
    stale: list[str] = []
    current_id: str | None = None
    in_orphans = False
    today = date.today().isoformat()
    for line in orphan_text.splitlines():
        if line.startswith("orphans:"):
            in_orphans = True
            continue
        if not in_orphans:
            continue
        item = re.match(r"^\s{2}-\s+id:\s*(.+?)\s*$", line)
        if item:
            current_id = item.group(1).strip().strip("\"'")
            continue
        review = re.match(r"^\s{4}next_review:\s*(.+?)\s*$", line)
        if review and current_id:
            value = review.group(1).strip().strip("\"'")
            if value and value < today:
                stale.append(current_id)
    return stale


def extract_orphan_entries(orphan_text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_orphans = False
    for line in orphan_text.splitlines():
        if line.strip() == "orphans: []":
            return []
        if line.startswith("orphans:"):
            in_orphans = True
            continue
        if not in_orphans:
            continue
        item = re.match(r"^\s{2}-\s+id:\s*(.+?)\s*$", line)
        if item:
            current = {"id": item.group(1).strip().strip("\"'")}
            entries.append(current)
            continue
        field = re.match(r"^\s{4}([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
        if field and current is not None:
            current[field.group(1)] = field.group(2).strip().strip("\"'")
    return entries


def extract_skeleton_refs(skeleton_text: str) -> list[str]:
    refs: list[str] = []
    in_ref_list = False
    for line in skeleton_text.splitlines():
        field = re.match(r"^\s{4}(contract_refs|decision_refs|evidence_refs):\s*(.*)$", line)
        if field:
            in_ref_list = True
            inline = field.group(2).strip()
            if inline and inline != "[]":
                refs.extend(re.findall(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.\-/]+", inline))
            continue
        if in_ref_list:
            item = re.match(r"^\s{6}-\s+(.+?)\s*$", line)
            if item:
                value = item.group(1).strip().strip("\"'")
                if value:
                    refs.append(value)
                continue
            if re.match(r"^\s{4}[A-Za-z_][A-Za-z0-9_]*:", line) or re.match(r"^\s{2}[A-Za-z0-9_.-]+:", line):
                in_ref_list = False
    return refs


def resolve_truth_ref(root: Path, ref: str) -> Path | None:
    normalized = ref.strip().strip("\"'")
    if not normalized or normalized.startswith("/") or ".." in Path(normalized).parts:
        return None
    if normalized.startswith(".aletheia/"):
        return root / normalized
    if normalized.startswith(("contracts/", "decisions/", "evidence/")):
        return root / ".aletheia" / normalized
    return None


def section_body(text: str, section_name: str) -> str | None:
    pattern = re.compile(rf"(?ims)^##\s+{re.escape(section_name)}\s*\n(.*?)(?=^##\s+|\Z)")
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def has_nonempty_section(text: str, section_name: str) -> bool:
    body = section_body(text, section_name)
    return body is not None and bool(body.strip())


def markdown_title(text: str, prefix: str) -> str | None:
    match = re.search(rf"(?im)^#\s+{re.escape(prefix)}:\s*(.+?)\s*$", text)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1).strip()).lower()


def markdown_refs(text: str) -> list[str]:
    refs: list[str] = []
    refs.extend(re.findall(r"`([^`]+)`", text))
    refs.extend(re.findall(r"\[.+?\]\(([^)]+)\)", text))
    for line in text.splitlines():
        item = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if item:
            value = item.group(1).strip().strip("\"'")
            if value and not value.startswith("[") and "`" not in value:
                refs.append(value)
    return refs


def metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?im)^\s*-?\s*{re.escape(key)}:\s*(.+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().lower()


def truth_record_files(root: Path, rel: str) -> list[Path]:
    directory = root / ".aletheia" / rel
    if not directory.exists():
        return []
    return sorted(
        path
        for path in directory.glob("*.md")
        if path.is_file() and path.name != "INDEX.md" and path.name != ".gitkeep"
    )


def validate_truth_record_semantics(root: Path, errors: list[str]) -> None:
    accepted_decisions: dict[str, str] = {}
    hypothesis_lifecycle: dict[str, tuple[str, str]] = {}
    for path in truth_record_files(root, "evidence"):
        text = path.read_text(encoding="utf-8")
        for section in ["Source refs", "Limitations", "Invalidation criteria", "Confidence impact"]:
            if not has_nonempty_section(text, section):
                rel = path.relative_to(root).as_posix()
                errors.append(f"evidence record missing required section: {rel} {section}")

    for path in truth_record_files(root, "hypotheses"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        lifecycle = metadata_value(text, "Lifecycle") or "hypothesis"
        hypothesis_lifecycle[rel] = (lifecycle, text)
        if not (has_nonempty_section(text, "Invalidation Criteria") or has_nonempty_section(text, "Invalidation criteria")):
            errors.append(f"hypothesis record missing required section: {rel} Invalidation criteria")
        if lifecycle in {"accepted", "operationalized", "evidence-backed"} and not has_nonempty_section(text, "Supporting Evidence"):
            errors.append(f"hypothesis lifecycle requires supporting evidence: {rel}")

    for path in truth_record_files(root, "decisions"):
        text = path.read_text(encoding="utf-8")
        if not re.search(r"(?im)^Status:\s*accepted\s*$", text):
            continue
        rel = path.relative_to(root).as_posix()
        title = markdown_title(text, "Decision")
        if title:
            if title in accepted_decisions:
                errors.append(f"duplicate accepted decision title: {title}")
            else:
                accepted_decisions[title] = rel
        evidence_links = section_body(text, "Evidence links")
        if not evidence_links:
            rel = path.relative_to(root).as_posix()
            errors.append(f"accepted decision missing evidence links: {rel}")
            continue
        for ref in markdown_refs(evidence_links):
            target = resolve_truth_ref(root, ref)
            if target is None:
                errors.append(f"accepted decision evidence link is outside allowed truth records: {ref}")
            elif not target.exists():
                errors.append(f"accepted decision evidence link target missing: {target.relative_to(root).as_posix()}")
        hypothesis_links = section_body(text, "Hypothesis links")
        if hypothesis_links:
            for ref in markdown_refs(hypothesis_links):
                normalized = ref.strip().strip("\"'")
                if normalized.startswith(".aletheia/"):
                    rel_ref = normalized
                elif normalized.startswith("hypotheses/"):
                    rel_ref = ".aletheia/" + normalized
                else:
                    continue
                state = hypothesis_lifecycle.get(rel_ref)
                if not state:
                    errors.append(f"accepted decision hypothesis link target missing: {rel_ref}")
                    continue
                lifecycle, hypothesis_text = state
                review_note = section_body(hypothesis_text, "Review Note") or ""
                has_review_override = review_note.strip() not in {"", "TBD."}
                if lifecycle in {"falsified", "weakened"} and has_review_override:
                    continue
                if lifecycle in {"falsified", "weakened"}:
                    errors.append(f"accepted decision references {lifecycle} hypothesis: {rel} -> {rel_ref}")


def validate_claude_settings(root: Path, errors: list[str]) -> None:
    path = root / ".claude" / "settings.json"
    if not path.exists():
        return
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Claude settings JSON invalid: {exc}")
        return
    hooks = settings.get("hooks", {}) if isinstance(settings, dict) else {}
    for event_name, command in REQUIRED_CLAUDE_COMMANDS.items():
        entries = hooks.get(event_name, []) if isinstance(hooks, dict) else []
        commands = []
        for entry in entries:
            for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
                if isinstance(hook, dict):
                    commands.append(hook.get("command"))
        if command not in commands:
            errors.append(f"Claude settings missing required hook command for {event_name}: {command}")


def validate_model_registry(root: Path, errors: list[str], warnings: list[str]) -> None:
    path = root / ".aletheia" / "governance" / "model_registry.json"
    if not path.exists():
        return
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"model registry JSON invalid: {exc}")
        return
    for section in ["default_policy", "capability_tiers", "task_classes", "registered_models", "denylist"]:
        if section not in registry:
            errors.append(f"model registry missing section: {section}")
    tiers = registry.get("capability_tiers", {}) or {}
    for tier in ["C0", "C1", "C2", "C3", "C4"]:
        if tier not in tiers:
            errors.append(f"model registry missing capability tier: {tier}")
    task_classes = registry.get("task_classes", {}) or {}
    for task in ["orientation", "mechanical_implementation", "research_design", "root_theory_revision", "checkpoint", "bootstrap_finalize"]:
        if task not in task_classes:
            errors.append(f"model registry missing task class: {task}")
    if not registry.get("registered_models"):
        warnings.append("model registry has no enabled registered models; writes require operator approval or registry customization")


def validate_runtime_policy(root: Path, errors: list[str]) -> None:
    path = root / ".aletheia" / "governance" / "runtime_policy.json"
    if not path.exists():
        return
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"runtime policy JSON invalid: {exc}")
        return
    if not isinstance(policy, dict):
        errors.append("runtime policy JSON invalid: expected object")
        return

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


def validate_actions(root: Path, errors: list[str]) -> None:
    path = root / ".aletheia" / "governance" / "actions.json"
    if not path.exists():
        return
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"actions registry JSON invalid: {exc}")
        return
    if not isinstance(registry, dict):
        errors.append("actions registry JSON invalid: expected object")
        return
    if registry.get("schema_version") != 1:
        errors.append("actions registry schema_version must be 1")
    actions = registry.get("actions")
    if not isinstance(actions, list) or not actions:
        errors.append("actions registry actions must be a non-empty list")
        return
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


def validate_capability_map(root: Path, errors: list[str]) -> None:
    path = root / ".aletheia" / "CAPABILITY_MAP.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    required_terms = [
        "help.py",
        "action.py",
        "actions.json",
        "truth.orient.runtime",
        "truth.status",
        "truth.validate",
        "truth.preflight",
        "truth.checkpoint.dry_run",
        "truth.orphan.create",
        "truth.orphan.archive",
        "truth.bootstrap.guided.inspect",
        "truth.bootstrap.finalize.inspect",
        "capability_audit.py",
        "truth_record.py list",
        "truth_record.py create",
        "truth_record.py show",
        "truth_record.py update",
        "truth_record.py archive",
        "truth_record.py create/list/show/update/archive orphan",
        "truth_record.py show charter current",
        "truth_record.py show user-preferences current",
        "actions-registry",
        "guided_bootstrap.py --inspect --json",
        "bootstrap_finalize.py --inspect --json",
        "generated-output boundaries",
        "model_gate.py --registry register",
        "model_gate.py --registry remove",
    ]
    for term in required_terms:
        if term not in text:
            errors.append(f"capability map missing term: {term}")


def validate_graph_and_skeleton(root: Path, errors: list[str], warnings: list[str], bootstrap_mode: bool) -> None:
    graph_path = root / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml"
    skeleton_path = root / ".aletheia" / "state" / "SKELETON.yaml"
    if not graph_path.exists() or not skeleton_path.exists():
        return
    graph_text = graph_path.read_text(encoding="utf-8")
    skeleton_text = skeleton_path.read_text(encoding="utf-8")
    for section in ["root:", "nodes:"]:
        if section not in graph_text:
            errors.append(f"system graph missing section: {section}")
    graph_children = extract_root_children_yaml(graph_text)
    skeleton_children = extract_skeleton_root_children(skeleton_text)
    if graph_children and skeleton_children and graph_children != skeleton_children:
        errors.append("skeleton root children do not match system graph root children")
    graph_nodes = extract_graph_node_ids(graph_text)
    skeleton_nodes = extract_skeleton_nodes(skeleton_text)
    if "root" not in skeleton_nodes:
        errors.append("skeleton missing root node")
    valid_layers = {"root", "trunk", "branch", "leaf"}
    for node_id, node in skeleton_nodes.items():
        layer = node.get("layer")
        if isinstance(layer, str) and layer not in valid_layers:
            errors.append(f"skeleton node has invalid layer: {node_id} {layer}")
        parent = node.get("parent")
        if node_id == "root":
            if parent is not None:
                errors.append("skeleton root parent must be null")
        elif not isinstance(parent, str) or not parent:
            errors.append(f"skeleton node missing parent: {node_id}")
        elif parent not in skeleton_nodes and parent not in graph_nodes:
            errors.append(f"skeleton node parent missing: {node_id} parent={parent}")
        children = node.get("children")
        if isinstance(children, list):
            if len(children) > 12:
                warnings.append(f"skeleton node may be overloaded: {node_id} has {len(children)} children")
            for child in children:
                if isinstance(child, str) and child not in skeleton_nodes and child not in graph_nodes:
                    errors.append(f"skeleton child target missing: {node_id} child={child}")
                elif isinstance(child, str) and child in skeleton_nodes:
                    child_parent = skeleton_nodes[child].get("parent")
                    if child_parent != node_id:
                        errors.append(f"skeleton child parent mismatch: {node_id} child={child} parent={child_parent}")
        if isinstance(parent, str) and parent in skeleton_nodes and node.get("status") != "archived":
            parent_children = skeleton_nodes[parent].get("children")
            if isinstance(parent_children, list) and node_id not in parent_children:
                errors.append(f"skeleton parent missing child link: {node_id} parent={parent}")
    cycles = detect_cycles(skeleton_nodes)
    if cycles:
        errors.append("skeleton contains parent cycle: " + ", ".join(cycles))
    active_path = root / ".aletheia" / "state" / "ACTIVE_STATE.md"
    if active_path.exists():
        active_nodes = extract_active_nodes(active_path.read_text(encoding="utf-8"))
        valid_active_nodes = set(graph_nodes) | set(skeleton_nodes)
        missing = sorted(node for node in active_nodes if node not in valid_active_nodes)
        if missing:
            errors.append("active state references unknown graph or skeleton nodes: " + ", ".join(missing))
        archived = sorted(
            node
            for node in active_nodes
            if node in skeleton_nodes and skeleton_nodes[node].get("status") == "archived"
        )
        if archived:
            errors.append("active state references archived skeleton node: " + ", ".join(archived))
    if "TBD" in graph_text:
        (warnings if bootstrap_mode else errors).append("system graph still contains TBD markers")
    for ref in extract_skeleton_refs(skeleton_text):
        target = resolve_truth_ref(root, ref)
        if target is None:
            errors.append(f"skeleton reference is outside allowed truth records: {ref}")
        elif not target.exists():
            errors.append(f"skeleton reference target missing: {target.relative_to(root).as_posix()}")


def validate_orphans(root: Path, errors: list[str], warnings: list[str]) -> None:
    path = root / ".aletheia" / "state" / "ORPHANS.yaml"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for section in ["schema: AIOS_ORPHANS", "review_policy:", "orphans:"]:
        if section not in text:
            errors.append(f"orphans state missing section: {section}")
    if ".." in text:
        errors.append("orphans state contains unsafe parent traversal marker")
    graph_path = root / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml"
    skeleton_path = root / ".aletheia" / "state" / "SKELETON.yaml"
    graph_nodes = extract_graph_node_ids(graph_path.read_text(encoding="utf-8")) if graph_path.exists() else {"root"}
    skeleton_nodes = extract_skeleton_nodes(skeleton_path.read_text(encoding="utf-8")) if skeleton_path.exists() else {}
    valid_parents = set(graph_nodes) | set(skeleton_nodes)
    seen: set[str] = set()
    for entry in extract_orphan_entries(text):
        orphan_id = entry.get("id", "")
        if not orphan_id:
            errors.append("orphan entry missing id")
        elif orphan_id in seen:
            errors.append(f"orphan entry duplicate id: {orphan_id}")
        seen.add(orphan_id)
        for field in ["status", "summary", "candidate_parent"]:
            if not entry.get(field):
                errors.append(f"orphan entry missing field: {orphan_id or 'unknown'} {field}")
        candidate_parent = entry.get("candidate_parent")
        if candidate_parent and candidate_parent != "unknown" and candidate_parent not in valid_parents:
            errors.append(f"orphan entry candidate parent missing: {orphan_id} candidate_parent={candidate_parent}")
    count = extract_orphan_count(text)
    if count:
        warnings.append(f"orphan incubator contains {count} entries requiring review")
    stale = extract_stale_orphan_ids(text)
    if stale:
        warnings.append("orphan review is stale: " + ", ".join(stale))


def main() -> int:
    root = repo_root()
    errors: list[str] = []
    warnings: list[str] = []
    bootstrap_mode = (root / "BOOTSTRAP.md").exists()

    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required path: {rel}")
        elif path.is_file() and not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty required path: {rel}")

    for rel in REQUIRED_DIRS:
        path = root / rel
        if not path.exists() or not path.is_dir():
            errors.append(f"missing required directory: {rel}")

    validate_claude_settings(root, errors)
    validate_model_registry(root, errors, warnings)
    validate_runtime_policy(root, errors)
    validate_actions(root, errors)
    validate_capability_map(root, errors)
    validate_graph_and_skeleton(root, errors, warnings, bootstrap_mode)
    validate_orphans(root, errors, warnings)
    validate_truth_record_semantics(root, errors)

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".git/") or rel.startswith(".aletheia/runtime/"):
            continue
        if any(pattern.search(rel) for pattern in PROTECTED_PATTERNS):
            warnings.append(f"protected-looking file exists in tree: {rel}")

    if not bootstrap_mode:
        for rel in CRITICAL_TBD_FILES:
            path = root / rel
            if path.exists() and "TBD" in path.read_text(encoding="utf-8"):
                errors.append(f"post-bootstrap critical file still contains TBD markers: {rel}")

    if warnings:
        print("AletheiaOS validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("AletheiaOS validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("AletheiaOS validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
