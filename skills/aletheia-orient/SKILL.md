---
name: aletheia-orient
description: Orient from the AletheiaOS project truth layer. Use before non-trivial tasks to load root mission, active frontier, active node, parent constraints, system graph, project skeleton, contracts, decisions, evidence, risks, and stop criteria without scanning the whole repository.
---

# Aletheia Orient

Load the smallest context that preserves the global skeleton and current project truth.

Read order:

1. `.aletheia/START_HERE.md`
2. `.aletheia/governance/CHARTER.md`
3. `.aletheia/governance/ATTENTION_POLICY.md`
4. `.aletheia/state/ACTIVE_STATE.md`
5. `.aletheia/state/SYSTEM_GRAPH.yaml`
6. `.aletheia/state/SKELETON.yaml`
7. Active node decisions, evidence, contracts, risks, and code paths.

Return:

- root mission;
- active frontier;
- active node;
- parent chain;
- expanded nodes;
- skipped siblings and why;
- loaded contracts;
- potential stale skeleton areas;
- success and invalidation criteria.
