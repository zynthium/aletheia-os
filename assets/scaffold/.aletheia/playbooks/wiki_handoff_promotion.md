# Wiki Handoff Promotion

Use this checklist after an external LLM Wiki produces an AletheiaOS Wiki
Handoff and the user has reviewed candidate findings.

## Promotion Checklist

1. Confirm source refs exist for every promoted claim.
2. Deduplicate against existing `.aletheia/` truth records before creating new files.
3. Promote observations and results to `.aletheia/evidence/`.
4. Promote uncertain explanations to `.aletheia/hypotheses/`.
5. Promote selected tradeoffs to `.aletheia/decisions/`.
6. Promote boundary guarantees to `.aletheia/contracts/`.
7. Promote failure modes to `.aletheia/risks/`.
8. Update active state and affected nodes.
9. Promote candidate skeleton changes only after checking parent fit.
10. Put unclear theory candidates, weak claims, and "do not promote yet"
    material into `.aletheia/state/ORPHANS.yaml` instead of the main tree.
11. Set lifecycle explicitly on hypotheses: `hypothesis`, `evidence-backed`,
    `accepted`, `operationalized`, `weakened`, `falsified`, or `archived`.
12. Link accepted decisions to evidence, and list any hypothesis they accept,
    weaken, falsify, or operationalize.
13. Run `python3 .aletheia/bin/validate.py`.
14. Run `python3 .aletheia/bin/checkpoint.py`.

## Guardrails

- Do not promote a claim without source refs.
- Do not treat a wiki page as durable truth.
- Do not create a duplicate promotion when the same claim already has a truth record;
  update the existing truth record with new source refs, limitations, or confidence impact.
- For conflicting claims, do not promote both sides as accepted truth. Record the
  conflict as evidence, hypothesis, or risk until a decision has explicit evidence links.
- Do not change root mission, priority order, root theory, or durable
  architecture decisions without human confirmation.
- Keep rejected, unclear, or unsupported material in the wiki layer.
- Do not force an unmounted finding into the main skeleton. Incubate it with
  candidate parents, evidence needed, and next review date.
- Treat counter-evidence as first-class evidence or risk; do not hide it in
  prose summaries.
- Do not let an accepted decision depend on a weakened or falsified hypothesis
  unless the hypothesis includes an explicit review note explaining why.
