#!/usr/bin/env python3
"""Claude Code PostToolUse hook: log file writes/edits to runtime log."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / ".aios_runtime"
LOG = LOG_DIR / "change_log.jsonl"
CURRENT_RUN_PATH = LOG_DIR / "current_agent_run.json"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    LOG_DIR.mkdir(exist_ok=True)
    current_run = {}
    if CURRENT_RUN_PATH.exists():
        try:
            current_run = json.loads(CURRENT_RUN_PATH.read_text(encoding="utf-8"))
        except Exception:
            current_run = {}

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": payload.get("hook_event_name"),
        "tool": payload.get("tool_name"),
        "file_path": (payload.get("tool_input") or {}).get("file_path"),
        "cwd": payload.get("cwd"),
        "agent_run_id": current_run.get("run_id"),
        "model_id": current_run.get("model_id"),
        "task_class": current_run.get("task_class"),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
