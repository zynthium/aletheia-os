from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_ROOT = PLUGIN_ROOT / "assets" / "scaffold"


def copy_tree_without_overwrite(src: Path, dst: Path) -> list[Path]:
    written: list[Path] = []
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        written.append(target)
    return written


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return data


def hook_entry_key(entry: dict[str, Any]) -> tuple[str, str, str]:
    hooks = entry.get("hooks", [])
    command = ""
    if hooks and isinstance(hooks, list) and isinstance(hooks[0], dict):
        command = str(hooks[0].get("command", ""))
    return (str(entry.get("matcher", "")), str(entry.get("type", "")), command)


def ensure_claude_settings(target: Path) -> str:
    src = SCAFFOLD_ROOT / ".claude" / "settings.json"
    dst = target / ".claude" / "settings.json"
    required = load_json(src)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return "created"

    existing = load_json(dst)
    existing_hooks = existing.setdefault("hooks", {})
    changed = False
    for event_name, required_entries in (required.get("hooks", {}) or {}).items():
        current_entries = existing_hooks.setdefault(event_name, [])
        current_keys = {hook_entry_key(entry) for entry in current_entries if isinstance(entry, dict)}
        for required_entry in required_entries:
            key = hook_entry_key(required_entry)
            if key not in current_keys:
                current_entries.append(required_entry)
                current_keys.add(key)
                changed = True

    if changed:
        dst.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
        return "merged"
    return "unchanged"
