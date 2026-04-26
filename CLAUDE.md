@AGENTS.md

# CLAUDE.md — Claude Code Project Memory

## Claude Code-specific workflow

## Model gate and attribution

Claude Code project hooks run `scripts/aios_model_gate.py` on session start and before write-capable tools. Session start records detected model metadata into the runtime environment when available. Before durable writes, explicitly gate the task:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

If the gate blocks the task, stop and report the model id, task class, required tier, and allowed fallback.


- Use planning before changing `project_os/`, core interfaces, production code, experiments, or simulations.
- Use subagents for exploration, adversarial review, evidence curation, engineering review, and objective/portfolio review when the task is multi-step.
- Keep the main conversation anchored on the active node and parent constraints.
- Prefer durable file updates over conversational summaries.
- At the start of a non-trivial session, run or mentally reproduce `python3 scripts/aios_orient.py`.

## Context management

For long sessions, use compaction with this preservation target:

```text
Preserve root mission, priority order, active frontier, active node, parent constraints, modified files, evidence generated, decisions made, contracts changed, validation run, blockers, checkpoint status, and next action.
```

After a task completes:

1. write or update a session note;
2. update `project_os/02_ACTIVE_STATE.md`;
3. update evidence, decisions, contracts, graph, or node files when affected;
4. run validation;
5. create a checkpoint commit when appropriate;
6. start the next task from repository state, not from stale chat momentum.

## Attention and drift control

Use `project_os/10_ATTENTION_POLICY.md` as the context-loading policy. Do not load broad local implementation context before the active system node and parent constraints are identified.

Stop and reorient if:

- the active node is unclear;
- a local edit changes an upstream assumption;
- implementation feasibility changes the design space;
- the task begins optimizing a proxy metric rather than the explicit objective;
- the current conversation has become a poor representation of repository state.

## Hook behavior

Project hooks are configured in `.claude/settings.json`.

- Session start detects model metadata and reminds the assistant to gate the task.
- Pre-tool hooks block write-capable tool calls unless an allowed agent run is recorded.
- File writes/edits are logged to `.aios_runtime/change_log.jsonl`.
- Stop events run `scripts/aios_stop_hook.py`.
- Automatic commits require `AIOS_AUTOCOMMIT=1`.

## Subagents

Use `.claude/agents/` roles when relevant:

- `project-architect`: graph structure, constraints, branch weights, upstream/downstream impact.
- `adversarial-reviewer`: falsification, leakage, hidden assumptions, overfitting, feasibility traps.
- `evidence-curator`: evidence ledger, decision records, session distillation.
- `systems-engineer`: productionization, interfaces, tests, automation, reproducibility.
- `objective-optimizer`: trade-offs, portfolio/resource allocation, priority rebalance.
