---
kind: quality_gate
id: p11_qg_hook
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of hook artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Hook"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, hook, event, lifecycle, trigger, intercept]
tldr: "Gates ensuring hook artifacts define safe, scoped event interceptors with trigger configs, timeout, and error strategies."
domain: "hook — pre/post event interceptors for system lifecycle events"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.91
related:
  - hook-builder
  - bld_architecture_hook
  - bld_schema_hook
---
## Quality Gate

# Gate: Hook
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: hook` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | Uppercase, spaces, or leading digit |
| H03 | ID equals filename stem | `id: pre_tool` in file `post_stop.md` |
| H04 | Kind equals literal `hook` | Any other kind value |
| H05 | Quality field is `null` | Any non-null value |
| H06 | All required fields present | Missing: event, trigger, script_path, blocking, timeout_ms |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Trigger specificity | 1.0 | Event + matcher condition both defined (e.g., tool name pattern) | Event only, no matcher | No trigger config |
| S02 | Blocking behavior justified | 1.0 | `blocking: true/false` stated with rationale in description | Blocking stated, no rationale | Blocking field absent |
| S03 | Timeout apownteness | 1.0 | Timeout fits event type (PreToolUse < 5000ms, PostToolUse < 30000ms) | Timeout present but oversized | No timeout or zero |
| S04 | Script path resolvable | 1.0 | Path exists or clearly references known convention | Path plausibly correct | Path invented or ambiguous |
| S05 | Error strategy completeness | 0.5 | Strategy + fallback behavior + log target all specified | Strategy only | None |
| S06 | Condition guard | 1.0 | `conditions` field narrows hook scope (env var, file exists, etc.) | Condition present but vague | No condition — fires always |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to pool as golden hook pattern |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | Emergency incident hook needed immediately; trigger config incomplete due to unknown event schema |
| Approver | System owner only |
| Audit trail | `bypass_reason` field required in frontmatter |
| Expiry | 48 hours; hook must reach full compliance or be deactivated |

## Examples

# Examples: hook-builder
## Golden Example
INPUT: "Create a hook that tracks tool usage after each tool call for metrics"
OUTPUT:
```yaml
id: p04_hook_post_tool_metrics
kind: hook
pillar: P04
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
trigger_event: "post_tool_use"
script_path: ".claude/hooks/tool_metrics.sh"
execution: "post"
blocking: false
domain: "observability"
quality: null
tags: [hook, metrics, post-tool, P04, observability, tracking]
tldr: "Logs tool name, duration, and success status to metrics file after each tool invocation"
timeout: 5000
conditions: ["tool_name != AskUserQuestion"]
async: true
error_handling: "log"
logging: true
environment: ["METRICS_FILE=.claude/metrics/tool_usage.jsonl", "SESSION_ID"]
keywords: [tool-metrics, post-tool-hook, usage-tracking, observability]
density_score: 0.88
```
## Trigger Configuration
Event: post_tool_use
Execution: post (fires after tool complete)
Conditions:
- tool_name != AskUserQuestion (skip interactive tools)
## Script
Path: .claude/hooks/tool_metrics.sh
Language: bash
Arguments: none (reads from environment)
```bash
echo "{\"tool\":\"$TOOL_NAME\",\"duration_ms\":$DURATION,\"success\":$SUCCESS,\"ts\":\"$(date -Is)\"}" >> "$METRICS_FILE"
```
## Input/Output
Input (from event): tool_name, duration_ms, success (boolean), output_size
Output (to caller): none (async, fire-and-forget)
## Error Handling
Strategy: log (never block on metrics failure)
- On script failure: log error to stderr, continue
- On timeout: kill script, log timeout event
- On missing script: log warning, skip execution
WHY THIS IS GOLDEN:
- quality: null (H05 pass) | id p04_hook_ pattern (H02 pass) | kind: hook (H04 pass)
- 22 fields present (H06 pass) | trigger_event: post_tool_use valid (H07 pass)
- timeout: 5000 <= 30000 (H08 pass) | blocking: false (H09 n/a)
- tldr: 79ch (S01 pass) | tags: 6 items (S02 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
