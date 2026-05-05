#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


TRUTH_FILES = {
    "charter": ".aletheia/governance/CHARTER.md",
    "attention": ".aletheia/governance/ATTENTION_POLICY.md",
    "active": ".aletheia/state/ACTIVE_STATE.md",
    "graph": ".aletheia/state/SYSTEM_GRAPH.yaml",
    "skeleton": ".aletheia/state/SKELETON.yaml",
    "frontier": ".aletheia/state/FRONTIER_BOARD.md",
    "risks": ".aletheia/state/RISK_REGISTER.md",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read(root: Path, rel: str) -> str:
    path = root / rel
    if not path.exists():
        return f"MISSING: {rel}"
    return path.read_text(encoding="utf-8").rstrip()


def section(text: str, name: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1).strip() if match else "unknown"


def active_nodes(active_text: str) -> list[str]:
    nodes: list[str] = []
    for value in re.findall(r"`([A-Za-z0-9_.-]+)`", section(active_text, "Active nodes")):
        if value not in nodes:
            nodes.append(value)
    return nodes or ["root"]


def skeleton_refs(skeleton_text: str, ref_name: str) -> list[str]:
    match = re.search(rf"(?ms)^\s{{4}}{re.escape(ref_name)}:\s*\n((?:\s{{6}}- .+\n)+)", skeleton_text)
    if not match:
        return []
    return [line.split("-", 1)[1].strip() for line in match.group(1).splitlines() if "-" in line]


def print_block(title: str, content: str) -> None:
    print(f"## {title}")
    print()
    print(content.rstrip() if content.strip() else "None")
    print()


def main() -> int:
    root = repo_root()
    active_text = read(root, TRUTH_FILES["active"])
    skeleton_text = read(root, TRUTH_FILES["skeleton"])
    nodes = active_nodes(active_text)
    warnings: list[str] = []
    for rel in TRUTH_FILES.values():
        if not (root / rel).exists():
            warnings.append(f"missing truth file: {rel}")
    if "TBD" in read(root, TRUTH_FILES["charter"]):
        warnings.append("charter still contains TBD markers")
    if "TBD" in active_text:
        warnings.append("active state still contains TBD markers")

    print("# AletheiaOS Project Truth Orientation")
    print()
    print(f"Repository: {root}")
    print()
    print_block("Project Truth", read(root, TRUTH_FILES["charter"]))
    print_block("Active Frontier", section(active_text, "Active frontier"))
    print_block("Active Node", "\n".join(nodes))
    print_block("Parent Constraints", read(root, TRUTH_FILES["attention"]))
    print_block("System Graph", read(root, TRUTH_FILES["graph"]))
    print_block("Project Skeleton", skeleton_text)
    print_block("Linked Evidence", "\n".join(skeleton_refs(skeleton_text, "evidence_refs")))
    print_block("Linked Contracts", "\n".join(skeleton_refs(skeleton_text, "contract_refs")))
    print_block("Known Risks", read(root, TRUTH_FILES["risks"]))
    print_block("Missing Or Stale Truth Warnings", "\n".join(warnings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
