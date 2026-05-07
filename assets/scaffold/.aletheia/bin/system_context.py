#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


USER_PREFERENCES = ".aletheia/state/USER_PREFERENCES.md"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read(root: Path, rel: str) -> str:
    path = root / rel
    if not path.exists():
        return f"MISSING: {rel}"
    return path.read_text(encoding="utf-8").rstrip()


def run_context_pack(root: Path, with_runtime: bool) -> str:
    command = [sys.executable, ".aletheia/bin/context_pack.py"]
    if with_runtime:
        command.append("--with-runtime")
    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return (
            "Context pack failed.\n\n"
            f"Return code: {result.returncode}\n\n"
            f"stdout:\n{result.stdout.rstrip()}\n\n"
            f"stderr:\n{result.stderr.rstrip()}"
        )
    return result.stdout.rstrip()


def build_prompt(root: Path, with_runtime: bool) -> str:
    runtime_note = "including runtime context" if with_runtime else "stable context only"
    return f"""# AletheiaOS Prompt Context

Use this block as dynamic agent context for the current repository. It is generated from repo-native truth files, not from chat memory.

## Operating Rules

- Treat the repository as the durable project truth source.
- Follow the daily loop: orient -> work -> update truth -> validate -> checkpoint.
- Before durable writes, record or verify model-gate attribution.
- Keep generated runtime context after stable project truth.
- Do not copy secrets into `.aletheia/`.

## Context Mode

- mode: {runtime_note}
- repository: {root}

## User Preferences

{read(root, USER_PREFERENCES)}

## Project Context Pack

{run_context_pack(root, with_runtime)}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build prompt-ready AletheiaOS context for agent system prompts.")
    parser.add_argument("--with-runtime", action="store_true", help="append current run and recent session context")
    parser.add_argument("--json", action="store_true", help="emit machine-readable prompt context")
    args = parser.parse_args()

    root = repo_root()
    prompt = build_prompt(root, args.with_runtime)
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "repo": str(root),
                    "with_runtime": args.with_runtime,
                    "prompt": prompt,
                },
                indent=2,
            )
        )
        return 0
    print(prompt.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
