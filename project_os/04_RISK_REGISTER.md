# Risk Register

## Risk taxonomy

- **Reality risk**: the world, market, physics, or customer behavior does not match assumptions.
- **Model risk**: the theory or abstraction is incomplete or misleading.
- **Evidence risk**: evidence is biased, non-representative, leaked, overfit, or misinterpreted.
- **Engineering risk**: implementation is incorrect, irreproducible, slow, unsafe, or hard to maintain.
- **Interface risk**: boundaries between modules/disciplines/layers are wrong.
- **Optimization risk**: proxy metrics replace real objectives.
- **Operational risk**: deployment, manufacturing, execution, monitoring, or team processes fail.
- **Governance risk**: decisions are not recorded and context drifts.

## Open risks

| ID | Risk | Type | Severity | Likelihood | Affected nodes | Mitigation | Owner | Status |
|---|---|---|---:|---:|---|---|---|---|
| RISK-0001 | Project identity still undefined. | governance | 3 | 5 | root | Complete bootstrap. | user | open |

## Trigger conditions

Define conditions that force a review.

- New evidence contradicts a protected assumption.
- A blocker is classified as Type C or D.
- A branch consumes significant resources without evidence gain.
- Code changes alter a contract or objective proxy.
- The project accumulates orphan claims or orphan implementations.
