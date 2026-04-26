# AGENTS.md — Agent Operating Protocol

This repository uses a durable project-state system. The repository is the long-term memory; the AI assistant is the local executor and reviewer.

## Always read first for non-trivial tasks

1. `START_HERE.md`
2. `project_os/00_CHARTER.md`
3. `project_os/10_ATTENTION_POLICY.md`
4. `project_os/11_MODEL_GOVERNANCE.md`
5. `project_os/02_ACTIVE_STATE.md`
6. the relevant node(s) in `project_os/01_SYSTEM_GRAPH.yaml` or `project_os/nodes/`
7. relevant `project_os/contracts/` files if changing interfaces or boundaries
8. relevant `project_os/evidence/` and `project_os/decisions/` files if changing claims, priorities, or architecture

For a compact session preload, run:

```bash
python3 scripts/aios_orient.py
```

## Model gate before writes

Before any durable write, implementation change, research update, architecture decision, or checkpoint, run or verify:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Task classes are defined in `project_os/model_registry.json`. Unknown or under-tier models are read-only by default. If the gate rejects the model, do not continue with smaller local edits; report the rejection and the required minimum tier.

Include agent attribution in session notes and checkpoint commits:

```text
Agent run id:
Provider:
Model id:
Capability tier:
Task class:
Gate status:
```

## Global View Checksum

Before executing, identify or produce:

```text
Root mission:
Priority order:
Active frontier:
Active node:
Parent node and constraints:
Current objective:
Explicit non-objectives:
Success criteria:
Invalidation / stop criteria:
Likely downstream impact:
Required durable updates:
Verification path:
Model gate status:
Agent run id:
Checkpoint plan:
```

If the active node cannot be identified, do not proceed as if the task were local. Propose a provisional task card or ask for the minimum missing information.

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
- Do not load the whole repository by default; follow `project_os/10_ATTENTION_POLICY.md` and load context by tier.

## Blocker classification

When blocked, classify the blocker:

- **A — Implementation limitation**: concept may hold, but present tools, data, skills, or infrastructure cannot realize it.
- **B — Interface mismatch**: module, discipline, layer, or abstraction boundary is wrong.
- **C — Parent-assumption invalidation**: evidence contradicts an upstream premise.
- **D — Objective conflict**: the project goal, market requirement, physical constraint, or optimization target must be reconsidered.

Do not patch locally until the blocker type and upstream impact are recorded.

## Code placement rules

Durable implementation code belongs under:

```text
src/<project_package_name>/
```

Directory roles:

- `project_os/`: governance, theory, evidence, decisions, contracts, active state.
- `src/`: final durable implementation code.
- `experiments/`: exploratory work and experiment runs.
- `simulations/`: simulation scenarios, replays, synthetic environments, stress cases.
- `tests/`: verification of code, assumptions, contracts, leakage, boundaries, and regressions.
- `scripts/`: thin operational wrappers and repository tooling.

When promoting exploratory work to implementation:

1. move reusable logic into `src/`;
2. add or update tests;
3. link to relevant project node, evidence, decision, or contract;
4. update `project_os/02_ACTIVE_STATE.md`;
5. validate before checkpoint.

## Completion standard

For non-trivial work, completion also requires model attribution: an agent run record under `project_os/agent_runs/` or an explicit reason why no model gate was required.


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
