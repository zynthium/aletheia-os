from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PluginManifestTests(unittest.TestCase):
    def test_codex_manifest_uses_complete_plugin_schema(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "aletheia-os")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["author"]["name"], "zynthium")
        self.assertEqual(manifest["repository"], "https://github.com/zynthium/aletheia-os")
        self.assertEqual(manifest["homepage"], "https://github.com/zynthium/aletheia-os")
        self.assertEqual(manifest["interface"]["developerName"], "zynthium")
        self.assertEqual(manifest["interface"]["websiteURL"], "https://github.com/zynthium/aletheia-os")
        self.assertIn("truth layer", manifest["description"])
        self.assertIn("project truth", manifest["interface"]["shortDescription"])
        self.assertIn("architecture", manifest["interface"]["longDescription"])
        self.assertIn("evidence", manifest["interface"]["longDescription"])
        self.assertIn("truth-layer", manifest["keywords"])
        self.assertIsInstance(manifest["interface"]["defaultPrompt"], list)
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        for prompt in manifest["interface"]["defaultPrompt"]:
            self.assertLessEqual(len(prompt), 128)
        self.assertIn("longDescription", manifest["interface"])
        self.assertIn("developerName", manifest["interface"])
        self.assertIn("category", manifest["interface"])
        self.assertIn("capabilities", manifest["interface"])

    def test_claude_manifest_uses_plugin_root_components(self) -> None:
        codex_manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude_manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertEqual(claude_manifest["name"], codex_manifest["name"])
        self.assertEqual(claude_manifest["description"], codex_manifest["description"])
        self.assertEqual(claude_manifest["version"], codex_manifest["version"])
        self.assertEqual(claude_manifest["author"], codex_manifest["author"])
        self.assertEqual(claude_manifest["skills"], "./skills/")
        self.assertTrue((ROOT / "skills" / "aletheia-bootstrap" / "SKILL.md").exists())
        self.assertFalse((ROOT / ".claude-plugin" / "skills").exists())

    def test_package_output_uses_manifest_name(self) -> None:
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
            self.assertEqual([path.name for path in Path(tmp).iterdir()], ["aletheia-os"])
            self.assertTrue((release_root / ".codex-plugin" / "plugin.json").exists())
            self.assertTrue((release_root / ".claude-plugin" / "plugin.json").exists())

    def test_readme_documents_simple_installation(self) -> None:
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertFalse((ROOT / ("README" + ".md")).exists())
        self.assertIn("仓库原生事实层", readme)
        self.assertIn("One repo. One project truth. Many agents.", readme)
        self.assertIn("不是另一个 coding workflow", readme)
        self.assertIn("Global View Checksum", readme)
        self.assertIn("OpenSpec", readme)
        self.assertIn("Superpowers", readme)
        self.assertIn(".claude-plugin/plugin.json", readme)
        self.assertIn("python3 scripts/install_aletheia.py --host both --scope user", readme)
        self.assertIn("zynthium/aletheia-os", readme)
        self.assertIn("claude plugin marketplace add zynthium/aletheia-os --scope user", readme)
        self.assertIn("codex plugin marketplace add zynthium/aletheia-os", readme)
        self.assertIn("/plugin", readme)
        self.assertIn("/plugins", readme)

    def test_plugin_content_avoids_migration_and_compatibility_language(self) -> None:
        banned_patterns = [
            r"\bmigration\b",
            r"\bmigrate\b",
            r"\bimport\b",
            r"\blegacy\b",
            r"\bcompat\b",
            r"\bCompatibility\b",
            "迁移",
            "导入",
            "兼容",
        ]
        checked_roots = [
            ROOT / "README.zh-CN.md",
            ROOT / "skills",
            ROOT / "agents",
            ROOT / "codex-agents",
            ROOT / "assets" / "scaffold",
            ROOT / ".codex-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / ".agents" / "plugins" / "marketplace.json",
        ]
        offenders: list[str] = []
        for checked in checked_roots:
            paths = [checked] if checked.is_file() else [path for path in checked.rglob("*") if path.is_file()]
            for path in paths:
                if ".gitkeep" in path.name:
                    continue
                if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".txt"}:
                    continue
                text = path.read_text(encoding="utf-8")
                for pattern in banned_patterns:
                    if re.search(pattern, text):
                        offenders.append(f"{path.relative_to(ROOT)} contains {pattern}")

        self.assertEqual(offenders, [])

    def test_plugin_content_uses_zynthium_repository_identity(self) -> None:
        checked_roots = [
            ROOT / "README.zh-CN.md",
            ROOT / ".codex-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / ".agents" / "plugins" / "marketplace.json",
        ]
        offenders: list[str] = []
        for checked in checked_roots:
            if not checked.exists():
                offenders.append(f"missing {checked.relative_to(ROOT)}")
                continue
            text = checked.read_text(encoding="utf-8")
            if "joeslee" in text or "github.com/joeslee" in text:
                offenders.append(str(checked.relative_to(ROOT)))

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
