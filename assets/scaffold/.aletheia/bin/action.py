#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ACTIONS_PATH = ".aletheia/governance/actions.json"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_registry(root: Path) -> dict[str, Any]:
    path = root / ACTIONS_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"action registry invalid: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("actions"), list):
        raise SystemExit("action registry invalid: expected object with actions list")
    return data


def find_action(registry: dict[str, Any], action_id: str) -> dict[str, Any]:
    for action in registry["actions"]:
        if isinstance(action, dict) and action.get("id") == action_id:
            return action
    raise SystemExit(f"unknown action: {action_id}")


def parse_arg(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"invalid --arg value, expected key=value: {value}")
        key, arg_value = value.split("=", 1)
        if not key:
            raise SystemExit(f"invalid --arg value, empty key: {value}")
        parsed[key] = arg_value
    return parsed


def command_for(action: dict[str, Any], args: dict[str, str] | None = None) -> list[str]:
    command = action.get("command")
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command) or not command:
        raise SystemExit(f"action has invalid command: {action.get('id')}")
    resolved: list[str] = []
    args = args or {}
    for part in command:
        if part.startswith("{{") and part.endswith("}}"):
            key = part[2:-2]
            if key not in args:
                raise SystemExit(f"action requires --arg {key}=...")
            resolved.append(args[key])
            continue
        resolved.append(part)
    if resolved[0] == "python3":
        resolved[0] = sys.executable
    return resolved


def emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def emit_action_markdown(action: dict[str, Any]) -> None:
    print(f"# {action['title']}")
    print()
    print(f"- id: {action['id']}")
    print(f"- intent: {action['intent']}")
    print(f"- risk: {action['risk']}")
    print(f"- command: `{' '.join(action['command'])}`")


def list_actions(registry: dict[str, Any], json_output: bool) -> int:
    payload = {
        "schema_version": registry.get("schema_version", 1),
        "actions": registry["actions"],
    }
    if json_output:
        emit_json(payload)
        return 0
    print("# AletheiaOS Actions")
    print()
    for action in registry["actions"]:
        print(f"- `{action['id']}` ({action['risk']}): {action['title']}")
    return 0


def explain_action(registry: dict[str, Any], action_id: str, json_output: bool) -> int:
    action = find_action(registry, action_id)
    if json_output:
        emit_json({"schema_version": registry.get("schema_version", 1), "action": action})
        return 0
    emit_action_markdown(action)
    return 0


def next_actions(registry: dict[str, Any], json_output: bool) -> int:
    recommended = registry.get("recommended_actions", [])
    if not isinstance(recommended, list) or not all(isinstance(action_id, str) for action_id in recommended):
        raise SystemExit("action registry invalid: recommended_actions must be a list of strings")
    actions = [find_action(registry, action_id) for action_id in recommended]
    payload = {
        "schema_version": registry.get("schema_version", 1),
        "recommended_actions": recommended,
        "actions": actions,
    }
    if json_output:
        emit_json(payload)
        return 0
    print("# Recommended AletheiaOS Actions")
    print()
    for action in actions:
        print(f"- `{action['id']}` ({action['risk']}): {action['title']}")
    return 0


def run_action(
    root: Path,
    registry: dict[str, Any],
    action_id: str,
    json_output: bool,
    action_args: dict[str, str],
    confirm_risk: bool,
) -> int:
    action = find_action(registry, action_id)
    risk = action.get("risk")
    if risk != "read-only" and not confirm_risk:
        print(f"action {action_id} has {risk} risk and requires --confirm-risk", file=sys.stderr)
        return 2
    command = command_for(action, action_args)
    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    expected = action.get("verification", {}).get("returncode", 0)
    passed = result.returncode == expected
    payload = {
        "schema_version": registry.get("schema_version", 1),
        "action_id": action_id,
        "command": command,
        "result": {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
        "verification": {
            "expected_returncode": expected,
            "passed": passed,
        },
    }
    if json_output:
        emit_json(payload)
    else:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    return 0 if passed else result.returncode or 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover and run AletheiaOS agent actions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available actions.")
    list_parser.add_argument("--json", action="store_true", help="Emit machine-readable action list.")

    explain_parser = subparsers.add_parser("explain", help="Explain one action.")
    explain_parser.add_argument("action_id")
    explain_parser.add_argument("--json", action="store_true", help="Emit machine-readable action details.")

    run_parser = subparsers.add_parser("run", help="Run one action.")
    run_parser.add_argument("action_id")
    run_parser.add_argument("--arg", action="append", default=[], help="Provide action input as key=value.")
    run_parser.add_argument("--confirm-risk", action="store_true", help="Allow writes-state, admin, or checkpoint actions.")
    run_parser.add_argument("--json", action="store_true", help="Emit machine-readable run result.")

    next_parser = subparsers.add_parser("next", help="Show recommended next actions.")
    next_parser.add_argument("--json", action="store_true", help="Emit machine-readable recommendations.")

    args = parser.parse_args()
    root = repo_root()
    registry = load_registry(root)
    if args.command == "list":
        return list_actions(registry, args.json)
    if args.command == "explain":
        return explain_action(registry, args.action_id, args.json)
    if args.command == "run":
        return run_action(root, registry, args.action_id, args.json, parse_arg(args.arg), args.confirm_risk)
    if args.command == "next":
        return next_actions(registry, args.json)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
