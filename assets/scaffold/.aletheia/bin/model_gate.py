#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_POLICY = {
    "unknown_model_policy": "read_only",
    "require_registered_model_for_writes": True,
    "require_agent_run_for_checkpoint": True,
    "allow_self_attested_tier": False,
    "minimum_tier_for_bootstrap_finalize": "C3",
    "minimum_tier_for_checkpoint": "C2",
    "unclassified_write_minimum_tier": "C3",
}

DEFAULT_TASK_CLASSES = {
    "orientation": {"min_tier": "C0", "write_allowed": False},
    "documentation_noncritical": {"min_tier": "C1", "write_allowed": True},
    "mechanical_implementation": {"min_tier": "C2", "write_allowed": True},
    "bugfix_local": {"min_tier": "C2", "write_allowed": True},
    "cross_boundary_refactor": {"min_tier": "C3", "write_allowed": True},
    "research_design": {"min_tier": "C3", "write_allowed": True},
    "hypothesis_update": {"min_tier": "C3", "write_allowed": True},
    "architecture_decision": {"min_tier": "C3", "write_allowed": True},
    "production_safety_critical": {"min_tier": "C4", "write_allowed": True},
    "root_theory_revision": {"min_tier": "C4", "write_allowed": True},
    "checkpoint": {"min_tier": "C2", "write_allowed": True},
    "bootstrap_finalize": {"min_tier": "C3", "write_allowed": True},
}

TIER_RANK = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_ONLY_BASH_PREFIXES = (
    "git status",
    "git diff",
    "git log",
    "git show",
    "ls",
    "pwd",
    "sed ",
    "rg ",
    "find ",
    "python3 .aletheia/bin/orient.py",
    "python3 .aletheia/bin/context_pack.py",
    "python3 .aletheia/bin/validate.py",
)
SHELL_CONTROL_TOKENS = ("&&", "||", ";", "|", ">", "<", "\n", "`", "$(")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_registry(root: Path) -> dict[str, Any]:
    registry = load_json(root / ".aletheia" / "governance" / "model_registry.json", {})
    if not isinstance(registry, dict):
        registry = {}
    registry.setdefault("default_policy", DEFAULT_POLICY.copy())
    registry.setdefault("task_classes", DEFAULT_TASK_CLASSES.copy())
    registry.setdefault("capability_tiers", {tier: {"rank": rank} for tier, rank in TIER_RANK.items()})
    registry.setdefault("registered_models", {})
    registry.setdefault("denylist", [])
    return registry


def candidate_model_keys(provider: str, model_id: str) -> list[str]:
    keys = []
    if model_id:
        keys.append(model_id)
    if provider and model_id:
        keys.append(f"{provider}/{model_id}")
    return keys


def registered_entry(registry: dict[str, Any], provider: str, model_id: str) -> tuple[str, dict[str, Any] | None]:
    registered = registry.get("registered_models", {}) or {}
    for key in candidate_model_keys(provider, model_id):
        entry = registered.get(key)
        if isinstance(entry, dict):
            return key, entry
    for key, entry in registered.items():
        if not isinstance(entry, dict):
            continue
        aliases = entry.get("aliases", []) if isinstance(entry.get("aliases", []), list) else []
        if any(alias in candidate_model_keys(provider, model_id) for alias in aliases):
            return key, entry
    return "", None


def tier_rank(tier: str | None) -> int:
    return TIER_RANK.get(str(tier or ""), -1)


def detect_provider(args: argparse.Namespace, payload: dict[str, Any] | None = None) -> str:
    if args.provider:
        return args.provider
    if payload and payload.get("model"):
        model = str(payload["model"])
        if model.startswith("claude"):
            return "anthropic"
        if model.startswith("gpt") or model.startswith("o"):
            return "openai"
    return os.environ.get("AIOS_AGENT_PROVIDER") or os.environ.get("AIOS_PROVIDER") or "unknown"


def detect_model(args: argparse.Namespace, payload: dict[str, Any] | None = None) -> str:
    if args.model_id:
        return args.model_id
    if args.model:
        return args.model
    if payload and payload.get("model"):
        return str(payload["model"])
    for key in ["AIOS_MODEL_ID", "AIOS_MODEL", "ANTHROPIC_MODEL", "CLAUDE_MODEL", "OPENAI_MODEL", "CODEX_MODEL", "MODEL"]:
        value = os.environ.get(key)
        if value:
            return value
    return "unknown"


def detect_tool(args: argparse.Namespace, payload: dict[str, Any] | None = None) -> str:
    if args.agent_tool:
        return args.agent_tool
    if payload and payload.get("session_id"):
        return "claude-code"
    return os.environ.get("AIOS_AGENT_TOOL") or os.environ.get("AIOS_TOOL") or "unknown"


def denied_model_ids(registry: dict[str, Any]) -> set[str]:
    denied = {"unknown"}
    for item in registry.get("denylist", []) or []:
        if isinstance(item, str):
            denied.add(item)
        elif isinstance(item, dict) and item.get("model_id"):
            denied.add(str(item["model_id"]))
    return denied


def resolve_tier(
    registry: dict[str, Any],
    provider: str,
    model_id: str,
    requested_tier: str | None,
    operator_approved: bool,
) -> tuple[str, str]:
    key, entry = registered_entry(registry, provider, model_id)
    if entry:
        return str(entry.get("tier", "unknown")), f"registered:{key}"
    if operator_approved and requested_tier:
        return requested_tier, "operator_approved"
    allow_self = bool((registry.get("default_policy", {}) or {}).get("allow_self_attested_tier", False))
    if allow_self and requested_tier:
        return requested_tier, "self_attested"
    if requested_tier:
        return "unknown", "self_attested_rejected"
    return "unknown", "unknown"


def evaluate_gate(args: argparse.Namespace, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root()
    registry = load_registry(root)
    task_classes = registry.get("task_classes", DEFAULT_TASK_CLASSES) or DEFAULT_TASK_CLASSES
    task_class = args.task_class or os.environ.get("AIOS_TASK_CLASS") or "orientation"
    if task_class not in task_classes:
        raise RuntimeError(f"unknown task class: {task_class}")

    provider = detect_provider(args, payload)
    model_id = detect_model(args, payload)
    agent_tool = detect_tool(args, payload)
    requested_tier = args.tier or args.capability_tier or os.environ.get("AIOS_MODEL_TIER") or os.environ.get("AIOS_CAPABILITY_TIER")
    operator_approved = bool(args.operator_approved or os.environ.get("AIOS_OPERATOR_APPROVED") == "1")
    actual_tier, registry_status = resolve_tier(registry, provider, model_id, requested_tier, operator_approved)
    policy = task_classes[task_class]
    required = str(policy.get("min_tier", "C0"))
    denied = model_id in denied_model_ids(registry)
    allowed = tier_rank(actual_tier) >= tier_rank(required) and not denied
    if denied:
        reason = "model is denied or unknown"
    elif registry_status == "self_attested_rejected":
        reason = "self-attested tier requires operator approval or registry entry"
        allowed = False
    elif not allowed:
        reason = f"requires tier {required}, got {actual_tier}"
    else:
        reason = "allowed"

    return {
        "run_id": f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(3)}",
        "provider": provider,
        "model_id": model_id,
        "agent_tool": agent_tool,
        "capability_tier": actual_tier,
        "task_class": task_class,
        "required_min_tier": required,
        "registry_status": registry_status,
        "write_allowed": bool(policy.get("write_allowed", False)),
        "gate_status": "allowed" if allowed else "rejected",
        "reason": reason,
        "objective": args.objective or os.environ.get("AIOS_OBJECTIVE") or "unspecified",
        "recorded_at": utc_now(),
    }


def record_run(root: Path, gate: dict[str, Any]) -> None:
    agent_runs = root / ".aletheia" / "agent_runs"
    runtime = root / ".aletheia" / "runtime"
    agent_runs.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    write_json(agent_runs / f"{gate['run_id']}.json", gate)
    write_json(runtime / "current_agent_run.json", gate)


def load_current_run(root: Path) -> dict[str, Any] | None:
    data = load_json(root / ".aletheia" / "runtime" / "current_agent_run.json", None)
    return data if isinstance(data, dict) else None


def bash_is_read_only(command: str) -> bool:
    stripped = command.strip()
    return any(stripped == prefix.strip() or stripped.startswith(prefix) for prefix in READ_ONLY_BASH_PREFIXES)


def payload_has_write_intent(payload: dict[str, Any]) -> bool:
    tool = payload.get("tool_name")
    if tool in WRITE_TOOLS:
        return True
    if tool == "Bash":
        command = str((payload.get("tool_input") or {}).get("command", ""))
        return not bash_is_read_only(command)
    return False


def standalone_model_gate_record_command(command: str) -> bool:
    stripped = command.strip()
    if any(token in stripped for token in SHELL_CONTROL_TOKENS):
        return False
    try:
        parts = shlex.split(stripped)
    except ValueError:
        return False
    if len(parts) < 3:
        return False
    if parts[0] != "python3" or parts[1] != ".aletheia/bin/model_gate.py":
        return False
    if "--hook-mode" in parts:
        return False
    return "--record" in parts


def payload_is_standalone_model_gate_record(payload: dict[str, Any]) -> bool:
    if payload.get("tool_name") != "Bash":
        return False
    command = str((payload.get("tool_input") or {}).get("command", ""))
    return standalone_model_gate_record_command(command)


def hook_deny(reason: str) -> int:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


def session_start(args: argparse.Namespace) -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    gate = evaluate_gate(args, payload)
    record_run(repo_root(), gate)
    print(
        "AletheiaOS model governance active. "
        f"Detected model: {gate['provider']}/{gate['model_id']} tier={gate['capability_tier']} gate={gate['gate_status']}"
    )
    return 0


def pre_tool_use(args: argparse.Namespace) -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    if not payload_has_write_intent(payload):
        return 0
    if args.task_class:
        registry = load_registry(repo_root())
        task_classes = registry.get("task_classes", DEFAULT_TASK_CLASSES) or DEFAULT_TASK_CLASSES
        if args.task_class not in task_classes:
            return hook_deny(f"unknown task class: {args.task_class}")
    if payload_is_standalone_model_gate_record(payload):
        return 0
    current = load_current_run(repo_root())
    if not current:
        command = str((payload.get("tool_input") or {}).get("command", ""))
        if "model_gate.py" in command:
            return hook_deny(
                "AletheiaOS model gate blocked this command. Before a current agent run exists, "
                "only a standalone model gate record command is allowed."
            )
        return hook_deny("AletheiaOS model gate blocked a write-capable tool call because no current agent run is recorded.")
    if current.get("gate_status") != "allowed":
        return hook_deny(f"AletheiaOS model gate blocked a write-capable tool call: {current.get('reason', 'gate rejected')}")
    if current.get("write_allowed") is not True:
        return hook_deny(
            "AletheiaOS model gate blocked a write-capable tool call because "
            f"task_class={current.get('task_class', 'unknown')} does not allow write-capable tool calls."
        )
    return 0


def cli_gate(args: argparse.Namespace) -> int:
    gate = evaluate_gate(args)
    if args.record:
        record_run(repo_root(), gate)
    if args.json:
        print(json.dumps(gate, indent=2))
    else:
        print("AIOS model gate")
        for key in [
            "provider",
            "model_id",
            "task_class",
            "capability_tier",
            "required_min_tier",
            "registry_status",
            "write_allowed",
            "gate_status",
            "reason",
            "run_id",
        ]:
            print(f"  {key}: {gate[key]}")
    return 0 if gate["gate_status"] == "allowed" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AletheiaOS model gate.")
    parser.add_argument("--hook-mode", choices=["sessionstart", "pretooluse"], default=None)
    parser.add_argument("--task-class", default=None)
    parser.add_argument("--objective", default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--agent-tool", default=None)
    parser.add_argument("--tier", default=None)
    parser.add_argument("--capability-tier", default=None)
    parser.add_argument("--operator-approved", action="store_true")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        if args.hook_mode == "sessionstart":
            return session_start(args)
        if args.hook_mode == "pretooluse":
            return pre_tool_use(args)
        return cli_gate(args)
    except RuntimeError as exc:
        if args.hook_mode == "pretooluse":
            return hook_deny(str(exc))
        print(f"AIOS model gate error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
