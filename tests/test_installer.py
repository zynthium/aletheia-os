from __future__ import annotations

import json
import os
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

    def test_installer_non_dry_run_executes_cli_and_copies_codex_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fakebin = root / "bin"
            project = root / "project"
            log = root / "commands.log"
            fakebin.mkdir()
            project.mkdir()
            for name in ["codex", "claude"]:
                command = fakebin / name
                command.write_text(
                    "#!/bin/sh\n"
                    f"printf '{name} %s\\n' \"$*\" >> \"{log}\"\n",
                    encoding="utf-8",
                )
                command.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fakebin}{os.pathsep}{env.get('PATH', '')}"

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/install_aletheia.py",
                    "--host",
                    "both",
                    "--scope",
                    "project",
                    "--project",
                    str(project),
                    "--source",
                    str(ROOT),
                    "--with-codex-agents",
                    "--init-project",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            commands = log.read_text(encoding="utf-8")
            self.assertIn(f"claude plugin marketplace add {ROOT} --scope project", commands)
            self.assertIn("claude plugin install aletheia-os@aletheia-os --scope project", commands)
            self.assertIn(f"codex plugin marketplace add {ROOT}", commands)
            self.assertTrue((project / ".codex" / "agents" / "truth-auditor.toml").exists())
            self.assertTrue((project / ".aletheia" / "START_HERE.md").exists())
            self.assertTrue((project / ".claude" / "settings.json").exists())

    def test_installer_reports_missing_host_executable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            env = os.environ.copy()
            env["PATH"] = str(project / "empty-bin")
            (project / "empty-bin").mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/install_aletheia.py",
                    "--host",
                    "claude",
                    "--scope",
                    "project",
                    "--project",
                    str(project),
                    "--source",
                    str(ROOT),
                ],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 127, output)
            self.assertIn("missing executable: claude", output)

    def test_installer_stops_when_host_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fakebin = root / "bin"
            project = root / "project"
            log = root / "commands.log"
            fakebin.mkdir()
            project.mkdir()
            claude = fakebin / "claude"
            claude.write_text(
                "#!/bin/sh\n"
                f"printf 'claude %s\\n' \"$*\" >> \"{log}\"\n"
                "case \"$*\" in\n"
                "  *'marketplace add'*) exit 42 ;;\n"
                "  *) exit 0 ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            claude.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fakebin}{os.pathsep}{env.get('PATH', '')}"

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/install_aletheia.py",
                    "--host",
                    "claude",
                    "--scope",
                    "project",
                    "--project",
                    str(project),
                    "--source",
                    str(ROOT),
                    "--init-project",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 42, output)
            commands = log.read_text(encoding="utf-8")
            self.assertIn("claude plugin marketplace add", commands)
            self.assertNotIn("claude plugin install", commands)
            self.assertFalse((project / ".aletheia").exists())


if __name__ == "__main__":
    unittest.main()
