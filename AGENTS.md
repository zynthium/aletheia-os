# AGENTS.md — Agent Operating Protocol

This repository uses a durable project-state system. The repository is the long-term memory; the AI assistant is the local executor and reviewer.

## Always read first for non-trivial tasks

1. `project_os/00_CHARTER.md`
2. `project_os/02_ACTIVE_STATE.md`
3. the relevant node(s) in `project_os/01_SYSTEM_GRAPH.yaml` or `project_os/nodes/`
4. relevant `project_os/contracts/` files if changing interfaces or boundaries
5. relevant `project_os/evidence/` and `project_os/decisions/` files if changing claims, priorities, or architecture

## Operating cycle

Before executing, identify:

- active node;
- parent constraints;
- current objective;
- non-objectives;
- success criteria;
- invalidation criteria;
- likely downstream impact;
- required evidence or decision update.

After executing, update durable state:

- `project_os/02_ACTIVE_STATE.md` for current frontier and blockers;
- `project_os/evidence/` for experiments, simulations, observations, derivations, or proofs;
- `project_os/decisions/` for durable architectural/theoretical/product decisions;
- `project_os/contracts/` for boundary or interface changes;
- `project_os/session_notes/` for session distillation;
- `project_os/01_SYSTEM_GRAPH.yaml` or `project_os/nodes/` if priority, confidence, dependency, or status changed.

## Non-negotiable constraints

- Do not optimize locally against stale or implicit objectives.
- Do not create a new branch of work without linking it to a node in the system graph.
- Do not treat performance, simulation output, market response, or implementation success as self-explanatory evidence; interpret it against a claim.
- Do not silently change parent assumptions.
- Do not move a prototype toward production without an interface contract and invalidation criteria.
- Do not claim a task is complete if durable project state was not updated when it should have been.

## Blocker classification

When blocked, classify the blocker:

- **A — Implementation limitation**: concept may hold, but present tools, data, skills, or infrastructure cannot realize it.
- **B — Interface mismatch**: module, discipline, layer, or abstraction boundary is wrong.
- **C — Parent-assumption invalidation**: evidence contradicts an upstream premise.
- **D — Objective conflict**: the project goal, market requirement, physical constraint, or optimization target must be reconsidered.

Do not patch locally until the blocker type and upstream impact are recorded.

## Completion standard

A task is complete only when:

1. the requested work is done;
2. validation or explicit verification was run, or the inability to run it is recorded;
3. durable state is updated;
4. git checkpoint is created or explicitly deferred with reason;
5. unresolved risks are listed.

## Checkpoint policy

Run before final response for any non-trivial task:

```bash
python3 scripts/aios_validate.py
python3 scripts/aios_checkpoint.py --auto
```

If committing is inappropriate, explain why and leave the repository in a coherent state.

## Response format for research/design tasks

Return:

1. active node;
2. parent constraints;
3. assumptions;
4. method;
5. evidence required;
6. invalidation criteria;
7. expected graph impact;
8. deliverables;
9. checkpoint status.

## Response format for implementation tasks

Return:

1. files changed;
2. contracts affected;
3. tests or checks run;
4. project-state files updated;
5. unresolved risks;
6. checkpoint status.
