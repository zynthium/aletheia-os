# Guided Bootstrap Playbook

This playbook tells an AI coding assistant how to initialize an AletheiaOS project when prior project materials may already exist.

## Trigger

Use this playbook when:

- `BOOTSTRAP.md` exists;
- the operator asks to initialize, adopt, migrate, or set up AletheiaOS;
- the repository contains prior notes, code, experiments, notebooks, simulations, or design docs.

## Assistant responsibilities

The assistant is responsible for orchestrating bootstrap. The operator should not need to know which internal scripts to run.

The assistant must:

1. orient from project governance files;
2. gate itself before writes;
3. inventory existing materials;
4. classify sources by reliability and sensitivity;
5. synthesize durable project state;
6. validate;
7. finalize;
8. checkpoint;
9. report.

## Sequence

### 1. Orient

Read:

- `START_HERE.md`
- `AGENTS.md`
- `aletheia_os/10_ATTENTION_POLICY.md`
- `aletheia_os/11_MODEL_GOVERNANCE.md`
- `aletheia_os/12_INTAKE_POLICY.md`
- `BOOTSTRAP.md`

Then produce the Global View Checksum.

### 2. Gate

Run:

```bash
python3 scripts/aios_model_gate.py --task-class bootstrap_finalize --record --objective "Guided bootstrap"
```

If the gate denies write access, stop.

### 3. Inventory

Run:

```bash
python3 scripts/aios_intake_inventory.py
```

Use the resulting inventory to decide whether the project is greenfield, brownfield, or migration.

### 4. Selective read

Do not read everything. Load materials in this order:

1. root README and mission docs;
2. architecture and design docs;
3. hypothesis/theory notes;
4. evidence, experiment, or simulation reports;
5. tests and validation files;
6. implementation entry points;
7. operations/risk/safety notes.

Skip secrets, raw data, large files, build outputs, dependency directories, and caches.

### 5. Synthesize

Create or update durable project state. Convert materials into the correct record type instead of copying them indiscriminately.

### 6. Validate and finalize

Run:

```bash
python3 scripts/aios_validate.py
python3 scripts/aios_orient.py
python3 scripts/aios_bootstrap.py --finalize
```

### 7. Report

Report the import summary, confidence level, unresolved conflicts, deferred items, checkpoint status, and next task card.

## Stop conditions

Stop and ask for operator input only if:

- secrets or credentials are encountered;
- repository state is too ambiguous to classify safely;
- model gate denies the write;
- validation fails for reasons that require owner intent;
- existing materials appear to imply safety-critical or regulated behavior.
