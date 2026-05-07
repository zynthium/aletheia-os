#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


FILES = [
    ".aletheia/CAPABILITY_MAP.md",
    ".aletheia/governance/CHARTER.md",
    ".aletheia/governance/ATTENTION_POLICY.md",
    ".aletheia/governance/MODEL_GOVERNANCE.md",
    ".aletheia/governance/TREE_GOVERNANCE.md",
    ".aletheia/governance/model_registry.json",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/ORPHANS.yaml",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def clip(text: str, limit: int = 5000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]\n"


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def record_inventory(root: Path) -> str:
    sections = {
        "decisions": root / ".aletheia" / "decisions",
        "evidence": root / ".aletheia" / "evidence",
        "contracts": root / ".aletheia" / "contracts",
        "hypotheses": root / ".aletheia" / "hypotheses",
        "nodes": root / ".aletheia" / "nodes",
        "risks": root / ".aletheia" / "risks",
        "session_notes": root / ".aletheia" / "session_notes",
        "agent_runs": root / ".aletheia" / "agent_runs",
    }
    lines: list[str] = []
    for name, directory in sections.items():
        lines.append(f"### {name}")
        records = []
        if directory.exists():
            records = sorted(
                path
                for path in directory.glob("*")
                if path.is_file() and path.name not in {".gitkeep", "INDEX.md"}
            )
        if records:
            lines.extend(f"- `{relative(path, root)}`" for path in records)
        else:
            lines.append("None")
        lines.append("")
    return "\n".join(lines).rstrip()


def source_inventory_summary(root: Path) -> str:
    path = root / ".aletheia" / "source_inventory" / "inventory.json"
    if not path.exists():
        return "No source inventory found. Run `python3 .aletheia/bin/source_inventory.py`."
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"Source inventory is invalid: {exc}"
    if not isinstance(data, dict):
        return "Source inventory is invalid: expected JSON object."
    items = data.get("items")
    if not isinstance(items, list):
        return "Source inventory is invalid: expected items list."

    kind_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    full_content_candidates = 0
    deferred_or_unsafe = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        classification = item.get("initial_classification")
        if isinstance(kind, str):
            kind_counts[kind] += 1
        if isinstance(classification, str):
            classification_counts[classification] += 1
        if item.get("should_read_full_content") is True:
            full_content_candidates += 1
        if classification in {"unsafe_or_sensitive", "deferred_due_to_size"}:
            deferred_or_unsafe += 1

    lines = [
        "- inventory: `.aletheia/source_inventory/inventory.json`",
        f"- total items: {len(items)}",
        "- by kind:",
    ]
    if kind_counts:
        lines.extend(f"  - {name}: {count}" for name, count in sorted(kind_counts.items()))
    else:
        lines.append("  - None")
    lines.append("- by classification:")
    if classification_counts:
        lines.extend(f"  - {name}: {count}" for name, count in sorted(classification_counts.items()))
    else:
        lines.append("  - None")
    lines.extend(
        [
            "- reading guidance:",
            f"  - full content candidates: {full_content_candidates}",
            f"  - deferred or unsafe: {deferred_or_unsafe}",
        ]
    )
    return "\n".join(lines)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an AletheiaOS project truth context pack.")
    parser.add_argument(
        "--with-runtime",
        action="store_true",
        help="append current agent run and recent session notes after stable project truth",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    print("# AletheiaOS Project Truth Context Pack\n")
    print("Use this pack to ground agent work in stable project truth. Add `--with-runtime` for run/session context.\n")
    for rel in FILES:
        path = root / rel
        print(f"## {rel}\n")
        if path.exists():
            print(clip(path.read_text(encoding="utf-8")).rstrip())
        else:
            print("MISSING")
        print()
    print("## Source Inventory Summary\n")
    print(source_inventory_summary(root))
    print()
    print("## Truth Record Inventory\n")
    print(record_inventory(root))
    print()
    if args.with_runtime:
        print("## Current Agent Run\n")
        print(current_agent_run(root))
        print()
        print("## Recent Session Notes\n")
        print(recent_session_notes(root))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
