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

TREE_SIGNAL_TERMS = ("skeleton", "orphan", "tree")
DURABILITY_NOTE = (
    "Generated/runtime outputs under .aletheia/runtime/, .aletheia/overview/, "
    "and .aletheia/source_inventory/ are local status artifacts, not durable truth by default."
)
NEXT_ACTIONS = [
    "python3 .aletheia/bin/preflight.py --json",
    "python3 .aletheia/bin/validate.py",
    "python3 .aletheia/bin/checkpoint.py --dry-run",
    "python3 .aletheia/bin/overview.py",
]
RECOMMENDED_ACTIONS = [
    "truth.preflight",
    "truth.validate",
    "truth.checkpoint.dry_run",
    "truth.overview",
]


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


def recent_changes(root: Path, limit: int = 5) -> list[dict[str, Any]]:
    path = root / ".aletheia" / "runtime" / "change_log.jsonl"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    changes: list[dict[str, Any]] = []
    for line in lines:
        try:
            data = json.loads(line)
        except Exception as exc:
            changes.append({"invalid": str(exc), "raw": line})
            continue
        if isinstance(data, dict):
            changes.append(data)
        else:
            changes.append({"invalid": "expected JSON object", "raw": line})
    return changes


def generated_outputs() -> list[dict[str, Any]]:
    return [
        {
            "path": ".aletheia/runtime/",
            "durable_truth": False,
            "checkpoint_default": "excluded",
            "purpose": "Current run attribution, hook logs, and recent change log.",
        },
        {
            "path": ".aletheia/overview/",
            "durable_truth": False,
            "checkpoint_default": "excluded",
            "purpose": "Generated local status JSON and HTML.",
        },
        {
            "path": ".aletheia/source_inventory/",
            "durable_truth": False,
            "checkpoint_default": "excluded",
            "purpose": "Generated source inventory and bootstrap report inputs.",
        },
        {
            "path": "docs/overview/",
            "durable_truth": False,
            "checkpoint_default": "not included in default state patterns",
            "purpose": "Optional generated public overview export.",
        },
    ]


def count_skeleton_nodes(root: Path) -> int:
    path = root / ".aletheia" / "state" / "SKELETON.yaml"
    if not path.exists():
        return 0
    return len(re.findall(r"(?m)^\s{2}[A-Za-z0-9_.-]+:\s*$", path.read_text(encoding="utf-8")))


def count_orphans(root: Path) -> int:
    path = root / ".aletheia" / "state" / "ORPHANS.yaml"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    if "orphans: []" in text:
        return 0
    return len(re.findall(r"(?m)^\s{2}-\s+id:\s*\S+", text))


def tree_signal_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if any(term in line.lower() for term in TREE_SIGNAL_TERMS)]


def stale_orphan_count(stdout: str) -> int:
    total = 0
    for line in stdout.splitlines():
        match = re.search(r"orphan review is stale:\s*(.+?)\s*$", line)
        if not match:
            continue
        total += len([item for item in re.split(r"\s*,\s*", match.group(1).strip()) if item])
    return total


def tree_health(root: Path, validation_state: dict[str, Any]) -> dict[str, Any]:
    stdout = validation_state.get("stdout", "")
    stderr = validation_state.get("stderr", "")
    stdout_tree_lines = tree_signal_lines(stdout)
    stderr_tree_lines = tree_signal_lines(stderr)
    semantic_review_signals = [line.strip(" -") for line in stdout_tree_lines]
    structural_error_signals = [line.strip(" -") for line in stderr_tree_lines]
    tree_lines = [
        line.strip(" -")
        for line in [*stdout_tree_lines, *stderr_tree_lines]
    ]
    orphan_count = count_orphans(root)
    stale_count = stale_orphan_count(stdout)
    human_review_needed = bool(semantic_review_signals) or stale_count > 0 or orphan_count > 0
    structural_fix_needed = bool(structural_error_signals)
    return {
        "skeleton_nodes": count_skeleton_nodes(root),
        "orphan_count": orphan_count,
        "stale_orphan_count": stale_count,
        "warning_count": len(stdout_tree_lines),
        "error_count": len(stderr_tree_lines),
        "semantic_review_count": len(semantic_review_signals),
        "structural_error_count": len(structural_error_signals),
        "human_review_needed": human_review_needed,
        "structural_fix_needed": structural_fix_needed,
        "review_needed": human_review_needed,
        "semantic_review_signals": semantic_review_signals,
        "structural_error_signals": structural_error_signals,
        "signals": tree_lines,
    }


def build_status(root: Path) -> dict[str, Any]:
    validation_state = validation(root)
    return {
        "repo": str(root),
        "durability_note": DURABILITY_NOTE,
        "active_state": active_state(root),
        "validation": validation_state,
        "records": record_counts(root),
        "tree_health": tree_health(root, validation_state),
        "runtime_gate": runtime_gate(root),
        "recent_changes": recent_changes(root),
        "generated_outputs": generated_outputs(),
        "next_actions": NEXT_ACTIONS,
        "recommended_actions": RECOMMENDED_ACTIONS,
    }


def print_markdown(status: dict[str, Any]) -> None:
    active = status["active_state"]
    validation_state = status["validation"]
    print("# AletheiaOS Status Refresh")
    print()
    print("## Durability")
    print()
    print(status["durability_note"])
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
    print("## Tree Health")
    print()
    tree = status["tree_health"]
    print(f"- skeleton nodes: {tree['skeleton_nodes']}")
    print(f"- orphan count: {tree['orphan_count']}")
    print(f"- stale orphan count: {tree['stale_orphan_count']}")
    print(f"- tree warning count: {tree['warning_count']}")
    print(f"- tree error count: {tree['error_count']}")
    print(f"- semantic review signal count: {tree['semantic_review_count']}")
    print(f"- structural error signal count: {tree['structural_error_count']}")
    print(f"- human review needed: {tree['human_review_needed']}")
    print(f"- structural fix needed: {tree['structural_fix_needed']}")
    print(f"- review needed: {tree['review_needed']}")
    if tree["semantic_review_signals"]:
        for signal in tree["semantic_review_signals"]:
            print(f"- semantic review signal: {signal}")
    else:
        print("- semantic review signals: none")
    if tree["structural_error_signals"]:
        for signal in tree["structural_error_signals"]:
            print(f"- structural error signal: {signal}")
    else:
        print("- structural error signals: none")
    if tree["signals"]:
        for signal in tree["signals"]:
            print(f"- signal: {signal}")
    else:
        print("- signals: none")
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
    print("## Recent Changes")
    print()
    changes = status["recent_changes"]
    if not changes:
        print("None")
    else:
        for change in changes:
            target = change.get("file_path") or change.get("command") or "unknown target"
            fields = [
                f"ts={change.get('ts', 'unknown')}",
                f"event={change.get('event', 'unknown')}",
                f"tool={change.get('tool', 'unknown')}",
                f"target={target}",
            ]
            if change.get("model_id"):
                fields.append(f"model={change['model_id']}")
            print(f"- {'; '.join(fields)}")
    print()
    print("## Generated Outputs")
    print()
    for generated in status["generated_outputs"]:
        print(
            f"- {generated['path']} durable_truth={generated['durable_truth']} "
            f"checkpoint_default={generated['checkpoint_default']}"
        )
    print()
    print("## Next Actions")
    print()
    for action_id in status["recommended_actions"]:
        print(f"- action: `{action_id}`")
    for command in status["next_actions"]:
        print(f"- `{command}`")
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
