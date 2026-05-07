#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

TIER_RANK = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path) -> int:
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=root, check=False).returncode


def run_required(cmd: list[str], root: Path, label: str) -> None:
    rc = run(cmd, root)
    if rc != 0:
        raise SystemExit(f"{label} failed with exit code {rc}")


def infer_mode(items: list[dict]) -> str:
    code_count = sum(1 for item in items if item.get("kind") == "implementation_code")
    doc_count = sum(1 for item in items if "document" in item.get("kind", "") or "design" in item.get("kind", ""))
    evidence_count = sum(1 for item in items if "evidence" in item.get("kind", "") or "experiment" in item.get("kind", ""))
    if code_count >= 10 or evidence_count >= 3 or doc_count >= 3 or code_count >= 3:
        return "existing repository"
    return "new repository"


def tier_rank(tier: str | None) -> int:
    return TIER_RANK.get(str(tier or ""), -1)


def load_current_run(root: Path) -> dict:
    path = root / ".aletheia" / "runtime" / "current_agent_run.json"
    if not path.exists():
        raise SystemExit(
            "no bootstrap model gate run recorded. Run: "
            'python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> '
            '--model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"'
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"bootstrap model gate run is invalid: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("bootstrap model gate run is invalid: expected JSON object")
    return data


def require_bootstrap_gate(root: Path) -> None:
    run_data = load_current_run(root)
    if run_data.get("gate_status") != "allowed":
        raise SystemExit(f"bootstrap model gate was not allowed: {run_data.get('reason', 'gate rejected')}")
    if run_data.get("task_class") != "bootstrap_finalize":
        raise SystemExit(
            "current model gate run is not task_class=bootstrap_finalize: "
            f"{run_data.get('task_class', 'unknown')}"
        )
    if tier_rank(run_data.get("capability_tier")) < tier_rank("C3"):
        raise SystemExit(
            "bootstrap model gate requires capability tier C3 or higher: "
            f"{run_data.get('capability_tier', 'unknown')}"
        )
    if run_data.get("write_allowed") is not True:
        raise SystemExit("current bootstrap model gate run does not allow bootstrap writes")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare an AletheiaOS guided project truth inventory report.")
    parser.add_argument("--objective", default="Initialize AletheiaOS")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--skip-inventory", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    if not args.skip_gate:
        require_bootstrap_gate(root)
    if not args.skip_inventory:
        run_required(["python3", ".aletheia/bin/source_inventory.py"], root, "source inventory")

    inventory_dir = root / ".aletheia" / "source_inventory"
    inventory_path = inventory_dir / "inventory.json"
    if args.skip_inventory and not inventory_path.exists():
        raise SystemExit(
            "source inventory missing. Run python3 .aletheia/bin/source_inventory.py "
            "or omit --skip-inventory."
        )
    inventory = json.loads(inventory_path.read_text(encoding="utf-8")) if inventory_path.exists() else {"items": []}
    items = inventory.get("items", [])
    mode = infer_mode(items)
    by_class: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for item in items:
        by_class[item.get("initial_classification", "unknown")] = by_class.get(item.get("initial_classification", "unknown"), 0) + 1
        by_kind[item.get("kind", "unknown")] = by_kind.get(item.get("kind", "unknown"), 0) + 1

    def counts(mapping: dict[str, int]) -> str:
        return "\n".join(f"- {key}: {value}" for key, value in sorted(mapping.items())) or "None"

    report = f"""# Truth Inventory Report

## Metadata

- Generated at: {datetime.now(timezone.utc).isoformat()}
- Initialization mode: {mode}
- Objective: {args.objective}

## Inventory Summary

Total items: {len(items)}

### By initial classification

{counts(by_class)}

### By kind

{counts(by_kind)}

## Project Truth Records Created Or Updated

TBD - assistant must fill after synthesis.

## System Graph Impact

TBD - assistant must fill after synthesis.

## Open Questions

TBD - assistant must fill after synthesis.
"""
    inventory_dir.mkdir(parents=True, exist_ok=True)
    (inventory_dir / "TRUTH_INVENTORY_REPORT.md").write_text(report, encoding="utf-8")
    print(f"wrote {inventory_dir / 'TRUTH_INVENTORY_REPORT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
