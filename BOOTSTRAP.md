# BOOTSTRAP.md — First-Run Initialization Protocol

This file is intentionally temporary. It should be deleted after initialization and the result should be committed to git.

## Purpose

Initialize this repository as a durable AI-native project operating system. The final project should support complex theory + engineering + optimization programs without depending on any single chat context.

## Instructions for the AI assistant

You are initializing the project. Do not start implementation work yet.

### Step 1 — Read the core files

Read these files in order:

1. `README.md`
2. `AGENTS.md`
3. `project_os/00_CHARTER.md`
4. `project_os/01_SYSTEM_GRAPH.yaml`
5. `project_os/02_ACTIVE_STATE.md`
6. `project_os/09_DOMAIN_PROFILE.md`

### Step 2 — Establish project identity

If the user has not provided a domain, ask for only the minimum needed:

```text
What is the initial project domain, mission, and first active frontier?
```

If the user has already provided enough information, do not ask again. Infer a provisional domain profile and mark uncertain fields as `TBD`.

### Step 3 — Customize durable memory

Update these files:

- `project_os/00_CHARTER.md`
- `project_os/01_SYSTEM_GRAPH.yaml`
- `project_os/02_ACTIVE_STATE.md`
- `project_os/03_FRONTIER_BOARD.md`
- `project_os/04_RISK_REGISTER.md`
- `project_os/09_DOMAIN_PROFILE.md`

Keep the scaffold domain-neutral unless the user explicitly asks for a domain-specific project.

### Step 4 — Create initial records

Create, at minimum:

- one root node in `project_os/nodes/ROOT.yaml`
- one initial hypothesis or design thesis in `project_os/hypotheses/`
- one initial decision record in `project_os/decisions/`
- one first session note in `project_os/session_notes/`

### Step 5 — Validate

Run:

```bash
python3 scripts/aios_validate.py
```

Fix validation issues before finalizing.

### Step 6 — Finalize bootstrap

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

### Step 7 — Report result

Return:

1. initialized project identity;
2. active frontier;
3. files changed;
4. first checkpoint commit status;
5. next recommended task card.

## Forbidden during bootstrap

- Do not write production code.
- Do not run expensive experiments.
- Do not create many speculative branches.
- Do not delete the scaffold’s governance files.
- Do not skip the initial git checkpoint.
