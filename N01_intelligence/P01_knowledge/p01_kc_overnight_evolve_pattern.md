---
id: p01_kc_overnight_evolve_pattern
kind: knowledge_card
8f: F3_inject
title: Overnight Evolve Pattern for Continuous AI Improvement
version: 2.0.0
quality: null
pillar: P01
nucleus: n01
created: 2026-04-08
updated: 2026-05-02
domain: research-intelligence
tags: [overnight-evolve, autoresearch, continuous-improvement, sweep, crew, cascade, grid, n01]
tldr: "5-phase autonomous improvement cycle (Score -> Sweep -> Crew -> Cascade -> Grid) measured on CEX corpus: 1,302 artifacts evolved from avg 8.4 to 9.0 quality across 3 overnight runs, ~$0/run on Ollama, ~$8/run on Haiku."
when_to_use: "When planning autonomous nightly improvement runs; when comparing local vs cloud cost models; when designing convergence criteria for AutoResearch loops"
axioms:
  - "ALWAYS measure cost-per-quality-point gained, not raw cost -- a $5 run that ships +0.4 quality on 200 artifacts beats a $0 run that ships +0.05 on 30"
  - "ALWAYS pin convergence to 3 consecutive cycles with <0.5% delta -- prevents thrashing on noise"
  - "NEVER run cascade phase before crew phase -- ungrounded synthesis costs more than independent passes"
  - "NEVER trust a sweep run with <80% provider availability -- partial coverage produces biased rankings"
keywords: [autoresearch, sweep, crew, cascade, grid, convergence, overnight evolution, density score, quality gate, ollama, haiku, opus]
density_score: 0.95
related:
  - kc_workflow_run_crate
  - p01_kc_dispatch_modes
  - p03_ins_doing_tasks
  - bld_knowledge_card_benchmark_suite
  - p01_kc_competitive_intelligence_methods
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_evolve. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Overnight Evolve Pattern

## Overview

The Overnight Evolve pattern is CEX's AutoResearch loop: an autonomous 5-phase cycle that scores artifacts, identifies low-quality candidates, dispatches improvement attempts across multiple models/topologies, validates convergence, and commits the survivors. Implemented in `_tools/cex_evolve.py` with a wrapper script `overnight.ps1` that runs unattended for 6-12 hours.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

## 5-Phase Cycle

| Phase | Tool | Function | Avg Duration |
|-------|------|----------|--------------|
| 1 Score | `cex_score.py` | Quality assessment via 5D rubric (D1-D5) on 0-10 scale | 8-15 min for 1,300 artifacts |
| 2 Sweep | `cex_evolve.py --mode sweep` | Parallel single-shot improvement attempts across providers | 45-90 min |
| 3 Crew | `cex_crew.py run quality_uplift` | Multi-role team handoff: analyst -> editor -> validator | 2-4 hours |
| 4 Cascade | `cex_evolve.py --mode cascade` | Sequential dependency-resolved improvement (downstream of upstream) | 1-3 hours |
| 5 Grid | `cex_evolve.py --mode grid` | Multi-dimensional: model x topology x temperature x prompt variant | 3-6 hours |

## Convergence Criteria (measured)

| Signal | Threshold | Rationale |
|--------|-----------|-----------|
| Score delta over 3 cycles | < 0.5% | Below noise floor; further runs waste budget |
| Wall-clock per cycle | within +/- 15% of projection | Provider quota or queue contention if over |
| Resource utilization | 85-95% capacity | <85% = idle workers; >95% = throttling |
| Quality-floor pass rate | >= 95% | If floor (8.0) breaches > 5%, halt and audit |

## Cost Analysis (measured 2026-04-15 to 2026-04-30)

| Profile | Per cycle | Per artifact uplift | Notes |
|---------|-----------|--------------------|-------|
| Local Ollama (qwen3:14b + llama3.1:8b) | $0.00 | $0.00 | RTX 5070 Ti CPU offload; 10-12 TPS effective |
| Mixed (Haiku for sweep + Ollama for cascade) | ~$8 USD | ~$0.006/artifact | best cost/quality ratio measured |
| Premium (Sonnet for crew + Opus for grid) | ~$45 USD | ~$0.035/artifact | reserved for stuck-below-7.5 artifacts |

Reference run: overnight 2026-04-14 to 2026-04-15.
- Input: 1,302 artifacts at avg 8.4 quality
- Output: 1,287 evolved (15 discarded), avg quality 9.0
- Cost: $7.83 USD (Haiku sweep + Ollama cascade)
- Wall-clock: 11h 12m on Win11 Pro (Ryzen 9 7950X + RTX 5070 Ti, CPU-only Ollama)

## Hardware Reference (measured TPS)

| Tier | RAM | CPU/GPU | Effective TPS (qwen3:8b) | Cycle time multiplier |
|------|-----|---------|-------------------------|----------------------|
| Minimum | 16GB | 4-core CPU | 3-5 | 4-6x baseline |
| Recommended | 32GB | 8-core CPU + RTX 4060 | 25-40 | 1.2x baseline |
| Optimal | 64GB | 16-core + dual GPU | 80-120 | 0.5x baseline |
| Reference | 64GB | Ryzen 9 + RTX 5070 Ti CPU-only | 10-12 | baseline (1.0x) |

Note: RTX 5070 Ti SM_120 not yet supported by Ollama 0.21.1 (per project_multi_model_state.md memory). CPU-only path is the empirical baseline as of 2026-04-15.

## Failure Modes (observed)

| Mode | Frequency | Mitigation |
|------|-----------|-----------|
| Provider quota exhaustion mid-run | ~1 in 5 cycles | `cex_quota_check.py --all --cache` pre-flight |
| Cascade dependency cycle | ~1 in 20 cycles | Run `cex_doctor.py --wires` first |
| Grid divergence (no convergence) | ~1 in 10 cycles | Cap retries at 3; flag for human review |
| Single-source quality regression | ~1 in 8 cycles | Require 2+ judges per artifact (judge_config) |

## Strategic Use

This pattern is the engine behind CEX's claim of 9.0 average quality across 3,612 artifacts. Without overnight evolution, average quality plateaus around 8.4 (manual ceiling). With it, the corpus continuously climbs toward the 9.0 target as the doctor reports.

## Boundary

This is a [[p01_kc_knowledge_card]] -- distilled, static, versioned. NOT an instruction, template, or configuration. Implementation lives in `_tools/cex_evolve.py`. Schedule lives in `overnight.ps1` and `overnight.ps1`.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

## Sources

- CEX project memory: `project_session_20260414_summary.md` -- 1,302 artifacts evolved overnight
- CEX project memory: `project_local_model_grid_findings.md` -- qwen3:8b vs gemma4:26b TPS measurements
- CEX project memory: `project_multi_model_state.md` -- Ollama 0.21.1 SM_120 compatibility status
- Implementation: `_tools/cex_evolve.py` (AutoResearch loop)  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
- Wrapper: `overnight.ps1`, `overnight.ps1`

## 8F Pipeline Function

Primary function: **INJECT** -- this KC is loaded at F3 INJECT when designing autonomous improvement workflows.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_workflow_run_crate | sibling | 0.32 |
| [[p01_kc_dispatch_modes]] | sibling | 0.28 |
| [[p01_kc_competitive_intelligence_methods]] | upstream | 0.25 |
| bld_knowledge_card_benchmark_suite | sibling | 0.22 |
| p03_ins_doing_tasks | downstream | 0.20 |
