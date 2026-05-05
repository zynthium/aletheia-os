#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".cache",
    ".tox",
    "vendor",
    "target",
}
SENSITIVE_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in [
        r"\.env($|\.)",
        r"secret",
        r"credential",
        r"password",
        r"passwd",
        r"token",
        r"apikey",
        r"api[_-]?key",
        r"private[_-]?key",
        r"\.pem$",
        r"\.key$",
        r"id_rsa",
        r"account",
        r"auth",
        r"oauth",
    ]
]
LARGE_BYTES = 1_000_000


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def is_sensitive(path: Path) -> bool:
    normalized = str(path).replace("\\", "/")
    return any(pattern.search(normalized) for pattern in SENSITIVE_PATTERNS)


def infer_kind(path: Path) -> str:
    lower = str(path).lower().replace("\\", "/")
    for keyword, kind in [
        ("charter", "root_mission_or_charter"),
        ("mission", "root_mission_or_charter"),
        ("architecture", "system_architecture_or_design"),
        ("design", "system_architecture_or_design"),
        ("hypothesis", "research_theory_or_hypothesis"),
        ("evidence", "evidence_experiment_or_simulation"),
        ("experiment", "evidence_experiment_or_simulation"),
        ("simulation", "evidence_experiment_or_simulation"),
        ("test", "tests_or_validation"),
        ("contract", "interface_or_contract"),
        ("risk", "risk_safety_or_constraints"),
    ]:
        if keyword in lower:
            return kind
    return {
        ".md": "document",
        ".txt": "document",
        ".rst": "document",
        ".py": "implementation_code",
        ".ipynb": "notebook",
        ".yaml": "configuration",
        ".yml": "configuration",
        ".json": "configuration",
        ".toml": "configuration",
        ".csv": "data_or_report",
        ".parquet": "data",
        ".pdf": "document_or_report",
        ".html": "report_or_doc",
        ".sh": "script",
    }.get(path.suffix.lower(), "unknown_or_unclassified")


def classify_initial(path: Path, size: int, kind: str) -> str:
    if is_sensitive(path):
        return "unsafe_or_sensitive"
    if size > LARGE_BYTES:
        return "deferred_due_to_size"
    if "deprecated" in str(path).lower() or "archive" in str(path).lower() or "old" in str(path).lower():
        return "historical_context"
    if kind != "unknown_or_unclassified":
        return "useful_but_unverified"
    return "unknown"


def iter_files(root: Path):
    for base, dirs, files in os.walk(root):
        base_path = Path(base)
        rel_base = base_path.relative_to(root)
        dirs[:] = [name for name in dirs if name not in EXCLUDED_DIRS]
        if rel_base.parts and rel_base.parts[0] in EXCLUDED_DIRS:
            continue
        for name in files:
            path = base_path / name
            rel = path.relative_to(root)
            if rel.parts and rel.parts[0] in EXCLUDED_DIRS:
                continue
            yield rel


def main() -> int:
    root = repo_root()
    out_dir = root / ".aletheia" / "bootstrap_intake"
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for rel in sorted(iter_files(root), key=lambda item: str(item)):
        full = root / rel
        try:
            size = full.stat().st_size
        except OSError:
            continue
        kind = infer_kind(rel)
        classification = classify_initial(rel, size, kind)
        items.append(
            {
                "path": str(rel).replace("\\", "/"),
                "size_bytes": size,
                "kind": kind,
                "initial_classification": classification,
                "should_read_full_content": classification not in {"unsafe_or_sensitive", "deferred_due_to_size"},
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(root),
        "large_threshold_bytes": LARGE_BYTES,
        "items": items,
    }
    (out_dir / "inventory.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Bootstrap Intake Inventory", "", f"Generated at: {payload['generated_at']}", "", "## Items", ""]
    for item in items:
        lines.append(
            f"- `{item['path']}` - {item['kind']} - {item['initial_classification']} - {item['size_bytes']} bytes"
        )
    (out_dir / "inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_dir / 'inventory.json'}")
    print(f"wrote {out_dir / 'inventory.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
