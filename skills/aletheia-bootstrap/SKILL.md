---
name: aletheia-bootstrap
description: Initialize an AletheiaOS project truth layer. Use when the user asks to add AletheiaOS to a repository or generate the repo-native .aletheia facts, constraints, evidence, and attribution control plane.
---

# Aletheia Bootstrap

Use the plugin scaffold to initialize `.aletheia/` as the target repository's project truth layer.

## Primitive Capabilities

Use these primitives. Do not add orchestration to runtime scripts for bootstrap judgment:

- `scripts/init_aletheia.py` to copy the scaffold into the target repository.
- `model_gate.py --record` to record bootstrap attribution.
- `source_inventory.py` to classify existing source material.
- `guided_bootstrap.py` to prepare the first truth inventory report.
- `truth_record.py create/update` or direct truth-file edits to write confirmed project truth.
- `orient.py`, `validate.py`, and `checkpoint.py` to verify and checkpoint the initialized truth layer.

## Prompt Recipe

The skill is a prompt recipe for first-run truth synthesis, not a single bootstrap tool.

Rules:

- Do not invent a project mission for an empty repository.
- Do not overwrite existing project files unless the user explicitly requests replacement.
- Keep project truth in `.aletheia/`.
- Ensure mandatory Claude Code hooks are present in `.claude/settings.json` and point to `.aletheia/bin/`.
- Keep source code, tests, public docs, build files, and CI files in their conventional locations.
- After initialization, orient from `.aletheia/START_HERE.md` before local implementation.
