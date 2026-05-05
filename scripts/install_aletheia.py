#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from shlex import join as shell_join


PLUGIN_NAME = "aletheia-os"
DEFAULT_SOURCE = "zynthium/aletheia-os"
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CODEX_AGENTS_ROOT = PLUGIN_ROOT / "codex-agents"


def run_command(command: list[str], cwd: Path | None, dry_run: bool) -> int:
    if cwd:
        print(f"cwd: {cwd}")
    print(f"$ {shell_join(command)}")
    if dry_run:
        return 0

    try:
        completed = subprocess.run(command, cwd=cwd, check=False)
    except FileNotFoundError:
        print(f"missing executable: {command[0]}", file=sys.stderr)
        return 127
    return completed.returncode


def copy_codex_agents(destination: Path, dry_run: bool) -> int:
    print(f"copy codex agents: {CODEX_AGENTS_ROOT} -> {destination}")
    if dry_run:
        return 0
    if not CODEX_AGENTS_ROOT.exists():
        print(f"missing codex agents directory: {CODEX_AGENTS_ROOT}", file=sys.stderr)
        return 1

    destination.mkdir(parents=True, exist_ok=True)
    for source in sorted(CODEX_AGENTS_ROOT.glob("*.toml")):
        shutil.copy2(source, destination / source.name)
    return 0


def codex_agents_destination(scope: str, project: Path) -> Path:
    if scope == "user":
        return Path.home() / ".codex" / "agents"
    return project / ".codex" / "agents"


def install_claude(source: str, scope: str, project: Path, dry_run: bool) -> int:
    cwd = project if scope in {"project", "local"} else None
    commands = [
        ["claude", "plugin", "marketplace", "add", source, "--scope", scope],
        ["claude", "plugin", "install", f"{PLUGIN_NAME}@{PLUGIN_NAME}", "--scope", scope],
    ]
    for command in commands:
        status = run_command(command, cwd, dry_run)
        if status != 0:
            return status
    return 0


def install_codex(source: str, scope: str, project: Path, dry_run: bool) -> int:
    status = run_command(["codex", "plugin", "marketplace", "add", source], None, dry_run)
    if status != 0:
        return status

    if scope == "user":
        print("Open Codex /plugins and enable aletheia-os from the AletheiaOS marketplace.")
    else:
        print(
            "Open Codex /plugins in the target project and enable aletheia-os from the "
            "AletheiaOS marketplace."
        )
        print("Codex CLI currently registers marketplaces but does not expose non-interactive plugin install.")
    return 0


def initialize_project(project: Path, dry_run: bool) -> int:
    command = [sys.executable, str(PLUGIN_ROOT / "scripts" / "init_aletheia.py"), str(project)]
    print("initialize AletheiaOS truth layer")
    return run_command(command, None, dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install AletheiaOS for Claude Code and Codex.")
    parser.add_argument("--host", choices=["claude", "codex", "both"], default="both")
    parser.add_argument("--scope", choices=["user", "project", "local"], default="user")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Target project for project/local scope")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Marketplace source repo, URL, or local path")
    parser.add_argument("--with-codex-agents", action="store_true", help="Copy optional Codex agent profiles")
    parser.add_argument("--init-project", action="store_true", help="Initialize .aletheia/ in the target project")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing them")
    args = parser.parse_args()

    project = args.project.resolve()
    if args.scope in {"project", "local"} or args.init_project:
        if not project.exists() or not project.is_dir():
            parser.error(f"project must be an existing directory: {project}")

    hosts = ["claude", "codex"] if args.host == "both" else [args.host]
    for host in hosts:
        if host == "claude":
            status = install_claude(args.source, args.scope, project, args.dry_run)
        else:
            status = install_codex(args.source, args.scope, project, args.dry_run)
        if status != 0:
            return status

    if args.with_codex_agents:
        status = copy_codex_agents(codex_agents_destination(args.scope, project), args.dry_run)
        if status != 0:
            return status

    if args.init_project:
        status = initialize_project(project, args.dry_run)
        if status != 0:
            return status

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
