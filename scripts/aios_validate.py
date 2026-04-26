#!/usr/bin/env python3
"""Validate the AletheiaOS repository structure.

This script intentionally uses only the Python standard library so it works in
fresh repositories. It performs structural, attention-policy, and lightweight
linkage checks.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "START_HERE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "aletheia_os/AGENTS.md",
    "aletheia_os/00_CHARTER.md",
    "aletheia_os/01_SYSTEM_GRAPH.yaml",
    "aletheia_os/02_ACTIVE_STATE.md",
    "aletheia_os/03_FRONTIER_BOARD.md",
    "aletheia_os/04_RISK_REGISTER.md",
    "aletheia_os/05_GLOSSARY.md",
    "aletheia_os/06_INTERFACE_CONTRACTS.md",
    "aletheia_os/07_EVIDENCE_INDEX.md",
    "aletheia_os/08_GIT_POLICY.md",
    "aletheia_os/09_DOMAIN_PROFILE.md",
    "aletheia_os/10_ATTENTION_POLICY.md",
    "aletheia_os/11_MODEL_GOVERNANCE.md",
    "aletheia_os/model_registry.json",
    "src/AGENTS.md",
    "tests/AGENTS.md",
    "experiments/AGENTS.md",
    "simulations/AGENTS.md",
    "configs/AGENTS.md",
    "docs/AGENTS.md",
    "infra/AGENTS.md",
]

REQUIRED_DIRS = [
    "aletheia_os/contracts",
    "aletheia_os/decisions",
    "aletheia_os/evidence",
    "aletheia_os/hypotheses",
    "aletheia_os/nodes",
    "aletheia_os/playbooks",
    "aletheia_os/session_notes",
    "aletheia_os/agent_runs",
    "aletheia_os/templates",
    "scripts",
    "src",
    "tests",
    "experiments",
    "simulations",
    "configs",
    "docs",
    "infra",
]

PROTECTED_PATTERNS = [
    re.compile(r"(^|/|\\)\.env(\.|$)"),
    re.compile(r"(^|/|\\)secrets(/|\\)"),
    re.compile(r"\.(pem|key|crt|credentials|secret)$", re.IGNORECASE),
]

CRITICAL_TBD_FILES = [
    "aletheia_os/00_CHARTER.md",
    "aletheia_os/01_SYSTEM_GRAPH.yaml",
    "aletheia_os/02_ACTIVE_STATE.md",
    "aletheia_os/09_DOMAIN_PROFILE.md",
    "aletheia_os/model_registry.json",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def extract_graph_node_ids(graph_text: str) -> set[str]:
    ids: set[str] = {"root"}
    in_nodes = False
    for line in graph_text.splitlines():
        if line.startswith("nodes:"):
            in_nodes = True
            continue
        if in_nodes:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                break
            m = re.match(r"^\s{2}([A-Za-z0-9_.-]+):\s*$", line)
            if m:
                ids.add(m.group(1))
    return ids


def extract_file_node_ids() -> set[str]:
    ids: set[str] = set()
    for p in (ROOT / "aletheia_os/nodes").glob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"^id:\s*([A-Za-z0-9_.-]+)\s*$", text, re.MULTILINE)
        if m:
            ids.add(m.group(1))
    return ids


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
            m = re.match(r"^\s*-\s*([A-Za-z0-9_.-]+)\s*$", line)
            if m:
                nodes.add(m.group(1))
    return nodes



def validate_model_registry(errors: list[str], warnings: list[str]) -> None:
    path = ROOT / "aletheia_os/model_registry.json"
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
    for required in ["C0", "C1", "C2", "C3", "C4"]:
        if required not in tiers:
            errors.append(f"model registry missing capability tier: {required}")

    task_classes = registry.get("task_classes", {}) or {}
    for required in ["orientation", "mechanical_implementation", "research_design", "production_safety_critical", "root_theory_revision", "checkpoint", "bootstrap_finalize"]:
        if required not in task_classes:
            errors.append(f"model registry missing task class: {required}")

    valid_tiers = set(tiers) or {"C0", "C1", "C2", "C3", "C4"}
    for name, task in task_classes.items():
        min_tier = str((task or {}).get("min_tier", ""))
        if min_tier not in valid_tiers:
            errors.append(f"task class {name} has invalid min_tier: {min_tier}")
        if "write_allowed" not in task:
            warnings.append(f"task class {name} missing write_allowed")

    registered = registry.get("registered_models", {}) or {}
    enabled = [k for k, v in registered.items() if str((v or {}).get("status", "allowed")) in {"allowed", "approved", "registered"}]
    if not enabled:
        warnings.append("model registry has no enabled registered models; non-trivial writes require operator override or registry customization")

def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    bootstrap_mode = (ROOT / "BOOTSTRAP.md").exists()

    for file in REQUIRED_FILES:
        p = ROOT / file
        if not p.exists():
            errors.append(f"missing required file: {file}")
        elif not p.read_text(encoding="utf-8").strip():
            errors.append(f"empty required file: {file}")

    for directory in REQUIRED_DIRS:
        p = ROOT / directory
        if not p.exists() or not p.is_dir():
            errors.append(f"missing required directory: {directory}")

    graph_nodes: set[str] = set()
    graph_path = ROOT / "aletheia_os/01_SYSTEM_GRAPH.yaml"
    if graph_path.exists():
        graph = graph_path.read_text(encoding="utf-8")
        for required in ["root:", "nodes:", "priority_formula:"]:
            if required not in graph:
                errors.append(f"system graph missing section: {required}")
        graph_nodes = extract_graph_node_ids(graph) | extract_file_node_ids()
        if "TBD" in graph:
            (warnings if bootstrap_mode else errors).append("system graph still contains TBD markers")

    active_state = ROOT / "aletheia_os/02_ACTIVE_STATE.md"
    if active_state.exists():
        text = active_state.read_text(encoding="utf-8")
        for heading in ["## Active frontier", "## Active nodes", "## Current blockers", "## Next actions"]:
            if heading not in text:
                errors.append(f"active state missing heading: {heading}")
        active_nodes = extract_active_nodes(text)
        missing_nodes = sorted(n for n in active_nodes if graph_nodes and n not in graph_nodes)
        if missing_nodes:
            errors.append("active state references unknown graph nodes: " + ", ".join(missing_nodes))

    # Attention entrypoint checks.
    start = ROOT / "START_HERE.md"
    if start.exists():
        start_text = start.read_text(encoding="utf-8")
        for phrase in ["Global View Checksum", "Read order", "aios_orient.py", "src/<project_package_name>/"]:
            if phrase not in start_text:
                errors.append(f"START_HERE.md missing required guidance: {phrase}")

    attention = ROOT / "aletheia_os/10_ATTENTION_POLICY.md"
    if attention.exists():
        att_text = attention.read_text(encoding="utf-8")
        for phrase in ["Context tiers", "Tier 0", "Global View Checksum", "Stop signs", "Context reset protocol"]:
            if phrase not in att_text:
                errors.append(f"attention policy missing section/guidance: {phrase}")

    root_agents = ROOT / "AGENTS.md"
    if root_agents.exists():
        agents_text = root_agents.read_text(encoding="utf-8")
        for phrase in ["START_HERE.md", "10_ATTENTION_POLICY", "Global View Checksum"]:
            if phrase not in agents_text:
                warnings.append(f"AGENTS.md should mention {phrase}")


    # Model governance checks.
    model_governance = ROOT / "aletheia_os/11_MODEL_GOVERNANCE.md"
    if model_governance.exists():
        mg_text = model_governance.read_text(encoding="utf-8")
        for phrase in ["Capability tiers", "Task classes", "Attribution requirement", "aios_model_gate.py"]:
            if phrase not in mg_text:
                errors.append(f"model governance policy missing required guidance: {phrase}")
    validate_model_registry(errors, warnings)

    model_gate = ROOT / "scripts/aios_model_gate.py"
    if not model_gate.exists():
        errors.append("missing model gate script: scripts/aios_model_gate.py")

    session_template = ROOT / "aletheia_os/templates/session_note_template.md"
    if session_template.exists():
        st = session_template.read_text(encoding="utf-8")
        for phrase in ["Agent attribution", "Model id", "Task class"]:
            if phrase not in st:
                warnings.append(f"session note template should include model attribution field: {phrase}")

    # Ensure evidence/decision/hypothesis files generally mention linked nodes.
    for folder in ["aletheia_os/evidence", "aletheia_os/decisions", "aletheia_os/hypotheses"]:
        for p in (ROOT / folder).glob("*.md"):
            text = p.read_text(encoding="utf-8")
            if "README" in p.name:
                continue
            if not re.search(r"Linked|Affected nodes|Linked nodes|system node|Affected", text, re.IGNORECASE):
                warnings.append(f"{rel(p)} may not declare linked/affected nodes")

    # Detect protected files accidentally added to repo tree.
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        r = rel(p)
        if r.startswith(".git/") or r.startswith(".aios_runtime/"):
            continue
        if any(rx.search(r) for rx in PROTECTED_PATTERNS):
            warnings.append(f"protected-looking file exists in tree: {r}")

    if not bootstrap_mode:
        for file in CRITICAL_TBD_FILES:
            p = ROOT / file
            if p.exists() and "TBD" in p.read_text(encoding="utf-8"):
                errors.append(f"post-bootstrap critical file still contains TBD markers: {file}")

    if warnings:
        print("AIOS validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("AIOS validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("AIOS validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
