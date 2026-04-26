#!/usr/bin/env python3
"""Bootstrap/finalize the AI Project OS scaffold."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, check=check, text=True)


def ensure_git() -> None:
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"], check=True)
    except subprocess.CalledProcessError:
        run(["git", "init"])


def configure_hooks() -> None:
    hooks = ROOT / ".githooks"
    hooks.mkdir(exist_ok=True)
    pre = hooks / "pre-commit"
    if pre.exists():
        pre.chmod(pre.stat().st_mode | 0o111)
    run(["git", "config", "core.hooksPath", ".githooks"])
    print("configured git core.hooksPath=.githooks")


def validate() -> int:
    return subprocess.run([sys.executable, "scripts/aios_validate.py"], cwd=ROOT).returncode


def finalize() -> int:
    ensure_git()
    configure_hooks()
    rc = validate()
    if rc != 0:
        print("bootstrap blocked: validation failed")
        return rc

    bootstrap = ROOT / "BOOTSTRAP.md"
    if bootstrap.exists():
        bootstrap.unlink()
        print("removed BOOTSTRAP.md")

    commit = subprocess.run(
        [sys.executable, "scripts/aios_checkpoint.py", "--auto", "--message", "bootstrap: initialize AI project OS", "--allow-code-only"],
        cwd=ROOT,
        text=True,
    )
    return commit.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configure-hooks", action="store_true")
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args()

    if args.finalize:
        return finalize()
    if args.configure_hooks:
        ensure_git()
        configure_hooks()
        return 0

    print("No action selected. Use --configure-hooks or --finalize.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
