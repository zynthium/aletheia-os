# START HERE — AI Project Entry Point

This file is the stable entry point for any AI coding assistant working in this repository.

The repository is the durable memory. Chat history is not durable memory. Before any non-trivial work, build a top-down view from the files below, then narrow attention to the active task.

## Read order

For any non-trivial task, read in this order:

1. `AGENTS.md` — repository-wide operating protocol.
2. `project_os/00_CHARTER.md` — mission, priority order, non-negotiable constraints.
3. `project_os/10_ATTENTION_POLICY.md` — how to preserve global view under limited context.
4. `project_os/02_ACTIVE_STATE.md` — current frontier, active nodes, blockers, next actions.
5. Relevant node(s) in `project_os/01_SYSTEM_GRAPH.yaml` or `project_os/nodes/`.
6. Relevant contracts, evidence, decisions, code, tests, or experiment files only after the active node is identified.

For a compact session preload, run:

```bash
python3 scripts/aios_orient.py
```

## Global View Checksum

Before executing a task, the assistant should be able to answer:

```text
Root mission:
Active frontier:
Active node:
Parent node and constraints:
Current objective:
Explicit non-objectives:
Success criteria:
Invalidation / stop criteria:
Likely downstream impact:
Durable files that may need update:
Checkpoint policy for this task:
```

If any field is unknown, either infer a provisional value and mark it uncertain, or ask for the minimum missing information. Do not proceed by relying on conversational memory alone.

## Attention rule

Use a narrow working set, but keep the parent constraints visible. Load only the files required for the current active node and its immediate upstream/downstream boundaries. If the task starts to touch unrelated branches, stop and create or update a task card.

## Where implementation code belongs

Durable implementation code belongs under:

```text
src/<project_package_name>/
```

Exploratory work belongs under `experiments/` or `simulations/`. Governance, evidence, decisions, contracts, and active project memory belong under `project_os/`.

## Completion rule

A task is not complete until the durable state is coherent:

1. requested work completed or blocked with explicit reason;
2. verification run or inability to verify recorded;
3. affected evidence / decision / contract / active-state files updated when applicable;
4. session note written for substantial work;
5. checkpoint commit created or explicitly deferred with reason.
