# aletheia_os/ Agent Rules


## Model gate

For any durable write in this directory, the current AI assistant must have an allowed agent run for the task class:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Unknown or under-tier models may read and orient only.

This directory is durable project memory and governance. Do not place production implementation logic here.

Before modifying this directory:

1. Identify the active system node and parent constraints.
2. Identify whether the change affects mission, graph structure, evidence, decisions, contracts, risk, or active state.
3. Preserve traceability: claims link to nodes; node changes link to evidence or decisions.

After modifying this directory:

1. Update `aletheia_os/02_ACTIVE_STATE.md` if frontier, blockers, active nodes, or next actions changed.
2. Update `aletheia_os/07_EVIDENCE_INDEX.md` if evidence files were added or retired.
3. Update affected node files or `aletheia_os/01_SYSTEM_GRAPH.yaml` if weight, confidence, dependencies, or status changed.
4. Run `python3 scripts/aios_validate.py`.
5. Create or recommend a checkpoint.
