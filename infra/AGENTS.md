# infra/ Agent Rules


## Model gate

For any durable write in this directory, the current AI assistant must have an allowed agent run for the task class:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Unknown or under-tier models may read and orient only.

This directory contains deployment, environment, monitoring, container, or infrastructure definitions.

Rules:

- Infrastructure changes must preserve reproducibility, rollback, observability, and secret hygiene.
- Production-facing infrastructure changes should update affected contracts, runbooks, or decision records.
- Do not commit credentials, keys, tokens, or local-only infrastructure state.
