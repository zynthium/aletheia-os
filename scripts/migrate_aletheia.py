#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_ROOT = PLUGIN_ROOT / "assets" / "scaffold"

LEGACY_FILE_MAP = {
    "00_CHARTER.md": ".aletheia/governance/CHARTER.md",
    "10_ATTENTION_POLICY.md": ".aletheia/governance/ATTENTION_POLICY.md",
    "11_MODEL_GOVERNANCE.md": ".aletheia/governance/MODEL_GOVERNANCE.md",
    "08_GIT_POLICY.md": ".aletheia/governance/GIT_POLICY.md",
    "02_ACTIVE_STATE.md": ".aletheia/state/ACTIVE_STATE.md",
    "01_SYSTEM_GRAPH.yaml": ".aletheia/state/SYSTEM_GRAPH.yaml",
    "04_RISK_REGISTER.md": ".aletheia/state/RISK_REGISTER.md",
    "model_registry.json": ".aletheia/governance/model_registry.json",
}

LEGACY_DIR_MAP = {
    "agent_runs": ".aletheia/agent_runs",
    "contracts": ".aletheia/contracts",
    "decisions": ".aletheia/decisions",
    "evidence": ".aletheia/evidence",
    "nodes": ".aletheia/nodes",
    "risks": ".aletheia/risks",
    "session_notes": ".aletheia/session_notes",
    "templates": ".aletheia/templates",
}


def copy_tree_without_overwrite(src: Path, dst: Path) -> int:
    copied = 0
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
        copied += 1
    return copied


def copy_scaffold(target: Path) -> int:
    return copy_tree_without_overwrite(SCAFFOLD_ROOT, target)


def migrate_legacy(target: Path, overwrite_state: bool) -> int:
    legacy_root = target / "aletheia_os"
    if not legacy_root.exists():
        raise FileNotFoundError(f"missing legacy directory: {legacy_root}")

    copied = 0
    for legacy_rel, new_rel in LEGACY_FILE_MAP.items():
        src = legacy_root / legacy_rel
        dst = target / new_rel
        if not src.exists():
            continue
        if dst.exists() and not overwrite_state:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

    for legacy_rel, new_rel in LEGACY_DIR_MAP.items():
        src = legacy_root / legacy_rel
        dst = target / new_rel
        if not src.exists():
            continue
        copied += copy_tree_without_overwrite(src, dst)

    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy aletheia_os layout to .aletheia.")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.exists() or not target.is_dir():
        parser.error(f"target must be an existing directory: {target}")

    had_aletheia = (target / ".aletheia").exists()
    scaffold_copied = copy_scaffold(target)
    legacy_copied = migrate_legacy(target, overwrite_state=not had_aletheia)
    print(f"copied {scaffold_copied} scaffold files")
    print(f"copied {legacy_copied} legacy AletheiaOS files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
