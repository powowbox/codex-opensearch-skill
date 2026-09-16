"""Launch the official OpenSearch MCP server with a macOS Keychain password."""

import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping
from typing import Optional

DEFAULT_KEYCHAIN_SERVICE = "codex-opensearch"
DEFAULT_SERVER_PACKAGE = "opensearch-mcp-server-py==0.11.0"


class LauncherError(RuntimeError):
    """Raised when the launcher cannot safely start the MCP server."""


def _is_true(value: Optional[str]) -> bool:
    return str(value or "").lower() in {"1", "true", "yes", "on"}


def read_keychain_password(
    service: str,
    account: str,
    security_binary: Optional[str] = None,
) -> str:
    """Read one password from macOS Keychain without exposing it in arguments."""
    binary = security_binary or shutil.which("security")
    if not binary:
        raise LauncherError("The macOS 'security' command is unavailable.")

    result = subprocess.run(
        [binary, "find-generic-password", "-s", service, "-a", account, "-w"],
        capture_output=True,
        text=True,
        check=False,
    )
    password = result.stdout.rstrip("\n")
    if result.returncode or not password:
        raise LauncherError(
            "The OpenSearch password is absent from Keychain or cannot be read."
        )
    return password


def prepare_environment(
    source: Mapping[str, str],
    password_reader: Callable[[str, str], str] = read_keychain_password,
) -> dict[str, str]:
    """Build the child environment and add credentials from Keychain."""
    environment = dict(source)
    account = environment.get("OPENSEARCH_KEYCHAIN_ACCOUNT", "").strip()
    if not account:
        raise LauncherError("OPENSEARCH_KEYCHAIN_ACCOUNT is required.")

    service = environment.get(
        "OPENSEARCH_KEYCHAIN_SERVICE", DEFAULT_KEYCHAIN_SERVICE
    ).strip()
    if not service:
        raise LauncherError("OPENSEARCH_KEYCHAIN_SERVICE cannot be empty.")

    environment["OPENSEARCH_USERNAME"] = account
    environment["OPENSEARCH_PASSWORD"] = password_reader(service, account)
    return environment


def build_server_command(environment: Mapping[str, str]) -> list[str]:
    """Build an argument list for uvx without invoking a shell."""
    runner = environment.get("OPENSEARCH_MCP_RUNNER", "uvx").strip()
    package = environment.get(
        "OPENSEARCH_MCP_PACKAGE", DEFAULT_SERVER_PACKAGE
    ).strip()
    if not runner or not package:
        raise LauncherError("The MCP runner and package must be non-empty.")

    command = [runner]
    if _is_true(environment.get("OPENSEARCH_MCP_OFFLINE")):
        command.append("--offline")

    python_executable = environment.get("OPENSEARCH_MCP_PYTHON", "").strip()
    if python_executable:
        command.extend(["--python", python_executable])

    command.extend(
        [
            package,
            "--transport",
            environment.get("OPENSEARCH_MCP_TRANSPORT", "stdio"),
            "--mode",
            environment.get("OPENSEARCH_MCP_MODE", "single"),
        ]
    )
    return command


def main() -> int:
    """Prepare credentials and replace this process with the MCP server."""
    try:
        environment = prepare_environment(os.environ)
        command = build_server_command(environment)
        os.execvpe(command[0], command, environment)
    except LauncherError as error:
        print(f"codex-opensearch-mcp: {error}", file=sys.stderr)
        return 78
    except FileNotFoundError:
        print(
            "codex-opensearch-mcp: uvx is unavailable; install uv first.",
            file=sys.stderr,
        )
        return 127
    return 0


if __name__ == "__main__":
    sys.exit(main())
