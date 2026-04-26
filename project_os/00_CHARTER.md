# Project Charter

## Mission

TBD. Define the durable mission in one paragraph.

Example forms:

- Build a robust quantitative strategy research and execution system.
- Develop a theoretical model and simulation framework for a physical phenomenon.
- Design an aircraft/vehicle/industrial system under performance, safety, cost, and manufacturability constraints.
- Build a market/product/operations portfolio that maximizes long-run strategic value under uncertainty.

## Non-negotiable constraints

1. Every important claim must be falsifiable or explicitly marked as interpretive.
2. Every implementation must preserve traceability to the claim, requirement, or system node it serves.
3. Evidence must distinguish observation, simulation, proof, field feedback, market data, and expert judgment.
4. Local optimization must not override parent constraints silently.
5. Downstream feasibility failures may invalidate upstream design choices.
6. Revisions must be recorded; abandoned branches should remain auditable.
7. Project state must be recoverable from git and files, not chat memory.

## Priority order

Customize this list. A generic default:

1. truth / physical or market reality
2. safety / downside protection / catastrophic-risk control
3. strategic objective alignment
4. robustness across regimes or operating conditions
5. evidence quality
6. engineering reproducibility
7. efficiency, cost, and speed
8. elegance or simplicity

## What must never be optimized away

- TBD.

## Accepted evidence standards

Define the evidence bar for this project.

Examples:

- Quant trading: out-of-sample robustness, leakage checks, capacity, costs, regime splits, live decay monitoring.
- Physics: derivation consistency, dimensional analysis, limiting cases, simulation convergence, experimental comparability.
- Aircraft/vehicle: requirements traceability, safety margins, manufacturability, simulation validation, test data.
- Market strategy: customer evidence, competitive dynamics, unit economics, risk-adjusted portfolio effect.

## Decision authority

The AI assistant may propose, implement, and critique. The user owns final changes to mission, priority order, and root assumptions unless explicitly delegated.
