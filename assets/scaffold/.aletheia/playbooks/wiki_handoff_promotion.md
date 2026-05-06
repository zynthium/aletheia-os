# Wiki Handoff Promotion

Use this checklist after an external LLM Wiki produces an AletheiaOS Wiki
Handoff and the user has reviewed candidate findings.

## Promotion Checklist

1. Confirm source refs exist for every promoted claim.
2. Promote observations and results to `.aletheia/evidence/`.
3. Promote uncertain explanations to `.aletheia/hypotheses/`.
4. Promote selected tradeoffs to `.aletheia/decisions/`.
5. Promote boundary guarantees to `.aletheia/contracts/`.
6. Promote failure modes to `.aletheia/risks/`.
7. Update active state and affected nodes.
8. Run `python3 .aletheia/bin/validate.py`.
9. Run `python3 .aletheia/bin/checkpoint.py`.

## Guardrails

- Do not promote a claim without source refs.
- Do not treat a wiki page as durable truth.
- Do not change root mission, priority order, root theory, or durable
  architecture decisions without human confirmation.
- Keep rejected, unclear, or unsupported material in the wiki layer.
