#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TIER_ORDER = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}
BOOTSTRAP_GATE_COMMAND = (
    "python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize "
    "--provider <provider> --model-id <model_id> --tier C3 --operator-approved "
    '--record --objective "Initialize AletheiaOS"'
)
POST_BOOTSTRAP_REQUIRED_NO_TBD = [
    ".aletheia/governance/CHARTER.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/DOMAIN_PROFILE.md",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path, *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"{cmd[0]} is not available on PATH") from exc


def validate(root: Path) -> int:
    return subprocess.run([sys.executable, ".aletheia/bin/validate.py"], cwd=root, text=True).returncode


def bootstrap_model_gate_ready(root: Path) -> int:
    if os.environ.get("AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT") == "1":
        print("bootstrap model gate override enabled by AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1")
        return 0
    current_run_path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not current_run_path.exists():
        print("bootstrap blocked: no AI model gate run recorded")
        print(f"Run: {BOOTSTRAP_GATE_COMMAND}")
        return 1
    try:
        run_data = json.loads(current_run_path.read_text(encoding="utf-8"))
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


def post_bootstrap_ready(root: Path) -> int:
    failures = []
    for rel in POST_BOOTSTRAP_REQUIRED_NO_TBD:
        path = root / rel
        if path.exists() and "TBD" in path.read_text(encoding="utf-8"):
            failures.append(rel)
    if failures:
        print("bootstrap blocked: critical files still contain TBD markers:")
        for rel in failures:
            print(f"  - {rel}")
        print("Customize these files before deleting BOOTSTRAP.md and creating the initial checkpoint.")
        return 1
    return 0


def configure_hooks(root: Path) -> None:
    hooks = root / ".aletheia" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    pre_commit = hooks / "pre-commit"
    pre_commit.write_text("#!/bin/sh\npython3 .aletheia/bin/validate.py\n", encoding="utf-8")
    pre_commit.chmod(0o755)
    run(["git", "config", "core.hooksPath", ".aletheia/hooks"], root)


def ensure_git(root: Path) -> None:
    check = run(["git", "rev-parse", "--is-inside-work-tree"], root, capture=True)
    if check.returncode != 0:
        run(["git", "init"], root)


def write_session_note(root: Path) -> None:
    notes = root / ".aletheia" / "session_notes"
    notes.mkdir(parents=True, exist_ok=True)
    path = notes / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-bootstrap-finalize.md"
    path.write_text(
        "# Session Note: Bootstrap finalized\n\n"
        f"Date: {datetime.now(timezone.utc).date()}\n\n"
        "AletheiaOS bootstrap was finalized for this repository.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize AletheiaOS bootstrap for a target repository.")
    parser.add_argument("--keep-bootstrap", action="store_true")
    parser.add_argument("--no-checkpoint", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    rc = bootstrap_model_gate_ready(root)
    if rc != 0:
        return rc
    rc = validate(root)
    if rc != 0:
        print("bootstrap blocked: validation failed")
        return rc
    rc = post_bootstrap_ready(root)
    if rc != 0:
        return rc

    try:
        ensure_git(root)
        configure_hooks(root)
    except RuntimeError as exc:
        print(f"bootstrap blocked: {exc}")
        return 1
    write_session_note(root)

    bootstrap = root / "BOOTSTRAP.md"
    if bootstrap.exists() and not args.keep_bootstrap:
        bootstrap.unlink()
        print("removed BOOTSTRAP.md")

    rc = validate(root)
    if rc != 0:
        print("bootstrap blocked: post-bootstrap validation failed")
        return rc

    if not args.no_checkpoint:
        checkpoint = run(
            ["python3", ".aletheia/bin/checkpoint.py", "--auto", "--message", "bootstrap: initialize AletheiaOS", "--allow-code-only"],
            root,
        )
        return checkpoint.returncode

    print("bootstrap finalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
