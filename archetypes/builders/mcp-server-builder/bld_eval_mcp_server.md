---
kind: quality_gate
id: p11_qg_mcp_server
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of mcp_server artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: MCP Server"
version: "1.0.0"
author: builder_agent
tags: [quality-gate, mcp-server, protocol, P04, integration]
tldr: "Quality gate for mcp_server artifacts: enforces tool list, transport type, auth strategy, and JSON-Schema params."
domain: mcp_server
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [mcp server, tool list, transport type, auth strategy, json-schema]
density_score: 0.85
related:
  - bld_memory_mcp_server
  - mcp-server-builder
---
## Quality Gate

# Gate: MCP Server
## Definition
A `mcp_server` artifact specifies an MCP server: tools, resources, transport, and auth. Gates ensure identifiability, machine-readable tool schemas, and auth-transport alignment.
## HARD Gates
All HARD gates must pass. Any single failure sets score to 0 and blocks publish.
| ID  | Check | Failure consequence |
|-----|-------|---------------------|
| H01 | YAML frontmatter parses without error | Artifact unparseable by tooling |
| H02 | `id` matches `^p04_mcp_[a-z][a-z0-9_]+$` | Namespace violation — not discoverable |
| H03 | `id` equals filename stem exactly | Brain search failure — id/file mismatch |
| H04 | `kind` == literal string `"mcp_server"` | Type integrity failure |
| H05 | `quality` == `null` | Self-scoring violation — pool metric corruption |
| H06 | All required fields present and non-empty (`id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `name`, `transport`, `tools_provided`, `auth`, `tags`, `tldr`) | Incomplete artifact |
## SOFT Scoring
Weights sum to 100%. Each dimension scores 0 or its full weight.
| ID  | Dimension | Weight | Criteria |
|-----|-----------|--------|----------|
| S01 | tldr quality | 1.0 | `tldr` <= 160 chars, names the server's purpose and primary tool |
| S02 | Tool schemas have JSON-Schema params | 1.0 | Each tool entry includes `parameters` block with type annotations |
| S03 | Resource URIs follow templates | 1.0 | Resource URIs use `{variable}` template syntax, not hard-coded paths |
| S04 | Auth matches transport type | 1.0 | `stdio` paired with `none`; `sse`/`http` paired with `api_key`, `oauth`, or `bearer` |
| S05 | Error handling documented | 1.0 | Each tool documents at least one error code or failure mode |
| S06 | `tags` includes `"mcp-server"` | 0.5 | Minimum tag for routing |
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool + record in memory |
| >= 8.0 | PUBLISH | Commit to pool |
| >= 7.0 | REVIEW | Acceptable with documented improvement items |
| < 7.0 | REJECT | Revise and resubmit — do not publish |
| 0 (HARD fail) | REJECTED | Fix failing HARD gate(s) first |
## Bypass
Bypasses are logged and expire automatically.
| Field | Value |
|-------|-------|
| condition | Proof-of-concept server with single tool and no auth requirement (local stdio only) |
| approver | P04 integration owner |

## Examples

# Examples: mcp-server-builder
## Golden Example
INPUT: "Create MCP server for a document search service with hybrid BM25+vector search"
OUTPUT:
```yaml
id: p04_mcp_document_search
kind: mcp_server
pillar: P04
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
name: "Document Search MCP Server"
transport: stdio
tools_provided:
  - search_documents
  - get_document
  - list_collections
resources_provided:
  - mem://index/status
  - db://collections/{name}
auth: none
description: "MCP server exposing hybrid BM25+vector search over document collections via stdio"
health_check: "python server.py --health"
rate_limit: "100 req/min"
versioning: "semver, negotiated at connect"
quality: null
tags: [mcp_server, search, documents, P04]
tldr: "Document search MCP server: 3 tools, 2 resources, stdio transport, hybrid BM25+vector"
```
## Overview
Exposes document search capabilities to agents via MCP stdio transport.
Consumed by research agents and knowledge retrieval pipelines.
## Tools
### search_documents
Search documents using hybrid BM25+vector scoring.
Parameters:
- `query` (string, required): Natural language search query
- `collection` (string, optional): Target collection name; defaults to all
- `limit` (integer, optional): Max results; default 10, max 50
Returns: List of {id, title, score, excerpt} objects
### get_document
Retrieve full document by ID.
Parameters:
- `id` (string, required): Document identifier
- `collection` (string, required): Collection containing the document
Returns: {id, title, content, metadata} object
### list_collections
List available document collections with stats.
Parameters: none
Returns: List of {name, doc_count, last_updated} objects
## Resources
### mem://index/status
Content-Type: application/json
Current index health: doc count, last rebuild timestamp, vector dimensions.
### db://collections/{name}
Content-Type: application/json
Collection metadata: schema, doc count, embedding model, index type.
## Transport & Auth
Transport: stdio (local subprocess via `python server.py`)
Auth: none (process-level trust, no network exposure)
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_mcp_ pattern (H02 pass)
- kind: mcp_server (H04 pass)
- 19 required+recommended fields present (H06 pass)
## Anti-Example
INPUT: "Create MCP server for weather data"
BAD OUTPUT:
```yaml
id: weather-mcp
kind: tool_server
pillar: tools
name: Weather Server
tools: [get_weather, forecast]
auth: "yes"
quality: 9.0
tags: [weather]
```
Provides weather data to agents.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` populated (3-15), 1+ upstream, 1+ downstream
- Penalty: -0.3 if empty

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_mcp_server]] | upstream | 0.45 |
| [[bld_orchestration_mcp_server]] | upstream | 0.44 |
| [[mcp-server-builder]] | upstream | 0.44 |
| n00_mcp_server_manifest | upstream | 0.44 |
