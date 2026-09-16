# codex-opensearch-mcp

A small macOS launcher and configuration template for connecting Codex to the
[official OpenSearch MCP server](https://github.com/opensearch-project/opensearch-mcp-server-py).

This project does not implement or fork the OpenSearch MCP server. It keeps the
OpenSearch password in macOS Keychain, starts a pinned upstream server through
`uvx`, and documents a narrow read-only Codex configuration.

## Security model

- The password is read from macOS Keychain and passed only in the child process environment.
- The launcher never prints the password or places it in command-line arguments.
- The example configuration disables generic and write-capable tools.
- A genuinely read-only OpenSearch account remains the primary security boundary.
- Search-result limits must also be enforced through agent instructions and narrow queries.

## Requirements

- macOS with the `security` command
- Python 3.9 or later
- [`uv`](https://docs.astral.sh/uv/) and its `uvx` command
- A read-only OpenSearch account
- Codex with MCP server configuration support

## Installation

Install from a local checkout:

```bash
python3 -m pip install --user .
```

For development:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Create a generic-password entry in macOS Keychain with:

- service: `codex-opensearch`
- account: your read-only OpenSearch username
- password: your OpenSearch password

Keychain Access can create the entry without exposing the password in shell history.

Copy the example from [docs/codex-configuration.md](docs/codex-configuration.md)
into the Codex configuration and replace only the placeholders. Restart Codex
after changing its MCP configuration.

## Verification

```bash
python3 -m unittest discover -s tests
ruff check .
python3 -m build
```

Then ask Codex to list accessible indexes without retrieving documents. Confirm
that only the expected read-only tools are available.

## Configuration

The launcher recognizes these environment variables:

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENSEARCH_KEYCHAIN_ACCOUNT` | yes | — | Read-only OpenSearch username and Keychain account |
| `OPENSEARCH_KEYCHAIN_SERVICE` | no | `codex-opensearch` | Keychain service name |
| `OPENSEARCH_MCP_PACKAGE` | no | `opensearch-mcp-server-py==0.11.0` | Upstream package and version |
| `OPENSEARCH_MCP_RUNNER` | no | `uvx` | Executable used to run the server |
| `OPENSEARCH_MCP_PYTHON` | no | — | Python executable passed to `uvx` |
| `OPENSEARCH_MCP_OFFLINE` | no | `false` | Add `--offline` when true |
| `OPENSEARCH_MCP_TRANSPORT` | no | `stdio` | MCP transport |
| `OPENSEARCH_MCP_MODE` | no | `single` | Upstream connection mode |

All other `OPENSEARCH_*` variables are passed to the official server unchanged.

## Scope

This project currently supports macOS Keychain. Contributions for other native
secret stores are welcome if they preserve the rule that secrets never appear in
configuration files, logs, process arguments, or test fixtures.

## License

MIT. See [LICENSE](LICENSE).
