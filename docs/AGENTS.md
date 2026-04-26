# docs/ Agent Rules


## Model gate

For any durable write in this directory, the current AI assistant must have an allowed agent run for the task class:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Unknown or under-tier models may read and orient only.

This directory contains human-facing documentation.

Rules:

- Architecture or protocol docs should point back to relevant project nodes, contracts, and decision records.
- Do not let docs become a second source of truth when `aletheia_os/` already owns the durable project state.
- Update docs when public usage, architecture, or operational procedures change.
