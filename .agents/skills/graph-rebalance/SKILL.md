---
name: graph-rebalance
description: Rebalance system graph weights, dependencies, confidence, status, and branch priorities after evidence or blockers.
---

# Graph Rebalance Skill

Trigger when evidence, blockers, implementation feasibility, market/physical constraints, or objective changes affect priorities.

Return:
```yaml
changed_node: TBD
old_weight: TBD
new_weight: TBD
old_confidence: TBD
new_confidence: TBD
evidence_or_decision: TBD
branches_promoted: []
branches_demoted: []
branches_frozen: []
branches_killed: []
parent_review_required: true|false
reason: TBD
```

Do not change weight without evidence, decision, or explicitly marked judgment.
