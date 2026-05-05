from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

AGENTS = [
    "truth-auditor",
    "evidence-curator",
    "architecture-reviewer",
]


class SubagentPackagingTests(unittest.TestCase):
    def test_claude_and_codex_agents_have_matching_truth_layer_roles(self) -> None:
        for name in AGENTS:
            claude_path = ROOT / "agents" / f"{name}.md"
            codex_path = ROOT / "codex-agents" / f"{name}.toml"

            self.assertTrue(claude_path.exists(), f"missing Claude agent: {name}")
            self.assertTrue(codex_path.exists(), f"missing Codex agent: {name}")

            claude_text = claude_path.read_text(encoding="utf-8")
            codex = tomllib.loads(codex_path.read_text(encoding="utf-8"))

            self.assertIn("description:", claude_text)
            self.assertIn("capabilities:", claude_text)
            self.assertEqual(codex["name"], name)
            self.assertIn(".aletheia", claude_text)
            self.assertIn(".aletheia", codex["developer_instructions"])
            self.assertIn("truth", claude_text.lower())
            self.assertIn("truth", codex["description"].lower())
            self.assertRegex(claude_text, r"read-focused|只用于读取")
            self.assertRegex(codex["developer_instructions"], r"read-focused|只用于读取")
            self.assertIn("Do not implement code changes", claude_text)
            self.assertIn("Do not implement code changes", codex["developer_instructions"])

    def test_agent_surface_stays_small_and_optional(self) -> None:
        claude_agents = sorted(path.stem for path in (ROOT / "agents").glob("*.md"))
        codex_agents = sorted(path.stem for path in (ROOT / "codex-agents").glob("*.toml"))

        self.assertEqual(claude_agents, sorted(AGENTS))
        self.assertEqual(codex_agents, sorted(AGENTS))
        self.assertFalse((ROOT / "assets" / "scaffold" / ".codex" / "agents").exists())
        self.assertFalse((ROOT / "assets" / "scaffold" / ".claude" / "agents").exists())

    def test_package_output_includes_subagent_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "scripts/package_plugin.py", "--output", tmp],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            release_root = Path(tmp) / "aletheia-os"
            for name in AGENTS:
                self.assertTrue((release_root / "agents" / f"{name}.md").exists())
                self.assertTrue((release_root / "codex-agents" / f"{name}.toml").exists())

    def test_readme_documents_optional_cross_platform_subagents(self) -> None:
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertIn("可选 subagents", readme)
        self.assertIn("truth-auditor", readme)
        self.assertIn("evidence-curator", readme)
        self.assertIn("architecture-reviewer", readme)
        self.assertIn("agents/", readme)
        self.assertIn(".codex/agents/", readme)
        self.assertIn("codex-agents/", readme)
        self.assertIn("不改变核心闭环", readme)
        section = readme.split("## 可选 subagents", 1)[1].split("\n## ", 1)[0]
        self.assertIsNone(re.search(r"PM|shipper|workflow engine|虚拟团队", section))


if __name__ == "__main__":
    unittest.main()
