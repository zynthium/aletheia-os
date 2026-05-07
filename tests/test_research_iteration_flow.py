from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_repo(target: Path, *command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def replace_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(old, new), encoding="utf-8")


def write_bootstrap_truth(target: Path) -> None:
    replace_text(
        target / ".aletheia" / "governance" / "CHARTER.md",
        "TBD. Define the durable project mission in one paragraph.",
        "Maintain one falsifiable project truth for a quantitative trading research system where multiple market modeling lenses compete under evidence.",
    )
    replace_text(
        target / ".aletheia" / "governance" / "CHARTER.md",
        "5. Project truth must be recoverable from git and files, not chat memory.",
        "5. Project truth must be recoverable from git and files, not chat memory.\n"
        "6. No modeling lens is treated as globally true without out-of-sample evidence and explicit invalidation criteria.",
    )
    replace_text(
        target / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml",
        'title: "TBD Project Root"',
        'title: "Quant Research System"',
    )
    replace_text(
        target / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml",
        'thesis: "TBD: define the governing project thesis."',
        'thesis: "Market behavior has no single universal model; this project maintains the current best falsifiable modeling thesis across factor and game-theoretic lenses."',
    )
    replace_text(
        target / ".aletheia" / "state" / "SYSTEM_GRAPH.yaml",
        'thesis: "The explanatory or generative model behind the project."',
        'thesis: "Candidate explanations include indicator-factor persistence and game-theoretic participant behavior under liquidity constraints."',
    )
    replace_text(
        target / ".aletheia" / "state" / "SKELETON.yaml",
        'purpose: "TBD: define the project purpose."',
        'purpose: "Maintain a quant research truth layer that separates competing market modeling hypotheses, evidence, decisions, and implementation paths."',
    )
    replace_text(
        target / ".aletheia" / "state" / "SKELETON.yaml",
        "    evidence_refs: []",
        "    evidence_refs:\n"
        "      - .aletheia/evidence/EV-001-factor-baseline.md",
    )
    replace_text(
        target / ".aletheia" / "state" / "SKELETON.yaml",
        "    decision_refs: []",
        "    decision_refs:\n"
        "      - .aletheia/decisions/DEC-001-modeling-lens-policy.md",
    )
    replace_text(
        target / ".aletheia" / "state" / "ACTIVE_STATE.md",
        "- Domain: TBD\n- Mission: TBD",
        "- Domain: quantitative trading research\n"
        "- Mission: Maintain one current, falsifiable modeling thesis across indicator-factor and game-theoretic research lenses.",
    )
    replace_text(
        target / ".aletheia" / "state" / "ACTIVE_STATE.md",
        "Define the project charter, active node, and first falsifiable objective.",
        "Bootstrap competing market modeling lenses and keep only one current active modeling thesis in project truth.",
    )
    replace_text(
        target / ".aletheia" / "state" / "ACTIVE_STATE.md",
        "Bootstrap AletheiaOS | root | active | project owner + AI | TBD",
        "Bootstrap AletheiaOS | root | active | project owner + Codex | `.aletheia/evidence/EV-001-factor-baseline.md`",
    )
    (target / ".aletheia" / "state" / "DOMAIN_PROFILE.md").write_text(
        "# Domain Profile\n\n"
        "## Domain\n\n"
        "Quantitative trading research under non-stationary market regimes.\n\n"
        "## Objective Function\n\n"
        "Optimize for falsifiable modeling progress, downside-aware evidence, and explicit separation between signal discovery and market-structure explanation.\n\n"
        "## Evidence Standards\n\n"
        "Research claims require source data refs, sample split notes, limitations, invalidation criteria, and graph impact. A backtest is evidence, not final truth.\n\n"
        "## Failure Modes\n\n"
        "The project fails if a favored lens becomes implicit dogma, if weak backtests become accepted architecture, or if contradicted hypotheses remain active.\n",
        encoding="utf-8",
    )


def write_iteration_one_truth(target: Path) -> None:
    (target / ".aletheia" / "hypotheses" / "HYP-001-factor-momentum.md").write_text(
        "# Hypothesis: Indicator-factor momentum baseline\n\n"
        "Status: active\n"
        "Linked node: theory_model\n\n"
        "## Claim\n\n"
        "A rolling momentum and volatility factor can explain enough short-horizon return variation to serve as the initial modeling baseline.\n\n"
        "## Evidence Needed\n\n"
        "- Out-of-sample factor baseline evidence across at least two market regimes.\n\n"
        "## Invalidation Criteria\n\n"
        "Reject or downgrade if performance concentrates in one regime, collapses under liquidity stress, or cannot beat a naive baseline after costs.\n",
        encoding="utf-8",
    )
    (target / ".aletheia" / "hypotheses" / "HYP-002-game-liquidity.md").write_text(
        "# Hypothesis: Game-theoretic liquidity pressure model\n\n"
        "Status: candidate\n"
        "Linked node: theory_model\n\n"
        "## Claim\n\n"
        "Participant positioning, liquidity pressure, and stop-run dynamics may explain regime breaks that indicator factors miss.\n\n"
        "## Evidence Needed\n\n"
        "- Stress-regime observations where factor signals fail and participant-behavior proxies explain the failure.\n\n"
        "## Invalidation Criteria\n\n"
        "Reject if participant-behavior proxies add no explanatory power during factor drawdowns or cannot be operationalized without hindsight.",
        encoding="utf-8",
    )
    (target / ".aletheia" / "evidence" / "EV-001-factor-baseline.md").write_text(
        "# Evidence: Factor baseline initial backtest\n\n"
        "Date: 2026-05-07\n"
        "Evidence type: simulation\n"
        "Claim tested: Momentum and volatility factors can serve as the initial modeling baseline.\n"
        "Linked node: theory_model\n\n"
        "## Source refs\n\n"
        "- `research/factor_baseline.md`\n"
        "- `.aletheia/hypotheses/HYP-001-factor-momentum.md`\n\n"
        "## Method\n\n"
        "Simulated a small fixed fixture representing trend and range regimes with transaction-cost assumptions recorded in the fixture notes.\n\n"
        "## Result\n\n"
        "The factor lens produced positive aggregate signal quality in the trend fixture and weak behavior in the range fixture.\n\n"
        "## Limitations\n\n"
        "The fixture is synthetic, small, and not enough to prove market validity.\n\n"
        "## Interpretation\n\n"
        "The factor lens is acceptable as an initial baseline, not as a universal market model.\n\n"
        "## Invalidation criteria\n\n"
        "Contradicting out-of-sample evidence in stress or liquidity-break regimes should downgrade the factor-first thesis.\n\n"
        "## Graph impact\n\n"
        "- theory_model\n"
        "- evidence_validation\n\n"
        "## Confidence impact\n\n"
        "Raises factor baseline confidence to moderate while keeping game-theoretic modeling as a candidate lens.\n",
        encoding="utf-8",
    )
    (target / ".aletheia" / "decisions" / "DEC-001-modeling-lens-policy.md").write_text(
        "# Decision: Use factor baseline with explicit competing lenses\n\n"
        "Status: accepted\n"
        "Date: 2026-05-07\n\n"
        "## Context\n\n"
        "The project has no universal market model. Indicator-factor and game-theoretic lenses may each explain different regimes.\n\n"
        "## Decision\n\n"
        "Use the factor lens as the current implementation baseline while keeping the game-theoretic liquidity lens as an explicit competing hypothesis.\n\n"
        "## Alternatives considered\n\n"
        "- Pure factor modeling: rejected because it would hide participant-behavior explanations.\n"
        "- Pure game-theoretic modeling: rejected because it is not yet operationalized.\n\n"
        "## Consequences\n\n"
        "Research updates must preserve both lenses as explicit truth records until evidence closes or changes them.\n\n"
        "## Affected nodes\n\n"
        "- theory_model\n"
        "- system_design\n\n"
        "## Affected contracts\n\n"
        "None yet.\n\n"
        "## Evidence links\n\n"
        "- `.aletheia/evidence/EV-001-factor-baseline.md`\n\n"
        "## Invalidation criteria\n\n"
        "Revisit if stress-regime evidence shows factor signals fail for reasons better explained by liquidity or participant behavior.\n\n"
        "## Review trigger\n\n"
        "Review after the first stress-regime evidence record.\n",
        encoding="utf-8",
    )


def write_iteration_two_truth(target: Path) -> None:
    replace_text(
        target / ".aletheia" / "state" / "SKELETON.yaml",
        "    evidence_refs:\n"
        "      - .aletheia/evidence/EV-001-factor-baseline.md",
        "    evidence_refs:\n"
        "      - .aletheia/evidence/EV-001-factor-baseline.md\n"
        "      - .aletheia/evidence/EV-002-game-context-break.md",
    )
    replace_text(
        target / ".aletheia" / "hypotheses" / "HYP-001-factor-momentum.md",
        "Status: active",
        "Status: superseded",
    )
    replace_text(
        target / ".aletheia" / "hypotheses" / "HYP-002-game-liquidity.md",
        "Status: candidate",
        "Status: active",
    )
    (target / ".aletheia" / "evidence" / "EV-002-game-context-break.md").write_text(
        "# Evidence: Liquidity stress breaks factor baseline\n\n"
        "Date: 2026-05-07\n"
        "Evidence type: simulation\n"
        "Claim tested: Liquidity-pressure context explains a factor baseline failure during stress conditions.\n"
        "Linked node: theory_model\n\n"
        "## Source refs\n\n"
        "- `research/liquidity_stress.md`\n"
        "- `.aletheia/hypotheses/HYP-001-factor-momentum.md`\n"
        "- `.aletheia/hypotheses/HYP-002-game-liquidity.md`\n\n"
        "## Method\n\n"
        "Compared the factor baseline against a synthetic stress fixture with forced positioning and liquidity-withdrawal notes.\n\n"
        "## Result\n\n"
        "The factor baseline produced a false continuation signal while the game-theoretic liquidity lens explained the reversal setup.\n\n"
        "## Limitations\n\n"
        "The stress fixture is synthetic and only demonstrates a plausible failure mode, not a deployable strategy.\n\n"
        "## Interpretation\n\n"
        "The unique current project thesis should not be factor-first. It should treat factor signals as one lens gated by participant and liquidity context.\n\n"
        "## Invalidation criteria\n\n"
        "If future stress evidence shows liquidity context adds no predictive or explanatory value beyond factor features, downgrade this interpretation.\n\n"
        "## Graph impact\n\n"
        "- theory_model\n"
        "- risk_safety\n"
        "- evidence_validation\n\n"
        "## Confidence impact\n\n"
        "Downgrades factor-first confidence and promotes game-theoretic liquidity context into the active modeling thesis.\n",
        encoding="utf-8",
    )
    (target / ".aletheia" / "risks" / "RISK-001-factor-dogma.md").write_text(
        "# Risk: Factor lens becomes implicit dogma\n\n"
        "Status: open\n"
        "Type: B\n"
        "Affected node: theory_model\n\n"
        "## Failure mode\n\n"
        "The project treats indicator factors as the market model instead of one evidence-tested lens.\n\n"
        "## Signal\n\n"
        "Decisions accept factor outputs without checking participant behavior, liquidity, and stress-regime evidence.\n\n"
        "## Mitigation\n\n"
        "Require stress-regime evidence and explicit lens status before promoting a modeling decision.\n\n"
        "## Escalation\n\n"
        "Escalate if active state or decisions present factor-first modeling after contradicted evidence.\n",
        encoding="utf-8",
    )
    (target / ".aletheia" / "decisions" / "DEC-001-modeling-lens-policy.md").write_text(
        "# Decision: Use liquidity-gated multi-lens modeling thesis\n\n"
        "Status: accepted\n"
        "Date: 2026-05-07\n\n"
        "## Context\n\n"
        "Factor evidence supports a useful baseline, but stress-regime evidence shows a factor-first thesis can fail when participant behavior and liquidity pressure dominate.\n\n"
        "## Decision\n\n"
        "Maintain one current active modeling thesis: factor signals are candidate inputs gated by game-theoretic participant and liquidity context.\n\n"
        "## Alternatives considered\n\n"
        "- Keep factor-first modeling: rejected because EV-002 shows a plausible stress-regime failure.\n"
        "- Switch to pure game-theoretic modeling: rejected because it is explanatory but not yet a complete executable model.\n\n"
        "## Consequences\n\n"
        "Future implementation should expose both factor features and liquidity-context checks, while project truth marks factor-first modeling as superseded.\n\n"
        "## Affected nodes\n\n"
        "- theory_model\n"
        "- system_design\n"
        "- risk_safety\n\n"
        "## Affected contracts\n\n"
        "None yet.\n\n"
        "## Evidence links\n\n"
        "- `.aletheia/evidence/EV-001-factor-baseline.md`\n"
        "- `.aletheia/evidence/EV-002-game-context-break.md`\n\n"
        "## Invalidation criteria\n\n"
        "Revisit if future stress fixtures show liquidity context adds no explanatory value or cannot be operationalized without hindsight.\n\n"
        "## Review trigger\n\n"
        "Review before implementing the first executable strategy model.\n",
        encoding="utf-8",
    )
    (target / ".aletheia" / "state" / "ACTIVE_STATE.md").write_text(
        "# Active State\n\n"
        "## Current project identity\n\n"
        "- Domain: quantitative trading research\n"
        "- Mission: Maintain one current, falsifiable modeling thesis across indicator-factor and game-theoretic research lenses.\n"
        "- Current phase: research iteration\n\n"
        "## Active frontier\n\n"
        "```text\n"
        "Current thesis: factor signals are candidate inputs gated by game-theoretic participant and liquidity context.\n"
        "Next research frontier: operationalize liquidity-context checks without hindsight.\n"
        "```\n\n"
        "## Active nodes\n\n"
        "- `theory_model`\n"
        "- `evidence_validation`\n\n"
        "## Current blockers\n\n"
        "| Blocker | Type A/B/C/D | Affected node | Impact | Next action |\n"
        "|---|---:|---|---|---|\n"
        "| Liquidity context not operationalized | B | theory_model | Blocks executable strategy design | Define observable proxies and test fixtures |\n\n"
        "## Work in progress\n\n"
        "| Work item | Node | Status | Owner | Evidence/decision link |\n"
        "|---|---|---|---|---|\n"
        "| Compare modeling lenses | theory_model | active | project owner + Codex | `.aletheia/evidence/EV-002-game-context-break.md` |\n\n"
        "## Next actions\n\n"
        "1. Define observable liquidity-pressure proxies.\n"
        "2. Add a contract for model inputs before implementation.\n"
        "3. Validate the multi-lens thesis against another stress fixture.\n",
        encoding="utf-8",
    )


class ResearchIterationFlowTests(unittest.TestCase):
    def test_split_node_refactor_separates_overloaded_branch_without_new_record_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "split-node-loop"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            (target / ".aletheia" / "evidence" / "EV-302-overloaded-modeling.md").write_text(
                "# Evidence: Market modeling node carries two mechanisms\n\n"
                "Date: 2026-05-08\n"
                "Evidence type: observation\n"
                "Claim lifecycle impact: evidence-backed\n"
                "Claim tested: A single market_modeling branch is carrying both factor signals and liquidity context.\n"
                "Linked node: market_modeling\n\n"
                "## Source refs\n\n"
                "- `.aletheia/state/SKELETON.yaml`\n\n"
                "## Method\n\n"
                "Reviewed modeling records and found two independent explanatory mechanisms.\n\n"
                "## Result\n\n"
                "Factor modeling and liquidity context need separate leaves under the market_modeling branch.\n\n"
                "## Limitations\n\n"
                "This refactors project truth only; it does not choose either modeling lens as globally true.\n\n"
                "## Interpretation\n\n"
                "Split market_modeling into factor_modeling and liquidity_context children.\n\n"
                "## Invalidation criteria\n\n"
                "Revisit if future evidence shows one child fully subsumes the other.\n\n"
                "## Graph impact\n\n"
                "- theory_model\n"
                "- market_modeling\n"
                "- factor_modeling\n"
                "- liquidity_context\n\n"
                "## Confidence impact\n\n"
                "Raises confidence that the overloaded branch has been separated into clearer mechanisms.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "decisions" / "DEC-302-split-market-modeling.md").write_text(
                "# Decision: Split market modeling mechanisms\n\n"
                "Status: accepted\n"
                "Decision type: tree_refactor\n"
                "Date: 2026-05-08\n\n"
                "## Context\n\n"
                "The market_modeling branch mixes factor signal work with liquidity context reasoning.\n\n"
                "## Decision\n\n"
                "Keep `market_modeling` as a branch and split its mechanisms into `factor_modeling` and `liquidity_context` leaves.\n\n"
                "## Alternatives considered\n\n"
                "- Keep one node: rejected because agents would keep mixing evidence standards.\n"
                "- Add a separate theory registry: rejected because hypotheses, evidence, decisions, and skeleton nodes are enough.\n\n"
                "## Consequences\n\n"
                "Future evidence can attach to the specific modeling mechanism it supports or weakens.\n\n"
                "## Affected nodes\n\n"
                "- theory_model\n"
                "- market_modeling\n"
                "- factor_modeling\n"
                "- liquidity_context\n\n"
                "## Affected contracts\n\n"
                "None.\n\n"
                "## Evidence links\n\n"
                "- `.aletheia/evidence/EV-302-overloaded-modeling.md`\n\n"
                "## Hypothesis links\n\n"
                "None.\n\n"
                "## Invalidation criteria\n\n"
                "Revisit if one child becomes obsolete or the split creates duplicated evidence.\n\n"
                "## Review trigger\n\n"
                "Review when either child is archived, merged, or operationalized.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "state" / "SKELETON.yaml").write_text(
                (target / ".aletheia" / "state" / "SKELETON.yaml").read_text(encoding="utf-8")
                + "\n"
                "  market_modeling:\n"
                "    layer: branch\n"
                "    parent: theory_model\n"
                "    children:\n"
                "      - factor_modeling\n"
                "      - liquidity_context\n"
                "    purpose: \"Separate market modeling mechanisms under the theory model.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs:\n"
                "      - .aletheia/decisions/DEC-302-split-market-modeling.md\n"
                "    evidence_refs:\n"
                "      - .aletheia/evidence/EV-302-overloaded-modeling.md\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.5\n"
                "    last_reviewed: 2026-05-08\n"
                "  factor_modeling:\n"
                "    layer: leaf\n"
                "    parent: market_modeling\n"
                "    children: []\n"
                "    purpose: \"Model indicator and factor signals.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n"
                "  liquidity_context:\n"
                "    layer: leaf\n"
                "    parent: market_modeling\n"
                "    children: []\n"
                "    purpose: \"Model participant behavior and liquidity pressure context.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(
                active_state.read_text(encoding="utf-8").replace("- `root`", "- `market_modeling`"),
                encoding="utf-8",
            )

            validate = run_repo(target, sys.executable, ".aletheia/bin/validate.py")
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

            orient = run_repo(target, sys.executable, ".aletheia/bin/orient.py")
            self.assertEqual(orient.returncode, 0, orient.stdout + orient.stderr)
            self.assertIn("market_modeling", orient.stdout)
            self.assertIn("factor_modeling", orient.stdout)
            self.assertIn("liquidity_context", orient.stdout)

            status = run_repo(target, sys.executable, ".aletheia/bin/status.py", "--json")
            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            status_payload = json.loads(status.stdout)
            self.assertEqual(status_payload["active_state"]["active_nodes"], ["market_modeling"])
            self.assertFalse(status_payload["tree_health"]["review_needed"])

    def test_insert_parent_refactor_groups_existing_leaves_without_new_record_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "insert-parent-loop"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            (target / ".aletheia" / "evidence" / "EV-301-missing-parent.md").write_text(
                "# Evidence: Reproducibility leaves need a parent branch\n\n"
                "Date: 2026-05-08\n"
                "Evidence type: observation\n"
                "Claim lifecycle impact: evidence-backed\n"
                "Claim tested: Deterministic fixtures and replay checks share one execution concern.\n"
                "Linked node: reproducibility_checks\n\n"
                "## Source refs\n\n"
                "- `.aletheia/state/SKELETON.yaml`\n\n"
                "## Method\n\n"
                "Reviewed sibling leaf boundaries after repeated execution work touched both leaves.\n\n"
                "## Result\n\n"
                "The leaves share a missing intermediate parent: reproducibility_checks.\n\n"
                "## Limitations\n\n"
                "This only refactors the truth tree; it does not implement any checks.\n\n"
                "## Interpretation\n\n"
                "Insert reproducibility_checks between engineering_execution and the two existing leaves.\n\n"
                "## Invalidation criteria\n\n"
                "Revisit if the leaves diverge into unrelated execution concerns.\n\n"
                "## Graph impact\n\n"
                "- engineering_execution\n"
                "- reproducibility_checks\n"
                "- deterministic_fixtures\n"
                "- replay_validation\n\n"
                "## Confidence impact\n\n"
                "Raises confidence that reproducibility_checks is the correct intermediate branch.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "decisions" / "DEC-301-insert-reproducibility-parent.md").write_text(
                "# Decision: Insert reproducibility parent branch\n\n"
                "Status: accepted\n"
                "Decision type: tree_refactor\n"
                "Date: 2026-05-08\n\n"
                "## Context\n\n"
                "Two execution leaves share an unmodeled reproducibility concern.\n\n"
                "## Decision\n\n"
                "Insert `reproducibility_checks` as an intermediate skeleton parent under `engineering_execution`.\n\n"
                "## Alternatives considered\n\n"
                "- Keep leaves directly under engineering_execution: rejected because the shared boundary remains implicit.\n"
                "- Create a new record type: rejected because skeleton, evidence, and decisions already represent the refactor.\n\n"
                "## Consequences\n\n"
                "Future agents orient on reproducibility_checks before changing fixture or replay validation truth.\n\n"
                "## Affected nodes\n\n"
                "- engineering_execution\n"
                "- reproducibility_checks\n"
                "- deterministic_fixtures\n"
                "- replay_validation\n\n"
                "## Affected contracts\n\n"
                "None.\n\n"
                "## Evidence links\n\n"
                "- `.aletheia/evidence/EV-301-missing-parent.md`\n\n"
                "## Hypothesis links\n\n"
                "None.\n\n"
                "## Invalidation criteria\n\n"
                "Revisit if deterministic fixtures and replay validation no longer share a reproducibility boundary.\n\n"
                "## Review trigger\n\n"
                "Review when another reproducibility leaf appears or either child is archived.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "state" / "SKELETON.yaml").write_text(
                (target / ".aletheia" / "state" / "SKELETON.yaml").read_text(encoding="utf-8")
                + "\n"
                "  reproducibility_checks:\n"
                "    layer: branch\n"
                "    parent: engineering_execution\n"
                "    children:\n"
                "      - deterministic_fixtures\n"
                "      - replay_validation\n"
                "    purpose: \"Group durable reproducibility concerns under execution.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs:\n"
                "      - .aletheia/decisions/DEC-301-insert-reproducibility-parent.md\n"
                "    evidence_refs:\n"
                "      - .aletheia/evidence/EV-301-missing-parent.md\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.5\n"
                "    last_reviewed: 2026-05-08\n"
                "  deterministic_fixtures:\n"
                "    layer: leaf\n"
                "    parent: reproducibility_checks\n"
                "    children: []\n"
                "    purpose: \"Keep fixture generation deterministic.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n"
                "  replay_validation:\n"
                "    layer: leaf\n"
                "    parent: reproducibility_checks\n"
                "    children: []\n"
                "    purpose: \"Keep replay validation deterministic and inspectable.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs: []\n"
                "    evidence_refs: []\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(
                active_state.read_text(encoding="utf-8").replace("- `root`", "- `reproducibility_checks`"),
                encoding="utf-8",
            )

            validate = run_repo(target, sys.executable, ".aletheia/bin/validate.py")
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

            orient = run_repo(target, sys.executable, ".aletheia/bin/orient.py")
            self.assertEqual(orient.returncode, 0, orient.stdout + orient.stderr)
            self.assertIn("reproducibility_checks", orient.stdout)
            self.assertIn("deterministic_fixtures", orient.stdout)
            self.assertIn("replay_validation", orient.stdout)

            status = run_repo(target, sys.executable, ".aletheia/bin/status.py", "--json")
            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            status_payload = json.loads(status.stdout)
            self.assertEqual(status_payload["active_state"]["active_nodes"], ["reproducibility_checks"])
            self.assertFalse(status_payload["tree_health"]["review_needed"])

    def test_orphan_candidate_can_be_attached_to_the_truth_tree_without_new_record_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "tree-loop"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)

            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans:\n"
                "  - id: OR-201\n"
                "    title: Reproducibility checks deserve their own execution branch\n"
                "    disposition: incubating\n"
                "    candidate_parents:\n"
                "      - engineering_execution\n"
                "    next_review: 2026-05-30\n"
                "    evidence_refs:\n"
                "      - .aletheia/evidence/EV-201-reproducibility-gap.md\n",
                encoding="utf-8",
            )

            incubating_status = run_repo(target, sys.executable, ".aletheia/bin/status.py", "--json")
            self.assertEqual(incubating_status.returncode, 0, incubating_status.stdout + incubating_status.stderr)
            incubating_payload = json.loads(incubating_status.stdout)
            self.assertEqual(incubating_payload["tree_health"]["orphan_count"], 1)
            self.assertTrue(incubating_payload["tree_health"]["review_needed"])

            (target / ".aletheia" / "evidence" / "EV-201-reproducibility-gap.md").write_text(
                "# Evidence: Reproducibility checks are a distinct execution concern\n\n"
                "Date: 2026-05-08\n"
                "Evidence type: observation\n"
                "Claim lifecycle impact: evidence-backed\n"
                "Claim tested: Reproducibility checks need their own branch under engineering execution.\n"
                "Linked node: reproducibility_checks\n\n"
                "## Source refs\n\n"
                "- `.aletheia/state/ORPHANS.yaml#OR-201`\n\n"
                "## Method\n\n"
                "Reviewed the incubating orphan against engineering execution boundaries.\n\n"
                "## Result\n\n"
                "The concern is not a one-off task; it owns repeatable checks, fixture regeneration, and test reproducibility.\n\n"
                "## Limitations\n\n"
                "This establishes a tree position, not a full implementation plan.\n\n"
                "## Interpretation\n\n"
                "Attach the candidate as a skeleton leaf under engineering_execution and remove it from the incubator.\n\n"
                "## Invalidation criteria\n\n"
                "Archive the branch if reproducibility checks collapse into ordinary test maintenance.\n\n"
                "## Graph impact\n\n"
                "- engineering_execution\n"
                "- reproducibility_checks\n\n"
                "## Confidence impact\n\n"
                "Raises confidence that reproducibility checks are a durable execution branch.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "decisions" / "DEC-201-attach-reproducibility-checks.md").write_text(
                "# Decision: Attach reproducibility checks under engineering execution\n\n"
                "Status: accepted\n"
                "Decision type: tree_refactor\n"
                "Date: 2026-05-08\n\n"
                "## Context\n\n"
                "OR-201 identified a durable concern whose parent is engineering_execution.\n\n"
                "## Decision\n\n"
                "Attach `reproducibility_checks` as a skeleton leaf under `engineering_execution` and clear OR-201 from the incubator.\n\n"
                "## Alternatives considered\n\n"
                "- Keep incubating: rejected because the parent and support evidence are clear.\n"
                "- Add a new record family: rejected because skeleton, evidence, and decisions already represent the change.\n\n"
                "## Consequences\n\n"
                "Future work can orient directly on the reproducibility_checks branch without creating a parallel tree subsystem.\n\n"
                "## Affected nodes\n\n"
                "- engineering_execution\n"
                "- reproducibility_checks\n\n"
                "## Affected contracts\n\n"
                "None.\n\n"
                "## Evidence links\n\n"
                "- `.aletheia/evidence/EV-201-reproducibility-gap.md`\n\n"
                "## Hypothesis links\n\n"
                "None.\n\n"
                "## Invalidation criteria\n\n"
                "Revisit if reproducibility checks no longer need a dedicated execution boundary.\n\n"
                "## Review trigger\n\n"
                "Review when engineering_execution gains more than twelve children or reproducibility work becomes ordinary test maintenance.\n",
                encoding="utf-8",
            )
            skeleton = target / ".aletheia" / "state" / "SKELETON.yaml"
            skeleton.write_text(
                skeleton.read_text(encoding="utf-8")
                + "\n"
                "  reproducibility_checks:\n"
                "    layer: leaf\n"
                "    parent: engineering_execution\n"
                "    children: []\n"
                "    purpose: \"Keep project checks, fixtures, and validations reproducible.\"\n"
                "    invariants: []\n"
                "    inherited_constraints: []\n"
                "    adds: []\n"
                "    does_not_explain: []\n"
                "    interfaces: []\n"
                "    owned_paths: []\n"
                "    test_paths: []\n"
                "    contract_refs: []\n"
                "    decision_refs:\n"
                "      - .aletheia/decisions/DEC-201-attach-reproducibility-checks.md\n"
                "    evidence_refs:\n"
                "      - .aletheia/evidence/EV-201-reproducibility-gap.md\n"
                "    expand_when: []\n"
                "    stop_when: []\n"
                "    review_triggers: []\n"
                "    confidence: 0.4\n"
                "    last_reviewed: 2026-05-08\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(
                active_state.read_text(encoding="utf-8").replace(
                    "- `root`",
                    "- `reproducibility_checks`",
                ),
                encoding="utf-8",
            )
            (target / ".aletheia" / "state" / "ORPHANS.yaml").write_text(
                "version: 0.1\n"
                "schema: AIOS_ORPHANS\n"
                "updated: 2026-05-08\n\n"
                "review_policy:\n"
                "  default_review_days: 30\n"
                "  max_orphan_age_days: 90\n\n"
                "orphans: []\n",
                encoding="utf-8",
            )

            validate = run_repo(target, sys.executable, ".aletheia/bin/validate.py")
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

            orient = run_repo(target, sys.executable, ".aletheia/bin/orient.py")
            self.assertEqual(orient.returncode, 0, orient.stdout + orient.stderr)
            self.assertIn("reproducibility_checks", orient.stdout)
            self.assertIn("No incubating orphan entries.", orient.stdout)

            overview = run_repo(target, sys.executable, ".aletheia/bin/overview.py")
            self.assertEqual(overview.returncode, 0, overview.stdout + overview.stderr)
            overview_status = json.loads((target / ".aletheia" / "overview" / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(overview_status["tree_health"]["orphan_count"], 0)
            self.assertEqual(overview_status["tree_health"]["stale_orphan_count"], 0)
            self.assertFalse(overview_status["tree_health"]["review_needed"])

    def test_quant_research_iteration_preserves_one_current_truth_across_competing_lenses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "quant-research"
            target.mkdir()
            run_repo(target, "git", "init")
            run_repo(target, "git", "config", "user.email", "test@example.com")
            run_repo(target, "git", "config", "user.name", "Test User")
            (target / "README.md").write_text(
                "# Quant Research\n\n"
                "Research project comparing indicator-factor and game-theoretic market modeling lenses.\n",
                encoding="utf-8",
            )
            research = target / "research"
            research.mkdir()
            (research / "factor_baseline.md").write_text(
                "# Factor Baseline\n\nMomentum and volatility features are the first baseline.\n",
                encoding="utf-8",
            )
            (research / "liquidity_stress.md").write_text(
                "# Liquidity Stress\n\nParticipant positioning can break continuation signals.\n",
                encoding="utf-8",
            )
            run_repo(target, "git", "add", "README.md", "research")
            initial = run_repo(target, "git", "commit", "-m", "initial quant research notes")
            self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)

            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stderr)
            gate = run_repo(
                target,
                sys.executable,
                ".aletheia/bin/model_gate.py",
                "--task-class",
                "bootstrap_finalize",
                "--provider",
                "openai",
                "--model-id",
                "codex-e2e",
                "--tier",
                "C3",
                "--operator-approved",
                "--record",
                "--objective",
                "Initialize quant research AletheiaOS",
            )
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
            inventory = run_repo(target, sys.executable, ".aletheia/bin/source_inventory.py")
            self.assertEqual(inventory.returncode, 0, inventory.stdout + inventory.stderr)
            write_bootstrap_truth(target)
            write_iteration_one_truth(target)

            finalize = run_repo(target, sys.executable, ".aletheia/bin/bootstrap_finalize.py")
            self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)

            iteration_gate = run_repo(
                target,
                sys.executable,
                ".aletheia/bin/model_gate.py",
                "--task-class",
                "research_design",
                "--provider",
                "openai",
                "--model-id",
                "codex-e2e",
                "--tier",
                "C3",
                "--operator-approved",
                "--record",
                "--objective",
                "Revise quant modeling thesis after stress evidence",
            )
            self.assertEqual(iteration_gate.returncode, 0, iteration_gate.stdout + iteration_gate.stderr)
            write_iteration_two_truth(target)
            validate = run_repo(target, sys.executable, ".aletheia/bin/validate.py")
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            orient = run_repo(target, sys.executable, ".aletheia/bin/orient.py")
            self.assertEqual(orient.returncode, 0, orient.stdout + orient.stderr)
            self.assertIn("factor signals are candidate inputs gated by game-theoretic participant", orient.stdout)

            checkpoint = run_repo(
                target,
                sys.executable,
                ".aletheia/bin/checkpoint.py",
                "--auto",
                "--message",
                "research: revise quant modeling thesis",
            )
            self.assertEqual(checkpoint.returncode, 0, checkpoint.stdout + checkpoint.stderr)

            active_state = (target / ".aletheia" / "state" / "ACTIVE_STATE.md").read_text(encoding="utf-8")
            factor_hypothesis = (target / ".aletheia" / "hypotheses" / "HYP-001-factor-momentum.md").read_text(
                encoding="utf-8"
            )
            game_hypothesis = (target / ".aletheia" / "hypotheses" / "HYP-002-game-liquidity.md").read_text(
                encoding="utf-8"
            )
            decision = (target / ".aletheia" / "decisions" / "DEC-001-modeling-lens-policy.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Current thesis: factor signals are candidate inputs gated by game-theoretic", active_state)
            self.assertIn("Status: superseded", factor_hypothesis)
            self.assertIn("Status: active", game_hypothesis)
            self.assertIn(".aletheia/evidence/EV-001-factor-baseline.md", decision)
            self.assertIn(".aletheia/evidence/EV-002-game-context-break.md", decision)
            risk = (target / ".aletheia" / "risks" / "RISK-001-factor-dogma.md").read_text(encoding="utf-8")
            self.assertIn("Factor lens becomes implicit dogma", risk)

            committed = run_repo(target, "git", "log", "--format=%s%n%b", "-2")
            self.assertIn("research: revise quant modeling thesis", committed.stdout)
            self.assertIn("bootstrap: initialize AletheiaOS", committed.stdout)
            self.assertIn("AIOS-Agent-Model: codex-e2e", committed.stdout)


if __name__ == "__main__":
    unittest.main()
