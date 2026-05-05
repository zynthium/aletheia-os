#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ORIENTATION_FILES = [
    ".aletheia/START_HERE.md",
    ".aletheia/governance/CHARTER.md",
    ".aletheia/governance/ATTENTION_POLICY.md",
    ".aletheia/governance/MODEL_GOVERNANCE.md",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    root = repo_root()
    print("# AletheiaOS Orientation")
    print()
    print(f"Repository: {root}")
    for rel in ORIENTATION_FILES:
        path = root / rel
        print()
        print(f"--- {rel} ---")
        if not path.exists():
            print(f"MISSING: {rel}")
            continue
        print(path.read_text(encoding="utf-8").rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
