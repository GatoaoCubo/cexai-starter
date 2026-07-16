---
id: p01_kc_structural_scoring
kind: knowledge_card
kc_type: meta_kc
pillar: P01
version: 1.0.0
created: "2026-04-28"
updated: "2026-04-28"
author: N04
title: "Structural Scoring v2: Deterministic Artifact Quality Assessment"
domain: CEX system architecture
subdomain: quality gates
when_to_use: "When you need to validate artifact delivery integrity (on-disk + committed), format compliance (YAML, frontmatter), and content structure (density, wikilinks, tags) in zero API tokens"
tags: [structural-score, quality-gate, deterministic, zero-cost, artifact-validation]
tldr: "10-check deterministic rubric (1pt each, binary pass/fail). Replaces LLM self-judgment. Tools: cex_doctor.py, cex_compile.py, cex_score.py. Threshold: >=8/10 publish-ready, <6/10 reject. Zero API cost, <2sec runtime."
keywords: [structural_score, frontmatter, artifact-integrity, delivery-verification, deterministic-scoring]
long_tails: ["10-check structural scoring rubric", "deterministic artifact validation", "frontmatter integrity gates", "density scoring formula", "tool-based peer review"]
axioms:
  - "ALWAYS: structural_score is deterministic (same artifact = same score regardless of runtime, model, or session)"
  - "NEVER: conflate structural_score with quality (quality is subjective peer-review; structural_score is mechanical verification)"
  - "IF: artifact_on_disk FAIL, THEN: structural_score = BLOCKING regardless of other checks"
density_score: 0.88
data_source: "p07_sr_structural_score_v2.md (canonical spec)"
quality: null
---

## Executive Summary

Structural Scoring v2 is a deterministic, tool-based quality validation framework that replaces LLM self-judgment. 10 binary checks (1 point each). Any artifact always scores identically. Zero API cost. Runs under 2 seconds. Derived from STRESS_TEST (2026-04-28, 6 runtimes, Haiku/Sonnet signal-without-deliverable gaps closed by checks 9-10).

---

## Spec Table

| Property | Value |
|----------|-------|
| Framework | Deterministic (tool-based, not LLM-judged) |
| Total checks | 10 (binary: pass=1pt, fail=0pt) |
| Max score | 10.0 |
| Publish threshold | >= 8.0 |
| Review threshold | 6.0-7.9 (targeted fix) |
| Reject threshold | < 6.0 (rebuild) |
| Golden tier | >= 9.5 (calibration reference) |
| Cost | Zero API tokens |
| Runtime | < 2 seconds per artifact |
| Blocking check | #9 (artifact_on_disk FAIL = instant reject) |

---

## The 10 Checks (with tools)

| # | Check | Tool | Dimension | Pass Condition |
|---|-------|------|-----------|----------------|
| 1 | frontmatter_valid | cex_doctor.py | Parse Integrity | YAML parses; id/kind/pillar/quality present |
| 2 | density_above_085 | cex_doctor.py | Content Health | content/total byte ratio >= 0.75 minimum |
| 3 | wikilinks_resolve | cex_doctor.py | Content Health | All [\[target\]] found in cex_index |
| 4 | compile_clean | cex_compile.py | Parse Integrity | .md -> .yaml exit 0; schema valid |
| 5 | ascii_clean | cex_sanitize.py | File Hygiene | 0 non-ASCII bytes in .py/.sh/.ps1/.cmd |
| 6 | size_under_cap | cex_doctor.py | File Hygiene | < 8 KiB (regular); < 10 KiB (builder ISOs) |
| 7 | has_related | cex_score.py L1 | Content Health | Related Artifacts section; >= 1 wikilink row |
| 8 | has_tags | cex_score.py L1 | Content Health | tags: field; >= 1 entry |
| 9 | artifact_on_disk | path check | Delivery | File exists at path declared in signal |
| 10 | git_committed | git show | Delivery | `git show HEAD:{path}` exits 0 |

---

## Dimension Weights

| Dimension | Checks | Weight | Semantics |
|-----------|--------|--------|-----------|
| **Parse Integrity** | 1, 4 | 20% | YAML clean; compile produces .yaml without schema violations |
| **Content Health** | 2, 3, 7, 8 | 40% | Density >= 0.87; wikilinks resolve; metadata complete |
| **File Hygiene** | 5, 6 | 20% | ASCII-only; size within bounds |
| **Delivery** | 9, 10 | 20% | On disk at declared path AND committed to git HEAD |

---

## Scoring Tiers

| Tier | Score | Range | Action |
|------|-------|-------|--------|
| **GOLDEN** | >= 9.5 | 9.5-10.0 | All 10 pass; promote as calibration reference |
| **PUBLISH** | >= 8.0 | 8.0-9.4 | Production-ready; merge to nucleus pool |
| **REVIEW** | >= 6.0 | 6.0-7.9 | Targeted fix on failing checks; re-run validation |
| **REJECT** | < 6.0 | 0-5.9 | Return to F6 (PRODUCE); rebuild from builder ISOs |

**Hard override rule**: Check 9 (artifact_on_disk) FAIL = BLOCKING REJECT regardless of other scores.

---

## Frontmatter Integration

Tools write `structural_score` and `structural_details` (NOT self-reported):

```yaml
quality: null                  # stays null until peer review (semantic scoring deferred)
structural_score: 8            # integer 0-10 (deterministic)
structural_details:
  frontmatter_valid: true
  density_above_085: true
  wikilinks_resolve: false     # example: one wikilink broken
  compile_clean: true
  ascii_clean: true
  size_under_cap: true
  has_related: true
  has_tags: true
  artifact_on_disk: true
  git_committed: false         # example: staged but not committed yet
```

---

## 8F Pipeline Integration

Structural score plugs into **F7 GOVERN** (gate validation):

- **F6 PRODUCE**: Nucleus generates artifact with `quality: null` (no self-score)
- **F7 GOVERN**: 
  - Run tool council: `cex_doctor.py` + `cex_compile.py` + `cex_score.py L1`
  - Derive `structural_score` (0-10)
  - If structural_score < 8.0: return to F6 (max 2 retries)
  - If structural_score >= 8.0: proceed to F8
  - If artifact_on_disk FAIL: BLOCKING, no retries
- **F8 COLLABORATE**: Frontmatter + structural_score written; signal sent; git committed

---

## Tool Commands (Full Automation)

| Dimension | Command |
|-----------|---------|
| Parse Integrity | `python _tools/cex_doctor.py --scope {path}` `python _tools/cex_compile.py {path}` |
| Content Health | `python _tools/cex_score.py --apply {path} --layer structural` |
| File Hygiene | `python _tools/cex_sanitize.py --check --scope {path}` |
| Delivery | `test -f {path} && git show HEAD:{path} > /dev/null 2>&1` |

---

## Why Not LLM Self-Judgment?

**Root cause (STRESS_TEST 2026-04-28)**: Haiku and Sonnet emitted F8 COLLABORATE signals without on-disk deliverables. Structural scoring v2 adds checks 9 (artifact_on_disk) and 10 (git_committed) to close the gap at the toolchain level. No more "signal-without-deliverable" scenarios across any runtime.

**Design principle**: Structural score = verifiable facts only. LLM peer-review (semantic quality) is orthogonal and happens in `/evolve` post-dispatch.

---

## Cross-Nucleus Review Process

- **Grid dispatch**: N05 validates all other nuclei; producing nucleus does not self-score
- **Solo dispatch**: structural_score written immediately; semantic scoring deferred to `/evolve` sweep
- **Signal blocking rule**: `IF signal.status == "complete" AND artifact_on_disk == false: VERDICT = FAIL (BLOCKING)`

---

## Calibration Examples

| Tier | Example | Why |
|------|---------|-----|
| GOLDEN (10/10) | p07_efw_n05_operations.md | All 10 pass; on disk, committed, 0 broken wikilinks, density 0.95 |
| PUBLISH (8/10) | Typical nucleus output | Checks 1-8 pass; check 3 (1 wikilink) fails; check 10 already committed |
| REVIEW (6/10) | Signal before commit | Checks 1-8 pass; check 9 fails (file on disk staged only) |
| REJECT (4/10) | Signal without deliverable | Check 9 fails (no file); missing frontmatter |

---

## Anti-Patterns

1. **Self-scoring structural_score** -- Tools only. Never LLM-assigned.
2. **Using structural_score as quality proxy** -- Orthogonal domains (structural=mechanical, quality=semantic).
3. **Ignoring check 9 failures** -- If artifact not on disk, score = 0 (BLOCKING).
4. **Skipping compilation** -- Check 4 requires full cex_compile.py run (schema validation).

---

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p07_sr_structural_score_v2 | upstream | 0.95 |
| p01_kc_quality_gates | sibling | 0.82 |
| p11_fb_judge_config | related | 0.75 |
| p05_output_validator | downstream | 0.71 |
| p08_ac_verification | related | 0.65 |
