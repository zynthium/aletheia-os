# project_os/ Agent Rules

This directory is durable project memory and governance. Do not place production implementation logic here.

Before modifying this directory:

1. Identify the active system node and parent constraints.
2. Identify whether the change affects mission, graph structure, evidence, decisions, contracts, risk, or active state.
3. Preserve traceability: claims link to nodes; node changes link to evidence or decisions.

After modifying this directory:

1. Update `project_os/02_ACTIVE_STATE.md` if frontier, blockers, active nodes, or next actions changed.
2. Update `project_os/07_EVIDENCE_INDEX.md` if evidence files were added or retired.
3. Update affected node files or `project_os/01_SYSTEM_GRAPH.yaml` if weight, confidence, dependencies, or status changed.
4. Run `python3 scripts/aios_validate.py`.
5. Create or recommend a checkpoint.
