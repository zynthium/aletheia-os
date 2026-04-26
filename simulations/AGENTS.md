# simulations/ Agent Rules


## Model gate

For any durable write in this directory, the current AI assistant must have an allowed agent run for the task class:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Unknown or under-tier models may read and orient only.

This directory is for simulation scenarios, replay environments, synthetic worlds, and stress cases.

Rules:

- Simulations must state what claim, design assumption, or risk they test.
- Simulation output is not self-interpreting evidence; create or update an evidence record.
- Calibration assumptions, boundary conditions, and invalid regimes must be explicit.
- If simulation feasibility changes upstream design, classify the blocker and update project state.
