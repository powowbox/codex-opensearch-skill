# codex-opensearch-skill

A small macOS launcher and configuration template for connecting Codex to the
[official OpenSearch MCP server](https://github.com/opensearch-project/opensearch-mcp-server-py).

This project does not implement or fork the OpenSearch MCP server. It keeps the
OpenSearch password in macOS Keychain, starts a pinned upstream server through
`uvx`, and documents a narrow read-only Codex configuration.

The repository also includes an optional `opensearch-log-analysis` Codex skill
that keeps investigations read-only and limits how much log data enters the
model context.

## Security model

- The password is read from macOS Keychain and passed only in the child process environment.
- The launcher never prints the password or places it in command-line arguments.
- The example configuration disables generic and write-capable tools.
- A genuinely read-only OpenSearch account remains the primary security boundary.
- The bundled skill defines strict search-result limits and a bounded investigation workflow.

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

In **Keychain Access**, select the `login` keychain, choose **File > New
Password Item**, enter `codex-opensearch` as the Keychain Item Name, and use the
same username configured in `OPENSEARCH_KEYCHAIN_ACCOUNT` as the Account Name.
Enter the OpenSearch password and save the item.

Alternatively, create it from Terminal. Keep `-w` as the final option so macOS
prompts for the password instead of storing it in shell history:

```bash
security add-generic-password \
  -a "readonly-user" \
  -s "codex-opensearch" \
  -w
```

Replace `readonly-user` with the read-only OpenSearch username used in the
Codex configuration. Do not put the password directly in the command.

Copy the example from [docs/codex-configuration.md](docs/codex-configuration.md)
into the Codex configuration and replace only the placeholders. Restart Codex
after changing its MCP configuration.

## Install the Codex skill

The skill is stored in
[`skills/opensearch-log-analysis`](skills/opensearch-log-analysis). It is a
repository asset and is not installed by the Python package.

Copy it into the Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/opensearch-log-analysis \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex after installing or updating the skill.

The skill contains the reusable read-only investigation workflow, aggregation
and sampling limits, field selection rules, and the prohibition on scrolling or
full-result enumeration.

You can add project-specific search information to the repository's
`AGENTS.md`. Useful details include index patterns for each environment, fields
and values that identify an application, timestamp fields, correlation IDs, and
known log-message markers. Keep credentials and secrets out of this file. For
example:

```md
## OpenSearch log analysis

Use `$opensearch-log-analysis` for every OpenSearch investigation.

### Project log routing

- Production index pattern: `example-app-production-*`.
- Staging index pattern: `example-app-staging-*`.
- Filter applications with `service.name`.
- Known services are `orders-api` and `billing-worker`.
- Use `@timestamp` as the event time.
- Correlate requests with `trace.id` and `request.id`.
- If an index is unavailable, report the error instead of searching a broader
  index pattern.
- Maintain reusable OpenSearch search information in `OPEN_SEARCH_INFO.md`.
```

This keeps private routing knowledge close to the project while allowing the
same safety workflow to be reused elsewhere.

Adding the `Maintain reusable OpenSearch search information` directive above to
`AGENTS.md` opts the project in and authorizes the skill to create
`OPEN_SEARCH_INFO.md` when it is missing. Without this directive, the skill may
read and update an existing file but must not create one.

For opted-in projects, the skill reads `OPEN_SEARCH_INFO.md` before searching
and updates it only with verified, reusable fields or routing rules. It records
their scope, purpose, evidence source, and verification date. The file must not
contain secrets, personal data, real log values, raw samples, one-off findings,
or unverified assumptions. Read-only tasks receive a proposed documentation
update instead of a file change.

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
