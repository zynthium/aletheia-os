#!/usr/bin/env python3
"""Orient an AI coding assistant before work begins.

This script prints a top-down context pack and a checksum template. It is meant
for the start of a Claude Code / Codex session, after context compaction, or
whenever the assistant appears to be drifting into local optimization.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main() -> int:
    validate = run([sys.executable, "scripts/aios_validate.py"])
    print("# AIOS Orientation\n")
    print("## Validation\n")
    print(validate.stdout.strip() or "validation produced no output")
    print("\n---\n")

    pack = run([sys.executable, "scripts/aios_context_pack.py"])
    print(pack.stdout)

    print("## Required Global View Checksum\n")
    print("""```text
Root mission:
Priority order:
Active frontier:
Active node:
Parent node:
Parent constraints:
Explicit non-objectives:
Success criteria:
Invalidation criteria:
Downstream impact:
Required durable updates:
Verification path:
Model gate status:
Agent run id:
Checkpoint plan:
```""")

    if validate.returncode != 0:
        print("\nOrientation warning: validation failed. Fix project-state errors before substantial work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
