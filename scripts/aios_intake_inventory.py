#!/usr/bin/env python3
"""Create a safe bootstrap intake inventory for AletheiaOS."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT_DIR = ROOT / "aletheia_os" / "bootstrap_intake"
OUT_JSON = OUT_DIR / "inventory.json"
OUT_MD = OUT_DIR / "inventory.md"

EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules", "__pycache__",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".cache", ".tox",
    "vendor", "target", ".idea", ".vscode"
}

SENSITIVE_PATTERNS = [
    re.compile(p, re.I) for p in [
        r"\.env($|\.)", r"secret", r"credential", r"password", r"passwd", r"token", r"apikey",
        r"api[_-]?key", r"broker", r"private[_-]?key", r"\.pem$", r"\.key$", r"id_rsa",
        r"account", r"auth", r"oauth"
    ]
]

LARGE_BYTES = 1_000_000

EXT_KIND = {
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
    ".feather": "data",
    ".pdf": "document_or_report",
    ".html": "report_or_doc",
    ".sh": "script",
}

KEYWORD_KIND = [
    ("charter", "root_mission_or_charter"),
    ("mission", "root_mission_or_charter"),
    ("architecture", "system_architecture_or_design"),
    ("design", "system_architecture_or_design"),
    ("hypothesis", "research_theory_or_hypothesis"),
    ("theory", "research_theory_or_hypothesis"),
    ("evidence", "evidence_experiment_or_simulation"),
    ("experiment", "evidence_experiment_or_simulation"),
    ("simulation", "evidence_experiment_or_simulation"),
    ("test", "tests_or_validation"),
    ("contract", "interface_or_contract"),
    ("risk", "risk_safety_or_constraints"),
    ("safety", "risk_safety_or_constraints"),
    ("deploy", "operations_or_deployment"),
]


def is_sensitive(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    return any(p.search(s) for p in SENSITIVE_PATTERNS)


def infer_kind(path: Path) -> str:
    lower = str(path).lower().replace("\\", "/")
    for keyword, kind in KEYWORD_KIND:
        if keyword in lower:
            return kind
    return EXT_KIND.get(path.suffix.lower(), "unknown_or_unclassified")


def classify_initial(path: Path, size: int, kind: str) -> str:
    if is_sensitive(path):
        return "unsafe_or_sensitive"
    if size > LARGE_BYTES:
        return "deferred_due_to_size"
    if "deprecated" in str(path).lower() or "archive" in str(path).lower() or "old" in str(path).lower():
        return "historical_context"
    if kind in {"root_mission_or_charter", "system_architecture_or_design", "interface_or_contract", "tests_or_validation"}:
        return "useful_but_unverified"
    if kind in {"research_theory_or_hypothesis", "evidence_experiment_or_simulation"}:
        return "useful_but_unverified"
    return "unknown"


def iter_files():
    for base, dirs, files in os.walk(ROOT):
        base_path = Path(base)
        rel_base = base_path.relative_to(ROOT)
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        if rel_base.parts and rel_base.parts[0] in EXCLUDED_DIRS:
            continue
        for name in files:
            path = base_path / name
            rel = path.relative_to(ROOT)
            if rel.parts and rel.parts[0] in EXCLUDED_DIRS:
                continue
            yield rel


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for rel in sorted(iter_files(), key=lambda p: str(p)):
        full = ROOT / rel
        try:
            size = full.stat().st_size
        except OSError:
            continue
        kind = infer_kind(rel)
        classification = classify_initial(rel, size, kind)
        items.append({
            "path": str(rel).replace("\\", "/"),
            "size_bytes": size,
            "kind": kind,
            "initial_classification": classification,
            "should_read_full_content": classification not in {"unsafe_or_sensitive", "deferred_due_to_size"},
        })

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(ROOT),
        "large_threshold_bytes": LARGE_BYTES,
        "items": items,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {}
    for item in items:
        counts[item["initial_classification"]] = counts.get(item["initial_classification"], 0) + 1

    lines = ["# Bootstrap Intake Inventory", "", f"Generated at: {payload['generated_at']}", "", "## Summary", ""]
    for k in sorted(counts):
        lines.append(f"- {k}: {counts[k]}")
    lines.extend(["", "## Items", ""])
    for item in items:
        lines.append(f"- `{item['path']}` — {item['kind']} — {item['initial_classification']} — {item['size_bytes']} bytes")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
