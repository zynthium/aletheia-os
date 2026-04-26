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


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    LOG_DIR.mkdir(exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": payload.get("hook_event_name"),
        "tool": payload.get("tool_name"),
        "file_path": (payload.get("tool_input") or {}).get("file_path"),
        "cwd": payload.get("cwd"),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
