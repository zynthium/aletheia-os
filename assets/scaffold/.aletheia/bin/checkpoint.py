#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from git_trailers import (
    ALLOWED_NODE_STATES,
    ALLOWED_REVIEW,
    build_aios_trailers,
    parse_trailers,
    validate_trailer_values,
)


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
CHECKPOINT_EXCLUDED_PATTERNS = [
    ".aletheia/runtime/",
    ".aletheia/overview/",
    ".aletheia/source_inventory/",
    "**/__pycache__/",
    "**/*.pyc",
]
RUNTIME_POLICY = ".aletheia/governance/runtime_policy.json"

INTERRUPTED_GIT_MARKERS = [
    "MERGE_HEAD",
    "REBASE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
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


def git_dir(root: Path) -> Path:
    result = run(["git", "rev-parse", "--git-dir"], root, capture=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "git rev-parse --git-dir failed")
    path = Path(result.stdout.strip())
    if not path.is_absolute():
        path = root / path
    return path


def interrupted_git_operation(root: Path) -> str | None:
    git_path = git_dir(root)
    for marker in INTERRUPTED_GIT_MARKERS:
        if (git_path / marker).exists():
            return marker
    for directory in ["rebase-merge", "rebase-apply"]:
        if (git_path / directory).exists():
            return directory
    return None


def status_files(root: Path) -> list[str]:
    result = run(["git", "status", "--porcelain", "--untracked-files=all"], root, capture=True)
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


def checkpoint_excluded(file: str, patterns: list[str]) -> bool:
    path_parts = Path(file).parts
    for pattern in patterns:
        if pattern.startswith("**/") and pattern.endswith("/"):
            if pattern[3:].rstrip("/") in path_parts:
                return True
            continue
        if pattern.endswith("/") and file.startswith(pattern):
            return True
        if any(marker in pattern for marker in "*?[") and fnmatch.fnmatch(file, pattern):
            return True
        if file == pattern:
            return True
    return False


def has_state_update(files: list[str], patterns: list[str], excluded_patterns: list[str] | None = None) -> bool:
    excluded_patterns = excluded_patterns or []
    for file in files:
        if checkpoint_excluded(file, excluded_patterns):
            continue
        for pattern in patterns:
            if pattern.endswith("/"):
                if file.startswith(pattern):
                    return True
            elif file == pattern:
                return True
    return False


def state_files(root: Path, files: list[str], patterns: list[str], excluded_patterns: list[str] | None = None) -> list[str]:
    excluded_patterns = excluded_patterns or []
    state: list[str] = []
    for file in files:
        if checkpoint_excluded(file, excluded_patterns):
            continue
        for pattern in patterns:
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


def protected_files(files: list[str], patterns: list[str]) -> list[str]:
    compiled = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    return [file for file in files if any(pattern.search(file) for pattern in compiled)]


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


def list_policy_values(policy: dict, key: str, fallback: list[str]) -> list[str]:
    values = policy.get(key)
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        return list(fallback)
    return list(values)


def runtime_policy(root: Path) -> dict:
    policy = load_json(root / RUNTIME_POLICY)
    return {
        "checkpoint_state_patterns": list_policy_values(policy, "checkpoint_state_patterns", STATE_PATTERNS),
        "checkpoint_excluded_patterns": list_policy_values(
            policy,
            "checkpoint_excluded_patterns",
            CHECKPOINT_EXCLUDED_PATTERNS,
        ),
        "protected_path_patterns": list_policy_values(
            policy,
            "protected_path_patterns",
            [pattern.pattern for pattern in PROTECTED_PATTERNS],
        ),
    }


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


def inferred_traceability_action(args: argparse.Namespace) -> str | None:
    if args.tree_op == "bootstrap":
        return "truth.bootstrap.initialize"
    if args.node_state == "stable":
        return "truth.node.stabilize"
    if args.implements and not args.node_state:
        return "engineering.implements_truth"
    if args.tree_op:
        return "truth.tree.transition"
    return None


def traceability_validation(args: argparse.Namespace) -> str | None:
    if args.node_state == "stable":
        return "pass"
    return None


def checkpoint_traceability_trailers(args: argparse.Namespace) -> str:
    trailers = build_aios_trailers(
        action=inferred_traceability_action(args),
        tree_op=args.tree_op,
        node=args.node,
        parent=args.parent,
        node_state=args.node_state,
        evidence=args.evidence,
        decision=args.decision,
        implements=args.implements,
        supersedes=args.supersedes,
        validation=traceability_validation(args),
        review=args.review,
    )
    errors = validate_trailer_values(parse_trailers(trailers))
    if errors:
        raise ValueError("; ".join(errors))
    return trailers


def stable_checkpoint_blocker(args: argparse.Namespace) -> str | None:
    if args.node_state != "stable":
        return None
    if not args.evidence:
        return "stable node checkpoint requires --evidence"
    if not args.decision:
        return "stable node checkpoint requires --decision"
    if args.review != "human-confirmed":
        return "stable node checkpoint requires --review human-confirmed"
    return None


def combine_commit_message(message: str, traceability: str, run_data: dict) -> str:
    if traceability:
        message = message + "\n\n" + traceability
    return message + attribution_trailers(run_data)


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


def stage_state_files(root: Path, files: list[str]) -> int:
    if not files:
        print("checkpoint blocked: no AletheiaOS state paths exist")
        return 1
    result = run(["git", "add", "--", *files], root, capture=True)
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
    parser.add_argument("--tree-op")
    parser.add_argument("--node")
    parser.add_argument("--parent")
    parser.add_argument("--node-state", choices=sorted(ALLOWED_NODE_STATES))
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--decision", action="append", default=[])
    parser.add_argument("--implements", action="append", default=[])
    parser.add_argument("--supersedes", action="append", default=[])
    parser.add_argument("--review", choices=sorted(ALLOWED_REVIEW))
    args = parser.parse_args()

    root = repo_root()
    try:
        ensure_git(root)
        interrupted = interrupted_git_operation(root)
        if interrupted:
            print(f"checkpoint blocked: git operation in progress ({interrupted})")
            print("finish or abort the current merge/rebase/cherry-pick before checkpointing")
            return 6
        files = status_files(root)
    except RuntimeError as exc:
        print(f"checkpoint blocked: {exc}")
        return 1
    policy = runtime_policy(root)
    checkpoint_patterns = policy["checkpoint_state_patterns"]
    checkpoint_excluded_patterns = policy["checkpoint_excluded_patterns"]
    protected_patterns = policy["protected_path_patterns"]
    if not files:
        print("checkpoint skipped: working tree is clean")
        return 0

    protected = protected_files(files, protected_patterns)
    if protected:
        print("checkpoint blocked: protected-looking files are present:")
        for file in protected:
            print(f"  - {file}")
        return 2

    stable_blocker = stable_checkpoint_blocker(args)
    if stable_blocker:
        print(f"checkpoint blocked: {stable_blocker}")
        return 7

    try:
        traceability_trailers = checkpoint_traceability_trailers(args)
    except ValueError as exc:
        print(f"checkpoint blocked: {exc}")
        return 7

    if not args.no_validate:
        rc = validate(root)
        if rc != 0:
            print("checkpoint blocked: validation failed")
            return rc

    if not has_state_update(files, checkpoint_patterns, checkpoint_excluded_patterns) and not (
        args.allow_code_only or os.environ.get("AIOS_ALLOW_CODE_ONLY_COMMIT") == "1"
    ):
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

    candidate_files = files if args.include_worktree else state_files(
        root,
        files,
        checkpoint_patterns,
        checkpoint_excluded_patterns,
    )
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
    if traceability_trailers:
        print("traceability:")
        for line in traceability_trailers.splitlines():
            print(f"  {line}")

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
        rc = stage_state_files(root, candidate_files)
        if rc != 0:
            return rc

    commit_cmd = ["git", "commit", "-m", combine_commit_message(message, traceability_trailers, run_data)]
    if not args.include_worktree:
        commit_cmd.extend(["--", *candidate_files])
    commit = run(commit_cmd, root, capture=True)
    print(commit.stdout, end="")
    if commit.returncode != 0:
        print(commit.stderr, end="")
        print("checkpoint failed: git commit returned non-zero status")
    return commit.returncode


if __name__ == "__main__":
    raise SystemExit(main())
