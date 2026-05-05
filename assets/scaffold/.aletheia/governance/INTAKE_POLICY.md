# Intake Policy

Existing material is not automatically true. During bootstrap or research
intake, inventory source material, classify reliability and sensitivity, and
synthesize candidate truth with provenance before promotion.

## Categories

- `authoritative_current`
- `useful_but_unverified`
- `historical_context`
- `superseded`
- `conflicting`
- `unsafe_or_sensitive`
- `deferred_due_to_size`
- `unknown`

## Required Output

Research intake must write or update `.aletheia/truth_intake/registry.json`
and use `.aletheia/truth_intake/runs/<run_id>/` for temporary intake work.
The completed run workspace should be removed by
`.aletheia/bin/truth_intake.py finish` after the final checkpoint.

Bootstrap or fusion packets must include:

- initialization mode;
- inventory summary;
- classification summary;
- sensitive exclusions;
- candidate truth records;
- unresolved questions.

Promoted items must be recorded in `.aletheia/truth_intake/PROMOTION_LOG.md`
and linked from the durable truth records they update.
