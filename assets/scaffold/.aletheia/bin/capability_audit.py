#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_TERMS = [
    "help.py",
    "capability_audit.py",
    "orient.py",
    "context_pack.py",
    "preflight.py",
    "status.py",
    "truth_record.py",
    "model_gate.py",
    "runtime_policy.json",
    "source_inventory.py",
    "guided_bootstrap.py",
    "bootstrap_finalize.py",
    "validate.py",
    "overview.py",
    "checkpoint.py",
    "aletheia-bootstrap",
    "aletheia-orient",
    "aletheia-checkpoint",
    "aletheia-design-evidence",
    "aletheia-architecture-evolution",
    "aletheia-promote",
    "truth-auditor",
    "evidence-curator",
    "architecture-reviewer",
    "Codex enablement",
    "host limitation",
]

CRUD_TERMS = [
    "truth_record.py list",
    "truth_record.py create",
    "truth_record.py show",
    "truth_record.py update",
    "truth_record.py archive",
    "model_gate.py --registry register",
    "model_gate.py --registry remove",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def audit(root: Path) -> list[str]:
    path = root / ".aletheia" / "CAPABILITY_MAP.md"
    if not path.exists():
        return ["missing capability map: .aletheia/CAPABILITY_MAP.md"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"capability map missing term: {term}")
    for term in CRUD_TERMS:
        if term not in text:
            errors.append(f"capability map missing CRUD command: {term}")
    return errors


def main() -> int:
    errors = audit(repo_root())
    if errors:
        print("capability audit failed", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("capability audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
