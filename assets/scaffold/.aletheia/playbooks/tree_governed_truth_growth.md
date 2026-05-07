# Tree-Governed Truth Growth

Use this playbook when adding durable truth, promoting research findings, or
changing the project skeleton.

## Growth Rule

Every durable truth update must answer one question:

> Where does this belong in the root-based skeleton tree?

If the answer is unclear, do not force it into the main tree. Put it in
`.aletheia/state/ORPHANS.yaml` with candidate parents and review criteria.

## Actions

- `attach_orphan`: move an incubating item under a parent node after evidence review.
- `insert_parent`: add a missing intermediate branch above existing children.
- `promote_node`: turn an overgrown leaf into a branch.
- `demote_node`: simplify a weak branch into a leaf or supporting record.
- `split_node`: separate a node that carries multiple mechanisms.
- `merge_nodes`: combine duplicate or overlapping siblings.
- `move_subtree`: relocate a branch when its parent no longer explains it.
- `archive_branch`: retire a falsified or obsolete branch.

## Workflow

1. Orient on the current tree.
2. Identify the active node and parent constraints.
3. Decide whether the new material attaches, incubates, or triggers refactor.
4. If attaching, update affected node/skeleton refs and supporting records.
5. If incubating, update `.aletheia/state/ORPHANS.yaml`.
6. If restructuring, record a decision with evidence links and rollback criteria.
7. Run validation.
8. Checkpoint only when the user wants the truth update committed.

## Human Confirmation Required

Ask before changing:

- root mission;
- root theory;
- project priority order;
- durable architecture decisions;
- accepted decisions that govern multiple branches.

## Anti-Bloat Rule

Do not create a new record type just because a concept has a name. Prefer:

- `nodes` for durable tree positions;
- `hypotheses` for theory candidates;
- `evidence` for observations and results;
- `decisions` for accepted tradeoffs and tree refactors;
- `risks` for failure modes and unresolved contradictions;
- `ORPHANS.yaml` for unmounted candidates.

## Claim Lifecycle

Use lifecycle states on existing records instead of adding a claim registry:

- observations and results go to evidence;
- candidate explanations go to hypotheses with `Lifecycle: hypothesis`;
- hypotheses with support can move to `evidence-backed`;
- accepted decisions must link evidence and the hypotheses they accept;
- operationalized claims should point to the node, contract, decision, or code
  constraint that now depends on them;
- weakened or falsified hypotheses should stay visible and should not support
  accepted decisions without an explicit review note.
