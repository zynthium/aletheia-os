#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from aletheia_scaffold import SCAFFOLD_ROOT, copy_tree_without_overwrite, ensure_claude_settings


LEGACY_FILE_MAP = {
    "00_CHARTER.md": ".aletheia/governance/CHARTER.md",
    "10_ATTENTION_POLICY.md": ".aletheia/governance/ATTENTION_POLICY.md",
    "11_MODEL_GOVERNANCE.md": ".aletheia/governance/MODEL_GOVERNANCE.md",
    "12_INTAKE_POLICY.md": ".aletheia/governance/INTAKE_POLICY.md",
    "08_GIT_POLICY.md": ".aletheia/governance/GIT_POLICY.md",
    "02_ACTIVE_STATE.md": ".aletheia/state/ACTIVE_STATE.md",
    "01_SYSTEM_GRAPH.yaml": ".aletheia/state/SYSTEM_GRAPH.yaml",
    "03_FRONTIER_BOARD.md": ".aletheia/state/FRONTIER_BOARD.md",
    "04_RISK_REGISTER.md": ".aletheia/state/RISK_REGISTER.md",
    "05_GLOSSARY.md": ".aletheia/state/GLOSSARY.md",
    "06_INTERFACE_CONTRACTS.md": ".aletheia/contracts/INDEX.md",
    "07_EVIDENCE_INDEX.md": ".aletheia/evidence/INDEX.md",
    "09_DOMAIN_PROFILE.md": ".aletheia/state/DOMAIN_PROFILE.md",
    "model_registry.json": ".aletheia/governance/model_registry.json",
}

LEGACY_DIR_MAP = {
    "agent_runs": ".aletheia/agent_runs",
    "contracts": ".aletheia/contracts",
    "decisions": ".aletheia/decisions",
    "evidence": ".aletheia/evidence",
    "hypotheses": ".aletheia/hypotheses",
    "nodes": ".aletheia/nodes",
    "risks": ".aletheia/risks",
    "session_notes": ".aletheia/session_notes",
    "templates": ".aletheia/templates",
    "playbooks": ".aletheia/playbooks",
    "bootstrap_intake": ".aletheia/bootstrap_intake",
}

PATH_REWRITES = {
    "aletheia_os/00_CHARTER.md": ".aletheia/governance/CHARTER.md",
    "aletheia_os/01_SYSTEM_GRAPH.yaml": ".aletheia/state/SYSTEM_GRAPH.yaml",
    "aletheia_os/02_ACTIVE_STATE.md": ".aletheia/state/ACTIVE_STATE.md",
    "aletheia_os/03_FRONTIER_BOARD.md": ".aletheia/state/FRONTIER_BOARD.md",
    "aletheia_os/04_RISK_REGISTER.md": ".aletheia/state/RISK_REGISTER.md",
    "aletheia_os/05_GLOSSARY.md": ".aletheia/state/GLOSSARY.md",
    "aletheia_os/06_INTERFACE_CONTRACTS.md": ".aletheia/contracts/INDEX.md",
    "aletheia_os/07_EVIDENCE_INDEX.md": ".aletheia/evidence/INDEX.md",
    "aletheia_os/08_GIT_POLICY.md": ".aletheia/governance/GIT_POLICY.md",
    "aletheia_os/09_DOMAIN_PROFILE.md": ".aletheia/state/DOMAIN_PROFILE.md",
    "aletheia_os/10_ATTENTION_POLICY.md": ".aletheia/governance/ATTENTION_POLICY.md",
    "aletheia_os/11_MODEL_GOVERNANCE.md": ".aletheia/governance/MODEL_GOVERNANCE.md",
    "aletheia_os/12_INTAKE_POLICY.md": ".aletheia/governance/INTAKE_POLICY.md",
    "aletheia_os/model_registry.json": ".aletheia/governance/model_registry.json",
    "scripts/aios_context_pack.py": ".aletheia/bin/context_pack.py",
    "scripts/aios_intake_inventory.py": ".aletheia/bin/intake_inventory.py",
    "scripts/aios_guided_bootstrap.py": ".aletheia/bin/guided_bootstrap.py",
    "scripts/aios_validate.py": ".aletheia/bin/validate.py",
    "scripts/aios_orient.py": ".aletheia/bin/orient.py",
    "scripts/aios_model_gate.py": ".aletheia/bin/model_gate.py",
    "scripts/aios_checkpoint.py": ".aletheia/bin/checkpoint.py",
    "scripts/aios_bootstrap.py": ".aletheia/bin/bootstrap_finalize.py",
}

TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".sh"}


def rewrite_legacy_text(text: str) -> str:
    rewritten = text
    for old, new in PATH_REWRITES.items():
        rewritten = rewritten.replace(old, new)
    rewritten = rewritten.replace("aletheia_os/", ".aletheia/")
    rewritten = rewritten.replace("scripts/aios_", ".aletheia/bin/")
    return rewritten


def copy_with_rewrite(src: Path, dst: Path, overwrite: bool) -> bool:
    if dst.exists() and not overwrite:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in TEXT_SUFFIXES:
        dst.write_text(rewrite_legacy_text(src.read_text(encoding="utf-8")), encoding="utf-8")
    else:
        shutil.copy2(src, dst)
    return True


def copy_legacy_tree(src: Path, dst: Path) -> int:
    copied = 0
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            continue
        if copy_with_rewrite(path, target, overwrite=False):
            copied += 1
    return copied


def migrate_legacy(target: Path, overwrite_state: bool) -> tuple[int, list[str]]:
    legacy_root = target / "aletheia_os"
    if not legacy_root.exists():
        raise FileNotFoundError(f"missing legacy directory: {legacy_root}")

    copied = 0
    migrated: list[str] = []
    for legacy_rel, new_rel in LEGACY_FILE_MAP.items():
        src = legacy_root / legacy_rel
        dst = target / new_rel
        if src.exists() and copy_with_rewrite(src, dst, overwrite=overwrite_state):
            copied += 1
            migrated.append(f"{legacy_rel} -> {new_rel}")

    for legacy_rel, new_rel in LEGACY_DIR_MAP.items():
        src = legacy_root / legacy_rel
        dst = target / new_rel
        if not src.exists():
            continue
        before = copied
        copied += copy_legacy_tree(src, dst)
        if copied != before:
            migrated.append(f"{legacy_rel}/ -> {new_rel}/")

    return copied, migrated


def extract_root_children(graph_text: str) -> list[str]:
    in_root = False
    in_children = False
    children: list[str] = []
    for line in graph_text.splitlines():
        if line == "root:":
            in_root = True
            continue
        if in_root and line and not line.startswith(" "):
            break
        if in_root and line == "  children:":
            in_children = True
            continue
        if in_children:
            if line.startswith("    - "):
                children.append(line.split("-", 1)[1].strip())
                continue
            if line.startswith("  ") and not line.startswith("    "):
                break
    return children


def sync_skeleton_children(target: Path) -> bool:
    graph_path = target / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml"
    skeleton_path = target / ".aletheia" / "state" / "SKELETON.yaml"
    if not graph_path.exists() or not skeleton_path.exists():
        return False
    children = extract_root_children(graph_path.read_text(encoding="utf-8"))
    if not children:
        return False
    skeleton = skeleton_path.read_text(encoding="utf-8")
    block = "    children:\n" + "".join(f"      - {child}\n" for child in children)
    updated = re.sub(r"(?m)^    children:\n(?:      - .+\n)+", block, skeleton, count=1)
    if updated != skeleton:
        skeleton_path.write_text(updated, encoding="utf-8")
        return True
    return False


def write_import_report(target: Path, migrated: list[str], scaffold_count: int, legacy_count: int, claude_status: str, skeleton_synced: bool) -> Path:
    out_dir = target / ".aletheia" / "bootstrap_intake"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / "IMPORT_REPORT.md"
    lines = [
        "# Bootstrap Import Report",
        "",
        "## Metadata",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        "- Initialization mode: migration",
        "- Legacy directory: preserved at `aletheia_os/`",
        f"- Scaffold files copied: {scaffold_count}",
        f"- Legacy files copied: {legacy_count}",
        f"- Claude settings: {claude_status}",
        f"- Skeleton synchronized: {skeleton_synced}",
        "",
        "## Migrated Paths",
        "",
    ]
    lines.extend(f"- `{entry}`" for entry in migrated)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy aletheia_os layout to .aletheia.")
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite-state", action="store_true")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.exists() or not target.is_dir():
        parser.error(f"target must be an existing directory: {target}")
    if not (target / "aletheia_os").exists():
        parser.error(f"target must contain legacy aletheia_os directory: {target}")

    if args.dry_run:
        print(f"would copy scaffold from {SCAFFOLD_ROOT}")
        print(f"would migrate legacy directory: {target / 'aletheia_os'}")
        return 0

    had_aletheia = (target / ".aletheia").exists()
    scaffold_written = copy_tree_without_overwrite(SCAFFOLD_ROOT, target)
    claude_status = ensure_claude_settings(target)
    legacy_count, migrated = migrate_legacy(target, overwrite_state=args.overwrite_state or not had_aletheia)
    skeleton_synced = sync_skeleton_children(target)
    report = write_import_report(target, migrated, len(scaffold_written), legacy_count, claude_status, skeleton_synced)

    print(f"copied {len(scaffold_written)} scaffold files")
    print(f"copied {legacy_count} legacy AletheiaOS files")
    print("preserved legacy directory: aletheia_os/")
    print(f"wrote migration report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
