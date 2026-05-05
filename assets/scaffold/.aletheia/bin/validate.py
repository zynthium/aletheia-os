#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "AGENTS.md",
    "START_HERE.md",
    ".aletheia/START_HERE.md",
    ".aletheia/VERSION",
    ".aletheia/governance/CHARTER.md",
    ".aletheia/governance/ATTENTION_POLICY.md",
    ".aletheia/governance/MODEL_GOVERNANCE.md",
    ".aletheia/governance/GIT_POLICY.md",
    ".aletheia/governance/model_registry.json",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/RISK_REGISTER.md",
    ".aletheia/bin/orient.py",
    ".aletheia/bin/model_gate.py",
    ".aletheia/bin/validate.py",
    ".aletheia/bin/checkpoint.py",
    ".aletheia/bin/overview.py",
    ".aletheia/bin/bootstrap_finalize.py",
    ".aletheia/templates/DECISION.md",
    ".aletheia/templates/EVIDENCE.md",
    ".aletheia/templates/RISK.md",
    ".aletheia/templates/CONTRACT.md",
    ".aletheia/templates/SESSION_NOTE.md",
]

REQUIRED_SKELETON_ROOT_FIELDS = [
    "layer",
    "parent",
    "children",
    "purpose",
    "invariants",
    "interfaces",
    "owned_paths",
    "test_paths",
    "contract_refs",
    "decision_refs",
    "evidence_refs",
    "expand_when",
    "stop_when",
    "confidence",
    "last_reviewed",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def validate_skeleton(root: Path) -> list[str]:
    text = (root / ".aletheia" / "state" / "SKELETON.yaml").read_text(encoding="utf-8")
    if not re.search(r"(?m)^nodes:\s*$", text):
        return [".aletheia/state/SKELETON.yaml must contain nodes mapping"]
    root_match = re.search(r"(?m)^  root:\s*$", text)
    if not root_match:
        return [".aletheia/state/SKELETON.yaml must contain nodes.root mapping"]

    root_block_lines: list[str] = []
    for line in text[root_match.end() :].splitlines():
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", line):
            break
        root_block_lines.append(line)

    fields = set()
    for line in root_block_lines:
        field_match = re.match(r"^    ([A-Za-z_][A-Za-z0-9_]*):", line)
        if field_match:
            fields.add(field_match.group(1))

    missing = [field for field in REQUIRED_SKELETON_ROOT_FIELDS if field not in fields]
    return [f".aletheia/state/SKELETON.yaml nodes.root missing field: {field}" for field in missing]


def main() -> int:
    root = repo_root()
    errors = [f"missing required path: {rel}" for rel in REQUIRED_PATHS if not (root / rel).exists()]
    if not errors:
        errors.extend(validate_skeleton(root))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("AletheiaOS validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
