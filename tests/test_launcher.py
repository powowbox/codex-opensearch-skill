import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from codex_opensearch_mcp import launcher  # noqa: E402


class PrepareEnvironmentTests(unittest.TestCase):
    def test_loads_password_without_modifying_source(self):
        source = {
            "OPENSEARCH_KEYCHAIN_ACCOUNT": "readonly-user",
            "OPENSEARCH_KEYCHAIN_SERVICE": "example-service",
        }

        result = launcher.prepare_environment(source, lambda service, account: "secret")

        self.assertNotIn("OPENSEARCH_PASSWORD", source)
        self.assertEqual(result["OPENSEARCH_USERNAME"], "readonly-user")
        self.assertEqual(result["OPENSEARCH_PASSWORD"], "secret")

    def test_requires_keychain_account(self):
        with self.assertRaisesRegex(launcher.LauncherError, "ACCOUNT is required"):
            launcher.prepare_environment({}, lambda service, account: "secret")


class CommandTests(unittest.TestCase):
    def test_builds_default_command(self):
        command = launcher.build_server_command({})

        self.assertEqual(
            command,
            [
                "uvx",
                "opensearch-mcp-server-py==0.11.0",
                "--transport",
                "stdio",
                "--mode",
                "single",
            ],
        )

    def test_supports_offline_and_explicit_python(self):
        command = launcher.build_server_command(
            {
                "OPENSEARCH_MCP_OFFLINE": "true",
                "OPENSEARCH_MCP_PYTHON": "/path/to/python",
            }
        )

        self.assertEqual(
            command[0:4],
            ["uvx", "--offline", "--python", "/path/to/python"],
        )


class KeychainTests(unittest.TestCase):
    @mock.patch("codex_opensearch_mcp.launcher.subprocess.run")
    def test_reads_password_from_keychain(self, run):
        run.return_value = mock.Mock(returncode=0, stdout="secret\n")

        password = launcher.read_keychain_password(
            "example-service", "readonly-user", security_binary="security"
        )

        self.assertEqual(password, "secret")
        run.assert_called_once_with(
            [
                "security",
                "find-generic-password",
                "-s",
                "example-service",
                "-a",
                "readonly-user",
                "-w",
            ],
            capture_output=True,
            text=True,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
