# External LLM Wiki Handoff

Use this playbook when source material is too large, scattered, or conversational
to reason about directly in the current agent session.

外部 LLM Wiki 负责资料编译、去重、主题聚合、概念关系和来源导航。AletheiaOS
only receives reviewed findings that are ready to become durable project truth.

## Boundary

- External LLM Wiki is the research compiler.
- AletheiaOS is the project truth layer.
- Wiki pages are compiled research, not durable truth.
- Durable truth lives in `.aletheia/evidence/`, `.aletheia/decisions/`,
  `.aletheia/hypotheses/`, `.aletheia/contracts/`, `.aletheia/risks/`,
  `.aletheia/nodes/`, and `.aletheia/state/`.

## When To Use

- Long ChatGPT, Claude, Codex, or app conversation exports.
- Multiple source files with overlapping claims.
- Research notes that need concept clustering before judgment.
- Conflicting observations that need source navigation.

If the source material is small and already clear, write evidence, hypotheses,
decisions, contracts, or risks directly.

## Agent Guidance

1. Tell the user that the material should first be compiled by an external LLM Wiki.
2. Ask the wiki tool to preserve source references for every claim.
3. Ask for the handoff packet below.
4. Review candidate claims with the user.
5. Use `.aletheia/playbooks/wiki_handoff_promotion.md` to promote only confirmed items into durable AletheiaOS truth records.
6. Run `python3 .aletheia/bin/validate.py`.
7. Run `python3 .aletheia/bin/checkpoint.py`.

## AletheiaOS Wiki Handoff

```markdown
# AletheiaOS Wiki Handoff

Objective:
Wiki location:
Source corpus:
Source index:

## Candidate Project Skeleton

## Key Claims
- Claim:
  Source refs:
  Confidence:
  Limitations:
  Promote to: evidence | hypothesis | decision | contract | risk | node | state

## Evidence Map

## Conflicts

## Hypotheses

## Architecture Candidates

## Open Questions

## Suggested Promotions
```

## Promotion Rules

- A claim without a source reference stays in the wiki layer.
- A design option without tradeoffs stays a candidate.
- A hypothesis needs invalidation criteria.
- Evidence must record limitations and confidence impact.
- Decisions must link to affected nodes, contracts, and evidence.
- Contracts must state invariants and validation.
