#!/usr/bin/env python3
"""Print a compact context pack for an AI-agent session.

The pack is intentionally top-down: entry protocol, root constraints, attention
policy, active state, graph, and git policy. Local files should be loaded only
after an active node is identified.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "START_HERE.md",
    "AGENTS.md",
    "project_os/00_CHARTER.md",
    "project_os/10_ATTENTION_POLICY.md",
    "project_os/02_ACTIVE_STATE.md",
    "project_os/01_SYSTEM_GRAPH.yaml",
    "project_os/08_GIT_POLICY.md",
]


def clip(text: str, limit: int = 5000) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "\n...[truncated]"


def main() -> int:
    print("# AIOS Context Pack\n")
    for file in FILES:
        p = ROOT / file
        if not p.exists():
            print(f"## {file}\nMISSING\n")
            continue
        print(f"## {file}\n")
        print(clip(p.read_text(encoding="utf-8")))
        print("\n---\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
