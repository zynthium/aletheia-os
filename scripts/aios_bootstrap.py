#!/usr/bin/env python3
"""Bootstrap/finalize an AletheiaOS project."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_RUN_PATH = ROOT / ".aios_runtime/current_agent_run.json"
TIER_ORDER = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}

POST_BOOTSTRAP_REQUIRED_NO_TBD = [
    "aletheia_os/00_CHARTER.md",
    "aletheia_os/01_SYSTEM_GRAPH.yaml",
    "aletheia_os/02_ACTIVE_STATE.md",
    "aletheia_os/09_DOMAIN_PROFILE.md",
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



def bootstrap_model_gate_ready() -> int:
    if os.environ.get("AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT") == "1":
        print("bootstrap model gate override enabled by AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1")
        return 0
    if not CURRENT_RUN_PATH.exists():
        print("bootstrap blocked: no AI model gate run recorded")
        print("Run: python3 scripts/aios_model_gate.py --task-class bootstrap_finalize --record --objective \"Initialize AletheiaOS\"")
        return 1
    try:
        run_data = json.loads(CURRENT_RUN_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"bootstrap blocked: invalid current agent run record: {exc}")
        return 1
    if run_data.get("gate_status") != "allowed":
        print("bootstrap blocked: current AI model was not allowed by model gate")
        print(f"  run_id: {run_data.get('run_id')}")
        print(f"  gate_status: {run_data.get('gate_status')}")
        return 1
    if TIER_ORDER.get(str(run_data.get("capability_tier")), -1) < TIER_ORDER["C3"]:
        print("bootstrap blocked: bootstrap_finalize requires capability tier C3 or higher")
        print(f"  tier: {run_data.get('capability_tier')}")
        return 1
    if run_data.get("task_class") != "bootstrap_finalize":
        print("bootstrap blocked: current agent run is not task_class=bootstrap_finalize")
        print(f"  task_class: {run_data.get('task_class')}")
        return 1
    return 0

def finalize() -> int:
    rc = bootstrap_model_gate_ready()
    if rc != 0:
        return rc

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
        [sys.executable, "scripts/aios_checkpoint.py", "--auto", "--message", "bootstrap: initialize AletheiaOS", "--allow-code-only"],
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
