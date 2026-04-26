# src/ Agent Rules


## Model gate

For any durable write in this directory, the current AI assistant must have an allowed agent run for the task class:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Unknown or under-tier models may read and orient only.

This directory contains durable implementation code: libraries, applications, production modules, simulation engines, and reusable engineering assets.

Code placement rule:

```text
src/<project_package_name>/
```

Before changing code here:

1. Read `START_HERE.md`, `aletheia_os/00_CHARTER.md`, `aletheia_os/10_ATTENTION_POLICY.md`, and `aletheia_os/02_ACTIVE_STATE.md`.
2. Identify the active system node and relevant parent constraints.
3. Identify affected contracts in `aletheia_os/contracts/` or `aletheia_os/06_INTERFACE_CONTRACTS.md`.
4. Classify the change as prototype, research-validated, production-candidate, or production.

Rules:

- `src/` may be imported by `experiments/`, `simulations/`, `tests/`, and scripts.
- `src/` must not depend on `experiments/` or runtime contents of `aletheia_os/`.
- Business logic belongs in `src/`, not in `scripts/` or notebooks.
- Behavior-changing code must be paired with tests or an explicit reason tests cannot yet exist.
- Production-facing modules should have traceability to relevant project nodes, evidence, decisions, or contracts.

After changing code here:

1. Update tests.
2. Update affected contracts or decision records when boundaries changed.
3. Update `aletheia_os/02_ACTIVE_STATE.md` or session notes for substantial work.
4. Run validation and checkpoint when coherent.
