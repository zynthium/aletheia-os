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
- **Attention Policy**: how AI agents preserve top-down awareness under limited context
- **Checkpoint Policy**: when to validate, commit, rebalance, or stop

The aim is to prevent local AI-agent drift: every task should know its parent constraints, current node, success criteria, invalidation criteria, and downstream consequences.

## First-time initialization

For any AI coding assistant, `START_HERE.md` is the stable entry point after bootstrap. `BOOTSTRAP.md` is used only once and is deleted after initialization.

1. Create or enter a project directory.
2. Copy this scaffold into the directory.
3. Start Codex or Claude Code from the repository root.
4. Ask the assistant:

```text
Read BOOTSTRAP.md and initialize this project. Keep the abstraction domain-neutral unless I specify a domain profile. Before changing files, produce the Global View Checksum from START_HERE.md.
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

Use one active node per session. When starting or resuming work, run:

```bash
python3 scripts/aios_orient.py
```

This prints the top-down context pack and Global View Checksum template.

Workflow:

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

# Validate and print the top-down orientation pack
python3 scripts/aios_orient.py

# Create a safe project checkpoint commit
python3 scripts/aios_checkpoint.py --auto

# Finalize first-time initialization; removes BOOTSTRAP.md
python3 scripts/aios_bootstrap.py --finalize

# Enable local git pre-commit validation hook
python3 scripts/aios_bootstrap.py --configure-hooks
```

## Attention model

The scaffold uses a tiered attention policy rather than asking the assistant to read everything.

```text
Tier 0: START_HERE, AGENTS, Charter, Attention Policy, Active State
Tier 1: active system node and parent/child dependencies
Tier 2: contracts and decision records for crossed boundaries
Tier 3: evidence relevant to the current claim or promotion decision
Tier 4: local implementation files, tests, experiments, and simulations
```

This keeps the assistant anchored in the root mission while preventing the context window from being consumed by irrelevant branches. The detailed rules live in `project_os/10_ATTENTION_POLICY.md`.

## Where final implementation code belongs

For code-delivering projects, durable implementation code belongs under:

```text
src/<project_package_name>/
```

Examples:

```text
src/quant_system/
src/aircraft_design/
src/physics_sim/
src/market_optimizer/
```

Directory boundaries:

- `project_os/`: why the project exists, what is currently true, what evidence exists, what decisions were made.
- `src/`: reusable implementation code that may become production, simulation, or durable system code.
- `experiments/`: exploratory notebooks, runs, temporary analysis, and research trials.
- `simulations/`: scenario engines, replay environments, synthetic worlds, stress cases.
- `tests/`: verification of implementation, assumptions, interfaces, leakage, and regressions.
- `scripts/`: thin operational wrappers and repository tooling.

`experiments/` and `simulations/` may import from `src/`; `src/` must not import from `experiments/`.

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
├── START_HERE.md                  # Stable entry point for any AI coding assistant
├── AGENTS.md                      # Codex/repo-level agent operating rules
├── CLAUDE.md                      # Claude Code project memory, imports AGENTS.md
├── BOOTSTRAP.md                   # First-run initialization protocol; deleted after setup
├── README.md                      # Human-facing documentation
├── project_os/                    # Durable project memory and governance
│   ├── AGENTS.md
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
│   ├── 10_ATTENTION_POLICY.md
│   ├── contracts/
│   ├── decisions/
│   ├── evidence/
│   ├── hypotheses/
│   ├── nodes/
│   ├── playbooks/
│   ├── session_notes/
│   └── templates/
├── scripts/                       # Validation, orientation, bootstrap, checkpoint, context tooling
├── src/                           # Durable implementation code
├── tests/                         # Verification
├── experiments/                   # Exploratory work
├── simulations/                   # Simulation and stress scenarios
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
- Use `project_os/10_ATTENTION_POLICY.md` to prevent broad context loading and local drift.

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
