# tests/ Agent Rules

This directory verifies implementation, assumptions, boundaries, and regressions.

Before adding or changing tests:

1. Identify the system node, contract, evidence item, or failure mode being tested.
2. Distinguish ordinary code correctness from domain validity checks.
3. Prefer tests that protect against silent drift: leakage, invalid state transitions, contract violations, proxy optimization, or reproducibility failures.

After adding tests:

1. Record the relevant contract/evidence/decision link when the test protects a domain assumption.
2. Run the narrowest useful test set, then broader validation when appropriate.
3. Update active state if a test result changes blockers, confidence, or next actions.
