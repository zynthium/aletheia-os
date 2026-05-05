# Attention Policy

Load the smallest context that preserves the global skeleton.

## Context tiers

### Tier 0 - Always-on truth

Load for every non-trivial session:

- root entrypoint and `.aletheia/START_HERE.md`;
- `.aletheia/governance/CHARTER.md`;
- `.aletheia/governance/ATTENTION_POLICY.md`;
- `.aletheia/state/ACTIVE_STATE.md`;
- `.aletheia/governance/MODEL_GOVERNANCE.md` when durable writes are possible.

Purpose: preserve mission, constraints, active frontier, and completion rules.

### Tier 1 - Active node

Load after the task is located:

- relevant part of `.aletheia/state/SYSTEM_GRAPH.yaml`;
- relevant part of `.aletheia/state/SKELETON.yaml`;
- active node file under `.aletheia/nodes/` when present.

Purpose: identify the branch being changed and its parent/child dependencies.

### Tier 2 - Boundary records

Load when crossing modules, abstractions, teams, or runtime boundaries:

- relevant contracts in `.aletheia/contracts/`;
- relevant decisions in `.aletheia/decisions/`.

Purpose: avoid silently changing interfaces or carrying new assumptions across boundaries.

### Tier 3 - Evidence records

Load when evaluating, validating, reprioritizing, or promoting a branch:

- relevant evidence in `.aletheia/evidence/`;
- relevant hypotheses and risks.

Purpose: separate claim, method, result, interpretation, and graph impact.

### Tier 4 - Local files

Load source, tests, docs, scripts, experiments, or external references only after upstream truth is established.

Purpose: execute without losing the reason for execution.

## Read order

1. Root entrypoint and `.aletheia/START_HERE.md`.
2. Charter, attention policy, model governance, and active state.
3. System graph and project skeleton.
4. Active node parent chain, immediate children, and relevant boundary records.
5. Relevant source, tests, docs, or external references only after the active node is identified.

## Expansion rule

Do not scan the whole repository by default. Expand from root to active node, then load siblings only when the task crosses their interfaces or constraints.

## Stop rule

Stop expanding when the current node, parent constraints, contracts, decisions, and directly owned paths are sufficient to answer or execute the task.

## Stop signs

Stop local execution and reorient when:

- the active node is unclear;
- a local edit changes an upstream objective, theory, contract, or evidence interpretation;
- a result contradicts current project truth;
- the task expands into unrelated branches;
- the assistant starts optimizing a proxy instead of the stated objective.

## Context reset protocol

When finishing substantial work, hitting context pressure, or switching active nodes:

1. Write or update a session note.
2. Update active state when frontier, blockers, active nodes, or next actions changed.
3. Update evidence, decision, contract, risk, node, or graph records when affected.
4. Run `.aletheia/bin/validate.py`.
5. Create or explicitly defer a checkpoint.
