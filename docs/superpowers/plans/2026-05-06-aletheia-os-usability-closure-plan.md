# AletheiaOS Usability Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AletheiaOS easier to start, close the external LLM Wiki handoff loop, and keep generated/intermediate files out of durable project truth.

**Architecture:** Keep AletheiaOS core as a repo-native truth layer, not a workflow engine. Use small documentation, validation, and skill improvements around the existing runtime instead of adding a new command framework.

**Tech Stack:** Python standard library, Markdown scaffold files, Codex/Claude plugin manifests, unittest.

---

## Scope Boundaries

- Do not reintroduce git-native research intake.
- Do not add a database, vector store, web UI, or long-running service.
- Do not make external LLM Wiki a dependency.
- Keep `.aletheia/` as the default control plane.
- Make Claude Code support mandatory and Codex support equivalent where possible.

## Iteration 1: Fix First-Run Model Gate Friction

**Problem:** The default bootstrap instructions call `model_gate.py --task-class bootstrap_finalize --record` without provider/model/tier/operator approval. With the current default registry, this records a rejected run and blocks `bootstrap_finalize.py`.

**Files:**
- Modify: `assets/scaffold/BOOTSTRAP.md`
- Modify: `assets/scaffold/.aletheia/START_HERE.md`
- Modify: `assets/scaffold/.aletheia/bin/guided_bootstrap.py`
- Modify: `README.zh-CN.md`
- Test: `tests/test_bootstrap_finalize.py`
- Test: `tests/test_model_gate.py`

- [ ] Write a failing test proving `guided_bootstrap.py` exits non-zero when model gate fails.

Run:

```bash
python3 -m unittest tests.test_bootstrap_finalize -v
```

Expected before implementation: a new test fails because `guided_bootstrap.py` currently continues after a rejected gate.

- [ ] Update `guided_bootstrap.py` so failed subcommands stop the workflow.

Required behavior:

```text
if model_gate returns non-zero, guided_bootstrap.py exits with the same code.
if source_inventory returns non-zero, guided_bootstrap.py exits with the same code.
```

- [ ] Update bootstrap docs to show the explicit operator-approved first-run command.

Use this exact command pattern in `BOOTSTRAP.md`, `START_HERE.md`, and README:

```bash
python3 .aletheia/bin/model_gate.py --task-class bootstrap_finalize --provider <provider> --model-id <model_id> --tier C3 --operator-approved --record --objective "Initialize AletheiaOS"
```

Also state that project owners should later register trusted models in `.aletheia/governance/model_registry.json`.

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_model_gate tests.test_bootstrap_finalize -v
```

- [ ] Commit.

```bash
git add assets/scaffold/BOOTSTRAP.md assets/scaffold/.aletheia/START_HERE.md assets/scaffold/.aletheia/bin/guided_bootstrap.py README.zh-CN.md tests/test_bootstrap_finalize.py tests/test_model_gate.py
git commit -m "fix(bootstrap): make first-run model gate explicit"
```

## Iteration 2: Close External LLM Wiki Handoff Promotion

**Problem:** The external LLM Wiki playbook says to promote confirmed findings, but AletheiaOS does not provide an explicit skill or review checklist for that promotion step.

**Files:**
- Create: `skills/aletheia-promote/SKILL.md`
- Create: `assets/scaffold/.aletheia/playbooks/wiki_handoff_promotion.md`
- Modify: `assets/scaffold/.aletheia/playbooks/external_llm_wiki_handoff.md`
- Modify: `README.zh-CN.md`
- Modify: `scripts/package_plugin.py`
- Test: `tests/test_plugin_manifest.py`
- Test: `tests/test_external_wiki_intake_boundary.py`

- [ ] Write a failing test that asserts the plugin package includes `skills/aletheia-promote/SKILL.md`.

Run:

```bash
python3 -m unittest tests.test_plugin_manifest -v
```

Expected before implementation: the new required path is missing.

- [ ] Add `aletheia-promote` skill.

Skill responsibilities:

```text
Use when the user has an AletheiaOS Wiki Handoff or candidate research findings and wants to turn confirmed findings into durable AletheiaOS truth records.
Read the handoff.
Separate claim, evidence, hypothesis, decision, contract, risk, node, and state updates.
Ask for human confirmation before changing root mission, priority order, root theory, or durable architecture decisions.
Create or update only durable truth records under .aletheia/.
Run validate and checkpoint when the user wants completion.
```

- [ ] Add `wiki_handoff_promotion.md`.

The playbook must define this promotion checklist:

```text
1. Confirm source refs exist for every promoted claim.
2. Promote observations/results to evidence.
3. Promote uncertain explanations to hypotheses.
4. Promote selected tradeoffs to decisions.
5. Promote boundary guarantees to contracts.
6. Promote failure modes to risks.
7. Update active state and affected nodes.
8. Run validate.
9. Checkpoint.
```

- [ ] Update README so the external LLM Wiki loop ends with `aletheia-promote`, not an implicit manual step.

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_plugin_manifest tests.test_external_wiki_intake_boundary -v
```

- [ ] Commit.

```bash
git add skills/aletheia-promote/SKILL.md assets/scaffold/.aletheia/playbooks/wiki_handoff_promotion.md assets/scaffold/.aletheia/playbooks/external_llm_wiki_handoff.md README.zh-CN.md scripts/package_plugin.py tests/test_plugin_manifest.py tests/test_external_wiki_intake_boundary.py
git commit -m "feat(skills): add wiki handoff promotion protocol"
```

## Iteration 3: Simplify The User-Facing Path

**Problem:** README and START_HERE expose too many runtime commands as the main path. The product needs one obvious loop.

**Files:**
- Modify: `README.zh-CN.md`
- Modify: `assets/scaffold/.aletheia/START_HERE.md`
- Modify: `assets/scaffold/AGENTS.md`
- Test: `tests/test_plugin_manifest.py`

- [ ] Write a failing test that checks README includes one daily loop and keeps internal runtime commands in a reference section.

Required README phrases:

```text
日常闭环
orient -> work -> update truth -> validate -> checkpoint
运行时参考
```

- [ ] Rewrite README quick-start order.

Top-level user path:

```text
1. Install plugin.
2. Initialize .aletheia/.
3. Ask the agent to orient.
4. Do work.
5. Update truth records.
6. Validate and checkpoint.
```

Keep the long runtime list only under `运行时参考`.

- [ ] Rewrite `.aletheia/START_HERE.md` so it leads with the loop, then gives command references.

Main command set:

```bash
python3 .aletheia/bin/orient.py
python3 .aletheia/bin/validate.py
python3 .aletheia/bin/checkpoint.py
```

Bootstrap and diagnostic commands should be under separate headings.

- [ ] Run tests.

```bash
python3 -m unittest tests.test_plugin_manifest -v
```

- [ ] Commit.

```bash
git add README.zh-CN.md assets/scaffold/.aletheia/START_HERE.md assets/scaffold/AGENTS.md tests/test_plugin_manifest.py
git commit -m "docs: simplify AletheiaOS operating loop"
```

## Iteration 4: Keep Generated Files Out Of Durable Truth

**Problem:** `overview.py` writes generated files to `docs/overview/`, and `source_inventory.py` writes intermediate files under `.aletheia/source_inventory/` without an explicit generated-file boundary.

**Files:**
- Modify: `assets/scaffold/.aletheia/.gitignore`
- Modify: `assets/scaffold/.aletheia/bin/overview.py`
- Modify: `assets/scaffold/.aletheia/bin/checkpoint.py`
- Modify: `README.zh-CN.md`
- Test: `tests/test_runtime_validate.py`
- Test: `tests/test_checkpoint.py`

- [ ] Write a failing test proving `overview.py` defaults to `.aletheia/overview/`.

Run:

```bash
python3 -m unittest tests.test_runtime_validate -v
```

Expected before implementation: overview output is still `docs/overview/`.

- [ ] Change `overview.py` default output to `.aletheia/overview/`.

Add optional public export flag:

```bash
python3 .aletheia/bin/overview.py --public-docs
```

When `--public-docs` is used, output to `docs/overview/`.

- [ ] Update `.aletheia/.gitignore`.

Ignore generated/intermediate directories:

```gitignore
/runtime/
/overview/
/source_inventory/
```

- [ ] Remove `docs/overview/` from checkpoint durable state patterns.

`checkpoint.py` should not treat generated overview output as durable project truth.

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_runtime_validate tests.test_checkpoint -v
```

- [ ] Commit.

```bash
git add assets/scaffold/.aletheia/.gitignore assets/scaffold/.aletheia/bin/overview.py assets/scaffold/.aletheia/bin/checkpoint.py README.zh-CN.md tests/test_runtime_validate.py tests/test_checkpoint.py
git commit -m "refactor(runtime): keep generated outputs out of project truth"
```

## Iteration 5: Add Minimal Semantic Validation

**Problem:** Validation is structurally useful, but it does not enforce the minimum quality bar for durable claims.

**Files:**
- Modify: `assets/scaffold/.aletheia/templates/EVIDENCE.md`
- Modify: `assets/scaffold/.aletheia/templates/HYPOTHESIS.md`
- Modify: `assets/scaffold/.aletheia/templates/DECISION.md`
- Modify: `assets/scaffold/.aletheia/bin/validate.py`
- Test: `tests/test_runtime_validate.py`

- [ ] Write failing tests for semantic validation.

Cases:

```text
Evidence record missing Source refs fails validation.
Hypothesis missing Invalidation Criteria fails validation.
Decision missing Evidence links fails validation when status is accepted.
```

- [ ] Add `Source refs` to `EVIDENCE.md`.

Required section:

```markdown
## Source refs

List source refs, wiki handoff refs, experiment artifacts, commits, or state that this evidence depends on.
```

- [ ] Add validation helpers to `validate.py`.

Rules:

```text
.aletheia/evidence/*.md must include Source refs, Limitations, Invalidation criteria, and Confidence impact.
.aletheia/hypotheses/*.md must include Invalidation Criteria or Invalidation criteria.
.aletheia/decisions/*.md with Status: accepted must include a non-empty Evidence links section.
```

- [ ] Run focused tests.

```bash
python3 -m unittest tests.test_runtime_validate -v
```

- [ ] Commit.

```bash
git add assets/scaffold/.aletheia/templates/EVIDENCE.md assets/scaffold/.aletheia/templates/HYPOTHESIS.md assets/scaffold/.aletheia/templates/DECISION.md assets/scaffold/.aletheia/bin/validate.py tests/test_runtime_validate.py
git commit -m "feat(validate): add semantic truth record checks"
```

## Final Verification

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_scaffold.py assets/scaffold
python3 scripts/package_plugin.py --output /private/tmp/aletheia-os-dist
git diff --check
```

Expected:

```text
All tests pass.
scaffold validation passed.
plugin package smoke check passed.
git diff --check has no output.
```

## Recommended Release Shape

- One commit per iteration.
- Do not push until all final verification commands pass.
- After completion, `aletheia-os/main` should remain a plugin repository with no root `README.md` unless the user explicitly asks for it.
