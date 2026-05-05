#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from aletheia_scaffold import SCAFFOLD_ROOT, copy_tree_without_overwrite, ensure_claude_settings


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize AletheiaOS in a target repository.")
    parser.add_argument("target", type=Path, help="Target repository directory")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.exists() or not target.is_dir():
        parser.error(f"target must be an existing directory: {target}")
    if not SCAFFOLD_ROOT.exists():
        parser.error(f"missing scaffold root: {SCAFFOLD_ROOT}")

    written = copy_tree_without_overwrite(SCAFFOLD_ROOT, target)
    claude_status = ensure_claude_settings(target)
    print(f"initialized AletheiaOS scaffold in {target}")
    print(f"files written: {len(written)}")
    print(f"claude settings: {claude_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
