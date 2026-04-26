# configs/ Agent Rules

This directory contains runtime, experiment, simulation, deployment, and optimization configuration.

Rules:

- Configuration should express parameters and wiring, not hidden business logic.
- Config changes that alter project behavior must link to an active node, contract, evidence item, or decision record.
- Do not store secrets here. Use local environment variables or secret managers outside git.
- For production-facing config, document defaults, units, assumptions, and safe ranges.
