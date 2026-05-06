from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
        self.assertIn("外部 LLM Wiki 负责资料编译", protocol.read_text(encoding="utf-8"))
        self.assertNotIn("truth_intake.py", readme)
        self.assertNotIn("digest-plan", readme)


if __name__ == "__main__":
    unittest.main()
