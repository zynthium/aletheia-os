# Tree-Governed Truth Growth

Use this playbook when adding durable truth, promoting research findings, or
changing the project skeleton.

This playbook exists to prevent unstructured project growth. A durable truth
update is not complete until it answers:

- What root objective does it serve?
- Which parent node does it inherit from?
- What evidence supports it?
- What would weaken or falsify it?
- Should it attach to the main tree, remain orphaned, or trigger a tree refactor?

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
7. Choose the required traceability trailers from
   `.aletheia/governance/TREE_GOVERNANCE.md` before committing tree or skeleton
   changes.
8. Run validation.
9. Before claiming a node is stable, run the current stable-node prerequisite:

   ```bash
   python3 .aletheia/bin/checkpoint.py --dry-run
   ```

   Once the Git history audit runtime is installed, this post-checkpoint audit
   is also required before claiming stable:

   ```bash
   python3 .aletheia/bin/history_audit.py --json
   ```

10. Checkpoint only when the user wants the truth update committed, and include
    the matching `AIOS-Tree-Op` or `AIOS-Node-State` trailers.

## Minimal Tree Refactor Recipes

No new command. No new record family. Use the existing truth files, scripts, and
review records below.

### Attach orphan

1. Read `ORPHANS.yaml` and confirm the candidate parent from evidence.
2. Add or update the target node in `SKELETON.yaml`.
3. Move the orphan disposition out of incubating or remove the cleared entry.
4. Link the supporting `evidence` and `decisions`.
5. Prepare the `AIOS-Tree-Op: attach_orphan` trailer for the checkpoint commit.
6. Run `validate.py`, then inspect `status.py`, `orient.py`, and `overview.py`.

### Insert parent

1. Identify siblings that share an unmodeled intermediate purpose.
2. Add the parent branch to `SKELETON.yaml`.
3. Reparent the existing children under that branch.
4. Record the refactor in `decisions` with evidence links and rollback criteria.
5. Prepare the `AIOS-Tree-Op: insert_parent` trailer for the checkpoint commit.
6. Run `validate.py`, then inspect `status.py`, `orient.py`, and `overview.py`.

### Split node

1. Identify the overloaded node and the separate mechanisms it is carrying.
2. Keep the old node as the parent or archive it through a decision if it no
   longer has a clean purpose.
3. Add the new child nodes in `SKELETON.yaml`.
4. Move supporting refs to the child that now owns them.
5. Prepare the `AIOS-Tree-Op: split_node` trailer for the checkpoint commit.
6. Run `validate.py`, then inspect `status.py`, `orient.py`, and `overview.py`.

### Merge nodes

1. Identify duplicate or overlapping siblings.
2. Keep one canonical node in `SKELETON.yaml`.
3. Mark the duplicate node `status: archived` when history should stay visible.
4. Keep supporting `evidence` and `decisions` linked to the retained branch.
5. Prepare the relevant `AIOS-Node-State` trailer for any weakened, falsified,
   or archived node.
6. Run `validate.py`, then inspect `status.py`, `orient.py`, and `overview.py`.

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
