#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "AGENTS.md",
    "START_HERE.md",
    ".claude/settings.json",
    ".aletheia/START_HERE.md",
    ".aletheia/VERSION",
    ".aletheia/governance/CHARTER.md",
    ".aletheia/governance/ATTENTION_POLICY.md",
    ".aletheia/governance/MODEL_GOVERNANCE.md",
    ".aletheia/governance/GIT_POLICY.md",
    ".aletheia/governance/INTAKE_POLICY.md",
    ".aletheia/governance/model_registry.json",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/RISK_REGISTER.md",
    ".aletheia/state/FRONTIER_BOARD.md",
    ".aletheia/state/GLOSSARY.md",
    ".aletheia/state/DOMAIN_PROFILE.md",
    ".aletheia/contracts/INDEX.md",
    ".aletheia/evidence/INDEX.md",
    ".aletheia/nodes/ROOT.yaml",
    ".aletheia/bin/orient.py",
    ".aletheia/bin/context_pack.py",
    ".aletheia/bin/model_gate.py",
    ".aletheia/bin/validate.py",
    ".aletheia/bin/checkpoint.py",
    ".aletheia/bin/overview.py",
    ".aletheia/bin/bootstrap_finalize.py",
    ".aletheia/bin/intake_inventory.py",
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
    ".aletheia/templates/BOOTSTRAP_IMPORT_REPORT.md",
    ".aletheia/templates/BOOTSTRAP_INTAKE_MANIFEST.yaml",
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

LEGACY_REFERENCE_PATTERNS = [
    "aletheia_os/",
    "scripts/aios_",
    ".aios_runtime",
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


def validate_legacy_references(root: Path, errors: list[str]) -> None:
    skip_parts = {"bin", "runtime", "bootstrap_intake", "migrations"}
    for path in (root / ".aletheia").rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py"}:
            continue
        rel_parts = set(path.relative_to(root / ".aletheia").parts)
        if rel_parts & skip_parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(pattern in text for pattern in LEGACY_REFERENCE_PATTERNS):
            errors.append(f"legacy path reference in {path.relative_to(root).as_posix()}")


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
    active_path = root / ".aletheia" / "state" / "ACTIVE_STATE.md"
    if active_path.exists():
        active_nodes = extract_active_nodes(active_path.read_text(encoding="utf-8"))
        missing = sorted(node for node in active_nodes if node not in graph_nodes)
        if missing:
            errors.append("active state references unknown graph nodes: " + ", ".join(missing))
    if "TBD" in graph_text:
        (warnings if bootstrap_mode else errors).append("system graph still contains TBD markers")


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
    validate_graph_and_skeleton(root, errors, warnings, bootstrap_mode)
    validate_legacy_references(root, errors)

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
