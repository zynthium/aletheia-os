# infra/ Agent Rules

This directory contains deployment, environment, monitoring, container, or infrastructure definitions.

Rules:

- Infrastructure changes must preserve reproducibility, rollback, observability, and secret hygiene.
- Production-facing infrastructure changes should update affected contracts, runbooks, or decision records.
- Do not commit credentials, keys, tokens, or local-only infrastructure state.
