# Source Policy

Existing material is not automatically true. During bootstrap, inventory prior
materials, classify reliability and sensitivity, and synthesize durable state
with provenance.

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

Bootstrap source inventory must write `.aletheia/source_inventory/TRUTH_INVENTORY_REPORT.md`
with:

- initialization mode;
- inventory summary;
- classification summary;
- sensitive exclusions;
- durable records created or updated;
- unresolved questions.
