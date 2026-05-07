#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PROTECTED_PATTERNS = [
    re.compile(r"(^|/)\.env(\.|$)"),
    re.compile(r"(^|/)secrets/"),
    re.compile(r"\.(pem|key|crt|credentials|secret)$", re.IGNORECASE),
]

STATE_PATTERNS = [
    "AGENTS.md",
    "START_HERE.md",
    "BOOTSTRAP.md",
    ".claude/settings.json",
    ".aletheia/",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path, *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=root,
            check=False,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"{cmd[0]} is not available on PATH") from exc


def ensure_git(root: Path) -> None:
    available = run(["git", "--version"], root, capture=True)
    if available.returncode != 0:
        raise RuntimeError("git is not available on PATH")
    inside = run(["git", "rev-parse", "--is-inside-work-tree"], root, capture=True)
    if inside.returncode != 0:
        run(["git", "init"], root)


def status_files(root: Path) -> list[str]:
    result = run(["git", "status", "--porcelain"], root, capture=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "git status failed")
    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path)
    return files


def has_state_update(files: list[str]) -> bool:
    for file in files:
        for pattern in STATE_PATTERNS:
            if pattern.endswith("/"):
                if file.startswith(pattern):
                    return True
            elif file == pattern:
                return True
    return False


def state_files(root: Path, files: list[str]) -> list[str]:
    state: list[str] = []
    for file in files:
        for pattern in STATE_PATTERNS:
            if pattern.endswith("/"):
                if file.startswith(pattern):
                    state.append(file)
                    break
            elif file == pattern:
                state.append(file)
                break
            elif file.endswith("/") and pattern.startswith(file) and (root / pattern).exists():
                state.append(pattern)
                break
    return state


def protected_files(files: list[str]) -> list[str]:
    return [file for file in files if any(pattern.search(file) for pattern in PROTECTED_PATTERNS)]


def load_json(path: Path, *, strict: bool = False) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        if strict:
            raise ValueError(f"{path}: {exc}") from exc
        return {}
    if not isinstance(data, dict):
        if strict:
            raise ValueError(f"{path}: expected JSON object")
        return {}
    return data


def require_agent_run_for_checkpoint(root: Path) -> bool:
    registry = load_json(root / ".aletheia" / "governance" / "model_registry.json")
    policy = registry.get("default_policy", {}) if isinstance(registry.get("default_policy", {}), dict) else {}
    return bool(policy.get("require_agent_run_for_checkpoint", False))


def load_current_agent_run(root: Path) -> dict:
    run_data = load_json(root / ".aletheia" / "runtime" / "current_agent_run.json", strict=True)
    if run_data:
        return run_data
    return {}


def attribution_trailers(run_data: dict) -> str:
    if not run_data:
        return ""
    fields = [
        ("AIOS-Agent-Run", run_data.get("run_id", "unknown")),
        ("AIOS-Agent-Provider", run_data.get("provider", "unknown")),
        ("AIOS-Agent-Model", run_data.get("model_id", "unknown")),
        ("AIOS-Agent-Tier", run_data.get("capability_tier", "unknown")),
        ("AIOS-Task-Class", run_data.get("task_class", "unknown")),
        ("AIOS-Gate", run_data.get("gate_status", "unknown")),
    ]
    return "\n\n" + "\n".join(f"{key}: {value}" for key, value in fields)


def infer_message(files: list[str]) -> str:
    if "BOOTSTRAP.md" in files:
        return "bootstrap: initialize AletheiaOS"
    if any(file.startswith(".aletheia/evidence/") for file in files):
        return "evidence: update evidence ledger"
    if any(file.startswith(".aletheia/decisions/") for file in files):
        return "decision: update decision records"
    if any(file.startswith(".aletheia/contracts/") for file in files):
        return "contract: update interface contracts"
    if ".aletheia/state/SYSTEM_GRAPH.yaml" in files or any(file.startswith(".aletheia/nodes/") for file in files):
        return "graph: update system graph"
    if ".aletheia/state/ACTIVE_STATE.md" in files:
        return "state: update active project state"
    if any(file.startswith(("src/", "lib/", "app/", "tests/", "experiments/", "simulations/", "configs/", "infra/")) for file in files):
        return "engineering: update implementation"
    return "checkpoint: durable project state update"


def validate(root: Path) -> int:
    script = root / ".aletheia" / "bin" / "validate.py"
    if not script.exists():
        print("validation skipped: .aletheia/bin/validate.py missing")
        return 0
    return subprocess.run([sys.executable, ".aletheia/bin/validate.py"], cwd=root, text=True).returncode


def stage_state_paths(root: Path) -> int:
    existing = [pattern for pattern in STATE_PATTERNS if (root / pattern.rstrip("/")).exists()]
    if not existing:
        print("checkpoint blocked: no AletheiaOS state paths exist")
        return 1
    result = run(["git", "add", *existing], root, capture=True)
    if result.returncode != 0:
        print(result.stderr, end="")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and optionally create an AletheiaOS checkpoint.")
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--message", default=None)
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--allow-code-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-model-gate", action="store_true")
    parser.add_argument("--include-worktree", action="store_true", help="Stage the full worktree instead of only AletheiaOS state paths.")
    args = parser.parse_args()

    root = repo_root()
    try:
        ensure_git(root)
        files = status_files(root)
    except RuntimeError as exc:
        print(f"checkpoint blocked: {exc}")
        return 1
    if not files:
        print("checkpoint skipped: working tree is clean")
        return 0

    protected = protected_files(files)
    if protected:
        print("checkpoint blocked: protected-looking files are present:")
        for file in protected:
            print(f"  - {file}")
        return 2

    if not args.no_validate:
        rc = validate(root)
        if rc != 0:
            print("checkpoint blocked: validation failed")
            return rc

    if not has_state_update(files) and not (args.allow_code_only or os.environ.get("AIOS_ALLOW_CODE_ONLY_COMMIT") == "1"):
        print("checkpoint blocked: changes do not include durable project-state update")
        print("Update .aletheia state, evidence, decisions, contracts, nodes, or session notes.")
        return 3

    try:
        run_data = load_current_agent_run(root)
    except ValueError as exc:
        print(f"checkpoint blocked: current AI agent run record is invalid: {exc}")
        return 4
    allow_unattributed = args.no_model_gate or os.environ.get("AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT") == "1"
    if require_agent_run_for_checkpoint(root) and not run_data and not allow_unattributed:
        print("checkpoint blocked: no current AI agent run attribution found")
        print('Run: python3 .aletheia/bin/model_gate.py --task-class <task_class> --record --objective "..."')
        return 4
    if run_data and run_data.get("gate_status") != "allowed" and not allow_unattributed:
        print("checkpoint blocked: current AI agent run was not allowed by model gate")
        print(f"  run_id: {run_data.get('run_id')}")
        print(f"  gate_status: {run_data.get('gate_status')}")
        return 5

    candidate_files = files if args.include_worktree else state_files(root, files)
    non_checkpoint_files = [] if args.include_worktree else [file for file in files if file not in set(candidate_files)]
    message = args.message or infer_message(candidate_files or files)
    print("checkpoint candidate:")
    for file in candidate_files:
        print(f"  - {file}")
    if non_checkpoint_files:
        print("non-checkpoint worktree changes remain:")
        for file in non_checkpoint_files:
            print(f"  - {file}")
    print(f"message: {message}")
    if run_data:
        print(
            f"agent_run: {run_data.get('run_id', 'unknown')} "
            f"{run_data.get('provider', 'unknown')}/{run_data.get('model_id', 'unknown')} "
            f"tier={run_data.get('capability_tier', 'unknown')} task={run_data.get('task_class', 'unknown')}"
        )

    if args.dry_run:
        return 0
    if not args.auto:
        answer = input("Create checkpoint commit? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("checkpoint skipped by user")
            return 0

    if args.include_worktree:
        add = run(["git", "add", "-A"], root, capture=True)
        if add.returncode != 0:
            print(add.stderr, end="")
            return add.returncode
    else:
        rc = stage_state_paths(root)
        if rc != 0:
            return rc

    commit = run(["git", "commit", "-m", message + attribution_trailers(run_data)], root, capture=True)
    print(commit.stdout, end="")
    if commit.returncode != 0:
        print(commit.stderr, end="")
        print("checkpoint failed: git commit returned non-zero status")
    return commit.returncode


if __name__ == "__main__":
    raise SystemExit(main())
