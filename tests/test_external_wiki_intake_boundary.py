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


class ExternalWikiIntakeBoundaryTests(unittest.TestCase):
    def test_core_does_not_ship_git_native_research_intake_runtime(self) -> None:
        removed_paths = [
            "assets/scaffold/.aletheia/bin/truth_intake.py",
            "assets/scaffold/.aletheia/templates/BOOTSTRAP_SYNTHESIS_PACKET.md",
            "assets/scaffold/.aletheia/templates/CONVERSATION_DIGEST.md",
            "assets/scaffold/.aletheia/templates/FUSION_PACKET.md",
            "assets/scaffold/.aletheia/templates/PROMOTION_LOG.md",
            "assets/scaffold/.aletheia/truth_intake/PROMOTION_LOG.md",
            "assets/scaffold/.aletheia/truth_intake/registry.json",
            "assets/scaffold/.aletheia/truth_intake/inbox/.gitkeep",
            "assets/scaffold/.aletheia/truth_intake/runs/.gitkeep",
        ]

        offenders = [rel for rel in removed_paths if (ROOT / rel).exists()]

        self.assertEqual(offenders, [])

    def test_docs_present_external_llm_wiki_handoff_as_intake_boundary(self) -> None:
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        protocol = ROOT / "assets" / "scaffold" / ".aletheia" / "playbooks" / "external_llm_wiki_handoff.md"

        self.assertTrue(protocol.exists())
        self.assertIn("外部 LLM Wiki", readme)
        self.assertIn("AletheiaOS Wiki Handoff", readme)
        self.assertIn("aletheia-promote", readme)
        self.assertIn("外部 LLM Wiki 负责资料编译", protocol.read_text(encoding="utf-8"))
        self.assertNotIn("truth_intake.py", readme)
        self.assertNotIn("digest-plan", readme)

    def test_reviewed_wiki_handoff_can_be_promoted_to_valid_durable_truth_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init = run_script("scripts/init_aletheia.py", str(target))
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            subprocess.run(["git", "init"], cwd=target, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=False)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=target, check=False)
            subprocess.run(["git", "add", "-A"], cwd=target, check=False)
            baseline = subprocess.run(
                ["git", "commit", "-m", "test: initial scaffold"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)

            handoff = target / "wiki_handoff.md"
            handoff.write_text(
                "# AletheiaOS Wiki Handoff\n\n"
                "Objective: Promote reviewed market-modeling findings.\n"
                "Wiki location: lcwiki://quant-modeling\n"
                "Source corpus: chatgpt-export-2026-05-01.json\n"
                "Source index: lcwiki://quant-modeling/source-index\n\n"
                "## Key Claims\n"
                "- Claim: Indicator factors are useful candidate inputs but fail as a complete market model.\n"
                "  Source refs: chatgpt-export-2026-05-01.json#turn-18\n"
                "  Confidence: medium\n"
                "  Limitations: one research thread\n"
                "  Promote to: evidence | hypothesis\n"
                "- Claim: Liquidity games and participant constraints should gate factor interpretation.\n"
                "  Source refs: chatgpt-export-2026-05-01.json#turn-27\n"
                "  Confidence: medium\n"
                "  Limitations: needs simulation\n"
                "  Promote to: decision | risk\n"
                "- Claim: Unsupported claim should stay in wiki.\n"
                "  Source refs:\n"
                "  Confidence: low\n"
                "  Limitations: no source\n"
                "  Promote to: none\n",
                encoding="utf-8",
            )
            self.assertIn("Unsupported claim should stay in wiki", handoff.read_text(encoding="utf-8"))

            (target / ".aletheia" / "evidence" / "EV-wiki-factor-limit.md").write_text(
                "# Evidence: factor lens is incomplete\n\n"
                "Linked node: root\n\n"
                "## Source refs\n\n- `wiki_handoff.md` chatgpt-export-2026-05-01.json#turn-18\n\n"
                "## Method\n\nReviewed external LLM Wiki handoff and checked source references.\n\n"
                "## Result\n\nIndicator factors are useful candidate inputs but fail as a complete market model.\n\n"
                "## Limitations\n\nOne compiled research thread; simulation still needed.\n\n"
                "## Invalidation criteria\n\nA cross-regime backtest shows factor-only modeling keeps explanatory power under liquidity shocks.\n\n"
                "## Confidence impact\n\nRaises confidence that factors should be gated by market-structure context.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "hypotheses" / "HYP-market-structure-gate.md").write_text(
                "# Hypothesis: market structure gates factor interpretation\n\n"
                "Status: active\n\n"
                "## Claim\n\nLiquidity games and participant constraints gate factor interpretation.\n\n"
                "## Evidence Needed\n\nSimulation across participant constraint regimes.\n\n"
                "## Invalidation criteria\n\nFactor-only model remains stable when liquidity and participant constraints shift.\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "decisions" / "DEC-market-modeling-thesis.md").write_text(
                "# Decision: use market-structure-gated factors\n\n"
                "Status: accepted\n\n"
                "## Context\n\nExternal Wiki handoff compared factor and game-theoretic modeling lenses.\n\n"
                "## Decision\n\nTreat factor signals as candidate inputs gated by liquidity games and participant constraints.\n\n"
                "## Evidence links\n\n- `.aletheia/evidence/EV-wiki-factor-limit.md`\n",
                encoding="utf-8",
            )
            (target / ".aletheia" / "risks" / "RISK-factor-dogma.md").write_text(
                "# Risk: factor lens becomes implicit dogma\n\n"
                "Status: active\n\n"
                "Source refs: `wiki_handoff.md` chatgpt-export-2026-05-01.json#turn-27\n\n"
                "Mitigation: require market-structure invalidation checks before accepting factor-only conclusions.\n",
                encoding="utf-8",
            )
            active_state = target / ".aletheia" / "state" / "ACTIVE_STATE.md"
            active_state.write_text(
                active_state.read_text(encoding="utf-8")
                + "\nCurrent promoted thesis: factor signals are candidate inputs gated by liquidity games and participant constraints.\n",
                encoding="utf-8",
            )
            runtime = target / ".aletheia" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current_agent_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "RUN-wiki-promote",
                        "provider": "test",
                        "model_id": "test-model",
                        "capability_tier": "C3",
                        "task_class": "research_design",
                        "gate_status": "allowed",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            validate = subprocess.run(
                [sys.executable, ".aletheia/bin/validate.py"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            checkpoint = subprocess.run(
                [sys.executable, ".aletheia/bin/checkpoint.py", "--auto", "--dry-run"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            output = checkpoint.stdout + checkpoint.stderr
            self.assertEqual(checkpoint.returncode, 0, output)
            self.assertIn(".aletheia/evidence/EV-wiki-factor-limit.md", output)
            self.assertIn(".aletheia/hypotheses/HYP-market-structure-gate.md", output)
            self.assertIn(".aletheia/decisions/DEC-market-modeling-thesis.md", output)
            promoted_text = "\n".join(
                path.read_text(encoding="utf-8")
                for directory in ["evidence", "hypotheses", "decisions", "risks"]
                for path in (target / ".aletheia" / directory).glob("*.md")
            )
            self.assertNotIn("Unsupported claim should stay in wiki", promoted_text)


if __name__ == "__main__":
    unittest.main()
