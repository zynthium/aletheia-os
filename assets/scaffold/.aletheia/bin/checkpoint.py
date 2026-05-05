#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


STATE_ALLOWLIST = [
    ".aletheia",
    "AGENTS.md",
    "START_HERE.md",
    "BOOTSTRAP.md",
    "docs/overview",
]

SECRET_NAME_MARKERS = [
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "private_key",
    "id_rsa",
    "token",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)


def changed_paths(root: Path) -> list[str]:
    status = run(["git", "status", "--porcelain"], root)
    if status.returncode != 0:
        raise RuntimeError(status.stderr)
    paths = []
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        paths.append(line[3:])
    return paths


def has_secret_like_path(paths: list[str]) -> list[str]:
    hits = []
    for path in paths:
        lower = path.lower()
        if any(marker in lower for marker in SECRET_NAME_MARKERS):
            hits.append(path)
    return hits


def stage_state_paths(root: Path) -> int:
    existing = [path for path in STATE_ALLOWLIST if (root / path).exists()]
    if not existing:
        print("checkpoint blocked: no AletheiaOS state paths exist")
        return 1
    add = run(["git", "add", *existing], root)
    if add.returncode != 0:
        print(add.stderr, end="")
    return add.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and optionally create an AletheiaOS checkpoint.")
    parser.add_argument("--auto", action="store_true", help="Create a git commit after validation")
    parser.add_argument("--message", default="checkpoint: update AletheiaOS state")
    parser.add_argument("--include-worktree", action="store_true", help="Stage the full worktree after secret-name screening")
    args = parser.parse_args()

    root = repo_root()
    validate = run(["python3", ".aletheia/bin/validate.py"], root)
    print(validate.stdout, end="")
    if validate.returncode != 0:
        print(validate.stderr, end="")
        return validate.returncode

    if not args.auto:
        print("checkpoint deferred: pass --auto to create a git commit")
        return 0

    paths = changed_paths(root)
    if not paths:
        print("checkpoint skipped: no changes")
        return 0

    secret_hits = has_secret_like_path(paths)
    if secret_hits:
        print("checkpoint blocked: secret-like path names detected")
        for path in secret_hits:
            print(f"  {path}")
        return 1

    if args.include_worktree:
        add = run(["git", "add", "."], root)
        if add.returncode != 0:
            print(add.stderr, end="")
            return add.returncode
    else:
        staged = stage_state_paths(root)
        if staged != 0:
            return staged

    commit = run(["git", "commit", "-m", args.message], root)
    print(commit.stdout, end="")
    if commit.returncode != 0:
        print(commit.stderr, end="")
    return commit.returncode


if __name__ == "__main__":
    raise SystemExit(main())
