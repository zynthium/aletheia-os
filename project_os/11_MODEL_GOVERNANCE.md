# 11 — Model Governance and Attribution Policy

This policy controls which AI coding assistants may work on which classes of tasks and how their work is attributed.

The policy does **not** claim to measure true intelligence. It uses a practical capability gate: model identity, allowed capability tier, task class, write intent, and run attribution. Treat this as project governance. For hard security, enforce model/tool restrictions outside the repository as well.

## Core principle

Research-oriented projects should not accept work from an unqualified model merely because it can edit files.

Before any non-trivial task, the assistant must be classified against:

```text
model provider
model identifier
assistant tool / interface
capability tier
task class
write intent
operator approval status
```

If the model is unknown or below the required tier, it may orient, read public project files, or summarize local context, but it must not perform durable writes, change project state, modify implementation code, or create checkpoints.

## Capability tiers

| Tier | Meaning | Allowed role |
|---|---|---|
| C0 | Unknown, weak, or untrusted model | Read-only orientation only |
| C1 | Basic documentation/helper model | Summaries, formatting, non-critical documentation |
| C2 | Competent engineering model | Local implementation, tests, scripts, mechanical refactors |
| C3 | Research-engineering model | Hypothesis work, cross-boundary design, evidence interpretation, architecture |
| C4 | Strategic/research lead model | Root theory changes, safety-critical production decisions, high-stakes optimization |

## Task classes

Default minimums are stored in `project_os/model_registry.json`.

Typical mapping:

```text
orientation/read-only                 -> C0
non-critical documentation             -> C1
mechanical implementation              -> C2
local bug fix with tests               -> C2
cross-boundary refactor                -> C3
research design / hypothesis update    -> C3
evidence interpretation / graph weight -> C3
production trading / safety-critical   -> C4
root objective or theory revision       -> C4
```

## Start-of-work gate

Before edits, run:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Examples:

```bash
python3 scripts/aios_model_gate.py --task-class research_design --record --objective "Design regime-neutral evidence protocol"
python3 scripts/aios_model_gate.py --task-class mechanical_implementation --record --objective "Add unit tests for parser"
python3 scripts/aios_model_gate.py --task-class production_safety_critical --record --objective "Modify live risk kill switch"
```

For non-Claude tools, set model metadata explicitly when the tool does not expose it:

```bash
AIOS_AGENT_PROVIDER=openai \
AIOS_MODEL_ID="provider-model-id" \
AIOS_AGENT_TOOL=codex \
python3 scripts/aios_model_gate.py --task-class research_design --record --objective "..."
```

## Unknown model rule

The default policy is:

```text
unknown model -> read-only orientation; no durable writes; no checkpoint
```

To approve a model, edit `project_os/model_registry.json` and add it to `registered_models` with a tier and status.

Do not let the assistant self-upgrade its tier without explicit operator approval. Repository checks can discourage violations, but they are not a cryptographic security boundary.

## Attribution requirement

Every non-trivial task should create an agent run record under:

```text
project_os/agent_runs/
```

Every session note should include:

```text
agent run id
provider
model id
capability tier
task class
gate result
```

Every checkpoint commit should include commit trailers such as:

```text
AIOS-Agent-Run: RUN-20260426T120000Z-abcdef
AIOS-Agent-Provider: anthropic
AIOS-Agent-Model: <model-id>
AIOS-Agent-Tier: C3
AIOS-Task-Class: research_design
AIOS-Gate: allowed
```

This lets future reviewers answer:

```text
Which model made this change?
Was that model permitted for the task class?
Was the task engineering-only, research-level, or safety-critical?
Which durable state changed?
```

## Rejection rule

If the gate rejects the model, the assistant must stop and report:

```text
model id
registered tier or unknown status
requested task class
required minimum tier
allowed fallback action
what the operator must change to proceed
```

The correct fallback is not to continue with smaller local edits. The correct fallback is to switch to a stronger approved model, reduce the task class to a permitted read-only/documentation task, or obtain operator approval and update the registry.
