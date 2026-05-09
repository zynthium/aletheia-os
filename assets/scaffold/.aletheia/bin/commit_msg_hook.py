#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from git_trailers import parse_trailers, validate_trailer_values


TREE_SENSITIVE_PREFIXES = (
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/ORPHANS.yaml",
    ".aletheia/nodes/",
)
REFERENCE_TRAILERS = (
    "AIOS-Evidence",
    "AIOS-Decision",
    "AIOS-Implements",
    "AIOS-Supersedes",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def staged_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff --cached failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_tree_sensitive(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in TREE_SENSITIVE_PREFIXES)


def has_value(trailers: dict[str, list[str]], key: str, value: str | None = None) -> bool:
    values = trailers.get(key, [])
    if value is None:
        return bool(values)
    return value in values


def invalid_reference_path(value: str) -> bool:
    path = Path(value)
    return path.is_absolute() or ".." in path.parts


def validate_reference_paths(root: Path, trailers: dict[str, list[str]], errors: list[str]) -> None:
    for key in REFERENCE_TRAILERS:
        for value in trailers.get(key, []):
            if invalid_reference_path(value):
                errors.append(f"{key} uses unsafe path: {value}")
    if has_value(trailers, "AIOS-Node-State", "stable"):
        for key in ("AIOS-Evidence", "AIOS-Decision"):
            for value in trailers.get(key, []):
                if not invalid_reference_path(value) and not (root / value).exists():
                    errors.append(f"stable node marker references missing {key}: {value}")


def validate_tree_sensitive_change(trailers: dict[str, list[str]], errors: list[str]) -> None:
    if not has_value(trailers, "AIOS-Action"):
        errors.append("tree-sensitive changes require AIOS-Action")
    if not (has_value(trailers, "AIOS-Tree-Op") or has_value(trailers, "AIOS-Node-State")):
        errors.append("tree-sensitive changes require AIOS-Tree-Op or AIOS-Node-State")


def validate_stable_marker(trailers: dict[str, list[str]], errors: list[str]) -> None:
    if not has_value(trailers, "AIOS-Node-State", "stable"):
        return
    required = [
        ("AIOS-Action", "truth.node.stabilize", "stable node marker requires AIOS-Action: truth.node.stabilize"),
        ("AIOS-Node", None, "stable node marker requires AIOS-Node"),
        ("AIOS-Evidence", None, "stable node marker requires AIOS-Evidence"),
        ("AIOS-Decision", None, "stable node marker requires AIOS-Decision"),
        ("AIOS-Validation", "pass", "stable node marker requires AIOS-Validation: pass"),
        ("AIOS-Review", "human-confirmed", "stable node marker requires AIOS-Review: human-confirmed"),
    ]
    for key, value, message in required:
        if not has_value(trailers, key, value):
            errors.append(message)


def check_commit_message(root: Path, message: str) -> list[str]:
    trailers = parse_trailers(message)
    errors = validate_trailer_values(trailers)
    tree_sensitive = any(is_tree_sensitive(path) for path in staged_files(root))
    if tree_sensitive:
        validate_tree_sensitive_change(trailers, errors)
    validate_stable_marker(trailers, errors)
    validate_reference_paths(root, trailers, errors)
    return errors


def remediation_hints(errors: list[str]) -> list[str]:
    if not any(error.startswith("tree-sensitive changes require") for error in errors):
        return []
    return [
        "For bootstrap initialization, run bootstrap_finalize.py or use:",
        "python3 .aletheia/bin/checkpoint.py --auto --message \"bootstrap: initialize AletheiaOS\" --allow-code-only --tree-op bootstrap --node root --review not-required",
        "Use checkpoint.py for tree-sensitive commits, for example:",
        "python3 .aletheia/bin/checkpoint.py --auto --tree-op <operation> --node <node> --review agent-reviewed",
        "or add equivalent trailers manually:",
        "AIOS-Action: truth.bootstrap.initialize",
        "AIOS-Tree-Op: bootstrap",
        "AIOS-Node: root",
        "AIOS-Review: not-required",
        "or for non-bootstrap tree transitions:",
        "AIOS-Action: truth.tree.transition",
        "AIOS-Tree-Op: <operation>",
        "AIOS-Node: <node>",
        "AIOS-Review: agent-reviewed",
    ]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: commit_msg_hook.py <commit-message-file>")
        return 2
    root = repo_root()
    try:
        message = Path(argv[1]).read_text(encoding="utf-8")
        errors = check_commit_message(root, message)
    except Exception as exc:
        print("AletheiaOS commit message blocked:")
        print(f"  - {exc}")
        return 1
    if not errors:
        return 0
    print("AletheiaOS commit message blocked:")
    for error in errors:
        print(f"  - {error}")
    hints = remediation_hints(errors)
    if hints:
        print("AletheiaOS commit message remediation:")
        for hint in hints:
            print(f"  - {hint}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
