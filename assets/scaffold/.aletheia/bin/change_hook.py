#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    root = repo_root()
    runtime = root / ".aletheia" / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    current = {}
    current_path = runtime / "current_agent_run.json"
    if current_path.exists():
        try:
            current = json.loads(current_path.read_text(encoding="utf-8"))
        except Exception:
            current = {}
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": payload.get("hook_event_name"),
        "tool": payload.get("tool_name"),
        "file_path": (payload.get("tool_input") or {}).get("file_path"),
        "cwd": payload.get("cwd"),
        "agent_run_id": current.get("run_id"),
        "model_id": current.get("model_id"),
        "task_class": current.get("task_class"),
    }
    with (runtime / "change_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
