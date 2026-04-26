@AGENTS.md

# CLAUDE.md — Claude Code Project Memory

## Claude Code-specific workflow

- Use planning before changing `project_os/`, core interfaces, production code, experiments, or simulations.
- Use subagents for exploration, adversarial review, evidence curation, and engineering review when the task is multi-step.
- Keep the main conversation anchored on the active node and parent constraints.
- Prefer durable file updates over conversational summaries.

## Context management

For long sessions, use compaction with this preservation target:

```text
Preserve active node, parent constraints, modified files, evidence generated, decisions made, contracts changed, validation run, blockers, and next action.
```

After a task completes:

1. write or update a session note;
2. update `project_os/02_ACTIVE_STATE.md`;
3. run validation;
4. create a checkpoint commit when appropriate;
5. start the next task from repository state, not from stale chat momentum.

## Hook behavior

Project hooks are configured in `.claude/settings.json`.

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
