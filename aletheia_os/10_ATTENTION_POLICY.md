# Attention Policy

This policy exists because large AI-assisted projects fail when the assistant over-attends to local files and under-attends to parent constraints.

The goal is not to load everything. The goal is to load the right abstraction layers in the right order.

## Context tiers

### Tier 0 — Always-on orientation

Use for every non-trivial session:

- `START_HERE.md`
- `AGENTS.md`
- `aletheia_os/00_CHARTER.md`
- `aletheia_os/10_ATTENTION_POLICY.md`
- `aletheia_os/02_ACTIVE_STATE.md`
- `aletheia_os/11_MODEL_GOVERNANCE.md` when durable writes are possible
- `aletheia_os/model_registry.json` when model gating or attribution is involved

Purpose: preserve mission, constraints, current frontier, and completion rules.

### Tier 1 — Active-node context

Load only after the task is located:

- relevant section of `aletheia_os/01_SYSTEM_GRAPH.yaml`
- relevant file(s) in `aletheia_os/nodes/`
- relevant hypothesis or design thesis
- current task card or frontier-board entry

Purpose: identify the branch being changed and its parent/child dependencies.

### Tier 2 — Boundary context

Load when crossing modules, disciplines, abstractions, teams, or runtime boundaries:

- `aletheia_os/06_INTERFACE_CONTRACTS.md`
- relevant files in `aletheia_os/contracts/`
- relevant decision records in `aletheia_os/decisions/`

Purpose: avoid silently changing interfaces or smuggling new assumptions across boundaries.

### Tier 3 — Evidence context

Load when evaluating, validating, reprioritizing, or promoting a branch:

- relevant evidence files in `aletheia_os/evidence/`
- `aletheia_os/07_EVIDENCE_INDEX.md`
- experiment, simulation, proof, test, or market-observation artifacts

Purpose: separate claim, method, result, interpretation, and system-graph impact.

### Tier 4 — Local implementation context

Load only after the upstream context is established:

- relevant files under `src/`, `tests/`, `experiments/`, `simulations/`, `configs/`, or `infra/`
- local `AGENTS.md` files in those directories

Purpose: execute without losing the upstream reason for the execution.

## Attention budget rules

1. One active node per session by default.
2. Do not read the whole repository when a scoped context pack is sufficient.
3. Do not keep expanding context after a local answer is available; first verify whether parent constraints are satisfied.
4. If a task affects multiple trunks, create or update a decision record before implementation proceeds.
5. If local implementation reveals a blocker, classify it as A/B/C/D and assess upstream impact before patching.
6. If context becomes crowded, distill current state into `aletheia_os/session_notes/` and restart from `scripts/aios_orient.py`.
7. Never treat the newest file or latest chat turn as the highest-priority branch unless the frontier board or active state says so.

## Global View Checksum

Before executing, produce or internally maintain this checksum:

```text
Root mission:
Priority order:
Active frontier:
Active node:
Parent node:
Parent constraints:
Explicit non-objectives:
Success criteria:
Invalidation criteria:
Downstream impact:
Required durable updates:
Verification path:
Model gate status:
Agent run id:
Checkpoint plan:
```

If the checksum cannot be completed, the task is under-specified. Propose a provisional task card or ask for the minimum missing information.

## Context reset protocol

Use this when finishing a substantial task, hitting context pressure, or switching active nodes:

1. Write a session note in `aletheia_os/session_notes/`.
2. Update `aletheia_os/02_ACTIVE_STATE.md`.
3. Update evidence, decision, contract, node, or graph files if affected.
4. Run `python3 scripts/aios_validate.py`.
5. Run `python3 scripts/aios_checkpoint.py --auto` when appropriate.
6. Ensure the session note and checkpoint include model attribution.
7. Clear/reset the AI conversation and restart from `START_HERE.md` or `python3 scripts/aios_orient.py`.

## Stop signs

Stop local execution and reorient when any of these occur:

- the task no longer maps cleanly to a system node;
- a code change changes a theory, objective, contract, or evidence interpretation;
- a test result contradicts an upstream assumption;
- implementation feasibility changes the design space;
- the assistant begins optimizing a proxy metric instead of the stated objective;
- the working set expands into unrelated branches;
- the project-state files and implementation files disagree;
- the current model is unknown, under-tier, or rejected for the task class.
