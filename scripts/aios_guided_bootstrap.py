#!/usr/bin/env python3
"""Assistant-facing helper for AletheiaOS guided bootstrap."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
INTAKE_DIR = ROOT / "aletheia_os" / "bootstrap_intake"
INVENTORY_JSON = INTAKE_DIR / "inventory.json"
IMPORT_REPORT = INTAKE_DIR / "IMPORT_REPORT.md"


def run(cmd: list[str], *, check: bool = False) -> int:
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, check=check).returncode


def load_inventory() -> dict:
    if not INVENTORY_JSON.exists():
        return {"items": []}
    return json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))


def infer_mode(items: list[dict]) -> str:
    code_count = sum(1 for x in items if x.get("kind") == "implementation_code")
    doc_count = sum(1 for x in items if "document" in x.get("kind", "") or "design" in x.get("kind", ""))
    evidence_count = sum(1 for x in items if "evidence" in x.get("kind", "") or "experiment" in x.get("kind", ""))
    if code_count >= 10 or evidence_count >= 3:
        return "migration"
    if doc_count >= 3 or code_count >= 3:
        return "brownfield"
    return "greenfield"


def write_import_report(objective: str, inventory: dict) -> None:
    INTAKE_DIR.mkdir(parents=True, exist_ok=True)
    items = inventory.get("items", [])
    mode = infer_mode(items)
    by_class = {}
    by_kind = {}
    for item in items:
        by_class[item.get("initial_classification", "unknown")] = by_class.get(item.get("initial_classification", "unknown"), 0) + 1
        by_kind[item.get("kind", "unknown")] = by_kind.get(item.get("kind", "unknown"), 0) + 1

    def section_counts(mapping: dict) -> str:
        if not mapping:
            return "TBD"
        return "\n".join(f"- {k}: {v}" for k, v in sorted(mapping.items()))

    report = f"""# Bootstrap Import Report

## Metadata

- Generated at: {datetime.now(timezone.utc).isoformat()}
- Initialization mode: {mode}
- Objective: {objective}

## Inventory summary

Total items: {len(items)}

### By initial classification

{section_counts(by_class)}

### By kind

{section_counts(by_kind)}

## Authoritative current sources

TBD — the assistant must decide after selective reading.

## Useful but unverified sources

TBD — use `inventory.json` and selective reading.

## Historical context

TBD

## Superseded sources

TBD

## Conflicts requiring review

TBD

## Sensitive exclusions

Items initially classified as `unsafe_or_sensitive` were excluded from full-content reading.

## Deferred large items

Items initially classified as `deferred_due_to_size` should be processed later with a focused workflow.

## Durable records created or updated

TBD — the assistant must fill this after synthesis.

## System graph impact

TBD

## Active frontier after bootstrap

TBD

## Open questions

TBD

## Next recommended task card

TBD
"""
    IMPORT_REPORT.write_text(report, encoding="utf-8")
    print(f"wrote {IMPORT_REPORT}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--objective", default="Initialize AletheiaOS")
    parser.add_argument("--skip-gate", action="store_true")
    parser.add_argument("--skip-inventory", action="store_true")
    args = parser.parse_args()

    if not args.skip_gate:
        gate_script = ROOT / "scripts" / "aios_model_gate.py"
        if gate_script.exists():
            run(["python3", str(gate_script), "--task-class", "bootstrap_finalize", "--record", "--objective", args.objective], check=False)
        else:
            print("warning: scripts/aios_model_gate.py not found; gate not run")

    if not args.skip_inventory:
        inventory_script = ROOT / "scripts" / "aios_intake_inventory.py"
        if inventory_script.exists():
            run(["python3", str(inventory_script)], check=False)
        else:
            print("warning: scripts/aios_intake_inventory.py not found; inventory not run")

    inventory = load_inventory()
    write_import_report(args.objective, inventory)

    print("\nNext assistant steps:")
    print("1. Selectively read high-signal files from inventory.json.")
    print("2. Classify materials using aletheia_os/12_INTAKE_POLICY.md.")
    print("3. Update durable AletheiaOS records with provenance.")
    print("4. Run scripts/aios_validate.py and scripts/aios_orient.py.")
    print("5. Run scripts/aios_bootstrap.py --finalize when ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
