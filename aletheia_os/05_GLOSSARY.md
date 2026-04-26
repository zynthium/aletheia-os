# Glossary

Keep project terms stable. Ambiguous words create drift.

| Term | Definition | Scope | Notes |
|---|---|---|---|
| Active node | The system-graph node currently being worked on. | project governance | One primary active node per AI session. |
| Claim | A statement that can be evaluated by evidence, derivation, simulation, test, or field observation. | evidence | Claims should link to nodes. |
| Contract | An interface or boundary that preserves meaning across modules, disciplines, or teams. | engineering/design | Contracts can be software APIs, design constraints, manufacturing specs, market assumptions, or proof obligations. |
| Evidence | A durable record testing or informing a claim. | evidence | Not all evidence is equally strong. |
| Invalidation criteria | Conditions under which a claim, design, or branch should be revised or killed. | governance | Required for serious branches. |
| System graph | The constraint/dependency graph of objectives, theories, designs, capabilities, risks, and evidence. | project governance | The main anti-drift structure. |
| Capability tier | Practical project-governance level for an AI model, from C0 to C4. | model governance | Not a literal IQ score. Used to decide whether a model can perform a task class. |
| Agent run | Durable record of an AI assistant session/task attempt. | model governance | Stored under `aletheia_os/agent_runs/`. |
| Task class | Category of work with a minimum model capability tier. | model governance | Examples: `mechanical_implementation`, `research_design`, `production_safety_critical`. |
| Model gate | Scripted check that allows, denies, or limits the current AI assistant before durable writes. | model governance | Implemented by `scripts/aios_model_gate.py`. |

