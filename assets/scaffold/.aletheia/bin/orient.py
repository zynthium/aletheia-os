#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
RECORD_DIRS = {
    "decisions": ".aletheia/decisions",
    "evidence": ".aletheia/evidence",
    "contracts": ".aletheia/contracts",
    "hypotheses": ".aletheia/hypotheses",
    "nodes": ".aletheia/nodes",
    "risks": ".aletheia/risks",
    "session_notes": ".aletheia/session_notes",
    "agent_runs": ".aletheia/agent_runs",
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
    refs: list[str] = []
    in_refs = False
    for line in skeleton_text.splitlines():
        field = re.match(r"^\s{4}([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if field:
            if in_refs:
                break
            if field.group(1) == ref_name:
                in_refs = True
                inline = field.group(2).strip()
                if inline and inline != "[]":
                    refs.append(inline.strip("\"'"))
            continue
        if in_refs:
            item = re.match(r"^\s{6}-\s+(.+?)\s*$", line)
            if item:
                refs.append(item.group(1).strip().strip("\"'"))
                continue
            if line.strip():
                break
    return refs


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def current_agent_run(root: Path) -> str:
    path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not path.exists():
        return "No current agent run record."
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"Current agent run record is invalid: {exc}"
    if not isinstance(data, dict):
        return "Current agent run record is invalid: expected JSON object."
    fields = [
        "run_id",
        "provider",
        "model_id",
        "capability_tier",
        "task_class",
        "gate_status",
        "objective",
        "recorded_at",
    ]
    return "\n".join(f"- {field}: {data.get(field, 'unknown')}" for field in fields)


def recent_session_notes(root: Path, limit: int = 5) -> str:
    directory = root / ".aletheia" / "session_notes"
    if not directory.exists():
        return "None"
    notes = sorted(
        (path for path in directory.glob("*.md") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:limit]
    if not notes:
        return "None"
    return "\n".join(f"- `{relative(path, root)}`" for path in notes)


def record_inventory(root: Path, include_activity: bool = False) -> str:
    lines: list[str] = []
    for name, rel in RECORD_DIRS.items():
        if not include_activity and name in {"session_notes", "agent_runs"}:
            continue
        directory = root / rel
        records = []
        if directory.exists():
            records = sorted(
                path
                for path in directory.glob("*")
                if path.is_file() and path.name not in {".gitkeep", "INDEX.md"}
            )
        lines.append(f"### {name}")
        lines.extend(f"- `{relative(path, root)}`" for path in records[:10])
        if len(records) > 10:
            lines.append(f"- ... {len(records) - 10} more")
        if not records:
            lines.append("None")
        lines.append("")
    return "\n".join(lines).rstrip()


def print_block(title: str, content: str) -> None:
    print(f"## {title}")
    print()
    print(content.rstrip() if content.strip() else "None")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orient on AletheiaOS project truth.")
    parser.add_argument(
        "--with-runtime",
        action="store_true",
        help="Append high-churn current agent run and recent session note references.",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Omit record inventory and runtime sections for the most cache-friendly output.",
    )
    args = parser.parse_args()
    if args.static and args.with_runtime:
        parser.error("--static cannot be combined with --with-runtime")
    return args


def main() -> int:
    args = parse_args()
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
    print_block("Capability Map", read(root, ".aletheia/CAPABILITY_MAP.md"))
    if not args.static:
        print_block("Truth Record Inventory", record_inventory(root, include_activity=args.with_runtime))
    print_block("Missing Or Stale Truth Warnings", "\n".join(warnings))
    print_block(
        "Global View Checksum",
        """```text
Root mission:
Active frontier:
Active node:
Parent constraints:
Success criteria:
Invalidation criteria:
Required truth updates:
Verification path:
Model gate status:
Checkpoint plan:
```""",
    )
    if args.with_runtime:
        print_block("Current Agent Run", current_agent_run(root))
        print_block("Recent Session Notes", recent_session_notes(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
