---
id: p12_sc_research_n01
kind: schedule
pillar: P12
nucleus: n01
title: "N01 Research Cadences"
version: 1.0.0
quality: null
when_to_use: "Load to run N01 research on a cron cadence; defines what recurring research fires, when, and with which brief."
tags: [schedule, n01, research, cadence]
keywords: [research cadences, knowledge_card, benchmark, intel_sweep_targets, staleness_threshold_days, confidence_decay_per_day]
density_score: 0.94
related:
  - p12_wf_intelligence
  - p12_ct_research_sprint
  - p11_cn_research_n01
  - kc_schedule
updated: "2026-04-22"
---

## Purpose

N01 schedules define **research cadences**, not generic task timers.
The Analytical Envy lens makes N01 schedule-driven: recurring sweeps ensure
the corpus is never more than one cycle out of date.

## Standard N01 Research Cadences

| Cadence | Cron | Scope | Output Kind |
|---------|------|-------|-------------|
| `daily_intel_sweep` | `0 7 * * *` | New papers, peer/competitor updates, pricing changes | knowledge_card |
| `weekly_landscape_audit` | `0 9 * * 1` | Full landscape refresh for the tracked domain | knowledge_card |
| `monthly_benchmark_compare` | `0 8 1 * *` | Benchmark comparison update | benchmark |
| `quarterly_taxonomy_gap` | `0 8 1 */3 *` | Coverage vs. industry state-of-the-art | knowledge_card |

## Schedule Frontmatter Extensions

```yaml
intel_sweep_targets:
  - domain: competitive_intel
    staleness_threshold_days: 7
  - domain: research_papers
    staleness_threshold_days: 3
output_on_change_only: true # suppress no-diff runs -- don't waste tokens
confidence_decay_per_day: 0.005 # facts lose 0.5%/day confidence until refreshed
```

## Firing Contract

- Trigger each entry on its cron expression with the bound research brief (`p03_pt_research_brief.md`).
- Skip a run if its dependencies/quota are unavailable; log and continue.
- Write outputs to the configured destination; never overwrite without versioning.
- On completion, the `curation_nudge` flavors in `p11_cn_research_n01.md` may fire
  (e.g. `stale_fact_detected` if a tracked fact crossed its staleness threshold).

### How to use

```text
ROLE: You are the scheduler firing recurring N01 research.
ACT:
  - Trigger each entry on its cron expression with the bound research brief.
  - Skip a run if its dependencies/quota are unavailable; log and continue.
  - Write outputs to the configured destination; never overwrite without versioning.
OUTPUT: scheduled research deliverables on cadence.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_wf_intelligence]] | related | 0.34 |
| [[p12_ct_research_sprint]] | related | 0.30 |
| [[p11_cn_research_n01]] | downstream | 0.28 |
| [[kc_schedule]] | upstream | 0.24 |
