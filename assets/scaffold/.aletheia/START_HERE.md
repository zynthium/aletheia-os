# AletheiaOS Start Here

Build a top-down view of project truth before local work.

## Daily Loop

```text
orient -> work -> update truth -> validate -> checkpoint
```

Use this command set for normal work:

```bash
python3 .aletheia/bin/help.py
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py
```

## What You Can Ask AletheiaOS To Do

- Initialize project truth for a new or existing repository.
- Orient on the current mission, active state, system graph, skeleton, risks, and capabilities.
- Refresh context for long sessions with a context pack.
- Create, read, update, and archive truth records for evidence, decisions, contracts, hypotheses, risks, nodes, session notes, and agent runs.
- Validate project truth and checkpoint coherent state updates.
- Review truth alignment, evidence quality, and architecture drift with read-focused agents.

For the full capability guide, run:

```bash
python3 .aletheia/bin/help.py
```

## Read Order

1. `.aletheia/governance/CHARTER.md`
2. `.aletheia/governance/ATTENTION_POLICY.md`
3. `.aletheia/governance/MODEL_GOVERNANCE.md`
4. `.aletheia/governance/model_registry.json`
5. `.aletheia/state/ACTIVE_STATE.md`
6. `.aletheia/state/SYSTEM_GRAPH.yaml`
7. `.aletheia/state/SKELETON.yaml`
8. `.aletheia/state/RISK_REGISTER.md`
9. `.aletheia/state/FRONTIER_BOARD.md`, `.aletheia/state/DOMAIN_PROFILE.md`, and relevant decisions, evidence, contracts, risks, nodes, and source files.

For large conversation exports or scattered research material, use
`.aletheia/playbooks/external_llm_wiki_handoff.md` before writing durable truth.

## Model Gate

Before durable writes, run `.aletheia/bin/model_gate.py` with the correct task class:

```bash
python3 .aletheia/bin/model_gate.py --task-class <task_class> --provider <provider> --model-id <model_id> --record --objective "<short objective>"
```

Use this first-run bootstrap command only for project setup:

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
```

After bootstrap, register trusted models in `.aletheia/governance/model_registry.json`.
Use `python3 .aletheia/bin/model_gate.py --registry list` to inspect registry state,
and `--registry register <name> --provider <provider> --model-id <model_id> --tier C3`
to add a trusted model.

`model_gate.py` is a governance, attribution, and audit boundary. It is not a security sandbox.

## Bootstrap Commands

Run the first-run bootstrap model gate command above before guided bootstrap. `guided_bootstrap.py` verifies that recorded gate instead of creating a new one.

```bash
python3 .aletheia/bin/source_inventory.py
python3 .aletheia/bin/guided_bootstrap.py --objective "Initialize AletheiaOS"
python3 .aletheia/bin/bootstrap_finalize.py
```

## Diagnostic Commands

```bash
python3 .aletheia/bin/context_pack.py
python3 .aletheia/bin/context_pack.py --with-runtime
python3 .aletheia/bin/status.py
python3 .aletheia/bin/overview.py
```
