# Playbook — Rebalance System Graph

Trigger when evidence, blockers, or implementation feasibility changes priorities.

Ask:

1. Which node changed?
2. Which parent assumptions were affected?
3. Which branches should gain weight?
4. Which branches should lose weight?
5. Which branches should be frozen, killed, or promoted?
6. Did a downstream blocker reveal an upstream design flaw?
7. Is a decision record required?

Output required:

```yaml
node: TBD
old_weight: TBD
new_weight: TBD
old_confidence: TBD
new_confidence: TBD
evidence_or_decision: TBD
reason: TBD
downstream_impact: TBD
next_action: TBD
```
