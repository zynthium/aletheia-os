# Git Policy

Git is the memory boundary. If durable state is not committed, it is not final project memory.

## Truth Transition Commits

Git commits are AletheiaOS truth-transition records. `.aletheia/` stores the current truth state; Git history stores how that state changed.

Use AletheiaOS trailers when a commit changes the truth tree, stabilizes a node, weakens or falsifies a claim, archives a branch, or implements an accepted decision.

## Bootstrap Baseline

The first AletheiaOS checkpoint is a bootstrap baseline, not ordinary node
growth and not a stable-node claim. `bootstrap_finalize.py` creates this
checkpoint by default after validation and hook installation.

Bootstrap baseline commits use:

```text
AIOS-Action: truth.bootstrap.initialize
AIOS-Tree-Op: bootstrap
AIOS-Node: root
AIOS-Review: not-required
```

Do not replace the bootstrap baseline with an unmarked manual `git commit`.
If you skip the automatic checkpoint, add equivalent trailers manually.

## Stable Node Marker

`AIOS-Node-State: stable` is a strong traceability claim. It requires:

1. `AIOS-Action: truth.node.stabilize`
2. `AIOS-Node: <known node id>`
3. `AIOS-Evidence: <existing evidence record>`
4. `AIOS-Decision: <existing accepted decision record>`
5. `AIOS-Validation: pass`
6. `AIOS-Review: human-confirmed`

Do not use `stable` for unreviewed hypotheses, unsupported children, stale orphans, or root-level theory changes that have not received explicit human confirmation.

## Checkpoints

Create a checkpoint when one of these occurs:

1. active state changed;
2. system graph, skeleton, node weight, dependency, or status changed;
3. evidence, decision, risk, or contract records changed;
4. implementation changed and validation state is known;
5. session distillation produced durable next action;
6. a blocker changes upstream assumptions.

Do not auto-commit when validation fails, secrets are present, generated artifacts dominate the diff, the task is mid-flight, or the project owner explicitly asks not to commit.

The default checkpoint runtime stages the configured project-state paths after validation and secret-like path screening. Runtime path rules live in `.aletheia/governance/runtime_policy.json`.
