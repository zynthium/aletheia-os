# src/ Agent Rules

This directory contains durable implementation code: libraries, applications, production modules, simulation engines, and reusable engineering assets.

Code placement rule:

```text
src/<project_package_name>/
```

Before changing code here:

1. Read `START_HERE.md`, `project_os/00_CHARTER.md`, `project_os/10_ATTENTION_POLICY.md`, and `project_os/02_ACTIVE_STATE.md`.
2. Identify the active system node and relevant parent constraints.
3. Identify affected contracts in `project_os/contracts/` or `project_os/06_INTERFACE_CONTRACTS.md`.
4. Classify the change as prototype, research-validated, production-candidate, or production.

Rules:

- `src/` may be imported by `experiments/`, `simulations/`, `tests/`, and scripts.
- `src/` must not depend on `experiments/` or runtime contents of `project_os/`.
- Business logic belongs in `src/`, not in `scripts/` or notebooks.
- Behavior-changing code must be paired with tests or an explicit reason tests cannot yet exist.
- Production-facing modules should have traceability to relevant project nodes, evidence, decisions, or contracts.

After changing code here:

1. Update tests.
2. Update affected contracts or decision records when boundaries changed.
3. Update `project_os/02_ACTIVE_STATE.md` or session notes for substantial work.
4. Run validation and checkpoint when coherent.
