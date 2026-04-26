#!/usr/bin/env python3
"""Validate the AI Project OS scaffold.

This script intentionally uses only the Python standard library so it works in
fresh repositories. It performs structural and lightweight linkage checks.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "project_os/00_CHARTER.md",
    "project_os/01_SYSTEM_GRAPH.yaml",
    "project_os/02_ACTIVE_STATE.md",
    "project_os/03_FRONTIER_BOARD.md",
    "project_os/04_RISK_REGISTER.md",
    "project_os/05_GLOSSARY.md",
    "project_os/06_INTERFACE_CONTRACTS.md",
    "project_os/07_EVIDENCE_INDEX.md",
    "project_os/08_GIT_POLICY.md",
    "project_os/09_DOMAIN_PROFILE.md",
]

REQUIRED_DIRS = [
    "project_os/contracts",
    "project_os/decisions",
    "project_os/evidence",
    "project_os/hypotheses",
    "project_os/nodes",
    "project_os/playbooks",
    "project_os/session_notes",
    "project_os/templates",
    "scripts",
]

PROTECTED_PATTERNS = [
    re.compile(r"(^|/|\\)\.env(\.|$)"),
    re.compile(r"(^|/|\\)secrets(/|\\)"),
    re.compile(r"\.(pem|key|crt|credentials|secret)$", re.IGNORECASE),
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

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

    graph_path = ROOT / "project_os/01_SYSTEM_GRAPH.yaml"
    if graph_path.exists():
        graph = graph_path.read_text(encoding="utf-8")
        for required in ["root:", "nodes:", "priority_formula:"]:
            if required not in graph:
                errors.append(f"system graph missing section: {required}")
        if "TBD" in graph:
            warnings.append("system graph still contains TBD markers")

    active_state = ROOT / "project_os/02_ACTIVE_STATE.md"
    if active_state.exists():
        text = active_state.read_text(encoding="utf-8")
        for heading in ["## Active frontier", "## Active nodes", "## Current blockers", "## Next actions"]:
            if heading not in text:
                errors.append(f"active state missing heading: {heading}")

    # Ensure evidence/decision/hypothesis files generally mention linked nodes.
    for folder in ["project_os/evidence", "project_os/decisions", "project_os/hypotheses"]:
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
