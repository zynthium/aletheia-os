---
name: aletheia-promote
description: Promote reviewed AletheiaOS Wiki Handoff findings or candidate research findings into durable AletheiaOS truth records.
---

# Aletheia Promote

Use when the user has an AletheiaOS Wiki Handoff or candidate research findings
and wants to turn confirmed findings into durable AletheiaOS truth records.

Promotion rules:

1. Read the handoff before writing.
2. Separate claim, evidence, hypothesis, decision, contract, risk, node, and state updates.
3. Ask for human confirmation before changing root mission, priority order, root theory, or durable architecture decisions.
4. Create or update only durable truth records under `.aletheia/`.
5. Keep source refs attached to every promoted claim.
6. Deduplicate every candidate against existing truth records before writing.
7. Avoid duplicate promotion: update the existing truth record when the claim already exists.
8. For conflicting claims, do not promote both sides as accepted truth; keep them as evidence, hypotheses, or risks until a decision has explicit evidence links.
9. Leave unsupported or unclear claims in the wiki layer.
10. Run `.aletheia/bin/validate.py` before completion.
11. Run `.aletheia/bin/checkpoint.py` when the user wants the promoted truth committed.

Use `.aletheia/playbooks/wiki_handoff_promotion.md` as the checklist.
