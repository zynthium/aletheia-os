# AletheiaOS

[简体中文](README.zh-CN.md)

![AletheiaOS hero](docs/assets/readme-hero.jpg)

**A repo-native falsifiable truth tree layer for AI-assisted research and engineering.**

**One repo. One falsifiable truth tree. Many agents.**

AletheiaOS = Root-based Truth Tree + Scientific Method Loop + Repo-native Memory + Agent Governance.

AletheiaOS uses `.aletheia/` to maintain the single trusted fact source for a complex project: root objective, current state, system graph, project skeleton, tree governance rules, architecture constraints, research evidence, decision records, interface contracts, risks, and agent attribution. It is not just a repo-native truth layer, and it is not a generic project documentation system. It organizes project facts as a reviewable, falsifiable, evolvable truth tree.

The falsifiable truth tree layer is the upgraded form of a repo-native truth layer: the repo-native truth layer stores project facts, while truth tree governance constrains how those facts grow, get falsified, get promoted, and get refactored.

AletheiaOS maintains complex projects as a root-based truth tree:

- The root defines the core objective or research question.
- The trunk defines core objects, main theories, or the system skeleton.
- Branches hold sub-theories, subsystems, architecture directions, or research paths.
- Leaves hold concrete evidence, hypotheses, decisions, contracts, implementation, and tasks.
- Unmounted material enters the orphan/incubator for review, attachment, splitting, merging, or archival.

The tree evolves through a scientific-method loop: observation -> hypothesis -> evidence -> falsification criteria -> decision -> engineering -> feedback -> tree refactor.

In AletheiaOS, truth means the current most trusted, reviewable, falsifiable project facts. It does not mean absolute truth.

AletheiaOS is for long-running research and engineering projects where theory, implementation, evidence, risk, and optimization evolve together, and where local implementation findings can overturn top-level assumptions. AletheiaOS does not replace Codex, Claude Code, OpenSpec, Superpowers, gstack, Compound, or other AI coding workflows. It gives them the same repo-native project truth.

## Why AletheiaOS Exists

AI agents are good at local execution, but fragile at long-term consistency. AletheiaOS is not solving a missing-folder problem. It addresses unstructured growth in complex AI-assisted development:

- agents keep adding code, features, docs, and conclusions without tying them back to a root objective;
- new ideas have no clear trunk, branch, or parent node;
- local implementation, research findings, and architecture decisions drift apart or override parent constraints;
- important claims lack evidence strength, falsification criteria, downgrade conditions, or follow-up decisions;
- weakened or falsified hypotheses keep supporting active decisions;
- multiple agents or tools work from different versions of project truth;
- developers and researchers keep optimizing low-weight leaves while drifting away from the trunk.

AletheiaOS reduces this drift by making project facts explicit, tree-shaped, verifiable, and version-controlled. It makes agents locate the root objective, active node, parent constraints, and evidence state before deciding whether new material belongs in the main tree, the orphan/incubator, or a tree refactor.

## Who Should Use It

AletheiaOS fits developers who use AI agents to maintain complex research and engineering projects, especially when:

- project goals and constraints must survive over time;
- architecture keeps evolving;
- research findings and design tradeoffs must become evidence and decisions;
- claims, evidence, decisions, and implementation need clear boundaries;
- multiple agents should orient from the same project facts before each work session;
- important project state should not live only in chat context.

## Features

- Initialize a `.aletheia/` truth layer in a target repository.
- Guide agents to read mission, active state, system graph, skeleton, and active node from a single fact source.
- Run model capability gates and agent attribution before durable writes.
- Record evidence, decisions, contracts, risks, and session notes.
- Support architecture evolution, constraint tracing, and progressive system decomposition.
- Force agents to decide whether new facts belong in the main tree or in the orphan/incubator for review.
- In large-source scenarios, guide agents to compile research space in an external LLM Wiki before promoting confirmed findings into project truth.
- Use `python3 .aletheia/bin/help.py` and `.aletheia/CAPABILITY_MAP.md` to discover project-truth actions agents can perform.
- Provide repo-native validation, overview, bootstrap finalize, and checkpoint runtime.
- Manage task class, capability tier, registered models, and denylist through model registry.
- Maintain user actions, agent capabilities, and truth record CRUD coverage in `.aletheia/CAPABILITY_MAP.md`.

## Installation

### Recommended: One Command

Install globally into Claude Code and register the Codex marketplace:

```bash
python3 scripts/install_aletheia.py --host both --scope user
```

Install at project scope and copy optional Codex subagents into the target repository:

```bash
python3 scripts/install_aletheia.py --host both --scope project --project /path/to/target-repo --with-codex-agents
```

If you want installation to initialize the target repository's `.aletheia/` truth layer:

```bash
python3 scripts/install_aletheia.py --host both --scope project --project /path/to/target-repo --with-codex-agents --init-project
```

Claude Code can complete marketplace registration and plugin installation through the CLI. Codex CLI can currently register the marketplace; after registration, open `/plugins` in Codex and enable `aletheia-os` from the AletheiaOS marketplace. Codex plugin enablement is a host UI limitation, not a project capability that repository scripts can complete directly.

### Manual Installation

Global Claude Code installation:

```bash
claude plugin marketplace add zynthium/aletheia-os --scope user
claude plugin install aletheia-os@aletheia-os --scope user
```

Project-scoped Claude Code installation:

```bash
claude plugin marketplace add zynthium/aletheia-os --scope project
claude plugin install aletheia-os@aletheia-os --scope project
```

Register the Codex marketplace globally:

```bash
codex plugin marketplace add zynthium/aletheia-os
```

Then open `/plugins` in Codex and enable `aletheia-os`.

### Local Development Installation

For local development, test directly from the current checkout or from a release directory. AletheiaOS includes both `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json`, so the same release directory can be used by Codex and Claude Code.

```bash
python3 scripts/package_plugin.py --output /tmp/aletheia-os-dist
```

Output:

```text
/tmp/aletheia-os-dist/aletheia-os/
```

The directory contains `.codex-plugin/`, `.claude-plugin/`, `.agents/`, `agents/`, `codex-agents/`, `skills/`, `assets/`, `scripts/`, `README.md`, and `README.zh-CN.md`.

Local Claude Code smoke test:

```bash
claude plugin validate .
claude --plugin-dir .
```

Real host smoke acceptance is documented in [Host Smoke Checklist](docs/verification/host-smoke.zh-CN.md).

## Quick Start

1. Install the plugin.
2. Initialize the target repository's `.aletheia/`.
3. Ask the agent to orient on current project truth.
4. Do the current work.
5. Update affected truth records.
6. Validate and checkpoint.

### New Projects

A new project can start as a normal git repository and then add the AletheiaOS truth layer:

```bash
mkdir my-project
cd my-project
git init
python3 /path/to/aletheia-os/scripts/init_aletheia.py .
```

You can also generate `.aletheia/` during project-scoped plugin installation:

```bash
python3 /path/to/aletheia-os/scripts/install_aletheia.py --host both --scope project --project . --with-codex-agents --init-project
```

Then ask the AI assistant to follow `BOOTSTRAP.md` and build the first project-truth synthesis:

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/bootstrap_finalize.py
```

Do not let agents invent the mission, domain facts, or architecture conclusions for a new project. First write down project intent, constraints, known boundaries, and initial candidate directions, then synthesize them into `.aletheia/governance/`, `.aletheia/state/`, `.aletheia/nodes/`, `.aletheia/evidence/`, `.aletheia/decisions/`, `.aletheia/contracts/`, and `.aletheia/risks/`.

### Existing Projects

Existing projects can add AletheiaOS directly. Check the current worktree first, then initialize:

```bash
cd /path/to/existing-project
git status --short
python3 /path/to/aletheia-os/scripts/init_aletheia.py .
```

Initialization adds the AletheiaOS control plane without replacing existing source code, tests, build configuration, or public documentation. Then ask the AI assistant to build the first project-truth version from existing material:

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/bootstrap_finalize.py
```

The point is not to dump every existing artifact into `.aletheia/`. Start with a reviewable fact skeleton: current mission, system graph, project skeleton, active state, important decisions, boundary contracts, existing evidence, and major risks. Source code remains the implementation and data plane; `.aletheia/` stores long-term project truth that guides future agent work.

### Initialize a Target Repository

```bash
python3 scripts/init_aletheia.py /path/to/target-repo
```

The target repository receives:

```text
AGENTS.md
START_HERE.md
BOOTSTRAP.md
.claude/settings.json
.aletheia/
```

`.claude/settings.json` configures SessionStart, PreToolUse, PostToolUse, and Stop hooks that run gates and audits through `.aletheia/bin/model_gate.py`, `change_hook.py`, and `stop_hook.py`.

`bootstrap_finalize.py` installs AletheiaOS Git hooks and points the target repository's `core.hooksPath` at `.aletheia/hooks`. In other words, bootstrap finalize installs AletheiaOS Git hooks by default; this is the local hard constraint that keeps later commits passing `.aletheia/bin/validate.py`.

### Validate the Bundled Scaffold

```bash
python3 scripts/validate_scaffold.py assets/scaffold
```

## Daily Loop

```text
orient -> work -> update truth -> validate -> checkpoint
```

In daily use, agents should first read `.aletheia/START_HERE.md`, then work around the current active node. After non-trivial work, update evidence, decision, contract, risk, node, session note, or active state, then run validation and checkpoint.

## What Is in `.aletheia/`

An initialized target repository contains:

```text
.aletheia/
  START_HERE.md
  VERSION
  governance/
  state/
  hypotheses/
  nodes/
  playbooks/
  decisions/
  evidence/
  contracts/
  risks/
  session_notes/
  agent_runs/
  templates/
  bin/
```

`CAPABILITY_MAP.md` is the action parity inventory. It records the mapping between user actions and agent capabilities for installation, initialization, orient, context pack, tree governance review, truth record create/list/show/update/archive, model gate, source inventory, bootstrap finalize, validate, overview, checkpoint, truth promotion, and read-only review agents.

`bin/` provides help, capability audit, orient, context pack, system context, preflight, status refresh, truth record, model gate, source inventory, guided bootstrap, overview, validate, bootstrap finalize, checkpoint, and Claude hook runtime. `orient.py` outputs cache-friendly stable facts and a compact record inventory by default. `context_pack.py` outputs core truth files, the capability map, compact source inventory summary, and complete truth record inventory. `system_context.py` outputs a dynamic context block that can be pasted into an agent prompt, combining stable project facts, user preferences, capability map, and optional runtime context. Current agent run and recent session notes require explicit `--with-runtime` and are appended after stable context. `status.py` is the explicit dynamic refresh entry point for active state, validation, record counts, runtime gate, recent changes, generated-output boundaries, and next actions. `capability_audit.py` checks whether `.aletheia/CAPABILITY_MAP.md` covers runtime scripts, skills, review agents, and CRUD commands. `preflight.py` is the explicit check entry point for Codex and other hosts without automatic hook enforcement; it reads model gate, validation, git status, checkpoint candidate, generated-output boundaries, and recommended action ids. `playbooks/prompt_native_boundaries.md` documents which runtime scripts should stay primitive and which workflow judgment should move into skills or playbooks.

## Runtime Reference

```bash
python3 .aletheia/bin/bootstrap_finalize.py
python3 .aletheia/bin/help.py
python3 .aletheia/bin/action.py list --json
python3 .aletheia/bin/action.py next --json
python3 .aletheia/bin/action.py explain truth.validate --json
python3 .aletheia/bin/capability_audit.py
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/orient.py --with-runtime
python3 .aletheia/bin/orient.py --static
python3 .aletheia/bin/context_pack.py
python3 .aletheia/bin/context_pack.py --with-runtime
python3 .aletheia/bin/system_context.py
python3 .aletheia/bin/system_context.py --with-runtime
python3 .aletheia/bin/preflight.py
python3 .aletheia/bin/preflight.py --json
python3 .aletheia/bin/status.py
python3 .aletheia/bin/status.py --json
python3 .aletheia/bin/truth_record.py list evidence
python3 .aletheia/bin/truth_record.py create evidence --id EV-0001 --title "Claim title"
python3 .aletheia/bin/truth_record.py show evidence EV-0001
python3 .aletheia/bin/truth_record.py update evidence EV-0001 --status active
python3 .aletheia/bin/truth_record.py archive evidence EV-0001 --reason "Superseded by stronger evidence"
python3 .aletheia/bin/truth_record.py show charter current
python3 .aletheia/bin/truth_record.py create orphan --id ORPH-0001 --title "Unmounted claim"
python3 .aletheia/bin/truth_record.py list orphan --json
python3 .aletheia/bin/truth_record.py show orphan ORPH-0001 --json
python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --status reviewed
python3 .aletheia/bin/truth_record.py update orphan ORPH-0001 --candidate-parent root --source-ref .aletheia/evidence/EV-0001.md --next-review 2099-01-01 --evidence-needed "Confirm with source inventory" --disposition attach
python3 .aletheia/bin/truth_record.py archive orphan ORPH-0001 --reason "Disposition resolved"
python3 .aletheia/bin/model_gate.py --task-class <task_class> --provider <provider> --model-id <model_id> --record --objective "<objective>"
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
python3 .aletheia/bin/model_gate.py --registry list
python3 .aletheia/bin/model_gate.py --registry register <name> --provider <provider> --model-id <model_id> --tier C3
python3 .aletheia/bin/model_gate.py --registry disable <name>
python3 .aletheia/bin/model_gate.py --registry deprecate <name> --reason "<reason>"
python3 .aletheia/bin/model_gate.py --registry remove <name>
python3 .aletheia/bin/model_gate.py --registry deny <model_id> --reason "<reason>"
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --inspect --json
python3 .aletheia/bin/guided_bootstrap.py --objective "<objective>"
python3 .aletheia/bin/bootstrap_finalize.py --inspect --json
python3 .aletheia/bin/overview.py
python3 .aletheia/bin/overview.py --watch
python3 .aletheia/bin/overview.py --public-docs
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py --dry-run
python3 .aletheia/bin/checkpoint.py
```

During first bootstrap, use `--operator-approved` to explicitly authorize the current model for initialization. After the project is fixed, register trusted models in `.aletheia/governance/model_registry.json`; later durable writes are decided by the registry. Use `model_gate.py --registry list/register/show/enable/disable/deprecate/remove/deny/undeny` to maintain the registry explicitly instead of hand-editing JSON.

`model_gate.py` is a governance, attribution, and audit boundary. It is not a security sandbox, and it is not an unbypassable permission system. Its role is to make agents explicitly declare task class, model, tier, and objective before writes, then leave a reviewable record.

Claude Code enforces gates and audits through hooks. Codex currently uses skills, explicit commands, and optional subagents to follow the same protocol; AletheiaOS does not claim equivalent automatic hook enforcement in Codex. The explicit Codex loop is: `orient.py --with-runtime`, `status.py --json` or `preflight.py --json`, write truth, `validate.py`, `checkpoint.py --dry-run`.

truth_record.py supports `--json` output so agents can compose list, create, show, update, and archive results predictably. Fixed truth files can use `current` as the record id, for example `truth_record.py show capability-map current`, `truth_record.py show charter current`, `truth_record.py update active-state current --section "Active frontier" --content "..."`, and `truth_record.py archive runtime-policy current --reason "..."`. The common orphan incubator lifecycle is covered by `truth_record.py create/list/show/update/archive orphan`; review fields can be updated with `--candidate-parent`, `--source-ref`, `--next-review`, `--evidence-needed`, and `--disposition`. Complex review can still edit `.aletheia/state/ORPHANS.yaml` directly and then validate. Truth record deletion defaults to archive-only; permanent removal is a human/admin action and should first confirm there are no dangling references.

`checkpoint.py` stages only AletheiaOS state/control-plane paths by default. It stages the whole worktree only when `--include-worktree` is passed explicitly.

`guided_bootstrap.py` validates an already recorded bootstrap gate; it does not create new model authorization by itself. `guided_bootstrap.py --inspect --json` is a read-only check for gate, source inventory, and planned writes. `bootstrap_finalize.py --inspect --json` is a read-only check for model gate, validation, critical truth markers, Git readiness, and planned writes. `source_inventory.py` skips `.aletheia/`, `.claude/`, and root bootstrap control files by default, scanning only project-owned material. `context_pack.py` references only the aggregate source inventory summary and does not expand high-churn runtime records by default. Use `status.py --json` to refresh current state; do not move dynamic state into default orient/context pack. `preflight.py` reports context, runtime gate, validation, checkpoint candidate, generated-output boundaries, and suggested next steps in Codex and other hosts without automatic hook enforcement. `runtime_policy.json` stores read-only commands, source inventory rules, checkpoint state paths, excluded generated/runtime paths, and protected path patterns, making hook/checkpoint rules reviewable. When adding or changing a user-executable action, update `.aletheia/CAPABILITY_MAP.md`.

`overview.py` and `source_inventory.py` write generated/intermediate outputs under `.aletheia/` by default; those files are not durable project truth. `status.py --json`, `preflight.py --json`, and overview `status.json` explicitly label generated/runtime outputs. `overview.py --watch` can refresh local status JSON/HTML repeatedly. `docs/overview/` is generated only when `--public-docs` is passed explicitly.

## Core Model

AletheiaOS's core model is:

```text
root objective / research question
-> truth tree skeleton
-> hypotheses / evidence / decisions
-> contracts / nodes / implementation
-> validation / feedback / tree refactor
```

The older engineering chain still applies, but it is one engineering projection of the truth tree:

```text
mission -> system graph -> skeleton -> contracts -> evidence -> decisions -> code
```

Responsibilities:

- `skeleton` owns structure: root, trunk, branches, leaves, parent-child relations, and inherited constraints.
- `hypotheses`, `evidence`, and `decisions` own the scientific-method loop: observation, hypothesis, evidence, falsification criteria, acceptance, weakening, or archival.
- `contracts`, `nodes`, and code own engineering: turning accepted truth into boundary contracts, system nodes, and implementation constraints.
- `validate`, `preflight`, `overview`, and `checkpoint` make tree evolution reviewable, traceable, and reversible.

Directory responsibilities:

- `governance/` stores charter, attention policy, tree governance, model governance, model registry, runtime policy, git policy, and source policy.
- `state/` stores active state, system graph, project skeleton, orphan incubator, frontier board, glossary, domain profile, and risk register.
- `nodes/` stores drill-down system node facts.
- `evidence/` stores experiments, validation, observations, reasoning, and interpretation records.
- `decisions/` stores long-term project and architecture decisions.
- `contracts/` stores module, interface, and boundary contracts.
- `risks/` stores failure modes, uncertainty, and hypotheses awaiting falsification.
- `agent_runs/` stores agent attribution and model gate records.

Source code, tests, public docs, and build configuration stay in normal project directories. `.aletheia/` is a fact control plane, not a replacement for the implementation and data plane.

## Positioning Boundaries

AletheiaOS is:

- a repo-native truth layer;
- a falsifiable truth tree layer for AI-assisted research and engineering;
- real project memory for AI-assisted research and engineering;
- a governed system graph;
- a fact ledger for architecture constraints, research evidence, decisions, contracts, risks, and agent attribution;
- a project fact control plane that Codex, Claude Code, and similar tools can read and write together.

AletheiaOS is not another coding workflow, and it is not:

- a task manager;
- a generic notes app;
- a feature spec tool;
- a replacement for Claude/Codex memory;
- a TDD, review, ship, or virtual-team plugin;
- a replacement for human judgment;
- a magic layer that automatically makes unstructured projects consistent.

## Relationship to Other Tools

```text
Claude Code / Codex provide the agent runtime.
Superpowers / gstack / Compound guide how agents work.
OpenSpec manages change-level specs.
AletheiaOS maintains the project-level truth they all rely on.
```

AletheiaOS does not compete for the process entry point. It provides the `.aletheia/` fact layer so different agents, skills, and workflows can orient, execute, validate, and checkpoint against the same current truth.

Further reading: [AletheiaOS: a repo-native falsifiable truth tree layer for AI-assisted research and engineering](docs/articles/aletheia-os-project-introduction.zh-CN.md).

## Optional Subagents

AletheiaOS provides three optional truth-layer review subagents. They do not change the core loop and are not written into the target repository's default scaffold:

- `truth-auditor`: checks whether a change still conforms to `.aletheia/` mission, active state, system graph, active node, constraints, and checkpoint requirements.
- `evidence-curator`: checks evidence chains between claims, hypotheses, evidence, and decisions; flags missing evidence, weak falsification criteria, and over-inference.
- `architecture-reviewer`: checks drift between node boundaries, contracts, decisions, skeleton, and implementation.

Claude Code plugins can read profiles directly from the plugin root `agents/` directory. After installation, these three profiles are available with the plugin directory.

Codex custom agents currently load from project-level `.codex/agents/` or user-level `~/.codex/agents/` TOML files. The release package provides equivalent `codex-agents/` profiles. To use them in a target repository, copy them into that repository's `.codex/agents/`:

```bash
mkdir -p /path/to/target-repo/.codex/agents
cp /tmp/aletheia-os-dist/aletheia-os/codex-agents/*.toml /path/to/target-repo/.codex/agents/
```

These three subagents only read and review the `.aletheia/` truth layer. They do not implement features, schedule work, release software, or orchestrate delivery.

## External LLM Wiki Intake

AletheiaOS core does not include a material-ingestion system. Large bodies of unstructured material should first be compiled by an external LLM Wiki for deduplication, topic grouping, concept relationships, and source navigation. AletheiaOS only accepts reviewed findings that should become project truth.

```text
ChatGPT / Claude / Codex conversation material
-> external LLM Wiki compiles reviewable research space
-> AletheiaOS Wiki Handoff
-> aletheia-promote
-> evidence / hypothesis / decision / contract / risk / node / state
-> validate
-> checkpoint
```

When an agent finds material from long conversations, multi-source research, or conflicting observations, it should guide the user to use an external LLM Wiki first and require this handoff package:

```markdown
# AletheiaOS Wiki Handoff

Objective:
Wiki location:
Source corpus:
Source index:

## Candidate Project Skeleton

## Key Claims
- Claim:
  Source refs:
  Confidence:
  Limitations:
  Promote to: evidence | hypothesis | decision | contract | risk | node | state

## Evidence Map

## Conflicts

## Hypotheses

## Architecture Candidates

## Open Questions

## Suggested Promotions
```

Detailed rules live in `.aletheia/playbooks/external_llm_wiki_handoff.md` and `.aletheia/playbooks/wiki_handoff_promotion.md`. Wiki pages are compiled research. After `aletheia-promote` reviews the handoff, only content promoted into `.aletheia/evidence/`, `.aletheia/decisions/`, `.aletheia/hypotheses/`, `.aletheia/contracts/`, `.aletheia/risks/`, `.aletheia/nodes/`, or `.aletheia/state/` is durable project truth.

`orient` outputs a stable Global View Checksum and includes the capability map plus a durable truth record inventory summary by default. This helps agents identify the active node, parent constraints, success criteria, falsification criteria, truth records that need updates, verification path, and checkpoint plan before making changes. High-churn current agent run and recent session notes require explicit `python3 .aletheia/bin/orient.py --with-runtime`; the most stable upfront context can use `--static`.

Related plugin skills:

- `aletheia-bootstrap`: initialize the target repository's `.aletheia/` truth layer.
- `aletheia-orient`: build a project view from the single fact source and locate the active node.
- `aletheia-checkpoint`: validate and commit a coherent project truth update.
- `aletheia-design-evidence`: create falsifiable evidence for claims, experiments, and design branches.
- `aletheia-architecture-evolution`: support architecture decisions, contract changes, and skeleton traversal.
- `aletheia-promote`: promote confirmed findings from external LLM Wiki handoff into durable truth records.

## Design Principles

0. Project facts must grow from the root objective through trunk, branches, and leaves; unmounted material must not be forced into the main tree.
1. The repository is the long-term fact source; chat is not.
2. Every important claim should be falsifiable or explicitly marked as interpretive judgment.
3. Implementation must be traceable to objectives, system nodes, contracts, or evidence.
4. Architecture iteration is a design-research process that needs evidence and invalidation criteria.
5. `.aletheia/` is a truth layer, not a replacement for source code, tests, or public docs.
6. The plugin owns the operating protocol; the target repository owns real project facts.
7. Human overview should be generated from real project facts, not handwritten status pages.

Every important truth member must be able to explain:

- which higher-level objective it serves;
- which parent constraints it inherits;
- what its current evidence state is;
- what conditions would weaken or falsify it;
- whether it has been engineered into a contract, node, or implementation constraint.
