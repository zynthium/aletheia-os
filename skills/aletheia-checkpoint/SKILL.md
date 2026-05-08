---
name: aletheia-checkpoint
description: Validate and checkpoint AletheiaOS project truth. Use when the user asks to checkpoint, finish a substantial task, record session notes, validate model attribution, or prepare a coherent git commit for .aletheia facts and implementation changes.
---

# Aletheia Checkpoint

## Primitive Capabilities

Use these primitives. Do not add orchestration to runtime scripts for completion judgment:

- `status.py --json` to inspect active state, validation, record counts, runtime gate, recent changes, generated-output boundaries, and next actions.
- `preflight.py --json` to inspect hook-free context, validation, git state, checkpoint candidates, generated-output boundaries, and recommended action ids.
- `truth_record.py list/show/update/create` to ensure affected truth records exist and are current.
- `validate.py` to verify scaffold and truth semantics.
- `checkpoint.py --dry-run` to preview candidates.
- `checkpoint.py` to create the attributed commit when the user has not deferred commits.

## Prompt Recipe

The skill is a prompt recipe for deciding whether a checkpoint is appropriate.

Before claiming completion for non-trivial work:

1. Confirm model gate attribution exists for durable writes.
2. Confirm affected `.aletheia/` facts, decisions, evidence, risks, or contracts were updated.
3. Run repository validation when the user asks for verification or checkpointing.
4. For tree, skeleton, or durable architecture changes, choose the required
   traceability trailer from `.aletheia/governance/GIT_POLICY.md` and
   `.aletheia/governance/TREE_GOVERNANCE.md`.
5. Before claiming a node is stable, run the current stable-node prerequisite:

   ```bash
   python3 .aletheia/bin/checkpoint.py --dry-run
   ```

   Once the Git history audit runtime is installed, this post-checkpoint audit
   is also required before claiming stable:

   ```bash
   python3 .aletheia/bin/history_audit.py --json
   ```

6. Create a checkpoint only when validation state is known and the user has not deferred commits.
7. Preserve agent attribution and AletheiaOS traceability trailers in checkpoint commits.

Never hide unresolved risks.
