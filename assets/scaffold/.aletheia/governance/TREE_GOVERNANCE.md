# Tree Governance

AletheiaOS truth grows from a root-based skeleton. Durable truth should either
attach to the main tree or stay in the incubator until review.

## Core Rules

1. The project must have one root node.
2. Active main-tree nodes must have a parent, except `root`.
3. Child nodes must state what they inherit from the parent and what they add.
4. Unsupported or unclear material belongs in `.aletheia/state/ORPHANS.yaml`.
5. Root mission, root theory, priority order, and durable architecture changes require human confirmation.
6. Tree restructuring is a decision, not an untracked edit.

## Main Tree

SKELETON.yaml is the authoritative truth tree. SYSTEM_GRAPH.yaml is a coarse system map.
Use the system map for orientation and compatibility with earlier project views;
durable truth growth should attach to the skeleton or remain incubated until a
defensible parent exists.

The canonical tree is `.aletheia/state/SKELETON.yaml`. Use it to track:

- root, trunk, branch, and leaf layers;
- parent and child relationships;
- inherited constraints;
- supporting evidence, decisions, and contracts;
- review triggers and confidence.

## Incubator

Use `.aletheia/state/ORPHANS.yaml` for observations, candidate theories,
possible nodes, or imported findings that do not yet have a defensible parent.

Each incubator entry should state:

- why it is not attached yet;
- candidate parents, if any;
- evidence needed before promotion;
- next review date;
- disposition: incubating, attach, split, merge, archive, or promote_to_branch.

## Claim Lifecycle

AletheiaOS does not need a separate claim registry by default. Use existing
truth records and make lifecycle state explicit:

- `observation`: recorded fact or source-backed observation;
- `interpretation`: explanation of what an observation may mean;
- `hypothesis`: candidate explanation that needs evidence;
- `evidence-backed`: hypothesis with supporting evidence;
- `accepted`: decision-backed claim currently used by the project;
- `operationalized`: accepted claim that has become a contract, node, or implementation constraint;
- `weakened`: evidence lowered confidence but did not falsify it;
- `falsified`: evidence contradicts the claim;
- `archived`: no longer active, preserved for audit.

Lifecycle rules:

1. A hypothesis should not become accepted without supporting evidence.
2. An accepted decision must link evidence.
3. A falsified or weakened hypothesis should not support an accepted decision
   without an explicit review note.
4. Operationalized claims should point to the node, contract, or decision that
   now depends on them.
5. Counter-evidence should stay visible as evidence or risk, not disappear into
   prose summaries.

## Scientific Method Loop

Tree governance controls where truth belongs. The scientific-method loop
controls how truth earns, keeps, weakens, or loses its place.

1. Observe: record source-backed observations as evidence.
2. Hypothesize: express candidate explanations with scope and invalidation criteria.
3. Test: attach supporting and contradicting evidence.
4. Decide: accept, reject, weaken, operationalize, or incubate the claim.
5. Implement: convert accepted claims into nodes, contracts, or code constraints.
6. Review: use feedback to refactor, demote, archive, or reparent tree members.

## Tree Refactors

Tree refactors include attaching orphans, inserting parents, moving subtrees,
splitting overloaded nodes, merging duplicates, promoting leaves, demoting
branches, and archiving failed branches.

Record meaningful tree refactors as decisions with affected nodes, evidence
links, rollback conditions, and review triggers.

## Validation Severity

Hard validation errors should protect structure:

- missing root;
- missing parent for active main-tree nodes;
- parent references unknown node;
- cycles;
- invalid support refs.

Warnings should guide judgment:

- stale orphan review;
- overloaded node;
- unsupported leaf;
- weak or missing review metadata;
- likely missing intermediate branch.
