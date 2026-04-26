# Interface Contracts

Interface contracts define boundaries between components, theories, teams, modules, physical subsystems, market assumptions, or optimization layers.

A contract is needed when a change crosses a boundary.

## Contract principles

1. A boundary should preserve the meaning of upstream assumptions.
2. A downstream implementation should not smuggle in a changed objective.
3. A contract should define inputs, outputs, invariants, failure modes, and validation.
4. A contract should state which system-graph nodes it serves.
5. Changing a core contract requires a decision record.

## Contract index

| Contract | Affected nodes | Status | Owner | Last updated |
|---|---|---|---|---|
| TBD | TBD | draft | TBD | TBD |

## Generic contract shape

```yaml
id: CONTRACT-0001
name: TBD
status: draft
serves_nodes:
  - TBD
upstream_assumptions:
  - TBD
inputs:
  - name: TBD
    type: TBD
    meaning: TBD
outputs:
  - name: TBD
    type: TBD
    meaning: TBD
invariants:
  - TBD
failure_modes:
  - TBD
validation:
  - TBD
change_control:
  requires_decision_record: true
```
