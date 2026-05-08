# AletheiaOS Capability Map

This map keeps user-facing actions and agent-facing capabilities aligned.
Update it whenever a script, skill, host action, or durable truth record type changes.

| User Action | User Surface | Agent Capability | Status | Notes |
|---|---|---|---|---|
| Install AletheiaOS for Claude Code | `python3 scripts/install_aletheia.py --host claude` | Run installer script | Done | Claude marketplace registration and install are CLI-driven. |
| Register AletheiaOS for Codex | `python3 scripts/install_aletheia.py --host codex` | Run installer script | Partial | Codex marketplace registration is scripted; plugin enablement currently happens in `/plugins` as a host limitation. |
| Copy optional Codex agent profiles | `--with-codex-agents` | Run installer script | Done | Writes profiles to `.codex/agents/` or user agent directory. |
| Enable AletheiaOS in Codex | `/plugins` | Not available as a repo script | Partial | Codex enablement is a host UI action after marketplace registration; this is a host limitation, not a repo capability gap. |
| Initialize AletheiaOS scaffold | `python3 scripts/init_aletheia.py <repo>` or `aletheia-bootstrap` | Run init script | Done | Writes `.aletheia/`, root guidance, and Claude hooks without overwriting existing files. |
| Discover AletheiaOS capabilities | `python3 .aletheia/bin/help.py` | Print outcome-level capability guide | Done | Use when the user asks what AletheiaOS can do. |
| Discover agent actions | `python3 .aletheia/bin/action.py list --json` | Read `actions.json` and list agent-native action IDs | Done | Use when an agent needs structured action contracts instead of prose commands. |
| Explain agent action | `python3 .aletheia/bin/action.py explain truth.validate --json` | Read one `actions.json` action contract | Done | Action IDs include `truth.validate`, `truth.preflight`, `truth.checkpoint.dry_run`, `truth.orphan.*`, `truth.bootstrap.*.inspect`, and `capability.audit`. |
| Run agent action | `python3 .aletheia/bin/action.py run truth.validate --json` | Execute a registered action and verify its return code | Done | Read-only actions can be executed directly; writes-state, admin, and checkpoint actions carry explicit risk labels. |
| Recommend next agent actions | `python3 .aletheia/bin/action.py next --json` | Read recommended action IDs from `actions.json` | Done | Recommended IDs include `truth.orient.runtime`, `truth.status`, `truth.preflight`, `truth.validate`, and `truth.checkpoint.dry_run`; preflight also emits these action IDs for hook-free hosts. |
| Audit capability map coverage | `python3 .aletheia/bin/capability_audit.py` | Check capability map coverage for runtime scripts, skills, agents, and CRUD commands | Done | Use when runtime scripts, skills, review agents, or user actions change. |
| Orient on project truth | `python3 .aletheia/bin/orient.py` or `aletheia-orient` | Read truth files and active node records | Done | Default output is stable and compact; use `--with-runtime` for current run/session context or `--static` for the smallest output. |
| Build context pack | `python3 .aletheia/bin/context_pack.py` | Read core truth, capabilities, source summary, and record inventory | Done | Default output keeps stable truth first; use `--with-runtime` to append current run and recent session notes. |
| Build prompt-ready system context | `python3 .aletheia/bin/system_context.py` | Emit one prompt-ready context block from stable truth, `.aletheia/state/USER_PREFERENCES.md`, capabilities, and optional runtime context | Done | Use `--with-runtime` when host prompts should include current run and recent session context. |
| Refresh current status | `python3 .aletheia/bin/status.py` | Read active state, validation, record counts, runtime gate status, generated-output boundaries, and next actions | Done | Explicit dynamic refresh; use `--json` for agent-readable status and recommended action IDs. |
| Run hook-free preflight | `python3 .aletheia/bin/preflight.py` | Read context, model gate, validation, git status, checkpoint candidate state, generated-output boundaries, and next actions | Done | Use on Codex or other hosts without automatic hook enforcement; supports `--json`. |
| List truth records | `python3 .aletheia/bin/truth_record.py list <entity>` | Read truth record directory | Done | Supported entities include evidence, decisions, contracts, hypotheses, risks, nodes, session notes, and agent runs where applicable. |
| Create truth record | `python3 .aletheia/bin/truth_record.py create <entity> --id <id> --title <title>` | Create from template | Done | Creates a template-backed record in the relevant `.aletheia/` directory. |
| Show truth record | `python3 .aletheia/bin/truth_record.py show <entity> <id>` | Read one truth record | Done | Emits record content for agent grounding or user review. |
| Update truth record | `python3 .aletheia/bin/truth_record.py update <entity> <id> --status <status>` | Update title, status, or markdown section | Done | Supports `--title`, `--status`, and markdown `--section` plus `--content`; use `--json` for agent-readable output. |
| Archive truth record | `python3 .aletheia/bin/truth_record.py archive <entity> <id> --reason <reason>` | Mark record archived | Done | Preferred safe alternative to deletion. |
| Record model gate attribution | `python3 .aletheia/bin/model_gate.py --record ...` | Run model gate | Done | Writes `agent_runs/` and runtime current run record. |
| Manage model registry | `python3 .aletheia/bin/model_gate.py --registry <command>` | List, register, show, enable, disable, deprecate, remove, deny, and undeny models | Done | Keeps model gate policy editable through explicit commands instead of hand-editing JSON. |
| Configure runtime policy | `truth_record.py show/update/archive runtime-policy current` or edit `.aletheia/governance/runtime_policy.json` | Read, update, or archive declarative read-only, checkpoint, source inventory, and protected path rules | Done | Used by model gate, source inventory, preflight, and checkpoint runtime, with code fallbacks if the file is unavailable. |
| Configure agent actions | edit `.aletheia/governance/actions.json` then run `python3 .aletheia/bin/validate.py` | Maintain action IDs, risks, commands, outputs, and verification contracts | Done | `action.py`, `preflight.py`, validation, and `capability_audit.py` use these contracts as the agent-facing capability layer. |
| Inventory project sources | `python3 .aletheia/bin/source_inventory.py` | Run source inventory | Done | Writes generated inventory under `.aletheia/source_inventory/`. |
| Inspect guided bootstrap readiness | `python3 .aletheia/bin/guided_bootstrap.py --inspect --json` or `truth.bootstrap.guided.inspect` | Read bootstrap gate, source inventory readiness, next actions, and planned generated outputs | Done | Read-only primitive for deciding whether to run the guided bootstrap wrapper. |
| Prepare guided bootstrap report | `python3 .aletheia/bin/guided_bootstrap.py` | Run guided bootstrap helper | Done | Requires bootstrap model gate unless explicitly skipped; use `--inspect` first on hook-free hosts. |
| Inspect bootstrap finalize readiness | `python3 .aletheia/bin/bootstrap_finalize.py --inspect --json` or `truth.bootstrap.finalize.inspect` | Read model gate, validation, critical truth markers, Git readiness, next actions, and planned writes | Done | Read-only primitive for deciding whether to run the finalize wrapper. |
| Finalize bootstrap | `python3 .aletheia/bin/bootstrap_finalize.py` | Run finalize script | Done | Validates, installs Git hooks, writes session note, and checkpoints unless skipped. |
| Validate project truth | `python3 .aletheia/bin/validate.py` | Run validator | Done | Checks scaffold, graph, model registry, refs, and truth record semantics. |
| Generate overview | `python3 .aletheia/bin/overview.py` | Run overview script | Done | Writes generated status JSON and HTML under `.aletheia/overview/` by default, including recent changes, generated-output boundaries, and next actions. Use `--watch` for repeated local refreshes. |
| Review tree governance state | `python3 .aletheia/bin/system_context.py` or `truth.tree.review` | Read skeleton, tree governance policy, incubator state, and context pack | Done | Use before deciding whether new durable truth attaches to the main tree or stays incubated. |
| Refresh tree health | `python3 .aletheia/bin/status.py --json` or `truth.tree.health` | Read skeleton node count, orphan count, and tree-related validation signals | Done | Tree health is a summary signal, not a separate scoring engine. |
| Route orphan or incubating material | `truth_record.py create/list/show/update/archive orphan ...` or edit `.aletheia/state/ORPHANS.yaml` then validate | Use structured orphan lifecycle primitives for common cases; use `truth_record.py update orphan ORPH-0001 --candidate-parent root --source-ref .aletheia/evidence/EV-0001.md --next-review 2099-01-01 --evidence-needed "..." --disposition attach` for selected review fields; use direct state-file edits for broad review changes | Done | Action IDs: `truth.orphan.list`, `truth.orphan.create`, `truth.orphan.show`, `truth.orphan.update`, `truth.orphan.archive`. Unmounted claims, observations, and candidate theories stay here until review. |
| Record tree refactor decision | `truth_record.py create decision --id <id> --title "<title>"` | Use decision records with affected nodes, evidence links, invalidation criteria, and review trigger | Done | Tree refactors are decisions, not a separate CRUD family. |
| Create checkpoint | `python3 .aletheia/bin/checkpoint.py` or `aletheia-checkpoint` | Run checkpoint script | Done | Validates, screens protected-looking paths, stages state paths, and commits with attribution trailers. |
| Promote reviewed wiki handoff | `aletheia-promote` skill | Read handoff, write truth records, validate, optionally checkpoint | Done | Human confirmation required for root mission, priority order, root theory, or durable architecture decisions. |
| Design falsifiable evidence | `aletheia-design-evidence` skill | Create or revise evidence and related truth records | Done | Keeps source refs, method, limits, interpretation, invalidation criteria, and graph impact attached. |
| Evolve architecture truth | `aletheia-architecture-evolution` skill | Update decisions, contracts, skeleton, evidence, and active state | Done | Use for boundary, contract, dependency, or skeleton changes. |
| Review truth alignment | `truth-auditor` profile | Read `.aletheia/` and report gaps | Done | Read-focused only. |
| Review evidence quality | `evidence-curator` profile | Read evidence, hypotheses, and decisions | Done | Read-focused only. |
| Review architecture drift | `architecture-reviewer` profile | Read state, nodes, contracts, decisions, and source boundaries | Done | Read-focused only. |
| Create truth record | `truth_record.py create` or templates under `.aletheia/templates/` | Write a new record file in the relevant `.aletheia/` directory | Done | Use templates for evidence, decisions, contracts, hypotheses, risks, nodes, and session notes. |
| Read truth record | `truth_record.py list/show`, `.aletheia/` files and indexes | Read files directly, or use context pack and overview | Done | Context pack lists current records; runtime details require `--with-runtime`. |
| Update truth record | `truth_record.py update` or edit existing `.aletheia/` file | Modify title, status, or section, then validate and checkpoint | Done | Deduplicate before creating a new record; use direct file edits for broad rewrites. |
| Delete truth record | `truth_record.py archive` | Archive record, then validate refs | Done | Delete means archive-by-default for durable truth records; this is the archive-only agent primitive. Permanent removal is manual/admin repository maintenance. |
| Read fixed truth file | `truth_record.py show capability-map current` | Read fixed governance/state files through the same CRUD entrypoint | Done | Fixed entities use `current` as the record id. |
| Update fixed truth file | `truth_record.py update active-state current --section ...` | Update selected fixed markdown truth files through the same CRUD entrypoint | Done | Direct edits remain available for broad rewrites. |
| Archive fixed truth file | `truth_record.py archive runtime-policy current --reason ...` | Move fixed truth files into `.aletheia/archive/` | Done | Use only for admin/history workflows; validation may require recreating required files. |

## Agent Primitive Matrix

These are the atomic capabilities that prompt workflows and review agents should compose.
See `.aletheia/playbooks/prompt_native_boundaries.md` for the Primitive-To-Workflow Map
and Primitive Wrappers guidance.
Each workflow skill declares its `Primitive Capabilities` and `Prompt Recipe` so the skill remains prose-level judgment over these primitives.

| Primitive | Script or file | Scope |
|---|---|---|
| List/explain/run action contract | `action.py`, `actions.json` | Discover and execute declared agent actions. |
| Read project truth | `orient.py`, `context_pack.py`, `system_context.py` | Load stable truth, preferences, capabilities, inventory, and optional runtime context. |
| Refresh dynamic state | `status.py`, `preflight.py`, `overview.py` | Observe validation, record counts, runtime gate, git/checkpoint state, recent changes, generated-output boundaries, and next actions. |
| Manage truth records | `truth_record.py list/show/create/update/archive` | Create, read, update, and archive durable truth records. |
| Manage incubating truth | `truth_record.py create/list/show/update/archive orphan`, `.aletheia/state/ORPHANS.yaml`, `validate.py` | Hold unmounted candidates outside the main skeleton until review; selected fields include `--candidate-parent`, `--source-ref`, `--next-review`, `--evidence-needed`, and `--disposition`. |
| Manage model policy | `model_gate.py --registry ...` | List, register, show, enable, disable, deprecate, remove, deny, and undeny model entries. |
| Validate truth layer | `validate.py`, `capability_audit.py` | Check scaffold, refs, registry, action contracts, capability coverage, and record semantics. |
| Inspect workflow wrapper readiness | `guided_bootstrap.py --inspect`, `bootstrap_finalize.py --inspect`, `checkpoint.py --dry-run`, `preflight.py --json` | Read wrapper prerequisites, next actions, candidate files, and planned writes before mutation. |
| Checkpoint state | `checkpoint.py --dry-run`, `checkpoint.py` | Validate, screen, stage, and commit attributed truth updates. |

## CRUD Matrix

Delete for durable truth records means archive-by-default. Permanent removal is an explicit manual/admin repository operation, not the normal agent primitive.

| Entity | Create | Read | Update | Delete Equivalent | Notes |
|---|---|---|---|---|---|
| Project scaffold | `init_aletheia.py` | filesystem | rerun init merges missing hooks/files | manual removal | Existing files are not overwritten. |
| Capability map | scaffold creates file | `truth_record.py show capability-map current`, `context_pack.py` | `truth_record.py update capability-map current --section ...` or edit file | `truth_record.py archive capability-map current` | Validate should require this file. |
| Charter and governance files | scaffold creates files | `orient.py`, `context_pack.py`, `truth_record.py show charter current`, `truth_record.py show attention-policy current`, `truth_record.py show model-governance current`, `truth_record.py show tree-governance current`, `truth_record.py show git-policy current`, `truth_record.py show source-policy current` | `truth_record.py update <fixed-entity> current --section ...` or edit files | `truth_record.py archive <fixed-entity> current` | Root-level changes require human confirmation by prompt policy. |
| Model registry | `model_gate.py --registry register` | `model_gate.py --registry list/show` | `model_gate.py --registry enable/disable/deprecate/deny/undeny` | `model_gate.py --registry remove` | Gate uses enabled registered models, aliases, denylist entries, and deprecation metadata. |
| Runtime policy | scaffold creates `runtime_policy.json` | `truth_record.py show runtime-policy current`, `model_gate.py`, `checkpoint.py` | edit `runtime_policy.json` then validate | `truth_record.py archive runtime-policy current` | JSON fixed truth files can be shown or archived through `truth_record.py`; structured edits stay direct or command-specific. |
| Agent actions registry | scaffold creates `actions.json` | `truth_record.py show actions-registry current`, `action.py list/explain/next`, `preflight.py` | edit `actions.json` then validate | `truth_record.py archive actions-registry current` | JSON fixed truth files can be shown or archived through `truth_record.py`; action execution remains in `action.py`. |
| Active state, user preferences, and state files | scaffold creates files including `.aletheia/state/USER_PREFERENCES.md` | `truth_record.py show active-state current`, `truth_record.py show user-preferences current`, `truth_record.py show domain-profile current`, `truth_record.py show frontier-board current`, `truth_record.py show risk-register current`, `truth_record.py show glossary current`, `truth_record.py show skeleton current`, `orient.py`, `context_pack.py`, `system_context.py`, `status.py`, `overview.py` | `truth_record.py update <markdown-fixed-entity> current --section ...`, YAML/direct edits, then validate | `truth_record.py archive <fixed-entity> current` | Validate checks critical TBD markers after bootstrap. |
| Orphan incubator | `truth_record.py create orphan` | `truth_record.py list/show orphan`, `orient.py`, `context_pack.py`, `system_context.py`, `status.py`, `overview.py` | `truth_record.py update orphan <id> --status ...`, `--candidate-parent`, `--source-ref`, `--next-review`, `--evidence-needed`, or `--disposition`; direct `ORPHANS.yaml` edits remain for broad changes | `truth_record.py archive orphan <id>` | Used for unmounted observations, candidate theories, and weak claims that should not pollute the main tree. |
| Nodes | `truth_record.py create` | `truth_record.py list/show`, `orient.py`, `context_pack.py`, `overview.py` | `truth_record.py update` or edit files | `truth_record.py archive` | Validate checks active node references; permanent removal is manual/admin only. |
| Evidence | `truth_record.py create` | `truth_record.py list/show`, `context_pack.py`, `overview.py` | `truth_record.py update` or edit files | `truth_record.py archive` | Validate checks required sections; permanent removal is manual/admin only. |
| Decisions | `truth_record.py create` | `truth_record.py list/show`, `context_pack.py`, `overview.py` | `truth_record.py update` or edit files | `truth_record.py archive` | Accepted decisions need evidence links; permanent removal is manual/admin only. |
| Contracts | `truth_record.py create` | `truth_record.py list/show`, `context_pack.py`, `overview.py` | `truth_record.py update` or edit files | `truth_record.py archive` | Skeleton refs are validated; permanent removal is manual/admin only. |
| Hypotheses | `truth_record.py create` | `truth_record.py list/show`, `context_pack.py`, `overview.py` | `truth_record.py update` or edit files | `truth_record.py archive` | Validate checks invalidation criteria; permanent removal is manual/admin only. |
| Risks | `truth_record.py create` | `truth_record.py list/show`, `context_pack.py`, `overview.py` | `truth_record.py update` or edit files | `truth_record.py archive` | Risk register also carries portfolio-level risks; permanent removal is manual/admin only. |
| Session notes | `truth_record.py create` | `truth_record.py list/show`, `context_pack.py`, `status.py` | `truth_record.py update` or edit files | `truth_record.py archive` | Bootstrap finalize writes one automatically; permanent removal is manual/admin only. |
| Agent runs | `model_gate.py --record` | runtime files, context pack, status refresh | create a new run | manual removal | Current run lives in `.aletheia/runtime/`. |

## Maintenance Rule

When adding a user-facing action, add or update the matching row here, mention the
capability in the relevant skill or README section, and add validation or tests
when the action changes scaffold behavior.
