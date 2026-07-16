---
kind: quality_gate
id: p11_qg_toolkit
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of toolkit artifacts
pattern: few-shot learning for permission bundles with confirmation tiers
quality: null
title: 'Gate: Toolkit'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring toolkits enforce least-privilege with correct confirmation tiers,
  deny lists override allow lists, tool count stays under 15, and no implementation
  code leaks into the permission bundle.
domain: toolkit
created: '2026-04-06'
updated: '2026-04-06'
8f: "F7_govern"
keywords:
  - "p04_tk_{name}"
  - "toolkit"
  - "quality"
  - "tools"
  - "description"
  - "quality gate"
  - "gates failure"
density_score: 0.85
related:
  - toolkit-builder
  - bld_schema_toolkit
  - bld_memory_toolkit
---
## Quality Gate

## Definition
A toolkit is a permission bundle defining which tools an agent can access and under what constraints. It passes this gate when every write tool requires confirmation, deny lists are explicit with reasons, the tool count stays under 15, no tool implementation code is present, and the least-privilege principle is demonstrably applied.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches pattern `p04_tk_{name}` | Mismatched IDs cause routing failures |
| H03 | `kind` is exactly `toolkit` (literal match) | Kind drives the loader; wrong literal silently misroutes |
| H04 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H05 | `name` field is non-empty snake_case string | Invalid names break lookup and indexing |
| H06 | `tools` is a non-empty list with 1-15 entries | Empty toolkits are useless; >15 indicates domain split needed |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler prose | Mostly substantive | No filler; every line carries information |
| 2 | Least-privilege compliance (only tools the agent demonstrably needs) | 1.5 | Kitchen sink — every tool included | Most tools justified | Every tool has clear usage justification |
| 3 | Confirmation tier accuracy (tiers match risk: reads=auto, writes=confirm, dangerous=deny) | 1.5 | All tools on auto | Most tiers correct | Every tier accurately reflects operation risk |
| 4 | Deny lists are explicit with reasons (not just names) | 1.0 | No deny lists | Deny lists without reasons | Every denial has an evidence-based reason |
| 5 | Tool descriptions are precise (one-line purpose, not usage instructions) | 1.0 | Descriptions are paragraphs | Most are concise | Every description is under 80 chars and actionable |
| 6 | No cross-toolkit tool duplication | 0.5 | Many duplicates across toolkits | One or two overlaps | Zero duplicates; each tool in exactly one toolkit |

## Examples

# Examples: toolkit-builder
## Golden Example
INPUT: "Create a file operations toolkit for N03 build nucleus"
OUTPUT (`p04_tk_file_ops.yaml`):
```yaml
name: file_ops
category: file_ops
requires_confirmation: true
scope: nucleus
target_agent: n03
tools:
  - name: read_file
    description: Read file contents by absolute path
```
WHY THIS IS GOLDEN:
- filename follows `p04_tk_{name}.yaml`
- read tools are `auto`, write tools are `confirm`, delete is `deny`
- least-privilege: only 6 tools, all demonstrably needed for file operations
- `denied_for` on delete restricts non-build nuclei
## Golden MCP-Mapped Example
OUTPUT (`p04_tk_git_ops.yaml`):
```yaml
name: git_ops
category: git_ops
requires_confirmation: true
scope: nucleus
target_agent: n05
mcp_server: github-mcp
tools:
  - name: git_status
```
WHY THIS PASSES:
- MCP endpoints mapped for all tools
- force_push correctly denied for all non-ops nuclei
- confirmation tiers match risk accurately
- tool count is 7, well within the 15-tool limit
## Anti-Example
BAD OUTPUT (`p04_tk_everything.yaml`):
```yaml
name: everything
category: general
requires_confirmation: false
tools:
  - name: read_file
    description: Reads a file
    confirmation: auto
  - name: write_file
```
FAILURES:
1. name "everything" violates least-privilege — not domain-scoped
2. category "general" is not in the allowed enum
3. `requires_confirmation: false` when write/delete tools exist — security violation
4. write_file and delete_file have `confirmation: auto` — HARD gate H09 failure
5. execute_code with `confirmation: auto` — dangerous operation without restriction
6. 20+ tools exceeds 15-tool limit — HARD gate H06 failure
7. no `denied_for` on destructive tools
8. descriptions are vague ("Reads a file") — no actionable context

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
