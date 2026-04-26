#!/usr/bin/env python3
"""Bootstrap/finalize the AI Project OS scaffold."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POST_BOOTSTRAP_REQUIRED_NO_TBD = [
    "project_os/00_CHARTER.md",
    "project_os/01_SYSTEM_GRAPH.yaml",
    "project_os/02_ACTIVE_STATE.md",
    "project_os/09_DOMAIN_PROFILE.md",
]


def run(cmd: list[str], check: bool = True, quiet: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if quiet else None,
        stderr=subprocess.PIPE if quiet else None,
    )


def ensure_git() -> None:
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"], check=True, quiet=True)
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


def post_bootstrap_ready() -> int:
    failures: list[str] = []
    for file in POST_BOOTSTRAP_REQUIRED_NO_TBD:
        p = ROOT / file
        if p.exists() and "TBD" in p.read_text(encoding="utf-8"):
            failures.append(file)
    if failures:
        print("bootstrap blocked: critical files still contain TBD markers:")
        for file in failures:
            print(f"  - {file}")
        print("Customize these files before deleting BOOTSTRAP.md and creating the initial checkpoint.")
        return 1
    return 0


def finalize() -> int:
    # First validate project-state structure while BOOTSTRAP.md still exists.
    rc = validate()
    if rc != 0:
        print("bootstrap blocked: validation failed")
        return rc

    # Then enforce post-bootstrap readiness before deleting BOOTSTRAP.md or creating git state.
    rc = post_bootstrap_ready()
    if rc != 0:
        return rc

    ensure_git()
    configure_hooks()

    bootstrap = ROOT / "BOOTSTRAP.md"
    if bootstrap.exists():
        bootstrap.unlink()
        print("removed BOOTSTRAP.md")

    # Validate again after BOOTSTRAP.md is removed, because post-bootstrap validation is stricter.
    rc = validate()
    if rc != 0:
        print("bootstrap blocked: post-bootstrap validation failed")
        return rc

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
