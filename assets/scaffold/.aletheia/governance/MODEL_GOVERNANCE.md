# Model Governance

Before durable writes, implementation changes, research updates, architecture decisions, or checkpoints, run or verify the project model gate.

Unknown or under-tier models are read-only by default unless the project owner explicitly overrides the gate.

Model tiers, task classes, denylist entries, and registered model aliases are configured in `.aletheia/governance/model_registry.json`.

Record attribution for non-trivial work:

```text
Agent run id:
Provider:
Model id:
Capability tier:
Task class:
Gate status:
```

Task-class policy belongs in the local model registry once the project defines one.
