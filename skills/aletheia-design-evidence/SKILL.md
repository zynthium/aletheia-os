---
name: aletheia-design-evidence
description: Design falsifiable evidence for AletheiaOS project truth claims. Use when creating or revising hypotheses, architecture decisions, experiment plans, simulations, proofs, field checks, evidence records, invalidation criteria, or graph confidence updates.
---

# Aletheia Design Evidence

## Primitive Capabilities

Use these primitives. Do not add orchestration to runtime scripts for evidence judgment:

- `system_context.py` or `orient.py` to load active node, parent constraints, and relevant risks.
- `truth_record.py list/show` to inspect existing evidence, hypotheses, decisions, and risks.
- `truth_record.py create/update` to write evidence, hypothesis, risk, or decision records.
- `validate.py` to verify required evidence sections and references.
- `checkpoint.py` only when the user wants the evidence update committed.

## Prompt Recipe

The skill is a prompt recipe for designing falsifiable claims and evidence.

For each important claim, record:

- claim;
- method;
- evidence type;
- expected observation;
- invalidation criteria;
- interpretation rule;
- graph impact;
- follow-up decision.

Link the evidence back to affected system graph or skeleton nodes. Do not treat implementation success, benchmark output, or model confidence as self-explanatory evidence.
