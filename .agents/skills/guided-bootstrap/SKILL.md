---
name: guided-bootstrap
description: |
  Guided bootstrap skill for AletheiaOS: inventory, classify, and synthesize existing materials during initialization; run intake and guided bootstrap scripts yourself; apply model gate; do not rely on the user to execute internal commands.
---

# Guided Bootstrap Skill

Use this skill whenever a repository still contains `BOOTSTRAP.md` and you have been asked to initialize or set up the project.

This skill explains how the AI coding assistant should orchestrate bootstrap without relying on the operator to run scripts, especially when the project already contains research notes, code, notebooks, experiments, reports, simulations, or design documents.

## Procedure

1. Read `BOOTSTRAP.md`, `START_HERE.md`, `AGENTS.md`, `aletheia_os/10_ATTENTION_POLICY.md`, `aletheia_os/11_MODEL_GOVERNANCE.md`, and `aletheia_os/12_INTAKE_POLICY.md`.
2. Produce the Global View Checksum.
3. Run model gating before durable writes:

   ```bash
   python3 scripts/aios_model_gate.py --task-class bootstrap_finalize --record --objective "Guided bootstrap"
   ```

4. Run the intake inventory:

   ```bash
   python3 scripts/aios_intake_inventory.py
   ```

5. Classify existing materials according to `aletheia_os/12_INTAKE_POLICY.md`.
6. Run the guided bootstrap helper:

   ```bash
   python3 scripts/aios_guided_bootstrap.py --objective "Guided bootstrap"
   ```

7. Synthesize durable project memory. Do not merely summarize old materials; convert them into hypotheses, evidence, decisions, contracts, risks, historical context, or deferred items.
8. Run validation and orientation:

   ```bash
   python3 scripts/aios_validate.py
   python3 scripts/aios_orient.py
   ```

9. Finalize bootstrap:

   ```bash
   python3 scripts/aios_bootstrap.py --finalize
   ```

10. Report initialization mode, imported materials, conflicts, exclusions, updated records, checkpoint status, and next task card.

## Rules

- Do not ask the user to run internal scripts.
- Do not start production implementation during bootstrap.
- Do not treat legacy research as automatically true.
- Do not import secrets, credentials, raw account records, restricted vendor data, or large raw datasets into LLM context.
- Preserve provenance and uncertainty.
- Prefer references and concise summaries over copying large source material.
