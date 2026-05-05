#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


FILES = [
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
