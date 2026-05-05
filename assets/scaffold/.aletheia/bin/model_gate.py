#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path


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

TIER_RANK = {
    "C0": 0,
    "C1": 1,
    "C2": 2,
    "C3": 3,
    "C4": 4,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_registry(root: Path) -> dict:
    path = root / ".aletheia" / "governance" / "model_registry.json"
    if not path.exists():
        return {"task_classes": DEFAULT_TASK_CLASSES, "registered_models": {}, "denylist": []}
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry.setdefault("task_classes", DEFAULT_TASK_CLASSES)
    registry.setdefault("registered_models", {})
    registry.setdefault("denylist", [])
    return registry


def make_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"RUN-{stamp}-{secrets.token_hex(3)}"


def resolve_model(registry: dict, provider: str, model_id: str, explicit_tier: str) -> tuple[str, str]:
    if explicit_tier != "unknown":
        return explicit_tier, "explicit"

    candidates = [model_id, f"{provider}/{model_id}"]
    for candidate in candidates:
        registered = registry.get("registered_models", {}).get(candidate)
        if registered:
            return registered.get("tier", "unknown"), registered.get("status", "registered")

    return "unknown", "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AletheiaOS model gate.")
    parser.add_argument("--task-class", required=True)
    parser.add_argument("--objective", default="")
    parser.add_argument("--provider", default=os.environ.get("AIOS_AGENT_PROVIDER", "unknown"))
    parser.add_argument("--model-id", default=os.environ.get("AIOS_MODEL_ID", "unknown"))
    parser.add_argument("--capability-tier", default=os.environ.get("AIOS_CAPABILITY_TIER", "unknown"))
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    registry = load_registry(root)
    task_classes = registry.get("task_classes", DEFAULT_TASK_CLASSES)
    if args.task_class not in task_classes:
        parser.error(f"unknown task class: {args.task_class}")

    denied = {item.get("model_id") for item in registry.get("denylist", []) if isinstance(item, dict)}
    denied.add("unknown")
    policy = task_classes[args.task_class]
    required = policy["min_tier"]
    actual_tier, registry_status = resolve_model(
        registry,
        provider=args.provider,
        model_id=args.model_id,
        explicit_tier=args.capability_tier,
    )
    actual_rank = TIER_RANK.get(actual_tier, -1)
    required_rank = TIER_RANK[required]
    allowed = actual_rank >= required_rank and args.model_id not in denied
    gate_status = "allowed" if allowed else "rejected"
    run_id = make_run_id()

    record = {
        "run_id": run_id,
        "provider": args.provider,
        "model_id": args.model_id,
        "capability_tier": actual_tier,
        "task_class": args.task_class,
        "required_min_tier": required,
        "registry_status": registry_status,
        "write_allowed": policy["write_allowed"],
        "gate_status": gate_status,
        "objective": args.objective,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }

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
        "run_id",
    ]:
        print(f"  {key}: {record[key]}")

    if args.record:
        agent_runs = root / ".aletheia" / "agent_runs"
        runtime = root / ".aletheia" / "runtime"
        agent_runs.mkdir(parents=True, exist_ok=True)
        runtime.mkdir(parents=True, exist_ok=True)
        (agent_runs / f"{run_id}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        (runtime / "current_agent_run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    return 0 if allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
