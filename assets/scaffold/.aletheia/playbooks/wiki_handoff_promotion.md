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
9. Run `python3 .aletheia/bin/validate.py`.
10. Run `python3 .aletheia/bin/checkpoint.py`.

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
