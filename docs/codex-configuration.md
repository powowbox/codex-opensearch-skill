# Codex configuration

Install the package so `codex-opensearch-mcp` is available on the PATH used by
Codex, then add a configuration equivalent to the following:

```toml
[mcp_servers.opensearch]
command = "codex-opensearch-mcp"
enabled = true
startup_timeout_sec = 60
tool_timeout_sec = 120
enabled_tools = [
  "ListIndexTool",
  "IndexMappingTool",
  "SearchIndexTool",
  "GetShardsTool",
  "ClusterHealthTool",
  "CountTool",
  "ExplainTool",
  "MsearchTool",
  "DataDistributionTool",
  "LogPatternAnalysisTool",
  "MetricChangeAnalysisTool",
]

[mcp_servers.opensearch.env]
OPENSEARCH_KEYCHAIN_ACCOUNT = "readonly-user"
OPENSEARCH_KEYCHAIN_SERVICE = "codex-opensearch"
OPENSEARCH_URL = "https://opensearch.example.com/"
OPENSEARCH_SSL_VERIFY = "true"
OPENSEARCH_DYNAMIC_CONNECTION = "false"
OPENSEARCH_ENABLED_CATEGORIES = "skills"
OPENSEARCH_DISABLED_TOOLS = "GenericOpenSearchApiTool"
OPENSEARCH_DISABLED_TOOLS_REGEX = "^(?!(ListIndexTool|IndexMappingTool|SearchIndexTool|GetShardsTool|ClusterHealthTool|CountTool|ExplainTool|MsearchTool|DataDistributionTool|LogPatternAnalysisTool|MetricChangeAnalysisTool)$).*"
OPENSEARCH_SETTINGS_ALLOW_WRITE = "false"
OPENSEARCH_SETTINGS_ALLOW_WRITE_CATEGORIES = "skills"
```

Treat the upstream tool names and environment settings as version-specific.
Review them when changing `OPENSEARCH_MCP_PACKAGE`.

## Limiting returned data

Tool allowlists prevent many dangerous operations, but they do not cap the size
of valid search responses. Add repository or global agent instructions that:

- start with counts and aggregation-only queries using `size: 0`;
- use short time ranges and precise index/application filters;
- limit aggregations to a small number of buckets;
- retrieve a small representative sample and selected fields only;
- prohibit scrolling, exporting, pagination, and full-result enumeration.
