# AletheiaOS

[简体中文](README.zh-CN.md)

**Truthful project memory for AI-assisted research and engineering.**

AletheiaOS is an AI-native project operating system for long-horizon
research and engineering projects where theory, implementation, evidence,
risk, and optimization must co-evolve.

It is designed for projects that are too complex to be managed as ordinary
tickets, notes, or chat threads: quantitative trading systems, theoretical
research programs, aircraft or vehicle design, robotics, simulations, market
strategy, product strategy, and other evolving systems where local
implementation discoveries can invalidate top-level assumptions.

AletheiaOS treats the repository, not the chat window, as the durable memory
of the project. AI coding assistants such as Codex and Claude Code are used as
executors, investigators, reviewers, and synthesis engines, while the project
itself remains governed by charters, system graphs, evidence ledgers, model
gates, generated overviews, and git checkpoints.

## Why AletheiaOS exists

AI agents are powerful at local execution but fragile at long-horizon
coherence. In large research-engineering projects, they easily drift toward:

- local optimization
- stale assumptions
- unlinked claims
- forgotten parent constraints
- undocumented decisions
- code that no longer reflects the theory
- experiments that never update the project state
- unclear attribution of which model changed what

AletheiaOS prevents this by making project state explicit, structured,
validated, and version-controlled.

## What this is / is not

AletheiaOS is:

- a project memory system for AI-assisted work;
- a governance scaffold for long-horizon research and engineering;
- a way to preserve top-down constraints under limited model context;
- a framework for evidence, decisions, model attribution, and checkpoints;
- a repository-native operating protocol for Codex, Claude Code, and similar tools.

AletheiaOS is not:

- a task manager;
- a generic notes app;
- a replacement for git;
- a replacement for human judgment;
- a guarantee that weak AI models can perform high-level research;
- a magic layer that makes unstructured projects coherent automatically.

## Suitable project classes

Use AletheiaOS for projects where the goal cannot be reduced to a short
software ticket:

- quantitative trading research and productionization
- theoretical physics programs with simulations and engineering artifacts
- aircraft, vehicle, robotics, energy, chip, or manufacturing system design
- market strategy, product strategy, supply-chain optimization, or portfolio allocation
- any project where top-level constraints can be invalidated by downstream feasibility discoveries

## Core idea

AletheiaOS represents a project as a **constraint-governed system graph**:

- **Charter**: mission, non-negotiable constraints, priority order
- **System Graph**: objectives, theories, design branches, capabilities, interfaces, and dependencies
- **Active State**: current frontier, blockers, protected assumptions, next actions
- **Evidence Ledger**: experiments, simulations, field tests, market observations, proof attempts
- **Decision Records**: durable design/theory/product/engineering decisions
- **Interface Contracts**: boundaries between modules, disciplines, teams, or abstractions
- **Risk Register**: uncertainty, failure modes, invalidation paths
- **Attention Policy**: how AI agents preserve top-down awareness under limited context
- **Checkpoint Policy**: when to validate, commit, rebalance, or stop

The aim is to prevent local AI-agent drift. Every task should know its parent
constraints, current node, success criteria, invalidation criteria, and
downstream consequences.

## Human overview

AletheiaOS supports a generated human-facing overview layer.

The overview is not a manually maintained status page. It is generated from
the actual project state:

- system graph
- active state
- evidence ledger
- decision records
- risk register
- interface contracts
- git state
- validation results
- agent attribution records

Recommended generated artifacts:

```text
docs/overview/index.html        # project cockpit
docs/overview/system_map.svg    # system graph visualization
docs/overview/status.json       # compiled project state
docs/overview/nodes/            # drill-down pages for graph nodes
```

Truthfulness rules:

- overview artifacts are generated, not manually edited;
- missing state is shown as `unknown`, not inferred as healthy;
- stale state is shown explicitly;
- every displayed status links back to source files or git state;
- overview generation should fail or warn when project state is inconsistent.

## Use as a project scaffold

Use this repository as a GitHub template, or clone it into a new project and
run the bootstrap flow:

```bash
git clone https://github.com/<your-org>/aletheia-os.git my-project
cd my-project
rm -rf .git
git init
python3 scripts/aios_bootstrap.py --finalize
```

No remote is configured in this checkout, so replace `<your-org>` with the
actual repository owner before publishing the command.

## First-time initialization

For any AI coding assistant, `START_HERE.md` is the stable entry point after
bootstrap. `BOOTSTRAP.md` is used only once and is deleted after
initialization.

1. Create or enter a project directory.
2. Copy AletheiaOS into the directory.
3. Start Codex or Claude Code from the repository root.
4. Ask the assistant:

```text
Read BOOTSTRAP.md and initialize this project. Keep the abstraction domain-neutral unless I specify a domain profile. Before changing files, produce the Global View Checksum from START_HERE.md.
```

5. The assistant should customize:
   - `aletheia_os/00_CHARTER.md`
   - `aletheia_os/01_SYSTEM_GRAPH.yaml`
   - `aletheia_os/02_ACTIVE_STATE.md`
   - `aletheia_os/09_DOMAIN_PROFILE.md`
6. Run:

```bash
python3 scripts/aios_bootstrap.py --finalize
```

This validates AletheiaOS, configures local git hooks, removes
`BOOTSTRAP.md`, and creates the initial git checkpoint.

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

The current script prefix `aios_` stands for AletheiaOS.

```bash
# Validate required project-state files and linkage rules
python3 scripts/aios_validate.py

# Gate the current AI assistant for a task and record attribution
python3 scripts/aios_model_gate.py --task-class research_design --record --objective "short objective"

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

## Model governance and attribution

AletheiaOS includes a capability gate for AI coding assistants. It does not
assume every model is competent enough for research-heavy work. Before durable
writes, the assistant should run:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

The gate checks `aletheia_os/model_registry.json` and creates an attribution
record under `aletheia_os/agent_runs/`. Unknown models are read-only by
default. For tools that do not expose a model identifier, set explicit
metadata:

```bash
AIOS_AGENT_PROVIDER=openai \
AIOS_MODEL_ID="provider-model-id" \
AIOS_AGENT_TOOL=codex \
python3 scripts/aios_model_gate.py --task-class research_design --record --objective "Design evidence protocol"
```

Capability tiers are practical governance tiers, not literal IQ scores:

```text
C0: unknown/read-only
C1: basic helper/documentation
C2: engineering executor
C3: research-engineering model
C4: strategic research lead / safety-critical model
```

Every non-trivial checkpoint should include agent attribution trailers in the
git commit message. Configure approved models in
`aletheia_os/model_registry.json`; keep weak or unwanted models in the denylist.

## Attention model

AletheiaOS uses a tiered attention policy rather than asking the assistant to
read everything.

```text
Tier 0: START_HERE, AGENTS, Charter, Attention Policy, Model Governance, Active State
Tier 1: active system node and parent/child dependencies
Tier 2: contracts and decision records for crossed boundaries
Tier 3: evidence relevant to the current claim or promotion decision
Tier 4: local implementation files, tests, experiments, and simulations
```

This keeps the assistant anchored in the root mission while preventing the
context window from being consumed by irrelevant branches. The detailed rules
live in `aletheia_os/10_ATTENTION_POLICY.md`.

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

- `aletheia_os/`: why the project exists, what is currently true, what evidence exists, what decisions were made.
- `src/`: reusable implementation code that may become production, simulation, or durable system code.
- `experiments/`: exploratory notebooks, runs, temporary analysis, and research trials.
- `simulations/`: scenario engines, replay environments, synthetic worlds, stress cases.
- `tests/`: verification of implementation, assumptions, interfaces, leakage, and regressions.
- `scripts/`: thin operational wrappers and repository tooling.

`experiments/` and `simulations/` may import from `src/`; `src/` must not
import from `experiments/`.

## Auto checkpoint behavior

AletheiaOS supports conservative automatic git commits.

By default, Claude Code's stop hook only validates and reports whether a
checkpoint is recommended. To allow automatic commits on stop events, set:

```bash
export AIOS_AUTOCOMMIT=1
```

A stop-event checkpoint is allowed only when:

- validation passes;
- git has changes;
- no protected secret-like files are staged;
- an allowed agent run is recorded, unless the operator explicitly overrides attribution;
- the task has updated durable project state, such as `aletheia_os/02_ACTIVE_STATE.md`, `aletheia_os/evidence/`, `aletheia_os/decisions/`, `aletheia_os/contracts/`, or `aletheia_os/session_notes/`.

This avoids committing half-finished code-only edits without project-state
synchronization or model attribution. To allow code-only auto commits, set:

```bash
export AIOS_ALLOW_CODE_ONLY_COMMIT=1
```

To deliberately bypass missing model attribution for a manual/operator commit
only:

```bash
export AIOS_ALLOW_UNATTRIBUTED_CHECKPOINT=1
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
├── aletheia_os/                   # Durable project memory and governance
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
│   ├── 11_MODEL_GOVERNANCE.md
│   ├── model_registry.json
│   ├── agent_runs/
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
- Use `aletheia_os/10_ATTENTION_POLICY.md` to prevent broad context loading and local drift.

## Commit message convention

```text
bootstrap: initialize AletheiaOS
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
