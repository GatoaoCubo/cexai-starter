---
kind: quality_gate
id: p11_qg_bugloop
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of bugloop artifacts
quality: null
title: "Gate: bugloop"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, bugloop, P11, correction-cycle, auto-fix, verification]
tldr: "Pass/fail gate for bugloop artifacts: correction cycle completeness, fix strategy safety, and verification assertion coverage."
domain: "automated correction cycles — detect, fix, verify loops for regression prevention"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [automated correction cycles, correction cycle completeness, fix strategy safety, and verification assertion coverage, quality-gate, bugloop, correction-cycle]
density_score: 0.92
related:
  - bugloop-builder
---
## Quality Gate

# Gate: bugloop
## Definition
| Field | Value |
|---|---|
| metric | bugloop artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: bugloop` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | ID contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | `id: my_loop` but file is `other_loop.md` |
| H04 | Kind equals literal `bugloop` | `kind: workflow` or any other value |
| H05 | Quality field is null | `quality: 8.5` or any non-null value |
| H06 | All required fields present | Missing `detection`, `fix_strategy`, or `verification` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Detection precision | 1.0 | Triggers are specific (regex patterns, error signatures) not vague strings |
| Fix strategy safety | 1.0 | `auto_fix` calibrated by confidence; destructive ops require high confidence threshold |
| Max attempts boundary | 0.5 | `max_attempts` is finite and reasonable (1-10 range) |
| Verification coverage | 1.0 | Assertions cover the fix target, not just smoke checks |
| Assertion timeout bounds | 0.5 | Each assertion has explicit timeout or global timeout defined |
| Rollback policy | 1.0 | Rollback defined for each fix strategy that mutates state |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Emergency hotfix loop for production incident already verified manually |
| approver | Senior engineer on-call + team lead sign-off |
| audit_trail | Bypass reason logged in artifact comment block with incident ID |
| expiry | 72h — artifact must reach >= 7.0 within 72h or be retired |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics) |

## Examples

# Examples: bugloop-builder
## Golden Example
INPUT: "Create bugloop for detectar e corrigir failss de validation no KC pipeline automaticamente"
OUTPUT:
```yaml
id: p11_bl_kc_pipeline
kind: bugloop
pillar: P11
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "orchestrator"
domain: "knowledge_card_pipeline"
quality: null
tags: [bugloop, knowledge-card, test-failure, auto-fix]
tldr: "Auto-correct KC validation failures: detect test failure > patch frontmatter > re-run suite"
scope: "KC pipeline — validate_kc.py execution on pre-commit and scheduled runs"
detect:
  method: "test_failure"
  trigger: "on_commit"
  pattern: "FAILED tests/test_validate_kc\\.py::test_[a-z_]+"
fix:
  strategy: "patch_and_retry"
  auto_fix: true
  max_attempts: 3
verify:
  test_suite: "tests/test_validate_kc.py"
  assertions:
    - "exit_code == 0"
    - "no FAILED lines in stdout"
    - "validate_kc.py returns score >= 8.0"
  timeout: 120
cycle_count: 5
auto_fix: true
escalation:
  threshold: 3
  target: "signal_bus:bugloop_escalation"
confidence: 0.88
test_suite: "tests/test_validate_kc.py"
rollback:
  enabled: false
  strategy: "git_revert"
## Detection
Trigger fires on every commit via pre-commit hook calling validate_kc.py.
Pattern `FAILED tests/test_validate_kc\.py::test_[a-z_]+` matches pytest output.
Sources: pytest stdout, pre-commit hook exit code != 0.
Known failure classes: missing required frontmatter fields, id/filename mismatch,
quality != null, body sections absent, byte limit exceeded.
## Fix Strategy
Auto-fix is enabled (confidence 0.88) because KC failures are deterministic and
all known failure classes have reversible patch actions:
- missing field: inject default value from SCHEMA.md
- id mismatch: rename file to match id stem
- quality != null: set quality to null
- byte limit: truncate body at 4096 bytes preserving all sections
Max 3 attempts before escalation. patch_and_retry chosen because KC artifacts
are idempotent — re-applying patch is safe.
## Verification
Suite: tests/test_validate_kc.py (full suite, not subset).
Pass: all 3 assertions must hold. Timeout 120s covers full suite on slow CI.
If verify fails after successful fix attempt: increment cycle, try again.
## Escalation
Fires at cycle 3 (of 5 max). Target: signal_bus:bugloop_escalation.
Payload includes: artifact_id, failure_pattern matched, attempts made,
last pytest stdout, fix patches applied.
Human review required when escalation fires.
## Rollback
Disabled for KC pipeline — patch_and_retry strategy is reversible.
git_revert defined as fallback if rollback is manually enabled.
Trigger condition: N/A (rollback.enabled = false).
```

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
