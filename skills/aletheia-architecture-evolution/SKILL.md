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
- `validate.py` to verify graph, refs, contracts, and record semantics.
- `checkpoint.py` only when the user wants the coherent truth update committed.

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
