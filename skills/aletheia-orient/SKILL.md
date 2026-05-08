---
name: aletheia-orient
description: Orient from the AletheiaOS project truth layer. Use before non-trivial tasks to load root mission, active frontier, active node, parent constraints, system graph, project skeleton, contracts, decisions, evidence, risks, and stop criteria without scanning the whole repository.
---

# Aletheia Orient

Load the smallest context that preserves the global skeleton and current project truth.

## Primitive Capabilities

Use these primitives. Do not add orchestration to runtime scripts for orientation judgment:

- `system_context.py` for prompt-ready stable truth, preferences, capabilities, and optional runtime context.
- `orient.py` for compact project truth orientation.
- `context_pack.py` for fuller stable truth, capability map, source summary, and record inventory.
- `status.py --json` when dynamic validation, runtime gate, record counts, recent changes, generated-output boundaries, or next actions are needed.
- `truth_record.py list/show` for focused follow-up reads after the active node is known.

## Prompt Recipe

The skill is a prompt recipe for deciding how much context to load before work.

Read order:

1. `.aletheia/START_HERE.md`
2. `.aletheia/governance/CHARTER.md`
3. `.aletheia/governance/ATTENTION_POLICY.md`
4. `.aletheia/state/ACTIVE_STATE.md`
5. `.aletheia/state/SYSTEM_GRAPH.yaml`
6. `.aletheia/state/SKELETON.yaml`
7. `.aletheia/governance/TREE_GOVERNANCE.md`
8. `.aletheia/state/ORPHANS.yaml`
9. Active node decisions, evidence, contracts, risks, and code paths.

Return:

- root mission;
- active frontier;
- active node;
- parent chain;
- tree attachment or incubator route for the task;
- orphan candidates relevant to the task;
- expanded nodes;
- skipped siblings and why;
- loaded contracts;
- potential stale skeleton areas;
- success and invalidation criteria.
