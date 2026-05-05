#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_ROOT = REPO_ROOT / "assets" / "scaffold"


def copy_tree_without_overwrite(src: Path, dst: Path) -> list[Path]:
    written: list[Path] = []
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        written.append(target)
    return written


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
    print(f"initialized AletheiaOS scaffold in {target}")
    print(f"files written: {len(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
