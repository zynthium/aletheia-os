#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TIER_ORDER = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}
BOOTSTRAP_GATE_COMMAND = (
    "python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize "
    "--provider <provider> --model-id <model_id> --tier C3 --operator-approved "
    '--record --objective "Initialize AletheiaOS"'
)
POST_BOOTSTRAP_REQUIRED_NO_TBD = [
    ".aletheia/governance/CHARTER.md",
    ".aletheia/state/SYSTEM_GRAPH.yaml",
    ".aletheia/state/ACTIVE_STATE.md",
    ".aletheia/state/DOMAIN_PROFILE.md",
]
BOOTSTRAP_FINALIZE_COMMAND = "python3 .aletheia/bin/bootstrap_finalize.py"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path, *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"{cmd[0]} is not available on PATH") from exc


def validate(root: Path) -> int:
    return subprocess.run([sys.executable, ".aletheia/bin/validate.py"], cwd=root, text=True).returncode


def validation_result(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, ".aletheia/bin/validate.py", "--json"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def inspect_model_gate(root: Path) -> dict:
    if os.environ.get("AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT") == "1":
        return {
            "id": "model_gate",
            "ok": True,
            "status": "override",
            "message": "AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1 bypasses bootstrap model gate.",
        }
    current_run_path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not current_run_path.exists():
        return {
            "id": "model_gate",
            "ok": False,
            "status": "missing",
            "message": "No AI model gate run recorded.",
            "next_action": BOOTSTRAP_GATE_COMMAND,
        }
    try:
        run_data = json.loads(current_run_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "id": "model_gate",
            "ok": False,
            "status": "invalid",
            "message": f"Current AI model gate run is invalid: {exc}",
            "path": ".aletheia/runtime/current_agent_run.json",
        }
    failures = []
    if run_data.get("gate_status") != "allowed":
        failures.append(f"gate_status={run_data.get('gate_status', 'unknown')}")
    if TIER_ORDER.get(str(run_data.get("capability_tier")), -1) < TIER_ORDER["C3"]:
        failures.append(f"capability_tier={run_data.get('capability_tier', 'unknown')}")
    if run_data.get("task_class") != "bootstrap_finalize":
        failures.append(f"task_class={run_data.get('task_class', 'unknown')}")
    if failures:
        return {
            "id": "model_gate",
            "ok": False,
            "status": "blocked",
            "message": "Current AI model gate run is not sufficient for bootstrap finalize: "
            + ", ".join(failures),
            "run_id": run_data.get("run_id"),
            "next_action": BOOTSTRAP_GATE_COMMAND,
        }
    return {
        "id": "model_gate",
        "ok": True,
        "status": "ready",
        "message": "Recorded AI model gate run allows bootstrap finalize.",
        "run_id": run_data.get("run_id"),
        "provider": run_data.get("provider"),
        "model_id": run_data.get("model_id"),
    }


def inspect_validation(root: Path) -> dict:
    result = validation_result(root)
    warnings: list[str] = []
    errors: list[str] = []
    try:
        validation_payload = json.loads(result.stdout)
        if isinstance(validation_payload, dict):
            warnings = [item for item in validation_payload.get("warnings", []) if isinstance(item, str)]
            errors = [item for item in validation_payload.get("errors", []) if isinstance(item, str)]
    except Exception:
        pass
    payload = {
        "id": "validation",
        "ok": result.returncode == 0,
        "status": "ready" if result.returncode == 0 else "blocked",
        "message": "AletheiaOS validation passes." if result.returncode == 0 else "AletheiaOS validation fails.",
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "warnings": warnings,
        "errors": errors,
    }
    if result.returncode != 0:
        payload["next_action"] = "python3 .aletheia/bin/validate.py"
    return payload


def inspect_critical_files(root: Path) -> dict:
    failures = []
    for rel in POST_BOOTSTRAP_REQUIRED_NO_TBD:
        path = root / rel
        if path.exists() and "TBD" in path.read_text(encoding="utf-8"):
            failures.append(rel)
    if failures:
        return {
            "id": "critical_truth",
            "ok": False,
            "status": "blocked",
            "message": "Critical files still contain TBD markers.",
            "paths": failures,
            "next_action": "Customize critical truth files before finalizing bootstrap.",
        }
    return {
        "id": "critical_truth",
        "ok": True,
        "status": "ready",
        "message": "Critical truth files do not contain bootstrap TBD markers.",
        "paths": POST_BOOTSTRAP_REQUIRED_NO_TBD,
    }


def inspect_git(root: Path) -> dict:
    try:
        check = run(["git", "rev-parse", "--is-inside-work-tree"], root, capture=True)
    except RuntimeError as exc:
        return {
            "id": "git",
            "ok": False,
            "status": "blocked",
            "message": str(exc),
        }
    if check.returncode == 0:
        return {
            "id": "git",
            "ok": True,
            "status": "ready",
            "message": "Repository is already a git worktree.",
            "will_initialize": False,
        }
    return {
        "id": "git",
        "ok": True,
        "status": "will_initialize",
        "message": "bootstrap_finalize.py will initialize git before installing hooks.",
        "will_initialize": True,
    }


def inspect_bootstrap_finalize(root: Path) -> dict:
    checks = [
        inspect_model_gate(root),
        inspect_validation(root),
        inspect_critical_files(root),
        inspect_git(root),
    ]
    ready = all(check.get("ok") for check in checks)
    next_actions = [check["next_action"] for check in checks if check.get("next_action")]
    if ready:
        next_actions.append(BOOTSTRAP_FINALIZE_COMMAND)
    return {
        "schema_version": 1,
        "action": "truth.bootstrap.finalize.inspect",
        "ready": ready,
        "checks": checks,
        "next_actions": next_actions,
        "would_write": [
            ".aletheia/hooks/pre-commit",
            ".aletheia/hooks/commit-msg",
            ".aletheia/session_notes/<date>-bootstrap-finalize.md",
            "BOOTSTRAP.md removal unless --keep-bootstrap",
            "checkpoint commit unless --no-checkpoint",
        ],
    }


def print_inspection(payload: dict) -> None:
    print("# Bootstrap Finalize Inspection")
    print()
    print(f"- ready: {payload['ready']}")
    print()
    print("## Checks")
    print()
    for check in payload["checks"]:
        print(f"- {check['id']}: {check['status']} - {check['message']}")
    print()
    print("## Next Actions")
    print()
    for action in payload["next_actions"]:
        print(f"- `{action}`")
    print()
    print("## Would Write")
    print()
    for path in payload["would_write"]:
        print(f"- {path}")


def bootstrap_model_gate_ready(root: Path) -> int:
    if os.environ.get("AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT") == "1":
        print("bootstrap model gate override enabled by AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1")
        return 0
    current_run_path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not current_run_path.exists():
        print("bootstrap blocked: no AI model gate run recorded")
        print(f"Run: {BOOTSTRAP_GATE_COMMAND}")
        return 1
    try:
        run_data = json.loads(current_run_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"bootstrap blocked: invalid current agent run record: {exc}")
        return 1
    if run_data.get("gate_status") != "allowed":
        print("bootstrap blocked: current AI model was not allowed by model gate")
        print(f"  run_id: {run_data.get('run_id')}")
        print(f"  gate_status: {run_data.get('gate_status')}")
        return 1
    if TIER_ORDER.get(str(run_data.get("capability_tier")), -1) < TIER_ORDER["C3"]:
        print("bootstrap blocked: bootstrap_finalize requires capability tier C3 or higher")
        print(f"  tier: {run_data.get('capability_tier')}")
        return 1
    if run_data.get("task_class") != "bootstrap_finalize":
        print("bootstrap blocked: current agent run is not task_class=bootstrap_finalize")
        print(f"  task_class: {run_data.get('task_class')}")
        return 1
    return 0


def post_bootstrap_ready(root: Path) -> int:
    failures = []
    for rel in POST_BOOTSTRAP_REQUIRED_NO_TBD:
        path = root / rel
        if path.exists() and "TBD" in path.read_text(encoding="utf-8"):
            failures.append(rel)
    if failures:
        print("bootstrap blocked: critical files still contain TBD markers:")
        for rel in failures:
            print(f"  - {rel}")
        print("Customize these files before deleting BOOTSTRAP.md and creating the initial checkpoint.")
        return 1
    return 0


def configure_hooks(root: Path) -> None:
    existing = run(["git", "config", "--get", "core.hooksPath"], root, capture=True)
    previous = existing.stdout.strip() if existing.returncode == 0 else ""
    hooks = root / ".aletheia" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    pre_commit = hooks / "pre-commit"
    pre_commit.write_text("#!/bin/sh\npython3 .aletheia/bin/validate.py\n", encoding="utf-8")
    pre_commit.chmod(0o755)
    commit_msg = hooks / "commit-msg"
    commit_msg.write_text('#!/bin/sh\npython3 .aletheia/bin/commit_msg_hook.py "$1"\n', encoding="utf-8")
    commit_msg.chmod(0o755)
    run(["git", "config", "core.hooksPath", ".aletheia/hooks"], root)
    print("AletheiaOS Git hooks installed at .aletheia/hooks")
    if previous and previous != ".aletheia/hooks":
        print(f"core.hooksPath changed from {previous} to .aletheia/hooks")


def ensure_git(root: Path) -> None:
    check = run(["git", "rev-parse", "--is-inside-work-tree"], root, capture=True)
    if check.returncode != 0:
        run(["git", "init"], root)


def write_session_note(root: Path) -> None:
    notes = root / ".aletheia" / "session_notes"
    notes.mkdir(parents=True, exist_ok=True)
    path = notes / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-bootstrap-finalize.md"
    path.write_text(
        "# Session Note: Bootstrap finalized\n\n"
        f"Date: {datetime.now(timezone.utc).date()}\n\n"
        "AletheiaOS bootstrap was finalized for this repository.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize AletheiaOS bootstrap for a target repository.")
    parser.add_argument("--keep-bootstrap", action="store_true")
    parser.add_argument("--no-checkpoint", action="store_true")
    parser.add_argument("--inspect", action="store_true", help="inspect bootstrap finalize readiness without writing files")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output with --inspect")
    args = parser.parse_args()

    root = repo_root()
    if args.inspect:
        payload = inspect_bootstrap_finalize(root)
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print_inspection(payload)
        return 0
    if args.json:
        parser.error("--json is only supported with --inspect")

    rc = bootstrap_model_gate_ready(root)
    if rc != 0:
        return rc
    rc = validate(root)
    if rc != 0:
        print("bootstrap blocked: validation failed")
        return rc
    rc = post_bootstrap_ready(root)
    if rc != 0:
        return rc

    try:
        ensure_git(root)
        configure_hooks(root)
    except RuntimeError as exc:
        print(f"bootstrap blocked: {exc}")
        return 1
    write_session_note(root)

    bootstrap = root / "BOOTSTRAP.md"
    if bootstrap.exists() and not args.keep_bootstrap:
        bootstrap.unlink()
        print("removed BOOTSTRAP.md")

    rc = validate(root)
    if rc != 0:
        print("bootstrap blocked: post-bootstrap validation failed")
        return rc

    if not args.no_checkpoint:
        checkpoint = run(
            [
                "python3",
                ".aletheia/bin/checkpoint.py",
                "--auto",
                "--message",
                "bootstrap: initialize AletheiaOS",
                "--allow-code-only",
                "--tree-op",
                "incubate",
                "--node",
                "root",
                "--review",
                "not-required",
            ],
            root,
        )
        return checkpoint.returncode

    print("bootstrap finalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
