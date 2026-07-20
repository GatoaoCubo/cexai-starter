---
id: p04_mcp_cexai
kind: mcp_server
pillar: P04
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: "n05_operations"
title: "CEXAI MCP Server"
name: "CEXAI MCP Server"
transport: stdio
tools_provided:
  - cexai_resolve_intent
  - cexai_search
  - cexai_doctor
  - cexai_list_capabilities
  - cexai_plan_build
  - cexai_explain
  - cexai_build
  - cexai_job
resources_provided:
  - "cexai://artifact/{artifact_id}"
  - "cexai://kind/{kind}"
auth: none
description: "Local stdio server: 6 read-only/dry-run brain tools (T1) + 2 async 8F build-job tools (T2) + a content layer (T2.5: search excerpts + 2 MCP resources)."
rate_limit: "n/a (local stdio, single operator); job store caps concurrent builds"
versioning: "additive-only tool surface; golden regression pins tools/list shape per tier"
quality: null
tags: [mcp_server, cexai, job_store, stdio, tier2, resources]
tldr: "8-tool + 2-resource cexai MCP server: T1 read-only brain + T2 async 8F build jobs + T2.5 content (excerpts + cexai:// resources); stdio local."
related:
  - p01_kc_mcp_server
  - bld_memory_mcp_server
  - p01_kc_model_context_protocol
  - p11_qg_mcp_server
  - mcp-server-builder
  - bld_knowledge_card_mcp_server
  - p03_ins_mcp_server
---

## Overview
The CEXAI brain exposes itself over MCP as a local stdio server: 8 tools + 2
resources. Tier 1 (tools 1-6) is read-only/dry-run -- safe to call freely.
Tier 2 (tools 7-8) runs async 8F build jobs -- the one path that writes.

## Tools
| # | Tool | What it does | R/W | Timeout |
|---|------|---------------|-----|---------|
| 1 | `cexai_resolve_intent` | text -> kind/pillar/nucleus/verb | R | 20s |
| 2 | `cexai_search` | TF-IDF search, +excerpt opt | R | 30s |
| 3 | `cexai_doctor` | builder health summary | R | 120s |
| 4 | `cexai_list_capabilities` | builder/kind discovery | R | 30s |
| 5 | `cexai_plan_build` | 8F F1-F5 preview, never F6 | R | 30s |
| 6 | `cexai_explain` | glossary lookup | R | fast |
| 7 | `cexai_build` | async 8F job, +model opt | R* | job |
| 8 | `cexai_job` | status\|result\|cancel\|list | R/W | n/a |

\* execute=true is the ONE write/LLM path; log it.

## Job Contract
`queued -> running -> {done, error, cancelled, timeout}`. Bounded concurrency
per deployment. `model=` is checked against an allowlist; an unrecognized
model returns `ok:false` rather than falling through silently.

## build/run_8f Folding
A build request and a bare "run the 8F pipeline" request are the SAME F1-F8
sequence -- `run_8f` is `build` without a pre-resolved `kind`. Fold both into
ONE tool rather than shipping near-duplicate entry points; keeps the tool
surface small and easy to reason about.

## Resources (T2.5)
2 URI templates (MCP's second primitive, not tool-counted):
`cexai://artifact/{artifact_id}` (`.md` by id, size-capped),
`cexai://kind/{kind}` (kinds_meta.json entry, JSON). Id-based reads only --
refuses arbitrary filesystem paths (tenant configs, secrets, audit logs).

## Transport & Auth
stdio, local, no auth. Any tool with an irreversible action (fabricate,
deploy, delete) is out of scope for this tier -- gate it behind an explicit
higher-trust tier before exposing it over MCP.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_mcp_server]] | upstream | 0.32 |
| [[bld_memory_mcp_server]] | downstream | 0.26 |
| [[p01_kc_model_context_protocol]] | upstream | 0.26 |
| [[p11_qg_mcp_server]] | downstream | 0.26 |
| [[mcp-server-builder]] | related | 0.25 |
| [[bld_knowledge_card_mcp_server]] | related | 0.25 |
| [[p03_ins_mcp_server]] | upstream | 0.24 |
