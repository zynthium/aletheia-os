# AI-Native Project OS Scaffold

This repository is a domain-neutral operating scaffold for large, evolving projects where theory, engineering, evidence, and optimization must co-evolve.

It is designed for work with AI coding assistants such as Codex and Claude Code. The repository, not the chat window, is the long-term memory. The assistant is treated as a local executor, investigator, reviewer, and synthesis engine.

## Suitable project classes

Use this scaffold for projects where the goal cannot be reduced to a short software ticket:

- quantitative trading research and productionization
- theoretical physics programs with simulations and engineering artifacts
- aircraft, vehicle, robotics, energy, chip, or manufacturing system design
- market strategy, product strategy, supply-chain optimization, or portfolio allocation
- any project where top-level constraints can be invalidated by downstream feasibility discoveries

## Core idea

The project is represented as a **constraint-governed system graph**:

- **Charter**: mission, non-negotiable constraints, priority order
- **System Graph**: objectives, theories, design branches, capabilities, interfaces, and dependencies
- **Active State**: current frontier, blockers, protected assumptions, next actions
- **Evidence Ledger**: experiments, simulations, field tests, market observations, proof attempts
- **Decision Records**: durable design/theory/product/engineering decisions
- **Interface Contracts**: boundaries between modules, disciplines, teams, or abstractions
- **Risk Register**: uncertainty, failure modes, invalidation paths
- **Checkpoint Policy**: when to validate, commit, rebalance, or stop

The aim is to prevent local AI-agent drift: every task should know its parent constraints, current node, success criteria, invalidation criteria, and downstream consequences.

## First-time initialization

1. Create or enter a project directory.
2. Copy this scaffold into the directory.
3. Start Codex or Claude Code from the repository root.
4. Ask the assistant:

```text
Read BOOTSTRAP.md and initialize this project. Keep the abstraction domain-neutral unless I specify a domain profile.
```

5. The assistant should customize:
   - `project_os/00_CHARTER.md`
   - `project_os/01_SYSTEM_GRAPH.yaml`
   - `project_os/02_ACTIVE_STATE.md`
   - `project_os/09_DOMAIN_PROFILE.md`
6. Run:

```bash
python3 scripts/aios_bootstrap.py --finalize
```

This validates the scaffold, configures local git hooks, removes `BOOTSTRAP.md`, and creates the initial git checkpoint.

## Daily workflow

Use one active node per session.

```text
1. Orient: identify active graph node, parent constraints, success/failure criteria.
2. Frame: define goal, non-goals, tests, evidence requirements, and stop conditions.
3. Execute: implement, research, simulate, derive, test, or review.
4. Verify: run engineering checks, evidence checks, and graph-consistency checks.
5. Commit: update evidence, decisions, contracts, active state, and git checkpoint.
6. Distill: write a session note and clear/reset AI context.
```

## Important commands

```bash
# Validate required project-state files and linkage rules
python3 scripts/aios_validate.py

# Print a compact context pack for a new AI session
python3 scripts/aios_context_pack.py

# Create a safe project checkpoint commit
python3 scripts/aios_checkpoint.py --auto

# Finalize first-time initialization; removes BOOTSTRAP.md
python3 scripts/aios_bootstrap.py --finalize

# Enable local git pre-commit validation hook
python3 scripts/aios_bootstrap.py --configure-hooks
```

## Auto checkpoint behavior

This scaffold supports conservative automatic git commits.

By default, Claude Code's stop hook only validates and reports whether a checkpoint is recommended. To allow automatic commits on stop events, set:

```bash
export AIOS_AUTOCOMMIT=1
```

A stop-event checkpoint is allowed only when:

- validation passes;
- git has changes;
- no protected secret-like files are staged;
- the task has updated durable project state, such as `project_os/02_ACTIVE_STATE.md`, `project_os/evidence/`, `project_os/decisions/`, `project_os/contracts/`, or `project_os/session_notes/`.

This avoids committing half-finished code-only edits without project-state synchronization. To allow code-only auto commits, set:

```bash
export AIOS_ALLOW_CODE_ONLY_COMMIT=1
```

Manual checkpointing is always possible:

```bash
python3 scripts/aios_checkpoint.py --auto --message "checkpoint: complete active-node update"
```

## Directory map

```text
.
├── AGENTS.md                      # Codex/repo-level agent operating rules
├── CLAUDE.md                      # Claude Code project memory, imports AGENTS.md
├── BOOTSTRAP.md                   # First-run initialization protocol; deleted after setup
├── README.md                      # Human-facing documentation
├── project_os/                    # Durable project memory and governance
│   ├── 00_CHARTER.md
│   ├── 01_SYSTEM_GRAPH.yaml
│   ├── 02_ACTIVE_STATE.md
│   ├── 03_FRONTIER_BOARD.md
│   ├── 04_RISK_REGISTER.md
│   ├── 05_GLOSSARY.md
│   ├── 06_INTERFACE_CONTRACTS.md
│   ├── 07_EVIDENCE_INDEX.md
│   ├── 08_GIT_POLICY.md
│   ├── 09_DOMAIN_PROFILE.md
│   ├── contracts/
│   ├── decisions/
│   ├── evidence/
│   ├── hypotheses/
│   ├── nodes/
│   ├── playbooks/
│   ├── session_notes/
│   └── templates/
├── scripts/                       # Validation, bootstrap, checkpoint, context tooling
├── .agents/skills/                # Codex-compatible skills
├── .claude/skills/                # Claude Code-compatible skills
├── .claude/agents/                # Claude Code subagents
├── .claude/settings.json          # Project-level Claude Code hooks
└── .githooks/pre-commit           # Optional git hook path
```

## Operating rules

- Do not let the assistant work from chat memory alone.
- Do not accept unlinked claims. Every claim should attach to a system-graph node, evidence item, or decision record.
- Do not allow local optimization to rewrite global goals silently.
- Do not move an idea toward production without evidence, interfaces, and invalidation criteria.
- Treat implementation failures as possible upstream design evidence.
- Keep root instructions short; move repeatable workflows into skills and playbooks.

## Commit message convention

```text
bootstrap: initialize AI project OS
state: update active project state
graph: update system graph
hypothesis: add or revise hypothesis
evidence: add experiment/simulation/proof/field evidence
decision: add or revise decision record
contract: update interface or boundary contract
engineering: implement or refactor system component
risk: update risk register
session: add session distillation
checkpoint: durable project checkpoint
```
