#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".agents",
    ".aletheia",
    ".claude",
    ".codex",
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
DEFAULT_EXCLUDED_ROOT_FILES = {"AGENTS.md", "START_HERE.md", "BOOTSTRAP.md"}
DEFAULT_SENSITIVE_PATTERNS = [
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
DEFAULT_LARGE_BYTES = 1_000_000
DEFAULT_KIND_KEYWORDS = {
    "charter": "root_mission_or_charter",
    "mission": "root_mission_or_charter",
    "architecture": "system_architecture_or_design",
    "design": "system_architecture_or_design",
    "hypothesis": "research_theory_or_hypothesis",
    "evidence": "evidence_experiment_or_simulation",
    "experiment": "evidence_experiment_or_simulation",
    "simulation": "evidence_experiment_or_simulation",
    "test": "tests_or_validation",
    "contract": "interface_or_contract",
    "risk": "risk_safety_or_constraints",
}
DEFAULT_SUFFIX_KINDS = {
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
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def list_policy_values(policy: dict[str, Any], key: str, fallback: set[str] | list[str]) -> list[str]:
    values = policy.get(key)
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        return list(fallback)
    return values


def dict_policy_values(policy: dict[str, Any], key: str, fallback: dict[str, str]) -> dict[str, str]:
    values = policy.get(key)
    if not isinstance(values, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in values.items()):
        return dict(fallback)
    return dict(values)


def int_policy_value(policy: dict[str, Any], key: str, fallback: int) -> int:
    value = policy.get(key)
    return value if isinstance(value, int) and value > 0 else fallback


def runtime_policy(root: Path) -> dict[str, Any]:
    policy = load_json(root / ".aletheia" / "governance" / "runtime_policy.json")
    return {
        "excluded_dirs": set(list_policy_values(policy, "source_inventory_excluded_dirs", DEFAULT_EXCLUDED_DIRS)),
        "excluded_root_files": set(
            list_policy_values(policy, "source_inventory_excluded_root_files", DEFAULT_EXCLUDED_ROOT_FILES)
        ),
        "sensitive_patterns": list_policy_values(
            policy,
            "source_inventory_sensitive_patterns",
            DEFAULT_SENSITIVE_PATTERNS,
        ),
        "large_bytes": int_policy_value(policy, "source_inventory_large_bytes", DEFAULT_LARGE_BYTES),
        "kind_keywords": dict_policy_values(policy, "source_inventory_kind_keywords", DEFAULT_KIND_KEYWORDS),
        "suffix_kinds": dict_policy_values(policy, "source_inventory_suffix_kinds", DEFAULT_SUFFIX_KINDS),
    }


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def is_sensitive(path: Path, sensitive_patterns: list[re.Pattern[str]]) -> bool:
    normalized = str(path).replace("\\", "/")
    return any(pattern.search(normalized) for pattern in sensitive_patterns)


def infer_kind(path: Path, kind_keywords: dict[str, str], suffix_kinds: dict[str, str]) -> str:
    lower = str(path).lower().replace("\\", "/")
    for keyword, kind in kind_keywords.items():
        if keyword in lower:
            return kind
    return suffix_kinds.get(path.suffix.lower(), "unknown_or_unclassified")


def classify_initial(path: Path, size: int, kind: str, sensitive_patterns: list[re.Pattern[str]], large_bytes: int) -> str:
    if is_sensitive(path, sensitive_patterns):
        return "unsafe_or_sensitive"
    if size > large_bytes:
        return "deferred_due_to_size"
    if "deprecated" in str(path).lower() or "archive" in str(path).lower() or "old" in str(path).lower():
        return "historical_context"
    if kind != "unknown_or_unclassified":
        return "useful_but_unverified"
    return "unknown"


def iter_files(root: Path, excluded_dirs: set[str], excluded_root_files: set[str]):
    for base, dirs, files in os.walk(root):
        base_path = Path(base)
        rel_base = base_path.relative_to(root)
        if rel_base.parts and (base_path / ".git").exists():
            dirs[:] = []
            continue
        dirs[:] = [name for name in dirs if name not in excluded_dirs]
        if rel_base.parts and rel_base.parts[0] in excluded_dirs:
            continue
        for name in files:
            path = base_path / name
            if path.is_symlink() and not points_inside_root(path, root):
                continue
            rel = path.relative_to(root)
            if rel.parts and rel.parts[0] in excluded_dirs:
                continue
            if len(rel.parts) == 1 and rel.name in excluded_root_files:
                continue
            yield rel


def points_inside_root(path: Path, root: Path) -> bool:
    try:
        resolved = path.resolve(strict=True)
        resolved_root = root.resolve(strict=True)
    except OSError:
        return False
    return resolved == resolved_root or resolved_root in resolved.parents


def ensure_output_dir(path: Path, root: Path) -> None:
    if path.exists() and not path.is_dir():
        rel = path.relative_to(root)
        raise RuntimeError(f"{rel} exists and is not a directory")
    path.mkdir(parents=True, exist_ok=True)


def main() -> int:
    root = repo_root()
    policy = runtime_policy(root)
    sensitive_patterns: list[re.Pattern[str]] = []
    for pattern in policy["sensitive_patterns"]:
        try:
            sensitive_patterns.append(re.compile(pattern, re.I))
        except re.error:
            continue
    out_dir = root / ".aletheia" / "source_inventory"
    try:
        ensure_output_dir(out_dir, root)
    except OSError as exc:
        print(f"source inventory failed: cannot create {out_dir.relative_to(root)}: {exc}")
        return 1
    except RuntimeError as exc:
        print(f"source inventory failed: {exc}")
        return 1
    items = []
    for rel in sorted(iter_files(root, policy["excluded_dirs"], policy["excluded_root_files"]), key=lambda item: str(item)):
        full = root / rel
        try:
            size = full.stat().st_size
        except OSError:
            continue
        kind = infer_kind(rel, policy["kind_keywords"], policy["suffix_kinds"])
        classification = classify_initial(rel, size, kind, sensitive_patterns, policy["large_bytes"])
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
        "large_threshold_bytes": policy["large_bytes"],
        "items": items,
    }
    (out_dir / "inventory.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Source Inventory", "", f"Generated at: {payload['generated_at']}", "", "## Items", ""]
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
