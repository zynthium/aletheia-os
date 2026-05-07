#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


FILES = [
    ".aletheia/CAPABILITY_MAP.md",
    ".aletheia/governance/CHARTER.md",
    ".aletheia/governance/ATTENTION_POLICY.md",
    ".aletheia/governance/MODEL_GOVERNANCE.md",
    ".aletheia/governance/model_registry.json",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
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


def main() -> int:
    root = repo_root()
    print("# AletheiaOS Project Truth Context Pack\n")
    print("Use this pack to ground agent work in the repository's current project truth.\n")
    for rel in FILES:
        path = root / rel
        print(f"## {rel}\n")
        if path.exists():
            print(clip(path.read_text(encoding="utf-8")).rstrip())
        else:
            print("MISSING")
        print()
    print("## Current Agent Run\n")
    print(current_agent_run(root))
    print()
    print("## Recent Session Notes\n")
    print(recent_session_notes(root))
    print()
    print("## Truth Record Inventory\n")
    print(record_inventory(root))
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
