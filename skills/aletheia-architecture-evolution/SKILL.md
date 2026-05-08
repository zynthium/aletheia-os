---
name: aletheia-architecture-evolution
description: Evolve AletheiaOS architecture truth. Use when changing module boundaries, contracts, dependency direction, project skeleton nodes, ADR/RFC records, transition plans, or architecture drift checks.
---

# Aletheia Architecture Evolution

Treat architecture changes as falsifiable design research that updates project truth.

## Primitive Capabilities

Use these primitives. Do not add orchestration to runtime scripts for architecture judgment:

- `system_context.py` or `orient.py` to load mission, active node, parent constraints, skeleton, and contracts.
- `truth_record.py list/show` to inspect decisions, contracts, evidence, risks, hypotheses, and nodes.
- `truth_record.py create/update/archive` to record the durable architecture facts that changed.
- `truth_record.py create/list/show/update/archive orphan` to incubate candidate skeleton or theory changes before promotion.
- `status.py --json` to inspect tree health, orphan count, generated-output boundaries, and next actions.
- `validate.py` to verify graph, refs, contracts, and record semantics.
- `checkpoint.py --dry-run` and `checkpoint.py` only when the user wants the coherent truth update committed.

## Prompt Recipe

The skill is a prompt recipe for architectural judgment, not a monolithic tool.

Before changing architecture:

1. Identify the skeleton node and parent chain.
2. State the architecture hypothesis.
3. Load relevant contracts and decisions.
4. Define transition and rollback boundaries.
5. Define invalidation criteria.
6. Record expected graph impact.
7. Decide whether the change is a local node edit, an incubating candidate, or
   a tree refactor that needs a decision record.

After changing architecture, update decisions, contracts, skeleton paths, evidence, and active state.
Use `.aletheia/playbooks/tree_governed_truth_growth.md` before moving subtrees,
inserting parents, splitting nodes, or promoting leaves.
For tree, skeleton, or durable architecture changes, prepare the matching
AletheiaOS traceability trailers before checkpointing the commit.
Before claiming a node is stable, run the current stable-node prerequisite:

```bash
python3 .aletheia/bin/checkpoint.py --dry-run
```

Once the Git history audit runtime is installed, this post-checkpoint audit is
also required before claiming stable:

```bash
python3 .aletheia/bin/history_audit.py --json
```
