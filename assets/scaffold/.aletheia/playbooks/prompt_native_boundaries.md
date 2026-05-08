# Prompt-Native Boundary Assessment

This note classifies AletheiaOS runtime behavior so future changes keep scripts primitive and move judgment into skills or playbooks when practical.

## Primitive runtime scripts

These scripts should stay small and capability-oriented:

- `action.py`: list, explain, recommend, and run declarative action contracts from `actions.json`.
- `truth_record.py`: create, list, show, update, and archive truth records.
- `capability_audit.py`: check that the capability map covers runtime scripts, skills, review agents, and CRUD commands.
- `orient.py`: read stable project truth and print an orientation pack.
- `context_pack.py`: read stable truth, source summaries, and record inventory.
- `system_context.py`: compose prompt-ready context from stable truth, user preferences, capabilities, and optional runtime context.
- `status.py`: refresh validation, active state, record counts, and runtime gate state.
- `preflight.py`: read hook-free context, model gate, validation, git status, checkpoint candidate state, and next actions.
- `model_gate.py`: evaluate model registry policy, manage model registry entries, and record attribution.
- `validate.py`: check scaffold, graph, registry, runtime policy, refs, and truth record semantics.

## Workflow-coded scripts

These scripts intentionally contain more orchestration and should be reviewed before adding more policy:

- `guided_bootstrap.py`: prepares a first-run truth inventory report and enforces bootstrap gate prerequisites.
- `bootstrap_finalize.py`: validates bootstrap readiness, installs Git hooks, writes a session note, and optionally checkpoints.
- `checkpoint.py`: validates state, screens paths, stages durable state files, and writes attributed commits.
- `source_inventory.py`: classifies source material before truth synthesis using declarative runtime policy rules.
- `overview.py`: generates and optionally refreshes status JSON and HTML for human review.

## Primitive Wrappers

Workflow-coded scripts may remain as user-facing wrappers when they expose their
deterministic boundary as a read-only or dry-run primitive:

- `guided_bootstrap.py --inspect --json` reads bootstrap gate and source
  inventory readiness and reports generated outputs before writing a truth
  inventory report.
- `bootstrap_finalize.py --inspect --json` reads model gate, validation,
  critical bootstrap markers, and Git readiness before installing hooks, writing
  session notes, removing `BOOTSTRAP.md`, or checkpointing.
- `checkpoint.py --dry-run` validates, screens protected paths, and reports
  checkpoint candidates without staging or committing.
- `preflight.py --json` composes hook-free context, validation, Git status,
  checkpoint candidates, command hints, and recommended action ids.

The wrapper decides how to run deterministic mechanics. The skill or playbook
decides whether the wrapper should run at all.

## Keep in Python

Keep behavior in Python when it must be deterministic, locally verifiable, or hard to express safely in prose:

- path containment and traversal checks;
- Git status, staging, commit, and hook installation mechanics;
- protected path and generated/runtime exclusion handling;
- source inventory ignore, sensitive, size, keyword, and suffix rules declared in `runtime_policy.json`;
- JSON parsing, schema presence checks, and validation exit codes;
- stable machine-readable output.

## Move to skills or playbooks

Move behavior toward skills or playbooks when it is judgment, sequencing advice, or interpretation:

- how to synthesize mission, active state, risks, evidence, and decisions during bootstrap;
- when a claim is strong enough to promote from a wiki handoff;
- how to interpret evidence limitations and invalidation criteria;
- when an architecture boundary change requires decisions, contracts, or risks;
- which truth records a task should update before checkpointing.
- whether new material belongs on the skeleton tree or should remain in the
  incubator;
- when a branch should be split, merged, promoted, demoted, moved, or archived.

## Delete Policy

AletheiaOS treats deletion of durable truth records as archive-by-default.
For agent-facing CRUD, `truth_record.py archive` is the Delete equivalent because it
preserves auditability and keeps old links reviewable. Permanent removal remains a
manual/admin repository operation and should not be advertised as a normal agent
primitive unless reference checks and recovery guidance are added.

## Primitive-To-Workflow Map

Prompt workflows should compose the runtime primitives above instead of hiding new
business logic inside Python:

Each workflow skill should contain:

- `## Primitive Capabilities`: the scripts or action contracts the skill composes.
- `## Prompt Recipe`: the judgment, sequencing, and interpretation that belongs in prose.

| Workflow | Primitive capabilities it should compose |
|---|---|
| Bootstrap | `model_gate.py`, `source_inventory.py`, `guided_bootstrap.py --inspect`, `guided_bootstrap.py`, `bootstrap_finalize.py --inspect`, `bootstrap_finalize.py`, `truth_record.py`, `validate.py`, `checkpoint.py --dry-run`, `checkpoint.py` |
| Promotion | `context_pack.py`, `truth_record.py list/show/create/update/archive`, `validate.py`, optional `checkpoint.py` |
| Architecture evolution | `orient.py`, `truth_record.py`, `system_context.py`, `validate.py`, optional `checkpoint.py` |
| Tree-governed truth growth | `orient.py`, `context_pack.py`, `truth_record.py create/list/show/update/archive orphan`, direct state-file edits, `truth_record.py`, `validate.py`, optional `checkpoint.py` |
| Checkpoint | `status.py`, `preflight.py --json`, `validate.py`, `checkpoint.py --dry-run`, `checkpoint.py` |
| Review agents | `orient.py`, `context_pack.py`, `truth_record.py list/show`, source reads, `validate.py` |

## Review trigger

When adding a new runtime script or expanding an existing one, update this assessment if the change adds workflow judgment rather than primitive capability. Prefer a playbook or skill update first, then add Python only for deterministic execution or validation.
