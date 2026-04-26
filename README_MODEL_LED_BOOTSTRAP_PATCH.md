# Model-Led Bootstrap Patch

This patch converts AletheiaOS bootstrap from a user-script-driven flow into a model-led flow.

## What changed

- `BOOTSTRAP.md` now instructs the AI assistant to orchestrate bootstrap.
- `aletheia_os/12_INTAKE_POLICY.md` defines material classification rules.
- `scripts/aios_intake_inventory.py` creates a safe intake inventory.
- `scripts/aios_guided_bootstrap.py` runs model gate, inventory, and creates an import report scaffold.
- Guided bootstrap skills are added for Codex-style and Claude-style skill directories.
- README, AGENTS, START_HERE, and attention policy receive model-led bootstrap addenda.
- Claude settings are updated to include SessionStart, PreToolUse, PostToolUse, and Stop hooks.

## Operator instruction

After applying this patch, users can initialize a project by saying:

```text
Initialize this repository with AletheiaOS. Reuse existing research materials and code where appropriate. Do not start implementation work during bootstrap.
```

The assistant should run the internal commands itself.
