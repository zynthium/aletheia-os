# BOOTSTRAP.md — Model-Led First-Run Initialization Protocol

This file is intentionally temporary. It should be deleted after initialization and the result should be committed to git.

## Purpose

Initialize this repository as a durable AletheiaOS project. The final project should support complex theory + engineering + optimization programs without depending on any single chat context.

Bootstrap is model-led. The AI coding assistant, not the human operator, is responsible for orchestrating the initialization sequence.

The operator should only provide high-level intent, domain boundaries, and any access restrictions. The assistant must decide which internal scripts to run, when to inspect existing materials, and how to synthesize durable project state.

## Supported initialization modes

### Greenfield

Use this when the repository has little or no prior project material. Build the initial charter, system graph, active frontier, risk register, decision record, and session note from the user's stated mission.

### Brownfield

Use this when the repository already contains research notes, notebooks, code, experiments, reports, or design documents. The assistant must inventory and classify existing materials before synthesizing project state.

### Migration

Use this when AletheiaOS is being introduced into an existing mature repository. Preserve existing implementation code and build the governance layer around it.

## Operator-facing instruction

The operator does not need to know the internal script sequence. A valid initialization request can be as simple as:

```text
Initialize this repository with AletheiaOS. Reuse existing research materials and code where appropriate. Do not start implementation work during bootstrap.
```

For a quantitative research-to-production system, the operator may say:

```text
Initialize this repository with AletheiaOS for a quantitative trading research-to-production system. Reuse existing research notes, notebooks, experiments, code, reports, strategy documents, and design decisions where appropriate. Preserve provenance and uncertainty. Do not start new strategy implementation during bootstrap.
```

## Instructions for the AI assistant

You are initializing the project. Do not ask the operator to run internal scripts. Do not start implementation work yet.

### Step 1 — Orient

Read these files in order:

1. `START_HERE.md`
2. `README.md`
3. `AGENTS.md`
4. `aletheia_os/00_CHARTER.md`
5. `aletheia_os/10_ATTENTION_POLICY.md`
6. `aletheia_os/11_MODEL_GOVERNANCE.md`
7. `aletheia_os/model_registry.json`
8. `aletheia_os/12_INTAKE_POLICY.md` if present
9. `aletheia_os/01_SYSTEM_GRAPH.yaml`
10. `aletheia_os/02_ACTIVE_STATE.md`
11. `aletheia_os/09_DOMAIN_PROFILE.md`

Then produce the Global View Checksum from `START_HERE.md`. If the checksum cannot be completed, mark uncertain fields as `TBD` and continue with initialization rather than inventing precision.

### Step 2 — Gate the initializing model

Before editing durable project state, run model gating yourself:

```bash
python3 scripts/aios_model_gate.py --task-class bootstrap_finalize --record --objective "Initialize AletheiaOS"
```

If the model is unknown, use only an explicit operator-approved override. Do not self-approve. Do not finalize bootstrap with an ungated model.

### Step 3 — Determine initialization mode

Inspect the repository structure and select one:

- `greenfield`
- `brownfield`
- `migration`

If prior materials exist, default to `brownfield` or `migration`; do not initialize as if the project were empty.

### Step 4 — Inventory existing materials

Run:

```bash
python3 scripts/aios_intake_inventory.py
```

This should create:

- `aletheia_os/bootstrap_intake/inventory.json`
- `aletheia_os/bootstrap_intake/inventory.md`

The inventory must avoid secrets, credentials, large raw data, vendor caches, build artifacts, and obviously sensitive files.

### Step 5 — Classify and synthesize

Use `aletheia_os/12_INTAKE_POLICY.md` to classify material. Do not treat old research as automatically true. Preserve provenance, uncertainty, conflicts, and superseded materials.

Run the guided bootstrap helper:

```bash
python3 scripts/aios_guided_bootstrap.py --objective "Initialize AletheiaOS"
```

Then synthesize durable project memory. Update or create only what is justified:

- `aletheia_os/00_CHARTER.md`
- `aletheia_os/01_SYSTEM_GRAPH.yaml`
- `aletheia_os/02_ACTIVE_STATE.md`
- `aletheia_os/03_FRONTIER_BOARD.md`
- `aletheia_os/04_RISK_REGISTER.md`
- `aletheia_os/07_EVIDENCE_INDEX.md`
- `aletheia_os/09_DOMAIN_PROFILE.md`
- `aletheia_os/hypotheses/`
- `aletheia_os/evidence/`
- `aletheia_os/decisions/`
- `aletheia_os/contracts/`
- `aletheia_os/session_notes/`
- `aletheia_os/bootstrap_intake/IMPORT_REPORT.md`

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
- validate AletheiaOS;
- remove this `BOOTSTRAP.md` file;
- create the first git checkpoint.

### Step 8 — Report result

Return:

1. initialized project identity;
2. initialization mode;
3. imported materials summary;
4. active frontier;
5. Global View Checksum;
6. files changed;
7. model gate status and agent run id;
8. checkpoint commit status;
9. next recommended task card.

## Forbidden during bootstrap

- Do not ask the operator to run internal scripts.
- Do not write production code.
- Do not run expensive experiments.
- Do not create speculative alpha, theory, product, or engineering branches without evidence.
- Do not delete existing project materials unless explicitly instructed.
- Do not import secrets, credentials, broker keys, API tokens, or sensitive vendor data into durable memory.
- Do not treat legacy research as truth without classification.
- Do not skip the initial git checkpoint.
