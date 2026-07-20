---
id: p11_gr_builder_nucleus
kind: guardrail
8f: F7_govern
pillar: P11
title: Guardrails -- Builder Nucleus
version: 1.0.0
created: 2026-03-30
updated: 2026-07-17
author: builder_agent
domain: meta-construction
quality: null
tags: [guardrail, builder, N03, safety, govern]
tldr: "7 guardrails: G01 no overwrite without git backup, G02 kinds_meta only grows (deprecate never delete), G03 always validate frontmatter, G04 never publish below 8.0, G05 never auto-modify builder ISOs, G06 schema check before F6, G07 block proprietary contamination."
when_to_use: "Enforce (F7 GOVERN) on every N03 build before write/publish. Consult for 'what must a builder NEVER do, and how is each rule checked?'"
primary_8f: GOVERN
keywords: [kinds_meta.json, frontmatter, schema constraints, max_bytes, runner.f7, artifact, git check, dry-run]
density_score: 0.90
related:
  - p11_fb_kind
  - p11_fb_validation_schema
  - p11_fb_context_file
  - p11_fb_input_schema
---

# Guardrails: Builder Nucleus

### How to use

```text
8F verb: GOVERN (F7). The runner checks these G01-G07 rails before any write or
publish; a fired rail blocks the action (see Enforcement). They are hard rules,
not suggestions. Bind the enforcement context below; G04 (8.0 floor) and G01
(git-backed overwrite) are the most frequently triggered.
```

```yaml
artifact_path: {{artifact_path}}      # file being written/overwritten
score: {{score}}                      # composite score (G04 gate, >= 8.0)
git_available: {{git_available}}      # G01 requires a readable prior version
target_kind: {{target_kind}}          # G02/G06 schema + registry checks
```

## G01: Never Overwrite Without Backup
Before overwriting any existing artifact, the previous version must be readable.
The compile step preserves .md source. Git history is the backup.
If git is unavailable, refuse to overwrite.

## G02: Never Delete a Kind
kinds_meta.json only grows. Kinds can be deprecated (add deprecated: true) but never removed.
Removing a kind breaks every artifact that references it.

## G03: Never Skip Frontmatter Validation
Even in dry-run mode, F7 validates frontmatter structure.
An artifact without valid frontmatter is not an artifact.

## G04: Never Publish Below 8.0
Quality floor is absolute. If F7 returns < 8.0 after 2 retries, the artifact is NOT saved.
It is logged as failed with the quality score and issues.

## G05: Never Modify Builder ISOs Automatically
The 12 ISOs per builder (1:1 with the 12 pillars) are hand-crafted. No automated process
may modify them in place. Feedback on builders queues for human review and writes diffs
to `.cex/runtime/feedback/` rather than overwriting the source ISOs.

## G06: Never Build Without Schema Check
Before F6 PRODUCE, F1 MUST have loaded the schema constraints.
Building without knowing max_bytes leads to oversized artifacts.

## G07: Proprietary Contamination Block
If any output contains proprietary names, product references, or company-specific terms,
F7 rejects with a contamination violation. The builder re-generates with generic terms.

## Enforcement

| Guardrail | Enforced By | Severity |
|-----------|-------------|----------|
| G01 | Git check before write | BLOCK |
| G02 | Kind registry tool (no --delete flag) | DESIGN |
| G03 | Runner.F7 always runs | HARD |
| G04 | Runner.F7 threshold check | HARD |
| G05 | File permissions on builders/ | DESIGN |
| G06 | Runner.F1 is mandatory step | PIPELINE |
| G07 | grep + F7 check | HARD |

## Worked Example

### G04 in action -- a build that scores 7.4 after 2 retries

```python
# Inside the 8F runner's F7 loop (illustrative)
for attempt in range(1, max_retries + 2):
    score, gate_failures = run_f7(artifact_text)
    if score >= QUALITY_FLOOR:   # 8.0
        break
    if attempt > max_retries:
        # G04 triggers HERE -- below floor, retries exhausted
        log.error(
            "G04 BLOCK: artifact rejected after %s attempts (final score: %.2f)",
            attempt, score,
        )
        write_failure_record(artifact_id, score, gate_failures)
        return None  # artifact NEVER reaches F8 SAVE
    artifact_text = run_f6_revise(artifact_text, gate_failures)
```

The artifact is logged as failed; no `.md` file is written to the pillar
directory; no signal is emitted with `status="complete"`. The operator sees
`status="failed"` + the failing gate list and decides whether to re-spec.

## Edge Cases

| Edge case | Guardrail | Behavior |
|-----------|-----------|----------|
| Kind registered, used in 50 artifacts, now obsolete | G02 | Mark `deprecated: true`; never delete -- 50 referencing artifacts would break wikilink validity |
| Score = 7.99 (just below floor) | G04 | BLOCKED -- floor is absolute. Operator may override only after manual peer review |
| Builder ISO has a typo, breaking 200 artifacts | G05 | Cannot auto-fix -- feedback tool queues a diff for human review + apply |
| Output contains "Acme Corp" (proprietary contamination) | G07 | F7 rejects; builder regenerates with `{{COMPANY_NAME}}` placeholder |

## Invariants

1. **Quality floor is absolute** -- no override at runtime; only post-hoc via peer review.
2. **kinds_meta.json only grows** -- additive forever; deletion is forbidden by tooling design.
3. **No artifact reaches F8 without F7 PASS** -- the pipeline halts before save on retry exhaustion.
4. **Builder ISOs are immutable to automated processes** -- only human-reviewed diffs may modify them.
5. **Every artifact has frontmatter or it is not an artifact** -- G03 enforces it before F6.
6. **Proprietary names never enter the repo** -- G07 is a hard block, not a warning.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb_kind]] | related | 0.27 |
| [[p11_fb_validation_schema]] | related | 0.27 |
| [[p11_fb_context_file]] | related | 0.27 |
| [[p11_fb_input_schema]] | related | 0.27 |
