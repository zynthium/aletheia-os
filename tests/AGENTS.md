# tests/ Agent Rules


## Model gate

For any durable write in this directory, the current AI assistant must have an allowed agent run for the task class:

```bash
python3 scripts/aios_model_gate.py --task-class <task_class> --record --objective "<short objective>"
```

Unknown or under-tier models may read and orient only.

This directory verifies implementation, assumptions, boundaries, and regressions.

Before adding or changing tests:

1. Identify the system node, contract, evidence item, or failure mode being tested.
2. Distinguish ordinary code correctness from domain validity checks.
3. Prefer tests that protect against silent drift: leakage, invalid state transitions, contract violations, proxy optimization, or reproducibility failures.

After adding tests:

1. Record the relevant contract/evidence/decision link when the test protects a domain assumption.
2. Run the narrowest useful test set, then broader validation when appropriate.
3. Update active state if a test result changes blockers, confidence, or next actions.
