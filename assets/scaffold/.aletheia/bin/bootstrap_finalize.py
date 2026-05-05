#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)


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


def configure_hooks(root: Path) -> None:
    hooks = root / ".githooks"
    hooks.mkdir(exist_ok=True)
    pre_commit = hooks / "pre-commit"
    pre_commit.write_text(
        "#!/bin/sh\n"
        "python3 .aletheia/bin/validate.py\n",
        encoding="utf-8",
    )
    pre_commit.chmod(0o755)
    run(["git", "config", "core.hooksPath", ".githooks"], root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize AletheiaOS bootstrap for a target repository.")
    parser.add_argument("--configure-hooks", action="store_true")
    parser.add_argument("--checkpoint", action="store_true")
    parser.add_argument("--keep-bootstrap", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    validate = run(["python3", ".aletheia/bin/validate.py"], root)
    print(validate.stdout, end="")
    if validate.returncode != 0:
        print(validate.stderr, end="")
        return validate.returncode

    if args.configure_hooks:
        configure_hooks(root)
        print("configured git hooks")

    write_session_note(root)

    bootstrap = root / "BOOTSTRAP.md"
    if bootstrap.exists() and not args.keep_bootstrap:
        bootstrap.unlink()
        print("removed BOOTSTRAP.md")

    if args.checkpoint:
        checkpoint = run(["python3", ".aletheia/bin/checkpoint.py", "--auto"], root)
        print(checkpoint.stdout, end="")
        if checkpoint.returncode != 0:
            print(checkpoint.stderr, end="")
        return checkpoint.returncode

    print("bootstrap finalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
