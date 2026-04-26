#!/usr/bin/env python3
"""Create a conservative git checkpoint for durable project state."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_RUN_PATH = ROOT / ".aios_runtime/current_agent_run.json"
MODEL_REGISTRY_PATH = ROOT / "aletheia_os/model_registry.json"

PROTECTED_PATTERNS = [
    re.compile(r"(^|/)\.env(\.|$)"),
    re.compile(r"(^|/)secrets/"),
    re.compile(r"\.(pem|key|crt|credentials|secret)$", re.IGNORECASE),
]

STATE_PATTERNS = [
    "START_HERE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "aletheia_os/AGENTS.md",
    "src/AGENTS.md",
    "tests/AGENTS.md",
    "experiments/AGENTS.md",
    "simulations/AGENTS.md",
    "configs/AGENTS.md",
    "docs/AGENTS.md",
    "infra/AGENTS.md",
    "aletheia_os/10_ATTENTION_POLICY.md",
    "aletheia_os/11_MODEL_GOVERNANCE.md",
    "aletheia_os/model_registry.json",
    "aletheia_os/02_ACTIVE_STATE.md",
    "aletheia_os/01_SYSTEM_GRAPH.yaml",
    "aletheia_os/03_FRONTIER_BOARD.md",
    "aletheia_os/04_RISK_REGISTER.md",
    "aletheia_os/06_INTERFACE_CONTRACTS.md",
    "aletheia_os/07_EVIDENCE_INDEX.md",
    "aletheia_os/08_GIT_POLICY.md",
    "aletheia_os/09_DOMAIN_PROFILE.md",
    "aletheia_os/evidence/",
    "aletheia_os/decisions/",
    "aletheia_os/contracts/",
    "aletheia_os/hypotheses/",
    "aletheia_os/nodes/",
    "aletheia_os/session_notes/",
    "aletheia_os/agent_runs/",
]


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def git_available() -> bool:
    try:
        run(["git", "--version"], capture=True)
        return True
    except Exception:
        return False


def ensure_git() -> None:
    if not git_available():
        raise RuntimeError("git is not available on PATH")
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"], capture=True)
    except subprocess.CalledProcessError:
        run(["git", "init"])


def status_files() -> list[str]:
    result = run(["git", "status", "--porcelain"], capture=True)
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # Porcelain format: XY path or XY old -> new
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path)
    return files


def has_state_update(files: list[str]) -> bool:
    for f in files:
        if f == "BOOTSTRAP.md":
            return True
        for pat in STATE_PATTERNS:
            if pat.endswith("/"):
                if f.startswith(pat):
                    return True
            elif f == pat:
                return True
    return False


def has_protected(files: list[str]) -> list[str]:
    return [f for f in files if any(rx.search(f) for rx in PROTECTED_PATTERNS)]



def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def require_agent_run_for_checkpoint() -> bool:
    registry = load_json(MODEL_REGISTRY_PATH)
    default_policy = registry.get("default_policy", {}) if isinstance(registry.get("default_policy", {}), dict) else {}
    return bool(default_policy.get("require_agent_run_for_checkpoint", False))


def load_current_agent_run() -> dict:
    run_data = load_json(CURRENT_RUN_PATH)
    if run_data:
        return run_data
    provider = os.environ.get("AIOS_AGENT_PROVIDER") or os.environ.get("AIOS_PROVIDER")
    model = os.environ.get("AIOS_MODEL_ID") or os.environ.get("AIOS_MODEL")
    tier = os.environ.get("AIOS_MODEL_TIER") or os.environ.get("AIOS_CAPABILITY_TIER")
    task_class = os.environ.get("AIOS_TASK_CLASS")
    if provider or model or tier or task_class:
        return {
            "run_id": os.environ.get("AIOS_AGENT_RUN_ID", "unrecorded-env"),
            "provider": provider or "unknown",
            "model_id": model or "unknown",
            "capability_tier": tier or "unknown",
            "task_class": task_class or "unknown",
            "gate_status": os.environ.get("AIOS_GATE_STATUS", "unrecorded"),
        }
    return {}


def attribution_trailers(run_data: dict) -> str:
    if not run_data:
        return ""
    fields = [
        ("AIOS-Agent-Run", run_data.get("run_id", "unknown")),
        ("AIOS-Agent-Provider", run_data.get("provider", "unknown")),
        ("AIOS-Agent-Model", run_data.get("model_id", "unknown")),
        ("AIOS-Agent-Tier", run_data.get("capability_tier", "unknown")),
        ("AIOS-Task-Class", run_data.get("task_class", "unknown")),
        ("AIOS-Gate", run_data.get("gate_status", "unknown")),
    ]
    return "\n\n" + "\n".join(f"{k}: {v}" for k, v in fields)

def infer_message(files: list[str]) -> str:
    if "BOOTSTRAP.md" in files:
        return "bootstrap: initialize AletheiaOS"
    if "aletheia_os/11_MODEL_GOVERNANCE.md" in files or "aletheia_os/model_registry.json" in files:
        return "governance: update model gate policy"
    if "aletheia_os/10_ATTENTION_POLICY.md" in files or "START_HERE.md" in files:
        return "state: update orientation and attention policy"
    if any(f.startswith("aletheia_os/evidence/") for f in files):
        return "evidence: update evidence ledger"
    if any(f.startswith("aletheia_os/decisions/") for f in files):
        return "decision: update decision records"
    if any(f.startswith("aletheia_os/contracts/") for f in files) or "aletheia_os/06_INTERFACE_CONTRACTS.md" in files:
        return "contract: update interface contracts"
    if "aletheia_os/01_SYSTEM_GRAPH.yaml" in files or any(f.startswith("aletheia_os/nodes/") for f in files):
        return "graph: update system graph"
    if "aletheia_os/02_ACTIVE_STATE.md" in files or "aletheia_os/03_FRONTIER_BOARD.md" in files:
        return "state: update active project state"
    if any(f.startswith("aletheia_os/session_notes/") for f in files):
        return "session: add session distillation"
    if any(f.startswith(("src/", "lib/", "app/", "tests/", "experiments/", "simulations/", "configs/", "infra/")) for f in files):
        return "engineering: update implementation"
    return "checkpoint: durable project state update"


def validate() -> int:
    script = ROOT / "scripts/aios_validate.py"
    if not script.exists():
        print("validation skipped: scripts/aios_validate.py missing")
        return 0
    proc = subprocess.run([sys.executable, str(script)], cwd=ROOT, text=True)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="commit without interactive confirmation")
    parser.add_argument("--message", default=None, help="commit message")
    parser.add_argument("--no-validate", action="store_true", help="skip AIOS validation")
    parser.add_argument("--allow-code-only", action="store_true", help="allow commit even if no durable state file changed")
    parser.add_argument("--dry-run", action="store_true", help="print intended action without committing")
    parser.add_argument("--no-model-gate", action="store_true", help="operator override: do not require agent attribution for this checkpoint")
    args = parser.parse_args()

    ensure_git()

    files = status_files()
    if not files:
        print("checkpoint skipped: working tree is clean")
        return 0

    protected = has_protected(files)
    if protected:
        print("checkpoint blocked: protected-looking files are present:")
        for f in protected:
            print(f"  - {f}")
        return 2

    if not args.no_validate:
        rc = validate()
        if rc != 0:
            print("checkpoint blocked: validation failed")
            return rc

    allow_code_only = args.allow_code_only or os.environ.get("AIOS_ALLOW_CODE_ONLY_COMMIT") == "1"
    if not has_state_update(files) and not allow_code_only:
        print("checkpoint blocked: changes do not include durable project-state update")
        print("Update aletheia_os/02_ACTIVE_STATE.md, attention policy, evidence, decisions, contracts, nodes, or session notes.")
        print("Override with --allow-code-only or AIOS_ALLOW_CODE_ONLY_COMMIT=1 if intentional.")
        return 3

    run_data = load_current_agent_run()
    allow_unattributed = args.no_model_gate or os.environ.get("AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT") == "1"
    if require_agent_run_for_checkpoint() and not run_data and not allow_unattributed:
        print("checkpoint blocked: no current AI agent run attribution found")
        print('Run: python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "..."')
        print("Override with --no-model-gate or AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1 only with explicit operator intent.")
        return 4
    if run_data and run_data.get("gate_status") not in {"allowed", "unrecorded"} and not allow_unattributed:
        print("checkpoint blocked: current AI agent run was not allowed by model gate")
        print(f"  run_id: {run_data.get('run_id')}")
        print(f"  gate_status: {run_data.get('gate_status')}")
        return 5

    message = args.message or infer_message(files)
    message_with_trailers = message + attribution_trailers(run_data)

    print("checkpoint candidate:")
    for f in files:
        print(f"  - {f}")
    print(f"message: {message}")
    if run_data:
        print(f"agent_run: {run_data.get('run_id', 'unknown')} {run_data.get('provider', 'unknown')}/{run_data.get('model_id', 'unknown')} tier={run_data.get('capability_tier', 'unknown')} task={run_data.get('task_class', 'unknown')}")

    if args.dry_run:
        return 0

    if not args.auto:
        answer = input("Create checkpoint commit? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("checkpoint skipped by user")
            return 0

    run(["git", "add", "-A"])
    try:
        run(["git", "commit", "-m", message_with_trailers])
    except subprocess.CalledProcessError as exc:
        print("checkpoint failed: git commit returned non-zero status")
        print("Common cause: git user.name/user.email not configured.")
        return exc.returncode

    print("checkpoint committed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
