# AletheiaOS Capability Map

This map keeps user-facing actions and agent-facing capabilities aligned.
Update it whenever a script, skill, host action, or durable truth record type changes.

| User Action | User Surface | Agent Capability | Status | Notes |
|---|---|---|---|---|
| Install AletheiaOS for Claude Code | `python3 scripts/install_aletheia.py --host claude` | Run installer script | Done | Claude marketplace registration and install are CLI-driven. |
| Register AletheiaOS for Codex | `python3 scripts/install_aletheia.py --host codex` | Run installer script | Partial | Codex marketplace registration is scripted; plugin enablement currently happens in `/plugins`. |
| Copy optional Codex agent profiles | `--with-codex-agents` | Run installer script | Done | Writes profiles to `.codex/agents/` or user agent directory. |
| Initialize AletheiaOS scaffold | `python3 scripts/init_aletheia.py <repo>` | Run init script | Done | Writes `.aletheia/`, root guidance, and Claude hooks without overwriting existing files. |
| Orient on project truth | `python3 .aletheia/bin/orient.py` or `aletheia-orient` | Read truth files and active node records | Done | Default output is stable and compact; use `--with-runtime` for current run/session context or `--static` for the smallest output. |
| Build context pack | `python3 .aletheia/bin/context_pack.py` | Read core truth, capabilities, activity, and record inventory | Done | Use for full dynamic grounding in long sessions. |
| List truth records | `python3 .aletheia/bin/truth_record.py list <entity>` | Read truth record directory | Done | Supported entities include evidence, decisions, contracts, hypotheses, risks, nodes, session notes, and agent runs where applicable. |
| Create truth record | `python3 .aletheia/bin/truth_record.py create <entity> --id <id> --title <title>` | Create from template | Done | Creates a template-backed record in the relevant `.aletheia/` directory. |
| Show truth record | `python3 .aletheia/bin/truth_record.py show <entity> <id>` | Read one truth record | Done | Emits record content for agent grounding or user review. |
| Archive truth record | `python3 .aletheia/bin/truth_record.py archive <entity> <id> --reason <reason>` | Mark record archived | Done | Preferred safe alternative to deletion. |
| Record model gate attribution | `python3 .aletheia/bin/model_gate.py --record ...` | Run model gate | Done | Writes `agent_runs/` and runtime current run record. |
| Inventory project sources | `python3 .aletheia/bin/source_inventory.py` | Run source inventory | Done | Writes generated inventory under `.aletheia/source_inventory/`. |
| Prepare guided bootstrap report | `python3 .aletheia/bin/guided_bootstrap.py` | Run guided bootstrap helper | Done | Requires bootstrap model gate unless explicitly skipped. |
| Finalize bootstrap | `python3 .aletheia/bin/bootstrap_finalize.py` | Run finalize script | Done | Validates, installs Git hooks, writes session note, and checkpoints unless skipped. |
| Validate project truth | `python3 .aletheia/bin/validate.py` | Run validator | Done | Checks scaffold, graph, model registry, refs, and truth record semantics. |
| Generate overview | `python3 .aletheia/bin/overview.py` | Run overview script | Done | Writes generated status JSON and HTML under `.aletheia/overview/` by default. |
| Create checkpoint | `python3 .aletheia/bin/checkpoint.py` | Run checkpoint script | Done | Validates, screens protected-looking paths, stages state paths, and commits with attribution trailers. |
| Promote reviewed wiki handoff | `aletheia-promote` skill | Read handoff, write truth records, validate, optionally checkpoint | Done | Human confirmation required for root mission, priority order, root theory, or durable architecture decisions. |
| Design falsifiable evidence | `aletheia-design-evidence` skill | Create or revise evidence and related truth records | Done | Keeps source refs, method, limits, interpretation, invalidation criteria, and graph impact attached. |
| Evolve architecture truth | `aletheia-architecture-evolution` skill | Update decisions, contracts, skeleton, evidence, and active state | Done | Use for boundary, contract, dependency, or skeleton changes. |
| Review truth alignment | `truth-auditor` profile | Read `.aletheia/` and report gaps | Done | Read-focused only. |
| Review evidence quality | `evidence-curator` profile | Read evidence, hypotheses, and decisions | Done | Read-focused only. |
| Review architecture drift | `architecture-reviewer` profile | Read state, nodes, contracts, decisions, and source boundaries | Done | Read-focused only. |
| Create truth record | `truth_record.py create` or templates under `.aletheia/templates/` | Write a new record file in the relevant `.aletheia/` directory | Done | Use templates for evidence, decisions, contracts, hypotheses, risks, nodes, and session notes. |
| Read truth record | `truth_record.py list/show`, `.aletheia/` files and indexes | Read files directly, or use context pack and overview | Done | Context pack lists current records. |
| Update truth record | Edit existing `.aletheia/` file | Modify file, then validate and checkpoint | Done | Deduplicate before creating a new record. |
| Delete truth record | `truth_record.py archive` or file removal by user or agent | Archive or remove file, then validate refs | Partial | Prefer archiving by status change; no permanent delete command is provided. |

## CRUD Matrix

| Entity | Create | Read | Update | Delete Or Archive | Notes |
|---|---|---|---|---|---|
| Project scaffold | `init_aletheia.py` | filesystem | rerun init merges missing hooks/files | manual removal | Existing files are not overwritten. |
| Capability map | edit file | `context_pack.py` | edit file | manual removal | Validate should require this file. |
| Charter and governance files | edit files | `orient.py`, `context_pack.py` | edit files | manual removal | Root-level changes require human confirmation by prompt policy. |
| Active state and state files | edit files | `orient.py`, `context_pack.py`, `overview.py` | edit files | manual removal | Validate checks critical TBD markers after bootstrap. |
| Nodes | template/file write | `orient.py`, `context_pack.py`, `overview.py` | edit files | manual removal | Validate checks active node references. |
| Evidence | template/file write | `context_pack.py`, `overview.py` | edit files | manual removal | Validate checks required sections. |
| Decisions | template/file write | `context_pack.py`, `overview.py` | edit files | manual removal | Accepted decisions need evidence links. |
| Contracts | template/file write | `context_pack.py`, `overview.py` | edit files | manual removal | Skeleton refs are validated. |
| Hypotheses | template/file write | `context_pack.py`, `overview.py` | edit files | manual removal | Validate checks invalidation criteria. |
| Risks | template/file write | `context_pack.py`, `overview.py` | edit files | manual removal | Risk register also carries portfolio-level risks. |
| Session notes | template/file write | `context_pack.py` | edit files | manual removal | Bootstrap finalize writes one automatically. |
| Agent runs | `model_gate.py --record` | runtime files, context pack | create a new run | manual removal | Current run lives in `.aletheia/runtime/`. |

## Maintenance Rule

When adding a user-facing action, add or update the matching row here, mention the
capability in the relevant skill or README section, and add validation or tests
when the action changes scaffold behavior.
