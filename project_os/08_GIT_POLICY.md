# Git Policy

Git is the memory boundary. If it is not committed, it is not durable project state.

## When to commit

Create a checkpoint when one of these occurs:

- bootstrap initialized or finalized;
- active state changed;
- system graph, node weight, dependency, or status changed;
- evidence record created or updated;
- decision record created or updated;
- interface contract changed;
- implementation changed and validation state is known;
- session distillation produced a durable next action;
- a blocker changes upstream assumptions.

## When not to auto-commit

Do not auto-commit when:

- validation fails;
- protected secret-like files are present;
- code changed but no state file records why;
- the task is mid-flight;
- generated/heavy artifacts dominate the diff;
- user explicitly asks not to commit.


## Model attribution in commits

Every non-trivial checkpoint should include agent attribution trailers. `scripts/aios_checkpoint.py` reads `.aios_runtime/current_agent_run.json` and appends these trailers when available:

```text
AIOS-Agent-Run: RUN-...
AIOS-Agent-Provider: ...
AIOS-Agent-Model: ...
AIOS-Agent-Tier: C3
AIOS-Task-Class: research_design
AIOS-Gate: allowed
```

If no current agent run exists, checkpointing is blocked by default when `project_os/model_registry.json` requires attribution. Override only with explicit operator intent.

## Auto-commit controls

```bash
export AIOS_AUTOCOMMIT=1                 # allow Claude Code stop-hook auto commits
export AIOS_ALLOW_CODE_ONLY_COMMIT=1     # allow code-only auto commits when validation passes
export AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1 # operator override for missing agent attribution
```

Manual checkpoint:

```bash
python3 scripts/aios_checkpoint.py --auto --message "checkpoint: explain durable change"
```

## Commit message prefixes

- `bootstrap:` initialization
- `state:` active state or frontier change
- `graph:` system graph update
- `hypothesis:` hypothesis update
- `evidence:` evidence record
- `decision:` decision record
- `contract:` interface contract
- `engineering:` implementation
- `risk:` risk register
- `session:` session distillation
- `checkpoint:` generic durable checkpoint
