#!/usr/bin/env python3
"""AI model capability gate and attribution recorder.

Uses only the Python standard library. The gate is a project-governance
mechanism, not a cryptographic security boundary.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "aletheia_os/model_registry.json"
RUNTIME_DIR = ROOT / ".aios_runtime"
SESSION_MODEL_PATH = RUNTIME_DIR / "session_model.json"
CURRENT_RUN_PATH = RUNTIME_DIR / "current_agent_run.json"
AGENT_RUNS_DIR = ROOT / "aletheia_os/agent_runs"

TIER_ORDER = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_ONLY_BASH_PREFIXES = (
    "pwd",
    "ls",
    "find ",
    "rg ",
    "grep ",
    "cat ",
    "head ",
    "tail ",
    "sed -n",
    "git status",
    "git diff",
    "git log",
    "python3 scripts/aios_orient.py",
    "python scripts/aios_orient.py",
    "python3 scripts/aios_context_pack.py",
    "python scripts/aios_context_pack.py",
    "python3 scripts/aios_validate.py",
    "python scripts/aios_validate.py",
)
MODEL_GATE_COMMAND_MARKERS = (
    "scripts/aios_model_gate.py",
    "python3 scripts/aios_model_gate.py",
    "python scripts/aios_model_gate.py",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def shell_export(name: str, value: str) -> str:
    return f"export {name}={shlex.quote(value)}\n"


def normalize_model_key(provider: str | None, model_id: str | None) -> list[str]:
    keys: list[str] = []
    if provider and model_id:
        keys.append(f"{provider}/{model_id}")
    if model_id:
        keys.append(model_id)
    return keys


def detect_provider(args: argparse.Namespace, payload: dict[str, Any] | None = None) -> str:
    if args.provider:
        return args.provider
    if payload and payload.get("model") and payload.get("hook_event_name") in {"SessionStart", "PreToolUse"}:
        return "anthropic"
    return (
        os.environ.get("AIOS_AGENT_PROVIDER")
        or os.environ.get("AIOS_PROVIDER")
        or os.environ.get("LLM_PROVIDER")
        or "unknown"
    )


def detect_model(args: argparse.Namespace, payload: dict[str, Any] | None = None) -> str:
    if args.model:
        return args.model
    if payload and payload.get("model"):
        return str(payload["model"])
    for key in ["AIOS_MODEL_ID", "AIOS_MODEL", "ANTHROPIC_MODEL", "CLAUDE_MODEL", "OPENAI_MODEL", "CODEX_MODEL", "LLM_MODEL", "MODEL"]:
        if os.environ.get(key):
            return os.environ[key]
    session = load_json(SESSION_MODEL_PATH, {})
    if session.get("model_id"):
        return str(session["model_id"])
    return "unknown"


def detect_tool(args: argparse.Namespace, payload: dict[str, Any] | None = None) -> str:
    if args.agent_tool:
        return args.agent_tool
    if payload and payload.get("hook_event_name"):
        return "claude_code"
    return os.environ.get("AIOS_AGENT_TOOL") or os.environ.get("AIOS_TOOL") or "unknown"


def registered_entry(registry: dict[str, Any], provider: str, model_id: str) -> tuple[str, dict[str, Any] | None]:
    deny = registry.get("denylist", {}) or {}
    for key in normalize_model_key(provider, model_id):
        if key in deny:
            return "denied", deny[key]

    registered = registry.get("registered_models", {}) or {}
    for key in normalize_model_key(provider, model_id):
        if key in registered:
            entry = registered[key]
            status = str(entry.get("status", "allowed"))
            if status in {"example_disabled", "disabled", "denied", "deny"}:
                return status, entry
            return "registered", entry
    return "unknown", None


def tier_rank(tier: str | None) -> int:
    return TIER_ORDER.get(str(tier or "C0"), -1)


def infer_tier(
    registry: dict[str, Any],
    provider: str,
    model_id: str,
    args: argparse.Namespace,
) -> tuple[str, str, dict[str, Any] | None]:
    status, entry = registered_entry(registry, provider, model_id)
    if status == "registered" and entry:
        return str(entry.get("tier", "C0")), status, entry
    if status in {"denied", "deny", "disabled", "example_disabled"}:
        return "C0", status, entry

    operator_approved = args.operator_approved or os.environ.get("AIOS_OPERATOR_APPROVED") == "1"
    allow_self = bool((registry.get("default_policy", {}) or {}).get("allow_self_attested_tier", False))
    requested_tier = args.tier or os.environ.get("AIOS_MODEL_TIER") or os.environ.get("AIOS_CAPABILITY_TIER")
    if requested_tier and (operator_approved or allow_self):
        return requested_tier, "operator_approved_unregistered" if operator_approved else "self_attested", None
    return "C0", "unknown", None


def evaluate_gate(
    *,
    registry: dict[str, Any],
    provider: str,
    model_id: str,
    agent_tool: str,
    task_class: str,
    objective: str,
    write_intent: bool,
    args: argparse.Namespace,
) -> dict[str, Any]:
    task_classes = registry.get("task_classes", {}) or {}
    default_policy = registry.get("default_policy", {}) or {}
    task = task_classes.get(task_class)
    if task is None:
        task = {
            "min_tier": default_policy.get("unclassified_write_minimum_tier", "C3") if write_intent else "C0",
            "write_allowed": not write_intent,
            "description": "Unclassified task. Writes require explicit classification."
        }

    tier, registry_status, entry = infer_tier(registry, provider, model_id, args)
    min_tier = str(task.get("min_tier", "C0"))
    task_write_allowed = bool(task.get("write_allowed", False))
    operator_approved = args.operator_approved or os.environ.get("AIOS_OPERATOR_APPROVED") == "1"
    require_registered_for_writes = bool(default_policy.get("require_registered_model_for_writes", True))

    reasons: list[str] = []
    allowed = True
    read_only = False

    if registry_status in {"denied", "deny", "disabled", "example_disabled"}:
        allowed = False
        reasons.append(f"model registry status is {registry_status}")

    if write_intent and task_class not in task_classes:
        allowed = False
        reasons.append("write intent requires an explicit task class")

    if write_intent and not task_write_allowed:
        allowed = False
        reasons.append(f"task class {task_class!r} is read-only")

    if tier_rank(tier) < tier_rank(min_tier):
        allowed = False
        reasons.append(f"model tier {tier} is below required tier {min_tier} for task class {task_class}")

    if write_intent and require_registered_for_writes and registry_status not in {"registered", "operator_approved_unregistered"}:
        allowed = False
        reasons.append("model is not registered or operator-approved for writes")

    if not allowed and not write_intent and registry_status == "unknown":
        read_only = True

    if allowed:
        gate_status = "allowed"
    elif read_only or not write_intent:
        gate_status = "read_only"
    else:
        gate_status = "denied"

    return {
        "provider": provider,
        "model_id": model_id,
        "agent_tool": agent_tool,
        "capability_tier": tier,
        "task_class": task_class,
        "objective": objective,
        "gate_status": gate_status,
        "required_min_tier": min_tier,
        "model_registry_status": registry_status,
        "write_intent": write_intent,
        "operator_approved": bool(operator_approved),
        "allowed": gate_status == "allowed",
        "reasons": reasons,
        "registry_entry": entry or {},
    }


def new_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"RUN-{ts}-{secrets.token_hex(3)}"


def record_run(gate: dict[str, Any], metadata_source: str) -> dict[str, Any]:
    run = {
        "run_id": new_run_id(),
        "created_at": utc_now(),
        "provider": gate["provider"],
        "model_id": gate["model_id"],
        "agent_tool": gate["agent_tool"],
        "capability_tier": gate["capability_tier"],
        "task_class": gate["task_class"],
        "objective": gate["objective"],
        "gate_status": gate["gate_status"],
        "required_min_tier": gate["required_min_tier"],
        "model_registry_status": gate["model_registry_status"],
        "write_intent": gate["write_intent"],
        "metadata_source": metadata_source,
        "operator_approved": gate["operator_approved"],
        "reasons": gate["reasons"],
    }
    save_json(CURRENT_RUN_PATH, run)
    AGENT_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    save_json(AGENT_RUNS_DIR / f"{run['run_id']}.json", run)
    return run


def load_current_run() -> dict[str, Any] | None:
    data = load_json(CURRENT_RUN_PATH, None)
    if isinstance(data, dict):
        return data
    return None


def bash_is_read_only(command: str) -> bool:
    normalized = command.strip()
    if not normalized:
        return True
    if any(marker in normalized for marker in MODEL_GATE_COMMAND_MARKERS):
        return True
    if any(normalized == p.rstrip() or normalized.startswith(p) for p in READ_ONLY_BASH_PREFIXES):
        # Disallow obvious shell redirection or command chaining in commands classified as read-only.
        if any(token in normalized for token in [">", "| tee", "&& rm", "; rm", "&& mv", "; mv", "&& cp", "; cp"]):
            return False
        return True
    return False


def tool_has_write_intent(payload: dict[str, Any]) -> bool:
    tool = str(payload.get("tool_name", ""))
    if tool in WRITE_TOOLS:
        return True
    if tool == "Bash":
        command = str((payload.get("tool_input") or {}).get("command", ""))
        return not bash_is_read_only(command)
    return False


def session_start(args: argparse.Namespace) -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    provider = detect_provider(args, payload)
    model_id = detect_model(args, payload)
    agent_tool = detect_tool(args, payload)
    session = {
        "created_at": utc_now(),
        "provider": provider,
        "model_id": model_id,
        "agent_tool": agent_tool,
        "source": payload.get("source"),
        "session_id": payload.get("session_id"),
        "metadata_source": "claude_session_start_hook",
    }
    save_json(SESSION_MODEL_PATH, session)

    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(shell_export("AIOS_AGENT_PROVIDER", provider))
            f.write(shell_export("AIOS_MODEL_ID", model_id))
            f.write(shell_export("AIOS_AGENT_TOOL", agent_tool))

    context = (
        "AIOS model governance active. Detected model: "
        f"provider={provider}, model_id={model_id}, tool={agent_tool}. "
        "Before durable writes, run `python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective \"...\"`. "
        "Unknown or unregistered models are read-only by default."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }, ensure_ascii=False))
    return 0


def pre_tool_use(args: argparse.Namespace) -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    write_intent = tool_has_write_intent(payload)
    if not write_intent:
        return 0

    tool = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input") or {}
    if tool == "Bash" and any(marker in str(tool_input.get("command", "")) for marker in MODEL_GATE_COMMAND_MARKERS):
        return 0

    current = load_current_run()
    if not current:
        reason = (
            "AIOS model gate blocked a write-capable tool call because no current agent run is recorded. "
            "Run `python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective \"...\"` first."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }, ensure_ascii=False))
        return 0

    if current.get("gate_status") != "allowed":
        reason = (
            "AIOS model gate blocked a write-capable tool call. "
            f"Current run {current.get('run_id')} has gate_status={current.get('gate_status')}; "
            f"model={current.get('provider')}/{current.get('model_id')}; "
            f"tier={current.get('capability_tier')}; task_class={current.get('task_class')}."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }, ensure_ascii=False))
        return 0

    return 0


def cli_gate(args: argparse.Namespace) -> int:
    registry = load_json(REGISTRY_PATH, {})
    provider = detect_provider(args)
    model_id = detect_model(args)
    agent_tool = detect_tool(args)
    task_class = args.task_class or os.environ.get("AIOS_TASK_CLASS") or "orientation"
    objective = args.objective or os.environ.get("AIOS_OBJECTIVE") or "unspecified"
    write_intent = bool(args.write_intent or task_class != "orientation")

    gate = evaluate_gate(
        registry=registry,
        provider=provider,
        model_id=model_id,
        agent_tool=agent_tool,
        task_class=task_class,
        objective=objective,
        write_intent=write_intent,
        args=args,
    )

    run: dict[str, Any] | None = None
    if args.record:
        run = record_run(gate, metadata_source="manual_or_environment")

    if args.json:
        output = dict(gate)
        if run:
            output["run_id"] = run["run_id"]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print("AIOS model gate")
        print(f"  provider: {gate['provider']}")
        print(f"  model_id: {gate['model_id']}")
        print(f"  tool: {gate['agent_tool']}")
        print(f"  task_class: {gate['task_class']}")
        print(f"  capability_tier: {gate['capability_tier']}")
        print(f"  required_min_tier: {gate['required_min_tier']}")
        print(f"  registry_status: {gate['model_registry_status']}")
        print(f"  write_intent: {gate['write_intent']}")
        print(f"  gate_status: {gate['gate_status']}")
        if run:
            print(f"  run_id: {run['run_id']}")
        if gate["reasons"]:
            print("  reasons:")
            for reason in gate["reasons"]:
                print(f"    - {reason}")

    if gate["gate_status"] == "allowed":
        return 0
    if gate["gate_status"] == "read_only" and not write_intent:
        return 0
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hook-mode", choices=["sessionstart", "pretooluse"], default=None)
    parser.add_argument("--task-class", default=None)
    parser.add_argument("--objective", default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--agent-tool", default=None)
    parser.add_argument("--tier", default=None, help="operator-supplied tier for approved unregistered models")
    parser.add_argument("--operator-approved", action="store_true", help="operator has approved this unregistered model for the declared tier")
    parser.add_argument("--write-intent", action="store_true", help="force write-intent evaluation")
    parser.add_argument("--record", action="store_true", help="write current agent run and durable agent_runs record")
    parser.add_argument("--json", action="store_true", help="print JSON result for CLI use")
    args = parser.parse_args()

    try:
        if args.hook_mode == "sessionstart":
            return session_start(args)
        if args.hook_mode == "pretooluse":
            return pre_tool_use(args)
        return cli_gate(args)
    except RuntimeError as exc:
        if args.hook_mode == "pretooluse":
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": str(exc),
                }
            }, ensure_ascii=False))
            return 0
        print(f"AIOS model gate error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
