#!/usr/bin/env python3
"""Claude Code Stop hook: validate and optionally auto-checkpoint.

Set AIOS_AUTOCOMMIT=1 to create conservative checkpoint commits on stop.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_RUN_PATH = ROOT / ".aios_runtime/current_agent_run.json"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)



def current_run_summary() -> str:
    if not CURRENT_RUN_PATH.exists():
        return "AIOS stop hook: no current agent run attribution recorded."
    try:
        run = json.loads(CURRENT_RUN_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"AIOS stop hook: current agent run record is invalid: {exc}"
    return (
        "AIOS stop hook: current agent run "
        f"{run.get('run_id', 'unknown')} "
        f"{run.get('provider', 'unknown')}/{run.get('model_id', 'unknown')} "
        f"tier={run.get('capability_tier', 'unknown')} "
        f"task={run.get('task_class', 'unknown')} "
        f"gate={run.get('gate_status', 'unknown')}"
    )

def main() -> int:
    try:
        _payload = json.load(sys.stdin)
    except Exception:
        _payload = {}

    print(current_run_summary())

    validate = run([sys.executable, "scripts/aios_validate.py"])
    print(validate.stdout)
    if validate.returncode != 0:
        print("AIOS stop hook: validation failed. Do not finalize this task until errors are fixed.")
        return 0

    status = run(["git", "status", "--porcelain"])
    if status.returncode != 0:
        print("AIOS stop hook: git status failed; checkpoint skipped.")
        return 0
    if not status.stdout.strip():
        print("AIOS stop hook: working tree clean; no checkpoint needed.")
        return 0

    if os.environ.get("AIOS_AUTOCOMMIT") == "1":
        checkpoint = run([sys.executable, "scripts/aios_checkpoint.py", "--auto"])
        print(checkpoint.stdout)
        return 0

    print("AIOS stop hook: changes detected. Recommended next command:")
    print("  python3 scripts/aios_checkpoint.py --auto")
    print("Set AIOS_AUTOCOMMIT=1 to allow conservative auto-commits on stop events.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
