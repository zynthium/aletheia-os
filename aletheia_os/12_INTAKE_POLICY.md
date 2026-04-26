# Intake Policy

This policy governs how an AI coding assistant imports existing project materials during model-led bootstrap.

The goal is to preserve useful prior work without allowing stale, conflicting, sensitive, or unverified materials to corrupt durable project memory.

## Core principle

Existing material is not automatically true. It must be inventoried, classified, and synthesized with provenance.

During bootstrap, the assistant should answer four questions for every meaningful source:

1. What is this material?
2. How reliable is it now?
3. Which part of the system graph could it affect?
4. Should it become a hypothesis, evidence, decision, contract, risk, context note, or deferred item?

## Intake categories

### authoritative_current

Current, high-quality material that can safely shape durable project state.

Examples:

- accepted architecture documents;
- verified implementation code;
- validated experiment reports;
- final decisions made by the project owner;
- current interface contracts.

### useful_but_unverified

Material that appears useful but lacks validation, provenance, or current confirmation.

Examples:

- research notes;
- unfinished notebooks;
- old strategy ideas;
- draft formulas;
- one-off analysis scripts;
- undocumented model outputs.

These items may become hypotheses, open questions, or candidate evidence. They should not be treated as facts.

### historical_context

Material that explains how the project evolved but should not override current state.

Examples:

- old roadmaps;
- prior debates;
- retired design notes;
- earlier project philosophies;
- logs explaining why a branch existed.

### superseded

Material explicitly replaced or invalidated by newer evidence, decisions, or code.

Examples:

- old API contracts replaced by newer contracts;
- retired model assumptions;
- deprecated experiments;
- older designs contradicted by later decisions.

Superseded items should be recorded for auditability, not imported into active state.

### conflicting

Material that contradicts another source and requires resolution.

Examples:

- two strategy documents making incompatible assumptions;
- evidence records with opposing results;
- code behavior that contradicts an interface contract;
- risk rules that conflict with production behavior.

Conflicting items should be highlighted in the import report and not silently merged.

### unsafe_or_sensitive

Material that should not be loaded into ordinary LLM context or durable project memory.

Examples:

- API keys;
- broker credentials;
- passwords;
- tokens;
- private account identifiers;
- restricted vendor data;
- sensitive personal data;
- raw trading account records.

The assistant may record that such a file exists and was excluded, but must not quote or summarize sensitive content.

### deferred_due_to_size

Material that is potentially relevant but too large to inspect during bootstrap.

Examples:

- large market data files;
- long notebooks;
- binary artifacts;
- simulation dumps;
- large generated reports.

Record the path, size, inferred category, and recommended next inspection step.

### unknown

Material whose role cannot be determined safely.

Unknown items should remain in the import report for later human or higher-tier model review.

## Source-to-record mapping

Use this mapping when synthesizing durable project memory:

- theory notes -> hypotheses, system graph nodes, glossary, open questions;
- experiment reports -> evidence records and evidence index;
- design docs -> decision records and interface contracts;
- implementation code -> system graph capabilities and source placement notes;
- tests -> validation strategy and risk controls;
- operations notes -> risk register, deployment constraints, monitoring contracts;
- failure logs -> risk register, evidence records, decision records;
- stale docs -> historical context or superseded records.

## Import report requirements

Bootstrap must generate or update:

```text
aletheia_os/bootstrap_intake/IMPORT_REPORT.md
```

The report should include:

- initialization mode;
- inventory summary;
- classification summary;
- authoritative current sources;
- useful but unverified sources;
- conflicts;
- superseded material;
- sensitive exclusions;
- deferred large items;
- durable records created or updated;
- unresolved questions.

## Safety rules

- Never import secrets or credentials.
- Never collapse uncertainty into certainty.
- Never treat backtest output, simulation output, proof sketches, or design drafts as validated evidence without provenance.
- Never delete legacy material during bootstrap unless explicitly instructed.
- Prefer references and concise summaries over bulk copying.
- Preserve links from durable records back to original sources.
