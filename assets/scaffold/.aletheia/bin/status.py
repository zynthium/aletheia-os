#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


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


def section(text: str, name: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1).strip() if match else ""


def active_nodes(active_text: str) -> list[str]:
    nodes: list[str] = []
    for value in re.findall(r"`([A-Za-z0-9_.-]+)`", section(active_text, "Active nodes")):
        if value not in nodes:
            nodes.append(value)
    return nodes or ["root"]


def current_phase(active_text: str) -> str:
    match = re.search(r"(?im)^\s*-\s*Current phase:\s*(.+?)\s*$", active_text)
    return match.group(1).strip() if match else "unknown"


def active_state(root: Path) -> dict[str, Any]:
    path = root / ".aletheia" / "state" / "ACTIVE_STATE.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return {
        "path": ".aletheia/state/ACTIVE_STATE.md",
        "exists": path.exists(),
        "current_phase": current_phase(text),
        "active_nodes": active_nodes(text),
        "active_frontier": section(text, "Active frontier") or "unknown",
    }


def validation(root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, ".aletheia/bin/validate.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def record_counts(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name, rel in RECORD_DIRS.items():
        directory = root / rel
        if not directory.exists():
            counts[name] = 0
            continue
        counts[name] = len(
            [
                path
                for path in directory.glob("*")
                if path.is_file() and path.name not in {".gitkeep", "INDEX.md"}
            ]
        )
    return counts


def runtime_gate(root: Path) -> dict[str, Any] | None:
    path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"invalid": str(exc)}
    if not isinstance(data, dict):
        return {"invalid": "expected JSON object"}
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
    return {field: data.get(field) for field in fields if field in data}


def build_status(root: Path) -> dict[str, Any]:
    return {
        "repo": str(root),
        "active_state": active_state(root),
        "validation": validation(root),
        "records": record_counts(root),
        "runtime_gate": runtime_gate(root),
    }


def print_markdown(status: dict[str, Any]) -> None:
    active = status["active_state"]
    validation_state = status["validation"]
    print("# AletheiaOS Status Refresh")
    print()
    print("## Active State")
    print()
    print(f"- file exists: {active['exists']}")
    print(f"- current phase: {active['current_phase']}")
    print(f"- active nodes: {', '.join(active['active_nodes'])}")
    print()
    print("## Validation")
    print()
    print(f"- returncode: {validation_state['returncode']}")
    if validation_state["stdout"]:
        print(f"- stdout: {validation_state['stdout']}")
    if validation_state["stderr"]:
        print(f"- stderr: {validation_state['stderr']}")
    print()
    print("## Records")
    print()
    for name, count in sorted(status["records"].items()):
        print(f"- {name}: {count}")
    print()
    print("## Runtime Gate")
    print()
    gate = status["runtime_gate"]
    if gate is None:
        print("None")
    else:
        for key, value in gate.items():
            print(f"- {key}: {value}")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh compact AletheiaOS project status.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable status")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = build_status(repo_root())
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print_markdown(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
