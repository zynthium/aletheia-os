# Git Policy

Git is the memory boundary. If durable state is not committed, it is not final project memory.

Create a checkpoint when one of these occurs:

1. active state changed;
2. system graph, skeleton, node weight, dependency, or status changed;
3. evidence, decision, risk, or contract records changed;
4. implementation changed and validation state is known;
5. session distillation produced durable next action;
6. a blocker changes upstream assumptions.

Do not auto-commit when validation fails, secrets are present, generated artifacts dominate the diff, the task is mid-flight, or the project owner explicitly asks not to commit.

The default checkpoint runtime stages the configured project-state paths after validation and secret-like path screening. Runtime path rules live in `.aletheia/governance/runtime_policy.json`.
