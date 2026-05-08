# AletheiaOS Git Traceability Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AletheiaOS truth-tree growth reconstructable from repository files plus Git history, with explicit stable-node commit markers, hook enforcement, and history audit.

**Architecture:** Keep `.aletheia/` as the current truth-state control plane and use Git commits as the immutable transition log. Add a small trailer schema, checkpoint-generated metadata, commit-message hook checks, and history audit without introducing a separate ledger, database, service, or new tree CRUD subsystem.

**Tech Stack:** Python standard library, Git commit trailers, Markdown/YAML scaffold files, shell Git hooks, unittest.

---

## Scope Boundaries

- Do not create a separate `.aletheia/ledger/` or duplicate Git history in another durable record store.
- Do not add a database, web UI, daemon, background service, MCP server, or external dependency.
- Do not try to prove semantic truth automatically. Runtime checks verify structure, evidence links, decision links, explicit review markers, and legal state transitions.
- Do not make every normal documentation commit use tree trailers. Tree trailers are mandatory only for truth-tree state transitions and stable-node claims.
- Do not remove the current `orient -> work -> update truth -> validate -> checkpoint` loop.
- Do not make Codex claim automatic hook parity with Claude Code. Codex remains explicit: preflight, validate, checkpoint, and history audit.

## Problem Frame

AletheiaOS already has the correct current-state model: `SKELETON.yaml` for the authoritative tree, `ORPHANS.yaml` for incubating material, and evidence, hypotheses, decisions, contracts, risks, nodes, active state, and agent runs as supporting records. The weak point is the gap between conversational agent judgment and durable traceability.

Coding assistants are good at producing coherent explanations, but they naturally lose context across sessions, can stop before durable records are complete, and can leave human confirmation in chat instead of the repository. Git can close that gap if commits become structured transition records instead of only file snapshots.

This batch makes Git participate in AletheiaOS mechanics:

```text
current truth state in .aletheia/
+ structured commit trailers
+ validation and commit-message gates
+ history audit
= reviewable and reversible truth-tree growth
```

## Requirements

- R1. Define a machine-readable Git trailer schema for AletheiaOS truth-tree transitions.
- R2. Extend `checkpoint.py` so agents can generate valid trailers instead of hand-writing commit metadata.
- R3. Install a `commit-msg` hook during bootstrap finalize and use it to block malformed stable-node claims.
- R4. Add a history audit command that reconstructs node growth, stable markers, weakening, falsification, archival, and implementation links from Git history.
- R5. Keep validation staged: structural truth errors remain in `validate.py`; history and transition errors live in the new history audit path.
- R6. Surface the new audit path through `actions.json`, `CAPABILITY_MAP.md`, `help.py`, `status.py` or `preflight.py`, README, and skills.
- R7. Preserve default checkpoint behavior: stage only durable AletheiaOS state/control-plane paths unless `--include-worktree` is explicit.
- R8. Add tests that prove normal commits still work, tree changes require traceability, stable markers require evidence/decision/review, and history audit catches broken transitions.

## Design Decisions

- Use Git trailers, not subject prefixes, as the durable machine-readable protocol.
- Let `checkpoint.py` generate trailers. Humans can still write trailers manually, but hooks and audits judge the final commit message.
- Keep `validate.py` focused on current tree-state integrity. Add `history_audit.py` for temporal claims.
- Install generated hooks in `.aletheia/hooks/` at bootstrap time. The scaffold continues to store hook source logic in `.aletheia/bin/`.
- Treat `AIOS-Node-State: stable` as a strong claim. It must link evidence, link a decision, pass validation, and carry an explicit review marker.
- Treat implementation commits as traceable when they include `AIOS-Implements` pointing to an accepted decision, contract, or evidence-backed node.

## Trailer Schema

The first batch supports these trailers:

```text
AIOS-Action: truth.tree.transition | truth.node.stabilize | truth.node.weaken | truth.node.falsify | truth.node.archive | engineering.implements_truth
AIOS-Tree-Op: incubate | attach_orphan | insert_parent | split_node | merge_nodes | move_subtree | promote_node | demote_node | archive_branch
AIOS-Node: root | system_design | theory_model | evidence_validation | risk_safety
AIOS-Parent: root | system_design | theory_model | evidence_validation | risk_safety
AIOS-Node-State: candidate | stable | weakened | falsified | archived
AIOS-Evidence: .aletheia/evidence/EV-001-factor-baseline.md
AIOS-Decision: .aletheia/decisions/DEC-001-modeling-lens-policy.md
AIOS-Implements: .aletheia/decisions/DEC-001-modeling-lens-policy.md
AIOS-Supersedes: .aletheia/hypotheses/HYP-001-factor-momentum.md
AIOS-Validation: pass
AIOS-Review: human-confirmed | agent-reviewed | not-required
```

Stable-node commits require:

```text
AIOS-Action: truth.node.stabilize
AIOS-Node: <known node id>
AIOS-Node-State: stable
AIOS-Evidence: <existing .aletheia/evidence/*.md>
AIOS-Decision: <existing .aletheia/decisions/*.md>
AIOS-Validation: pass
AIOS-Review: human-confirmed
```

## File Structure

- Create: `assets/scaffold/.aletheia/bin/git_trailers.py`
  - Responsibility: parse, format, and validate AletheiaOS trailer key/value pairs.
- Create: `assets/scaffold/.aletheia/bin/commit_msg_hook.py`
  - Responsibility: enforce commit-message traceability rules from staged changes and the proposed commit message.
- Create: `assets/scaffold/.aletheia/bin/history_audit.py`
  - Responsibility: audit Git history for AletheiaOS trailer schema, stable-node requirements, and transition consistency.
- Modify: `assets/scaffold/.aletheia/bin/checkpoint.py`
  - Responsibility: expose tree traceability arguments and append generated trailers.
- Modify: `assets/scaffold/.aletheia/bin/bootstrap_finalize.py`
  - Responsibility: install `commit-msg` in addition to `pre-commit`.
- Modify: `assets/scaffold/.aletheia/bin/preflight.py`
  - Responsibility: report history-audit readiness and recommend `truth.history_audit`.
- Modify: `assets/scaffold/.aletheia/bin/status.py`
  - Responsibility: include compact history-audit signal without making it a hard status dependency.
- Modify: `assets/scaffold/.aletheia/bin/help.py`
  - Responsibility: list the new traceability and audit commands.
- Modify: `assets/scaffold/.aletheia/governance/GIT_POLICY.md`
  - Responsibility: define Git as transition-log boundary and document stable-node marker rules.
- Modify: `assets/scaffold/.aletheia/governance/TREE_GOVERNANCE.md`
  - Responsibility: connect tree refactors and stable-node claims to Git trailers.
- Modify: `assets/scaffold/.aletheia/governance/actions.json`
  - Responsibility: add `truth.history_audit` and document checkpoint traceability options.
- Modify: `assets/scaffold/.aletheia/CAPABILITY_MAP.md`
  - Responsibility: expose history audit, stable-node checkpoint, and commit-message enforcement as agent-visible actions.
- Modify: `assets/scaffold/.aletheia/playbooks/tree_governed_truth_growth.md`
  - Responsibility: add the Git transition protocol to attach, refactor, and stabilize workflows.
- Modify: `skills/aletheia-checkpoint/SKILL.md`
  - Responsibility: tell agents when to use traceability trailers and history audit.
- Modify: `skills/aletheia-architecture-evolution/SKILL.md`
  - Responsibility: require traceable commits for skeleton and durable architecture changes.
- Modify: `README.md` and `README.zh-CN.md`
  - Responsibility: explain Git as the transition ledger and document the explicit Codex loop.
- Test: `tests/test_git_traceability.py`
  - Responsibility: focused tests for trailer parsing, checkpoint trailer generation, commit-msg enforcement, and history audit.
- Test: `tests/test_checkpoint.py`
  - Responsibility: regress default checkpoint behavior and agent attribution trailer preservation.
- Test: `tests/test_bootstrap_finalize.py`
  - Responsibility: prove `commit-msg` hook installation and inspect output.
- Test: `tests/test_runtime_validate.py`
  - Responsibility: verify action/capability/status/preflight surfacing.
- Test: `tests/test_research_iteration_flow.py`
  - Responsibility: extend the end-to-end research iteration with stable-node transition history.
- Test: `tests/test_plugin_manifest.py`
  - Responsibility: package and scaffold validation coverage for new runtime scripts and documentation terms.

---

## Iteration 1: Define Trailer Protocol And Governance

**Goal:** Make the Git/AletheiaOS contract explicit before adding enforcement.

**Files:**
- Modify: `assets/scaffold/.aletheia/governance/GIT_POLICY.md`
- Modify: `assets/scaffold/.aletheia/governance/TREE_GOVERNANCE.md`
- Modify: `assets/scaffold/.aletheia/playbooks/tree_governed_truth_growth.md`
- Modify: `skills/aletheia-checkpoint/SKILL.md`
- Modify: `skills/aletheia-architecture-evolution/SKILL.md`
- Test: `tests/test_plugin_manifest.py`

- [ ] Add failing tests for required protocol language.

Add assertions to `tests/test_plugin_manifest.py` checking these exact terms in the scaffold:

```python
required_terms = [
    "AIOS-Action",
    "AIOS-Tree-Op",
    "AIOS-Node-State: stable",
    "AIOS-Validation: pass",
    "AIOS-Review: human-confirmed",
    "Git commits are AletheiaOS truth-transition records",
]
```

Run:

```bash
python3 -m unittest tests.test_plugin_manifest -v
```

Expected before implementation: FAIL with missing protocol terms.

- [ ] Update `GIT_POLICY.md`.

Add sections with these rules:

```markdown
## Truth Transition Commits

Git commits are AletheiaOS truth-transition records. `.aletheia/` stores the current truth state; Git history stores how that state changed.

Use AletheiaOS trailers when a commit changes the truth tree, stabilizes a node, weakens or falsifies a claim, archives a branch, or implements an accepted decision.

## Stable Node Marker

`AIOS-Node-State: stable` is a strong traceability claim. It requires:

1. `AIOS-Action: truth.node.stabilize`
2. `AIOS-Node: <known node id>`
3. `AIOS-Evidence: <existing evidence record>`
4. `AIOS-Decision: <existing accepted decision record>`
5. `AIOS-Validation: pass`
6. `AIOS-Review: human-confirmed`

Do not use `stable` for unreviewed hypotheses, unsupported children, stale orphans, or root-level theory changes that have not received explicit human confirmation.
```

- [ ] Update `TREE_GOVERNANCE.md`.

Add a "Git Transition Protocol" section mapping tree lifecycle to trailers:

```markdown
| Tree lifecycle | Required Git marker |
|---|---|
| incubating unmounted material | `AIOS-Tree-Op: incubate` |
| attaching an orphan | `AIOS-Tree-Op: attach_orphan` |
| inserting a parent | `AIOS-Tree-Op: insert_parent` |
| splitting a node | `AIOS-Tree-Op: split_node` |
| moving a subtree | `AIOS-Tree-Op: move_subtree` |
| stabilizing a node | `AIOS-Node-State: stable` |
| weakening a claim | `AIOS-Node-State: weakened` |
| falsifying a claim | `AIOS-Node-State: falsified` |
| archiving a branch | `AIOS-Node-State: archived` |
```

- [ ] Update playbook and skills.

Add instructions that agents must run:

```bash
python3 .aletheia/bin/checkpoint.py --dry-run
python3 .aletheia/bin/history_audit.py --json
```

before claiming a node is stable.

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_plugin_manifest -v
```

Expected: PASS.

- [ ] Commit.

```bash
git add assets/scaffold/.aletheia/governance/GIT_POLICY.md assets/scaffold/.aletheia/governance/TREE_GOVERNANCE.md assets/scaffold/.aletheia/playbooks/tree_governed_truth_growth.md skills/aletheia-checkpoint/SKILL.md skills/aletheia-architecture-evolution/SKILL.md tests/test_plugin_manifest.py
git commit -m "docs: define AletheiaOS git transition protocol"
```

---

## Iteration 2: Add Trailer Parsing And Checkpoint Generation

**Goal:** Make traceability metadata generated by `checkpoint.py` instead of hand-written.

**Files:**
- Create: `assets/scaffold/.aletheia/bin/git_trailers.py`
- Modify: `assets/scaffold/.aletheia/bin/checkpoint.py`
- Test: `tests/test_git_traceability.py`
- Test: `tests/test_checkpoint.py`

- [ ] Write failing tests for trailer parsing.

Create `tests/test_git_traceability.py` with tests that copy the scaffold to a temp repo and import `git_trailers.py` using `importlib.util.spec_from_file_location`.

Test cases:

```python
message = "subject\n\nbody\n\nAIOS-Action: truth.node.stabilize\nAIOS-Node: theory_model\n"
trailers = git_trailers.parse_trailers(message)
self.assertEqual(trailers["AIOS-Action"], ["truth.node.stabilize"])
self.assertEqual(trailers["AIOS-Node"], ["theory_model"])
```

```python
trailers = git_trailers.build_aios_trailers(
    action="truth.node.stabilize",
    tree_op=None,
    node="theory_model",
    parent="root",
    node_state="stable",
    evidence=[".aletheia/evidence/EV-001-factor-baseline.md"],
    decision=[".aletheia/decisions/DEC-001-modeling-lens-policy.md"],
    implements=[],
    supersedes=[],
    validation="pass",
    review="human-confirmed",
)
self.assertIn("AIOS-Node-State: stable", trailers)
self.assertIn("AIOS-Review: human-confirmed", trailers)
```

Run:

```bash
python3 -m unittest tests.test_git_traceability -v
```

Expected before implementation: FAIL because `git_trailers.py` does not exist.

- [ ] Implement `git_trailers.py`.

Required public functions:

```python
def parse_trailers(message: str) -> dict[str, list[str]]:
    ...

def build_aios_trailers(
    *,
    action: str | None,
    tree_op: str | None,
    node: str | None,
    parent: str | None,
    node_state: str | None,
    evidence: list[str],
    decision: list[str],
    implements: list[str],
    supersedes: list[str],
    validation: str | None,
    review: str | None,
) -> str:
    ...

def validate_trailer_values(trailers: dict[str, list[str]]) -> list[str]:
    ...
```

Allowed values:

```python
ALLOWED_ACTIONS = {
    "truth.tree.transition",
    "truth.node.stabilize",
    "truth.node.weaken",
    "truth.node.falsify",
    "truth.node.archive",
    "engineering.implements_truth",
}
ALLOWED_TREE_OPS = {
    "incubate",
    "attach_orphan",
    "insert_parent",
    "split_node",
    "merge_nodes",
    "move_subtree",
    "promote_node",
    "demote_node",
    "archive_branch",
}
ALLOWED_NODE_STATES = {"candidate", "stable", "weakened", "falsified", "archived"}
ALLOWED_VALIDATION = {"pass"}
ALLOWED_REVIEW = {"human-confirmed", "agent-reviewed", "not-required"}
```

- [ ] Write failing checkpoint test for generated trailers.

Add a test to `tests/test_checkpoint.py` that:

1. Initializes a temp repo.
2. Writes a valid current agent run.
3. Creates required evidence and accepted decision records.
4. Updates `.aletheia/state/ACTIVE_STATE.md`.
5. Runs:

```bash
python3 .aletheia/bin/checkpoint.py --auto --message "truth: stabilize theory node" --tree-op attach_orphan --node theory_model --parent root --node-state stable --evidence .aletheia/evidence/EV-001-factor-baseline.md --decision .aletheia/decisions/DEC-001-modeling-lens-policy.md --review human-confirmed
```

Expected committed message contains:

```text
AIOS-Action: truth.node.stabilize
AIOS-Tree-Op: attach_orphan
AIOS-Node: theory_model
AIOS-Parent: root
AIOS-Node-State: stable
AIOS-Evidence: .aletheia/evidence/EV-001-factor-baseline.md
AIOS-Decision: .aletheia/decisions/DEC-001-modeling-lens-policy.md
AIOS-Validation: pass
AIOS-Review: human-confirmed
```

- [ ] Extend `checkpoint.py` CLI.

Add arguments:

```python
parser.add_argument("--tree-op")
parser.add_argument("--node")
parser.add_argument("--parent")
parser.add_argument("--node-state", choices=["candidate", "stable", "weakened", "falsified", "archived"])
parser.add_argument("--evidence", action="append", default=[])
parser.add_argument("--decision", action="append", default=[])
parser.add_argument("--implements", action="append", default=[])
parser.add_argument("--supersedes", action="append", default=[])
parser.add_argument("--review", choices=["human-confirmed", "agent-reviewed", "not-required"])
```

When `--node-state stable` is present, infer:

```text
AIOS-Action: truth.node.stabilize
AIOS-Validation: pass
```

When `--implements` is present and no node state is supplied, infer:

```text
AIOS-Action: engineering.implements_truth
```

When `--tree-op` is present and no stable node state is supplied, infer:

```text
AIOS-Action: truth.tree.transition
```

- [ ] Block invalid stable checkpoint before Git commit.

In `checkpoint.py`, before staging:

```text
if node_state == stable and evidence is empty: block with "stable node checkpoint requires --evidence"
if node_state == stable and decision is empty: block with "stable node checkpoint requires --decision"
if node_state == stable and review != human-confirmed: block with "stable node checkpoint requires --review human-confirmed"
```

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_git_traceability tests.test_checkpoint -v
```

Expected: PASS.

- [ ] Commit.

```bash
git add assets/scaffold/.aletheia/bin/git_trailers.py assets/scaffold/.aletheia/bin/checkpoint.py tests/test_git_traceability.py tests/test_checkpoint.py
git commit -m "feat(checkpoint): emit AletheiaOS traceability trailers"
```

---

## Iteration 3: Enforce Commit Messages With Git Hooks

**Goal:** Prevent untraceable stable-node and tree-structure commits when hooks are installed.

**Files:**
- Create: `assets/scaffold/.aletheia/bin/commit_msg_hook.py`
- Modify: `assets/scaffold/.aletheia/bin/bootstrap_finalize.py`
- Test: `tests/test_git_traceability.py`
- Test: `tests/test_bootstrap_finalize.py`

- [ ] Write failing hook tests.

Add tests proving:

```text
commit_msg_hook.py allows a normal README-only commit without AIOS trailers.
commit_msg_hook.py rejects staged SKELETON.yaml changes without AIOS-Tree-Op or AIOS-Node-State.
commit_msg_hook.py rejects AIOS-Node-State: stable without evidence, decision, validation pass, and human-confirmed review.
commit_msg_hook.py accepts a stable message when all required trailers are present and referenced paths exist.
```

Run:

```bash
python3 -m unittest tests.test_git_traceability -v
```

Expected before implementation: FAIL because `commit_msg_hook.py` does not exist.

- [ ] Implement `commit_msg_hook.py`.

Inputs:

```text
argv[1] is the Git commit message file path.
Repository root is Path(__file__).resolve().parents[2].
```

Checks:

```text
git diff --cached --name-only --diff-filter=ACMRT
```

Tree-sensitive staged paths:

```python
TREE_SENSITIVE_PREFIXES = (
    ".aletheia/state/SKELETON.yaml",
    ".aletheia/state/ORPHANS.yaml",
    ".aletheia/nodes/",
)
```

Rules:

```text
If no tree-sensitive paths are staged and no AIOS-Node-State stable marker exists, return 0.
If tree-sensitive paths are staged, require AIOS-Action and one of AIOS-Tree-Op or AIOS-Node-State.
If AIOS-Node-State is stable, require AIOS-Action truth.node.stabilize, AIOS-Node, AIOS-Evidence, AIOS-Decision, AIOS-Validation pass, and AIOS-Review human-confirmed.
For AIOS-Evidence, AIOS-Decision, AIOS-Implements, and AIOS-Supersedes, reject absolute paths and paths containing `..`.
For stable evidence and decision refs, require the target files to exist.
```

Error output should start with:

```text
AletheiaOS commit message blocked:
```

- [ ] Extend `bootstrap_finalize.py` hook installation.

Change `configure_hooks` so it writes:

```sh
#!/bin/sh
python3 .aletheia/bin/validate.py
```

to `.aletheia/hooks/pre-commit`, and:

```sh
#!/bin/sh
python3 .aletheia/bin/commit_msg_hook.py "$1"
```

to `.aletheia/hooks/commit-msg`.

Also update `inspect_bootstrap_finalize()["would_write"]` to include:

```text
.aletheia/hooks/commit-msg
```

- [ ] Update bootstrap finalize tests.

Extend existing tests so:

```python
self.assertTrue((target / ".aletheia" / "hooks" / "commit-msg").exists())
self.assertIn("commit_msg_hook.py", (target / ".aletheia" / "hooks" / "commit-msg").read_text(encoding="utf-8"))
```

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_git_traceability tests.test_bootstrap_finalize -v
```

Expected: PASS.

- [ ] Commit.

```bash
git add assets/scaffold/.aletheia/bin/commit_msg_hook.py assets/scaffold/.aletheia/bin/bootstrap_finalize.py tests/test_git_traceability.py tests/test_bootstrap_finalize.py
git commit -m "feat(hooks): enforce AletheiaOS traceability trailers"
```

---

## Iteration 4: Add Git History Audit

**Goal:** Make AletheiaOS able to answer how a node became stable and whether its transition history is complete.

**Files:**
- Create: `assets/scaffold/.aletheia/bin/history_audit.py`
- Modify: `assets/scaffold/.aletheia/governance/actions.json`
- Modify: `assets/scaffold/.aletheia/CAPABILITY_MAP.md`
- Modify: `assets/scaffold/.aletheia/bin/help.py`
- Test: `tests/test_git_traceability.py`
- Test: `tests/test_runtime_validate.py`
- Test: `tests/test_plugin_manifest.py`

- [ ] Write failing history audit tests.

Add tests that create temp repos and assert:

```text
history_audit.py --json exits 0 when there are no AIOS trailers and validation passes.
history_audit.py --json reports error when a stable trailer references missing evidence.
history_audit.py --json reports stable node when a valid stable commit exists.
history_audit.py --node theory_model --json filters results to that node.
```

Expected JSON shape:

```json
{
  "ok": true,
  "returncode": 0,
  "errors": [],
  "warnings": [],
  "nodes": {
    "theory_model": {
      "latest_state": "stable",
      "stable_commit": "abc123",
      "evidence": [".aletheia/evidence/EV-001-factor-baseline.md"],
      "decision": [".aletheia/decisions/DEC-001-modeling-lens-policy.md"]
    }
  }
}
```

- [ ] Implement `history_audit.py`.

CLI:

```python
parser.add_argument("--json", action="store_true")
parser.add_argument("--node")
parser.add_argument("--max-count", type=int, default=500)
```

Git command:

```bash
git log --format=%H%x00%B%x00END%x00 --max-count <N>
```

Audit rules:

```text
Unknown AIOS trailer keys are warnings.
Invalid AIOS trailer values are errors.
Stable node trailers require existing evidence and decision paths in the current worktree.
A stable node followed later by weakened, falsified, or archived uses the latest state as current.
AIOS-Implements targets must exist and must point under .aletheia/decisions/, .aletheia/contracts/, .aletheia/evidence/, or .aletheia/nodes/.
```

Exit:

```text
0 when errors is empty.
1 when errors is not empty.
```

- [ ] Add action contract.

In `actions.json`, add:

```json
{
  "id": "truth.history_audit",
  "title": "Audit Git truth history",
  "intent": "Parse Git history for AletheiaOS traceability trailers, stable-node claims, implementation links, and transition errors.",
  "risk": "read-only",
  "command": ["python3", ".aletheia/bin/history_audit.py", "--json"],
  "inputs": {},
  "outputs": {"format": "json"},
  "verification": {"returncode": 0}
}
```

Add it to `recommended_actions` after `truth.validate`.

- [ ] Update capability and help surfaces.

Add rows/terms for:

```text
Audit Git truth history
truth.history_audit
history_audit.py --json
AIOS-Node-State: stable
```

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_git_traceability tests.test_runtime_validate tests.test_plugin_manifest -v
```

Expected: PASS.

- [ ] Commit.

```bash
git add assets/scaffold/.aletheia/bin/history_audit.py assets/scaffold/.aletheia/governance/actions.json assets/scaffold/.aletheia/CAPABILITY_MAP.md assets/scaffold/.aletheia/bin/help.py tests/test_git_traceability.py tests/test_runtime_validate.py tests/test_plugin_manifest.py
git commit -m "feat(audit): add Git truth history audit"
```

---

## Iteration 5: Surface Audit In Status, Preflight, And Daily Loop

**Goal:** Make hook-free hosts see the same traceability expectations before completion.

**Files:**
- Modify: `assets/scaffold/.aletheia/bin/preflight.py`
- Modify: `assets/scaffold/.aletheia/bin/status.py`
- Modify: `assets/scaffold/.aletheia/bin/overview.py`
- Modify: `assets/scaffold/.aletheia/START_HERE.md`
- Modify: `assets/scaffold/START_HERE.md`
- Test: `tests/test_runtime_validate.py`
- Test: `tests/test_agent_native_coverage.py`

- [ ] Write failing preflight/status tests.

Extend tests to require:

```python
self.assertIn("truth.history_audit", payload["recommended_actions"])
self.assertIn("history_audit", payload)
self.assertIn("returncode", payload["history_audit"])
```

For markdown output, require:

```text
## Git Truth History
```

- [ ] Add history audit summary to `preflight.py`.

Function:

```python
def history_audit(root: Path) -> dict:
    result = run([sys.executable, ".aletheia/bin/history_audit.py", "--json"], root)
    try:
        payload = json.loads(result.stdout)
    except Exception:
        payload = {"ok": False, "errors": ["history audit emitted invalid JSON"]}
    payload["returncode"] = result.returncode
    return payload
```

Add `truth.history_audit` to `RECOMMENDED_ACTIONS` and `python3 .aletheia/bin/history_audit.py --json` to `NEXT_ACTIONS`.

- [ ] Add compact history audit signal to `status.py`.

Include:

```json
"history_audit": {
  "returncode": 0,
  "error_count": 0,
  "warning_count": 0,
  "stable_node_count": 1
}
```

Do not make status fail when history audit fails. Status is a refresh surface.

- [ ] Add overview section.

Add `history_audit` to generated status JSON and render a compact HTML section titled:

```text
Git Truth History
```

- [ ] Update START_HERE daily loop.

Change diagnostic commands to include:

```bash
python3 .aletheia/bin/history_audit.py --json
```

State that stable-node claims require history audit in addition to validation.

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_runtime_validate tests.test_agent_native_coverage -v
```

Expected: PASS.

- [ ] Commit.

```bash
git add assets/scaffold/.aletheia/bin/preflight.py assets/scaffold/.aletheia/bin/status.py assets/scaffold/.aletheia/bin/overview.py assets/scaffold/.aletheia/START_HERE.md assets/scaffold/START_HERE.md tests/test_runtime_validate.py tests/test_agent_native_coverage.py
git commit -m "feat(status): surface Git truth history audit"
```

---

## Iteration 6: Extend End-To-End Research Iteration With Stable History

**Goal:** Prove the intended workflow across model gate, truth update, validation, checkpoint trailers, history audit, and Git log.

**Files:**
- Modify: `tests/test_research_iteration_flow.py`
- Modify: `docs/verification/host-smoke.zh-CN.md`

- [ ] Update research iteration flow test.

In the existing flow that revises the quant modeling thesis, change the final checkpoint command to:

```bash
python3 .aletheia/bin/checkpoint.py --auto --message "research: stabilize liquidity-gated modeling thesis" --tree-op promote_node --node theory_model --parent root --node-state stable --evidence .aletheia/evidence/EV-002-game-context-break.md --decision .aletheia/decisions/DEC-001-modeling-lens-policy.md --review human-confirmed
```

After commit, run:

```bash
python3 .aletheia/bin/history_audit.py --node theory_model --json
```

Assert:

```python
self.assertTrue(payload["ok"])
self.assertEqual(payload["nodes"]["theory_model"]["latest_state"], "stable")
self.assertIn(".aletheia/evidence/EV-002-game-context-break.md", payload["nodes"]["theory_model"]["evidence"])
self.assertIn("AIOS-Node-State: stable", committed.stdout)
```

- [ ] Add host smoke steps.

In `docs/verification/host-smoke.zh-CN.md`, add a traceability smoke section:

```text
1. Run `python3 .aletheia/bin/history_audit.py --json`.
2. Expected: returncode 0 and `ok: true`.
3. Create a dry-run checkpoint with `--node-state stable` and missing `--decision`.
4. Expected: checkpoint blocks before commit and prints `stable node checkpoint requires --decision`.
```

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_research_iteration_flow -v
```

Expected: PASS.

- [ ] Commit.

```bash
git add tests/test_research_iteration_flow.py docs/verification/host-smoke.zh-CN.md
git commit -m "test: cover traceable stable truth iteration"
```

---

## Iteration 7: Documentation, Packaging, And Full Verification

**Goal:** Align public docs, package contents, capability discovery, and the full test suite.

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `scripts/validate_scaffold.py`
- Modify: `scripts/package_plugin.py`
- Modify: `tests/test_plugin_manifest.py`
- Modify: `tests/test_runtime_validate.py`

- [ ] Update README sections.

Add a concise section after the current runtime/checkpoint explanation:

```markdown
### Git Traceability

AletheiaOS treats `.aletheia/` as the current truth state and Git history as the truth-transition log. Stable node growth is not complete until validation passes, supporting evidence and decision records are linked, a human-confirmed stable marker is committed, and `history_audit.py --json` can reconstruct the transition.

The explicit Codex loop for stable truth changes is:

```bash
python3 .aletheia/bin/orient.py --with-runtime
python3 .aletheia/bin/preflight.py --json
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py --dry-run
python3 .aletheia/bin/checkpoint.py --node <node> --node-state stable --evidence <evidence> --decision <decision> --review human-confirmed
python3 .aletheia/bin/history_audit.py --json
```
```

In the actual README command block, use concrete sample values:

```bash
python3 .aletheia/bin/checkpoint.py --node theory_model --node-state stable --evidence .aletheia/evidence/EV-001-factor-baseline.md --decision .aletheia/decisions/DEC-001-modeling-lens-policy.md --review human-confirmed
```

- [ ] Update scaffold validation required paths.

Add these required files:

```python
".aletheia/bin/git_trailers.py",
".aletheia/bin/commit_msg_hook.py",
".aletheia/bin/history_audit.py",
```

Add banned extra ledger surface:

```python
".aletheia/ledger",
```

- [ ] Update package allowlist.

Include new scripts in `scripts/package_plugin.py` packaged files.

- [ ] Update tests for package/scaffold drift.

`tests/test_plugin_manifest.py` should assert:

```python
self.assertTrue((release_root / "assets" / "scaffold" / ".aletheia" / "bin" / "history_audit.py").exists())
self.assertIn("truth.history_audit", capability_map)
self.assertIn("AIOS-Node-State: stable", english_readme)
self.assertIn("AIOS-Node-State: stable", readme)
```

- [ ] Run full verification.

```bash
python3 scripts/validate_scaffold.py assets/scaffold
python3 -m unittest discover tests
git diff --check
```

Expected:

```text
scaffold validation passed
Ran <current test count> tests
OK
git diff --check has no output
```

- [ ] Commit.

```bash
git add README.md README.zh-CN.md scripts/validate_scaffold.py scripts/package_plugin.py tests/test_plugin_manifest.py tests/test_runtime_validate.py
git commit -m "docs: document Git traceability loop"
```

---

## Release Criteria

- `python3 scripts/validate_scaffold.py assets/scaffold` passes.
- `python3 -m unittest discover tests` passes.
- `git diff --check` has no output.
- Bootstrap finalize installs both `.aletheia/hooks/pre-commit` and `.aletheia/hooks/commit-msg`.
- A stable-node checkpoint commit contains `AIOS-Node-State: stable`, `AIOS-Evidence`, `AIOS-Decision`, `AIOS-Validation: pass`, and `AIOS-Review: human-confirmed`.
- `history_audit.py --json` returns `ok: true` for the scaffold and for the research iteration fixture.
- Commit-msg hook blocks staged tree-sensitive changes without traceability metadata.
- Public docs explain that Git history is the truth-transition log and `.aletheia/` is the current truth state.

## Follow-Up Work Outside This Batch

- Annotated Git tags for major root/trunk stabilization points.
- CI workflow that runs `validate.py`, `history_audit.py --json`, scaffold validation, and full tests.
- PR template requiring traceability trailers when `.aletheia/state/SKELETON.yaml`, `.aletheia/state/ORPHANS.yaml`, or `.aletheia/nodes/` change.
- Optional `history_audit.py --since <ref>` and `--format markdown` reporting.
- Optional signed commit or signed tag policy for root mission and root theory revisions.

## Self-Review

- Spec coverage: R1 is covered by Iteration 1 and 2. R2 is covered by Iteration 2. R3 is covered by Iteration 3. R4 and R5 are covered by Iteration 4. R6 is covered by Iteration 5 and 7. R7 is preserved by Iteration 2 checkpoint tests and Iteration 7 full verification. R8 is covered by Iterations 3 through 7.
- Red-flag scan: the plan uses concrete sample node ids and record paths for examples. Generic command variables appear only in explanatory README text where the actual plan also supplies a concrete sample command.
- Type consistency: the same trailer keys, action ids, CLI flags, and file names are used across all iterations.
