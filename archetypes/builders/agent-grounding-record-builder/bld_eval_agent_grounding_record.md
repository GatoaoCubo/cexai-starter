---
kind: quality_gate
id: bld_quality_gate_agent_grounding_record
pillar: P11
llm_function: GOVERN
purpose: Define hard gates H01-H08 and soft scoring dimensions for agent_grounding_record quality control
quality: null
title: "Agent Grounding Record -- Quality Gate"
version: "1.0.0"
author: wave7_n05
tags: [agent_grounding_record, builder, quality_gate]
tldr: "8 hard gates (all must pass) + 5D soft scoring targeting >= 9.0 overall for compliance-grade provenance"
domain: "agent_grounding_record construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [define hard gates h, agent_grounding_record construction, hard gates, all must pass, d soft scoring targeting, overall for compliance-grade provenance, agent_grounding_record]
density_score: 0.85
---
## Quality Gate
# Agent Grounding Record -- Quality Gate
## Scoring Overview
| Layer       | Weight | Method                                                   |
|-------------|--------|----------------------------------------------------------|
| Structural  | 30%    | Hard gate pass/fail count (H01-H08, must all pass)      |
| Rubric      | 30%    | 5D dimension scoring (D1-D5 weighted)                    |
| Semantic    | 40%    | LLM evaluation when structural + rubric score >= 8.5    |
| Target      | --     | >= 9.0 overall for production-grade grounding record     |
A record that fails ANY hard gate receives a score of 0.0 regardless of rubric or semantic scores.
## Hard Gates (H01-H08)
ALL hard gates must pass. One FAIL = record is invalid = do not publish.
| Gate | Field / Check                  | Pass Condition                                                         | Fail Action                                          |
|------|-------------------------------|-------------------------------------------------------------------------|------------------------------------------------------|
| H01  | Frontmatter YAML              | Parses without error; all required frontmatter keys present             | Return to F6, fix YAML syntax                        |
| H02  | Artifact ID naming pattern    | Matches ^p10_gr_[a-z0-9_]+\.md$                                        | Rename file to match pattern before scoring          |
| H03  | kind field                    | Exactly "agent_grounding_record" (string match, no whitespace)          | Fix frontmatter kind field                           |
| H04  | inference_id present          | Non-empty string matching UUIDv4 pattern                               | Generate new UUIDv4; do not reuse existing IDs       |
| H05  | output_hash present           | 64 lowercase hex characters (SHA-256)                                  | Recompute from raw output; this gate never waives    |
| H06  | otel_span_id present          | Non-empty string; 16 hex chars (W3C format) preferred                  | Verify OTel instrumentation is active; retrieve span |
## Hard Gate Failure Reference
| Gate | Most Common Cause                             | Prevention                                                   |
|------|-----------------------------------------------|--------------------------------------------------------------|
| H01  | Copy-paste corruption in frontmatter YAML     | Validate YAML before finalizing                              |
| H02  | Wrong naming prefix (e.g. p01_ instead of p10_) | Check config ISO for naming convention before writing ID  |
| H03  | kind typo or wrong kind for this builder      | Load bld_manifest first; kind is agent_grounding_record      |
| H04  | Missing inference_id or copied from prior run | Generate fresh UUIDv4 at session start                       |
| H05  | Output hash computed after post-processing    | Hash the raw output BEFORE any formatting or truncation      |
| H06  | OTel not instrumented for this inference path | Add OTel GenAI semconv instrumentation to the inference layer|
## Soft Scoring Dimensions (D1-D5)
| Dim | Name                    | Weight | Scoring Criteria                                                              |
|-----|-------------------------|--------|-------------------------------------------------------------------------------|
| D1  | Provenance completeness | 0.30   | All required fields populated; no silent nulls; optional fields documented   |
| D2  | RAG-chunk coverage      | 0.25   | Every chunk has source_url AND content_hash; retrieval_score recorded         |
| D3  | Tool-call traceability  | 0.25   | Every tool-call has input_hash + output_hash + timestamp; status explicit    |
| D4  | C2PA integration        | 0.10   | c2pa_manifest_ref present (URI or explicit null); not omitted silently        |
| D5  | Downstream tracking     | 0.10   | downstream_use set; grounding_coverage_pct computed (not defaulted to 1.0)   |
### Rubric Summary (all dimensions)
| Score | General Criteria |
|-------|-----------------|
| 10 | All fields present, complete, computed from source data |
| 8-9 | All required fields; minor optional gaps |
| 6-7 | Required fields present; several optional omitted |
| 4-5 | One or more required fields missing |
| 0-3 | Structurally incomplete; unverifiable |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
