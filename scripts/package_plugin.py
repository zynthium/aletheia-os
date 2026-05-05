#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


REQUIRED = [
    ".codex-plugin/plugin.json",
    "README.zh-CN.md",
    "scripts/aletheia_scaffold.py",
    "scripts/init_aletheia.py",
    "scripts/validate_scaffold.py",
    "scripts/package_plugin.py",
    "skills/aletheia-bootstrap/SKILL.md",
    "skills/aletheia-orient/SKILL.md",
    "skills/aletheia-checkpoint/SKILL.md",
    "skills/aletheia-design-evidence/SKILL.md",
    "skills/aletheia-architecture-evolution/SKILL.md",
    "assets/scaffold/.aletheia/START_HERE.md",
    "assets/scaffold/.aletheia/.gitignore",
    "assets/scaffold/.claude/settings.json",
    "assets/scaffold/BOOTSTRAP.md",
    "assets/scaffold/.aletheia/governance/model_registry.json",
    "assets/scaffold/.aletheia/governance/INTAKE_POLICY.md",
    "assets/scaffold/.aletheia/state/RISK_REGISTER.md",
    "assets/scaffold/.aletheia/state/FRONTIER_BOARD.md",
    "assets/scaffold/.aletheia/state/GLOSSARY.md",
    "assets/scaffold/.aletheia/state/DOMAIN_PROFILE.md",
    "assets/scaffold/.aletheia/contracts/INDEX.md",
    "assets/scaffold/.aletheia/evidence/INDEX.md",
    "assets/scaffold/.aletheia/hypotheses/.gitkeep",
    "assets/scaffold/.aletheia/nodes/ROOT.yaml",
    "assets/scaffold/.aletheia/playbooks/guided_bootstrap.md",
    "assets/scaffold/.aletheia/bin/orient.py",
    "assets/scaffold/.aletheia/bin/context_pack.py",
    "assets/scaffold/.aletheia/bin/model_gate.py",
    "assets/scaffold/.aletheia/bin/validate.py",
    "assets/scaffold/.aletheia/bin/checkpoint.py",
    "assets/scaffold/.aletheia/bin/overview.py",
    "assets/scaffold/.aletheia/bin/bootstrap_finalize.py",
    "assets/scaffold/.aletheia/bin/intake_inventory.py",
    "assets/scaffold/.aletheia/bin/guided_bootstrap.py",
    "assets/scaffold/.aletheia/bin/change_hook.py",
    "assets/scaffold/.aletheia/bin/stop_hook.py",
    "assets/scaffold/.aletheia/templates/DECISION.md",
    "assets/scaffold/.aletheia/templates/EVIDENCE.md",
    "assets/scaffold/.aletheia/templates/RISK.md",
    "assets/scaffold/.aletheia/templates/CONTRACT.md",
    "assets/scaffold/.aletheia/templates/SESSION_NOTE.md",
    "assets/scaffold/.aletheia/templates/HYPOTHESIS.md",
    "assets/scaffold/.aletheia/templates/NODE.yaml",
    "assets/scaffold/.aletheia/templates/TASK_CARD.md",
    "assets/scaffold/.aletheia/templates/AGENT_RUN.json",
    "assets/scaffold/.aletheia/templates/BOOTSTRAP_IMPORT_REPORT.md",
    "assets/scaffold/.aletheia/templates/BOOTSTRAP_INTAKE_MANIFEST.yaml",
]

PACKAGE_DIRS = [
    ".codex-plugin",
    "skills",
    "assets",
    "scripts",
    "README.zh-CN.md",
]


def copy_release(root: Path, output: Path) -> Path:
    release_root = output / "aletheia-os-plugin"
    if release_root.exists():
        shutil.rmtree(release_root)
    release_root.mkdir(parents=True)

    for rel in PACKAGE_DIRS:
        src = root / rel
        dst = release_root / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    return release_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and package the AletheiaOS Codex plugin.")
    parser.add_argument("--output", type=Path, help="Directory where release package should be written")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    missing = [rel for rel in REQUIRED if not (root / rel).exists()]
    if missing:
        for rel in missing:
            print(f"missing: {rel}")
        return 1

    manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "aletheia-os":
        print("plugin manifest name must be aletheia-os")
        return 1

    print("plugin package smoke check passed")
    if args.output:
        release_root = copy_release(root, args.output.resolve())
        print(f"release package written: {release_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
