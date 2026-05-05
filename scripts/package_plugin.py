#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


EXPECTED_PLUGIN_NAME = "aletheia-os"
EXPECTED_REPOSITORY = "https://github.com/zynthium/aletheia-os"
EXPECTED_DEVELOPER = "zynthium"

REQUIRED = [
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
    "README.zh-CN.md",
    "agents/truth-auditor.md",
    "agents/evidence-curator.md",
    "agents/architecture-reviewer.md",
    "codex-agents/truth-auditor.toml",
    "codex-agents/evidence-curator.toml",
    "codex-agents/architecture-reviewer.toml",
    "scripts/aletheia_scaffold.py",
    "scripts/install_aletheia.py",
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
    "assets/scaffold/.aletheia/templates/TRUTH_INVENTORY_REPORT.md",
    "assets/scaffold/.aletheia/templates/TRUTH_INTAKE_MANIFEST.yaml",
]

PACKAGE_DIRS = [
    ".codex-plugin",
    ".claude-plugin",
    ".agents",
    "agents",
    "codex-agents",
    "skills",
    "assets",
    "scripts",
    "README.zh-CN.md",
]


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("name") != EXPECTED_PLUGIN_NAME:
        errors.append(f"plugin manifest name must be {EXPECTED_PLUGIN_NAME}")

    if manifest.get("skills") != "./skills/":
        errors.append('plugin manifest must set skills to "./skills/"')

    author = manifest.get("author")
    if not isinstance(author, dict) or author.get("name") != EXPECTED_DEVELOPER:
        errors.append(f"plugin manifest author.name must be {EXPECTED_DEVELOPER}")

    if manifest.get("homepage") != EXPECTED_REPOSITORY:
        errors.append(f"plugin manifest homepage must be {EXPECTED_REPOSITORY}")

    if manifest.get("repository") != EXPECTED_REPOSITORY:
        errors.append(f"plugin manifest repository must be {EXPECTED_REPOSITORY}")

    for key in ["author", "homepage", "repository", "license", "keywords"]:
        if key not in manifest:
            errors.append(f"plugin manifest missing field: {key}")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin manifest missing interface block")
        return errors

    if interface.get("developerName") != EXPECTED_DEVELOPER:
        errors.append(f"plugin manifest interface.developerName must be {EXPECTED_DEVELOPER}")

    if interface.get("websiteURL") != EXPECTED_REPOSITORY:
        errors.append(f"plugin manifest interface.websiteURL must be {EXPECTED_REPOSITORY}")

    for key in [
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "websiteURL",
        "defaultPrompt",
    ]:
        if key not in interface:
            errors.append(f"plugin manifest interface missing field: {key}")

    default_prompt = interface.get("defaultPrompt")
    if not isinstance(default_prompt, list):
        errors.append("plugin manifest interface.defaultPrompt must be an array")
    elif len(default_prompt) > 3:
        errors.append("plugin manifest interface.defaultPrompt must contain at most 3 prompts")
    elif not all(isinstance(item, str) for item in default_prompt):
        errors.append("plugin manifest interface.defaultPrompt must contain only strings")
    elif any(len(item) > 128 for item in default_prompt):
        errors.append("plugin manifest interface.defaultPrompt entries must be 128 characters or shorter")

    return errors


def validate_claude_manifest(codex_manifest: dict, claude_manifest: dict) -> list[str]:
    errors: list[str] = []
    for key in ["name", "version", "description", "author", "homepage", "repository", "license"]:
        if claude_manifest.get(key) != codex_manifest.get(key):
            errors.append(f"Claude plugin manifest field must match Codex manifest: {key}")

    if claude_manifest.get("skills") != "./skills/":
        errors.append('Claude plugin manifest must set skills to "./skills/"')

    return errors


def validate_marketplaces(claude_marketplace: dict, codex_marketplace: dict) -> list[str]:
    errors: list[str] = []
    if claude_marketplace.get("name") != EXPECTED_PLUGIN_NAME:
        errors.append(f"Claude marketplace name must be {EXPECTED_PLUGIN_NAME}")
    claude_plugins = claude_marketplace.get("plugins")
    if not isinstance(claude_plugins, list) or not claude_plugins:
        errors.append("Claude marketplace must include plugins")
    else:
        first = claude_plugins[0]
        if not isinstance(first, dict) or first.get("name") != EXPECTED_PLUGIN_NAME:
            errors.append(f"Claude marketplace plugin name must be {EXPECTED_PLUGIN_NAME}")

    if codex_marketplace.get("name") != EXPECTED_PLUGIN_NAME:
        errors.append(f"Codex marketplace name must be {EXPECTED_PLUGIN_NAME}")
    interface = codex_marketplace.get("interface")
    if not isinstance(interface, dict) or interface.get("displayName") != "AletheiaOS":
        errors.append("Codex marketplace interface.displayName must be AletheiaOS")
    codex_plugins = codex_marketplace.get("plugins")
    if not isinstance(codex_plugins, list) or not codex_plugins:
        errors.append("Codex marketplace must include plugins")
    else:
        first = codex_plugins[0]
        source = first.get("source") if isinstance(first, dict) else None
        policy = first.get("policy") if isinstance(first, dict) else None
        if not isinstance(first, dict) or first.get("name") != EXPECTED_PLUGIN_NAME:
            errors.append(f"Codex marketplace plugin name must be {EXPECTED_PLUGIN_NAME}")
        if not isinstance(source, dict) or source.get("source") != "local" or source.get("path") != "./":
            errors.append('Codex marketplace source must be local "./"')
        if (
            not isinstance(policy, dict)
            or policy.get("installation") != "AVAILABLE"
            or policy.get("authentication") != "ON_INSTALL"
        ):
            errors.append("Codex marketplace policy must be AVAILABLE/ON_INSTALL")
    return errors


def copy_release(root: Path, output: Path, plugin_name: str) -> Path:
    release_root = output / plugin_name
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
    claude_manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    claude_marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    codex_marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    manifest_errors = (
        validate_manifest(manifest)
        + validate_claude_manifest(manifest, claude_manifest)
        + validate_marketplaces(claude_marketplace, codex_marketplace)
    )
    if manifest_errors:
        for error in manifest_errors:
            print(error)
        return 1

    print("plugin package smoke check passed")
    if args.output:
        release_root = copy_release(root, args.output.resolve(), manifest["name"])
        print(f"release package written: {release_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
