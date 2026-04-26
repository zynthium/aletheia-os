#!/usr/bin/env python3
"""Create a conservative git checkpoint for durable project state."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_PATTERNS = [
    re.compile(r"(^|/)\.env(\.|$)"),
    re.compile(r"(^|/)secrets/"),
    re.compile(r"\.(pem|key|crt|credentials|secret)$", re.IGNORECASE),
]

STATE_PATTERNS = [
    "START_HERE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "project_os/AGENTS.md",
    "src/AGENTS.md",
    "tests/AGENTS.md",
    "experiments/AGENTS.md",
    "simulations/AGENTS.md",
    "configs/AGENTS.md",
    "docs/AGENTS.md",
    "infra/AGENTS.md",
    "project_os/10_ATTENTION_POLICY.md",
    "project_os/02_ACTIVE_STATE.md",
    "project_os/01_SYSTEM_GRAPH.yaml",
    "project_os/03_FRONTIER_BOARD.md",
    "project_os/04_RISK_REGISTER.md",
    "project_os/06_INTERFACE_CONTRACTS.md",
    "project_os/07_EVIDENCE_INDEX.md",
    "project_os/08_GIT_POLICY.md",
    "project_os/09_DOMAIN_PROFILE.md",
    "project_os/evidence/",
    "project_os/decisions/",
    "project_os/contracts/",
    "project_os/hypotheses/",
    "project_os/nodes/",
    "project_os/session_notes/",
]


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def git_available() -> bool:
    try:
        run(["git", "--version"], capture=True)
        return True
    except Exception:
        return False


def ensure_git() -> None:
    if not git_available():
        raise RuntimeError("git is not available on PATH")
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"], capture=True)
    except subprocess.CalledProcessError:
        run(["git", "init"])


def status_files() -> list[str]:
    result = run(["git", "status", "--porcelain"], capture=True)
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # Porcelain format: XY path or XY old -> new
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path)
    return files


def has_state_update(files: list[str]) -> bool:
    for f in files:
        if f == "BOOTSTRAP.md":
            return True
        for pat in STATE_PATTERNS:
            if pat.endswith("/"):
                if f.startswith(pat):
                    return True
            elif f == pat:
                return True
    return False


def has_protected(files: list[str]) -> list[str]:
    return [f for f in files if any(rx.search(f) for rx in PROTECTED_PATTERNS)]


def infer_message(files: list[str]) -> str:
    if "BOOTSTRAP.md" in files:
        return "bootstrap: initialize AI project OS"
    if "project_os/10_ATTENTION_POLICY.md" in files or "START_HERE.md" in files:
        return "state: update orientation and attention policy"
    if any(f.startswith("project_os/evidence/") for f in files):
        return "evidence: update evidence ledger"
    if any(f.startswith("project_os/decisions/") for f in files):
        return "decision: update decision records"
    if any(f.startswith("project_os/contracts/") for f in files) or "project_os/06_INTERFACE_CONTRACTS.md" in files:
        return "contract: update interface contracts"
    if "project_os/01_SYSTEM_GRAPH.yaml" in files or any(f.startswith("project_os/nodes/") for f in files):
        return "graph: update system graph"
    if "project_os/02_ACTIVE_STATE.md" in files or "project_os/03_FRONTIER_BOARD.md" in files:
        return "state: update active project state"
    if any(f.startswith("project_os/session_notes/") for f in files):
        return "session: add session distillation"
    if any(f.startswith(("src/", "lib/", "app/", "tests/", "experiments/", "simulations/", "configs/", "infra/")) for f in files):
        return "engineering: update implementation"
    return "checkpoint: durable project state update"


def validate() -> int:
    script = ROOT / "scripts/aios_validate.py"
    if not script.exists():
        print("validation skipped: scripts/aios_validate.py missing")
        return 0
    proc = subprocess.run([sys.executable, str(script)], cwd=ROOT, text=True)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="commit without interactive confirmation")
    parser.add_argument("--message", default=None, help="commit message")
    parser.add_argument("--no-validate", action="store_true", help="skip AIOS validation")
    parser.add_argument("--allow-code-only", action="store_true", help="allow commit even if no durable state file changed")
    parser.add_argument("--dry-run", action="store_true", help="print intended action without committing")
    args = parser.parse_args()

    ensure_git()

    files = status_files()
    if not files:
        print("checkpoint skipped: working tree is clean")
        return 0

    protected = has_protected(files)
    if protected:
        print("checkpoint blocked: protected-looking files are present:")
        for f in protected:
            print(f"  - {f}")
        return 2

    if not args.no_validate:
        rc = validate()
        if rc != 0:
            print("checkpoint blocked: validation failed")
            return rc

    allow_code_only = args.allow_code_only or os.environ.get("AIOS_ALLOW_CODE_ONLY_COMMIT") == "1"
    if not has_state_update(files) and not allow_code_only:
        print("checkpoint blocked: changes do not include durable project-state update")
        print("Update project_os/02_ACTIVE_STATE.md, attention policy, evidence, decisions, contracts, nodes, or session notes.")
        print("Override with --allow-code-only or AIOS_ALLOW_CODE_ONLY_COMMIT=1 if intentional.")
        return 3

    message = args.message or infer_message(files)

    print("checkpoint candidate:")
    for f in files:
        print(f"  - {f}")
    print(f"message: {message}")

    if args.dry_run:
        return 0

    if not args.auto:
        answer = input("Create checkpoint commit? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("checkpoint skipped by user")
            return 0

    run(["git", "add", "-A"])
    try:
        run(["git", "commit", "-m", message])
    except subprocess.CalledProcessError as exc:
        print("checkpoint failed: git commit returned non-zero status")
        print("Common cause: git user.name/user.email not configured.")
        return exc.returncode

    print("checkpoint committed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
