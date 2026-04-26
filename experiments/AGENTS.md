# experiments/ Agent Rules


## Model gate

For any durable write in this directory, the current AI assistant must have an allowed agent run for the task class:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Unknown or under-tier models may read and orient only.

This directory is for exploratory work, experiment configurations, notebooks, reports, and temporary analysis.

Rules:

- Experiments may import reusable code from `src/`.
- `src/` must not import from `experiments/`.
- A meaningful experiment should produce or update an evidence record in `project_os/evidence/`.
- Do not promote experimental code to production by copy-paste. Extract reusable logic into `src/`, add tests, and link to evidence/contracts.
- Record method, data, assumptions, result, interpretation, and graph impact.

After a substantial experiment:

1. Update `project_os/evidence/`.
2. Update `project_os/02_ACTIVE_STATE.md` and possibly `project_os/01_SYSTEM_GRAPH.yaml`.
3. Run validation and checkpoint when coherent.
