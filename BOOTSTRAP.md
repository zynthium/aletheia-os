# BOOTSTRAP.md — First-Run Initialization Protocol

This file is intentionally temporary. It should be deleted after initialization and the result should be committed to git.

## Purpose

Initialize this repository as a durable AI-native project operating system. The final project should support complex theory + engineering + optimization programs without depending on any single chat context.

## Instructions for the AI assistant

You are initializing the project. Do not start implementation work yet.

### Step 1 — Read the core files

Read these files in order:

1. `START_HERE.md`
2. `README.md`
3. `AGENTS.md`
4. `project_os/00_CHARTER.md`
5. `project_os/10_ATTENTION_POLICY.md`
6. `project_os/01_SYSTEM_GRAPH.yaml`
7. `project_os/11_MODEL_GOVERNANCE.md`
8. `project_os/model_registry.json`
9. `project_os/02_ACTIVE_STATE.md`
10. `project_os/09_DOMAIN_PROFILE.md`

Then produce the Global View Checksum from `START_HERE.md`. If the checksum cannot be completed, mark uncertain fields as `TBD` and continue with initialization rather than inventing precision.

### Step 2 — Gate the initializing model

Before editing durable project state, run:

```bash
python3 scripts/aios_model_gate.py --task-class bootstrap_finalize --record --objective "Initialize AI Project OS"
```

If the model is unknown, either register it in `project_os/model_registry.json` or use an explicit operator-approved override, for example:

```bash
AIOS_OPERATOR_APPROVED=1 \
AIOS_MODEL_TIER=C3 \
AIOS_MODEL_ID="provider-model-id" \
AIOS_AGENT_PROVIDER="provider" \
python3 scripts/aios_model_gate.py --task-class bootstrap_finalize --record --objective "Initialize AI Project OS"
```

Do not finalize bootstrap with an ungated model.

### Step 3 — Establish project identity

If the user has not provided a domain, ask for only the minimum needed:

```text
What is the initial project domain, mission, and first active frontier?
```

If the user has already provided enough information, do not ask again. Infer a provisional domain profile and mark uncertain fields as `TBD`.

### Step 4 — Customize durable memory

Update these files:

- `project_os/00_CHARTER.md`
- `project_os/01_SYSTEM_GRAPH.yaml`
- `project_os/02_ACTIVE_STATE.md`
- `project_os/03_FRONTIER_BOARD.md`
- `project_os/04_RISK_REGISTER.md`
- `project_os/09_DOMAIN_PROFILE.md`

Keep the scaffold domain-neutral unless the user explicitly asks for a domain-specific project.

### Step 5 — Create initial records

Create, at minimum:

- one root node in `project_os/nodes/ROOT.yaml`
- one initial hypothesis or design thesis in `project_os/hypotheses/`
- one initial decision record in `project_os/decisions/`
- one first session note in `project_os/session_notes/`

### Step 6 — Validate orientation and structure

Run:

```bash
python3 scripts/aios_orient.py
python3 scripts/aios_validate.py
```

Fix validation issues before finalizing. During bootstrap, `TBD` markers are allowed as warnings. After `BOOTSTRAP.md` is removed, critical `TBD` markers become validation errors.

### Step 7 — Finalize bootstrap

Run:

```bash
python3 scripts/aios_bootstrap.py --finalize
```

This should:

- initialize git if needed;
- configure `.githooks` as the local hooks path;
- validate the project OS;
- remove this `BOOTSTRAP.md` file;
- create the first git commit.

### Step 8 — Report result

Return:

1. initialized project identity;
2. active frontier;
3. Global View Checksum;
4. files changed;
5. initializing model gate status and agent run id;
6. first checkpoint commit status;
7. next recommended task card.

## Forbidden during bootstrap

- Do not write production code.
- Do not run expensive experiments.
- Do not create many speculative branches.
- Do not delete the scaffold’s governance files.
- Do not skip the initial git checkpoint.
