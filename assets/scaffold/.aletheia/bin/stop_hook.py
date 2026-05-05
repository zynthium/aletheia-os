#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def current_run_summary(root: Path) -> str:
    path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not path.exists():
        return "AletheiaOS stop hook: no current agent run attribution recorded."
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"AletheiaOS stop hook: current agent run record is invalid: {exc}"
    return (
        "AletheiaOS stop hook: current agent run "
        f"{data.get('run_id', 'unknown')} "
        f"{data.get('provider', 'unknown')}/{data.get('model_id', 'unknown')} "
        f"tier={data.get('capability_tier', 'unknown')} "
        f"task={data.get('task_class', 'unknown')} "
        f"gate={data.get('gate_status', 'unknown')}"
    )


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    root = repo_root()
    print(current_run_summary(root))
    validate = run(["python3", ".aletheia/bin/validate.py"], root)
    print(validate.stdout, end="")
    if validate.returncode != 0:
        print("AletheiaOS stop hook: validation failed. Do not finalize this task until errors are fixed.")
        return 0
    status = run(["git", "status", "--porcelain"], root)
    if status.returncode != 0 or not status.stdout.strip():
        print("AletheiaOS stop hook: no checkpoint needed.")
        return 0
    if os.environ.get("AIOS_AUTOCOMMIT") == "1":
        checkpoint = run(["python3", ".aletheia/bin/checkpoint.py", "--auto"], root)
        print(checkpoint.stdout, end="")
        return 0
    print("AletheiaOS stop hook: changes detected. Recommended next command:")
    print("  python3 .aletheia/bin/checkpoint.py --auto")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
