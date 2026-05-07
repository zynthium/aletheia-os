#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path


STATE_PATTERNS = [
    "AGENTS.md",
    "START_HERE.md",
    "BOOTSTRAP.md",
    ".claude/settings.json",
    ".aletheia/",
]
CHECKPOINT_EXCLUDED_PATTERNS = [
    ".aletheia/runtime/",
    ".aletheia/overview/",
    ".aletheia/source_inventory/",
    "**/__pycache__/",
    "**/*.pyc",
]
RUNTIME_POLICY = ".aletheia/governance/runtime_policy.json"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"invalid": str(exc)}
    return data if isinstance(data, dict) else {"invalid": "expected JSON object"}


def list_policy_values(policy: dict, key: str, fallback: list[str]) -> list[str]:
    values = policy.get(key)
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        return list(fallback)
    return list(values)


def runtime_policy(root: Path) -> dict[str, list[str]]:
    policy = load_json(root / RUNTIME_POLICY)
    return {
        "checkpoint_state_patterns": list_policy_values(policy, "checkpoint_state_patterns", STATE_PATTERNS),
        "checkpoint_excluded_patterns": list_policy_values(
            policy,
            "checkpoint_excluded_patterns",
            CHECKPOINT_EXCLUDED_PATTERNS,
        ),
    }


def checkpoint_excluded(file: str, patterns: list[str]) -> bool:
    path_parts = Path(file).parts
    for pattern in patterns:
        if pattern.startswith("**/") and pattern.endswith("/"):
            if pattern[3:].rstrip("/") in path_parts:
                return True
            continue
        if pattern.endswith("/") and file.startswith(pattern):
            return True
        if any(marker in pattern for marker in "*?[") and fnmatch.fnmatch(file, pattern):
            return True
        if file == pattern:
            return True
    return False


def state_files(files: list[str], patterns: list[str], excluded_patterns: list[str]) -> list[str]:
    candidates: list[str] = []
    for file in files:
        if checkpoint_excluded(file, excluded_patterns):
            continue
        for pattern in patterns:
            if pattern.endswith("/") and file.startswith(pattern):
                candidates.append(file)
                break
            if file == pattern:
                candidates.append(file)
                break
    return candidates


def git_status(root: Path) -> dict:
    result = run(["git", "status", "--porcelain", "--untracked-files=all"], root)
    files: list[str] = []
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            files.append(path)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "files": files,
    }


def validation(root: Path) -> dict:
    result = run([sys.executable, ".aletheia/bin/validate.py"], root)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


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


def context_state(root: Path) -> dict:
    path = root / ".aletheia" / "state" / "ACTIVE_STATE.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return {
        "active_state_path": ".aletheia/state/ACTIVE_STATE.md",
        "current_phase": current_phase(text),
        "active_nodes": active_nodes(text),
        "active_frontier": section(text, "Active frontier") or "unknown",
    }


def runtime_gate(root: Path) -> dict | None:
    path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not path.exists():
        return None
    return load_json(path)


def build_preflight(root: Path) -> dict:
    status = git_status(root)
    policy = runtime_policy(root)
    candidate_files = state_files(
        status["files"],
        policy["checkpoint_state_patterns"],
        policy["checkpoint_excluded_patterns"],
    )
    return {
        "repo": str(root),
        "host_note": "Use this on hosts without automatic hook enforcement, including Codex.",
        "context": context_state(root),
        "runtime_gate": runtime_gate(root),
        "validation": validation(root),
        "git": status,
        "checkpoint": {
            "has_candidate": bool(candidate_files),
            "candidate_files": candidate_files,
            "excluded_patterns": policy["checkpoint_excluded_patterns"],
        },
        "next_actions": [
            "python3 .aletheia/bin/orient.py --with-runtime",
            "python3 .aletheia/bin/validate.py",
            "python3 .aletheia/bin/checkpoint.py --dry-run",
        ],
        "recommended_actions": [
            "truth.orient.runtime",
            "truth.validate",
            "truth.checkpoint.dry_run",
        ],
    }


def print_markdown(payload: dict) -> None:
    print("# AletheiaOS Preflight")
    print()
    print("Use this on hosts without automatic hook enforcement, including Codex.")
    print()
    print("## Context")
    print()
    context = payload["context"]
    print(f"- current_phase: {context['current_phase']}")
    print(f"- active_nodes: {', '.join(context['active_nodes'])}")
    print()
    print("## Runtime Gate")
    print()
    gate = payload["runtime_gate"]
    if gate is None:
        print("None")
    else:
        for key in ["run_id", "provider", "model_id", "capability_tier", "task_class", "gate_status"]:
            if key in gate:
                print(f"- {key}: {gate[key]}")
    print()
    print("## Validation")
    print()
    validation_state = payload["validation"]
    print(f"- returncode: {validation_state['returncode']}")
    if validation_state["stdout"]:
        print(f"- stdout: {validation_state['stdout']}")
    if validation_state["stderr"]:
        print(f"- stderr: {validation_state['stderr']}")
    print()
    print("## Checkpoint Candidate")
    print()
    checkpoint = payload["checkpoint"]
    print(f"- has_candidate: {checkpoint['has_candidate']}")
    for path in checkpoint["candidate_files"]:
        print(f"- {path}")
    print()
    print("## Next Actions")
    print()
    for action_id in payload["recommended_actions"]:
        print(f"- action: `{action_id}`")
    for command in payload["next_actions"]:
        print(f"- `{command}`")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a read-only AletheiaOS preflight for hosts without hooks.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable preflight state")
    args = parser.parse_args()
    payload = build_preflight(repo_root())
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
