from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def run_installer(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/install_aletheia.py", "--dry-run", *args],
            cwd=cwd or ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_default_install_plan_uses_zynthium_marketplace_for_both_hosts(self) -> None:
        result = self.run_installer()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("claude plugin marketplace add zynthium/aletheia-os --scope user", result.stdout)
        self.assertIn("claude plugin install aletheia-os@aletheia-os --scope user", result.stdout)
        self.assertIn("codex plugin marketplace add zynthium/aletheia-os", result.stdout)
        self.assertIn("Open Codex /plugins", result.stdout)

    def test_project_install_plan_uses_project_cwd_and_can_copy_codex_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = self.run_installer(
                "--scope",
                "project",
                "--project",
                str(project),
                "--with-codex-agents",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(f"cwd: {project.resolve()}", result.stdout)
            self.assertIn("claude plugin marketplace add zynthium/aletheia-os --scope project", result.stdout)
            self.assertIn("copy codex agents", result.stdout)
            self.assertIn(str(project.resolve() / ".codex" / "agents"), result.stdout)

    def test_user_scope_codex_agents_target_home(self) -> None:
        result = self.run_installer("--host", "codex", "--scope", "user", "--with-codex-agents")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(str(Path.home() / ".codex" / "agents"), result.stdout)

    def test_init_project_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_installer("--host", "claude", "--project", tmp, "--init-project")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("initialize AletheiaOS truth layer", result.stdout)
            self.assertIn(f"scripts/init_aletheia.py {Path(tmp).resolve()}", result.stdout)

    def test_package_contains_installer_and_marketplaces(self) -> None:
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
            self.assertTrue((release_root / "scripts" / "install_aletheia.py").exists())
            self.assertTrue((release_root / ".claude-plugin" / "marketplace.json").exists())
            self.assertTrue((release_root / ".agents" / "plugins" / "marketplace.json").exists())

    def test_marketplace_manifests_point_to_local_plugin(self) -> None:
        claude_marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        codex_marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
        )

        self.assertEqual(claude_marketplace["name"], "aletheia-os")
        self.assertIn("plugins", claude_marketplace)
        self.assertEqual(codex_marketplace["name"], "aletheia-os")
        self.assertEqual(codex_marketplace["interface"]["displayName"], "AletheiaOS")
        self.assertEqual(codex_marketplace["plugins"][0]["name"], "aletheia-os")
        self.assertEqual(codex_marketplace["plugins"][0]["source"]["path"], "./")


if __name__ == "__main__":
    unittest.main()
