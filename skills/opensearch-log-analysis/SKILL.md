---
name: opensearch-log-analysis
description: Investigate OpenSearch logs through MCP with bounded counts, aggregations, patterns, and representative samples. Use for incident analysis, error tracing, request correlation, and log searches. OpenSearch access remains read-only; do not use this skill for cluster configuration or write operations.
---

# OpenSearch log analysis

Use OpenSearch evidence without flooding the model context. Read the active
project instructions first. Treat their index patterns, environment routing,
application filters, log formats, and correlation fields as authoritative.

## Investigation workflow

1. Identify the intended index or index pattern, application, environment, and
   shortest relevant time range. If the required index is unknown or
   inaccessible, report that condition instead of broadening the search.
2. Start with counts, aggregation-only queries, and pattern analysis. Use
   `size: 0` when only aggregations are needed and request at most 50 buckets.
3. Narrow the query with the strongest available fields before requesting raw
   documents: service, environment, severity, endpoint, request ID, class,
   exception, session, or other project-defined correlation values.
4. Retrieve at most 20 representative documents by default. Do not retrieve
   more than 100 raw documents during one investigation unless the user
   explicitly requests a larger bounded sample.
5. Request only fields needed for the current hypothesis. Avoid large message
   bodies and unrelated metadata unless they are necessary evidence.
6. Correlate representative logs with the corresponding source path. Base the
   conclusion on both log evidence and current code when source is available.

## Reusable project knowledge

- Read `OPEN_SEARCH_INFO.md` at the repository root before an investigation if
  it exists.
- When an investigation reveals a verified, reusable field or routing rule,
  update the file. Create it only when the project instructions explicitly
  request it.
- Record the field name, meaning, applicable indexes, environments or
  applications, correlation purpose, evidence source, and verification date.
- Use placeholders in examples. Never record credentials, tokens, personal
  data, real log values, raw log samples, one-off observations, or unverified
  assumptions.
- If the current task is read-only or forbids file changes, report the proposed
  addition without modifying the file.

## Hard boundaries

- Keep all OpenSearch actions read-only. Never change documents, indexes,
  settings, templates, aliases, security configuration, or cluster state.
- Always scope searches to the intended index. Never replace a missing or
  inaccessible index with a broader pattern implicitly.
- Never scroll, paginate, export, or enumerate an entire result set. Use counts
  and aggregations to measure it.
- If a response is unexpectedly large, stop retrieving documents and refine
  the index, time range, filters, fields, or limits.
- Do not expose credentials, tokens, personal data, or unnecessary production
  payloads in queries, samples, or the final report.

## Report

State the index scope, time range, filters, counts, representative evidence,
related source path, conclusion, and remaining uncertainty. Distinguish results
observed in logs from behavior inferred from source code.
