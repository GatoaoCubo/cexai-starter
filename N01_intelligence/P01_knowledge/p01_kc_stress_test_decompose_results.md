---
id: p01_kc_stress_test_decompose_results
kind: knowledge_card
pillar: P01
title: "STRESS_TEST_DECOMPOSE: Multi-Runtime 8F Capability Matrix"
version: "3.0.0"
created: "2026-04-28"
updated: "2026-04-29"
author: "knowledge-card-builder"
domain: multi-runtime AI evaluation
quality: null
tags: [stress-test, 8f-decompose, routing, benchmark, multi-runtime, capability-matrix]
tldr: "78 runs across 8 model configs. Opus+Sonnet: 10/10 Mode A. Haiku: 9/10 Mode A/B. Gemini flash-lite: 6.3 Mode A -> 7.9 Mode B (+1.7 lift). Codex GPT-4.1: 9.5 Mode B (code tasks). Ollama: 7/10 Mode B all 9 tasks. qwen3:14b and cex-student: 0/10 Mode B (FAIL). 8F decomposition is the universal lift mechanism for non-Claude runtimes."
when_to_use: "Selecting LLM tier and mode for a CEX task; routing decisions in nucleus_models.yaml; validating 8F pipeline coverage per model"
keywords: [8f pipeline model, stress test decompose, haiku mode A, ollama mode B, gemini mode B, codex mode B, routing truth table]
long_tails:
  - "which Claude model handles full 8F autonomously"
  - "ollama llama3 8b stress test results cex pipeline"
  - "gemini flash lite 8F decomposed mode B results"
  - "codex gpt-4.1 code task routing benchmark"
  - "8F decomposition lift across runtimes"
axioms:
  - "ALWAYS use Mode A for Claude models -- decomposition adds zero lift and extra complexity"
  - "IF runtime is Gemini THEN use Mode B -- decomposition lifts avg +1.7 points (6.3 -> 7.9)"
  - "IF task is code-focused (T05/T07/T08) AND budget allows THEN route to Codex Mode B -- 10/10 on code tasks"
  - "IF runtime is Ollama THEN use Mode B with canonical handoff format -- 9/9 tasks pass at 7/10"
  - "ALWAYS include 'task: dispatch' + '# Task for N0X' anchors in any handoff -- fixes Haiku pass rate from 2/9 to 9/9"
  - "NEVER send T09 (cross-ref audit) to free-tier models -- requires cloud model reasoning depth"
  - "NEVER use PowerShell && in handoff instructions -- Gemini runs in PS context where && is invalid"
linked_artifacts:
  primary: spec_stress_test_decompose
  related: [spec_8f_decompose, p02_fc_cex_model_fallback, p08_adr_runtime_coverage_n05, p01_kc_claude_model_capabilities_2026]
density_score: 0.93
data_source: "stress_results.tsv (78 rows) + session_20260428_v1_5 MEMORY"
related:
  - p02_fc_cex_model_fallback
  - p08_adr_runtime_coverage_n05
  - p01_kc_claude_model_capabilities_2026
  - p01_kc_ollama_deployment_guide
  - p01_kc_spawn_config
  - p01_kc_token_efficiency_gap_map
  - p02_fb_model_cascade
  - p02_mc_claude_opus_4
---

# STRESS_TEST_DECOMPOSE: Multi-Runtime 8F Capability Matrix

## Executive Summary

78 runs across 8 model configs x 3 modes. Opus and Sonnet achieve 10/10 on all 9 tasks in Mode A (full autonomy). Haiku achieves 9/10 in Mode A -- prior 2/6 failure was a handoff format bug. Gemini flash-lite: Mode A avg 6.3, Mode B avg 7.9 (+1.7 lift from 8F decomposition). Codex GPT-4.1: 9.5 avg on code-focused tasks in Mode B (10/10 on pipeline, bugloop, optimizer). Ollama (llama3.1:8b): 7/10 on all 9 tasks in Mode B. qwen3:14b: 0/10 on 3 tasks Mode B (600s timeouts). cex-student (fine-tuned): 0/10 on T01 Mode B (not yet viable). Critical finding: **8F decomposition is the universal lift mechanism** -- every non-Claude runtime benefits from Opus pre-compiling the thinking phases, but model quality sets a hard floor.

## Spec Table

| Dimension | Value |
|-----------|-------|
| Experiment | STRESS_TEST_DECOMPOSE (8F Decompose Mission) |
| Total runs | 78 / 87 planned (90% coverage) |
| Task types | 9 (T01-T09: KC, system prompt, agent, rubric, pipeline, workflow, fix, score-evolve, audit) |
| Modes tested | A=full autonomy, B=decomposed (Opus F1-F4 + model F6 + tools F7-F8), C=raw prompt only |
| Models tested | Opus, Sonnet, Haiku (Claude); llama3.1:8b (Ollama); gemini-2.5-flash-lite (Gemini); codex-gpt-4.1 (Codex); qwen3:14b (Ollama); cex-student (fine-tuned) |
| F-stage count | 8 (F1 CONSTRAIN through F8 COLLABORATE) |
| Pass threshold | 7/10 publish, 8/10 pool, 9.5/10 golden |
| Batch runners | run_gemini_mode_a.sh, run_gemini_mode_b.sh, run_codex_mode_b.sh |

## Patterns (What Works)

| Model | Mode | Tasks Pass | Avg Score | F-stages | Avg Time |
|-------|------|-----------|-----------|----------|----------|
| Opus | A | 9/9 | 10.0 | 100% (72/72) | <5s |
| Sonnet | A | 9/9 | 10.0 | 100% (72/72) | <5s |
| Haiku | A | 9/9 | 9.0 | 96% (69/72) | 165s |
| Haiku | B | 9/9 | 9.0 | 100% (72/72) | 82s |
| Gemini flash-lite | A | 2/6 | 6.3 | 54% (26/48) | 81s |
| Gemini flash-lite | B | 8/9 | 7.9* | 92% (66/72) | 89s |
| Codex GPT-4.1 | B | 4/4 | 9.5 | 100% (32/32) | 129s |
| Ollama llama3.1:8b | B | 9/9 | 7.0 | 100% (72/72) | 256s** |
| Ollama llama3.1:8b | C | 1/6 | 1.0 | 33% (16/48) | 267s |
| qwen3:14b | B | 0/3 | 0.0 | 50% (12/24) | 600s |
| cex-student (FT) | B | 0/1 | 0.0 | 50% (4/8) | 601s |

*Gemini B avg excludes T09 TIMEOUT (8/9 tasks = 7.9; including T09 = 7.0)
**Ollama times vary: T01=574s via 8f_runner, T02=1643s, T03-T09=9-22s via batch runner
***qwen3:14b and cex-student hit 600s timeout on all attempted tasks (F5+ stages never reached)

- **8F decomposition is universal lift**: Gemini +1.7 (6.3->7.9), Ollama +6.0 (1.0->7.0), Codex B 9.5 with no Mode A baseline needed
- **Haiku production-viable**: 9/10 across ALL task types in Mode A; ~10x cheaper than Opus
- **Codex excels at code tasks**: T05 (pipeline) 10, T07 (bugloop) 10, T08 (optimizer) 10 -- route code-focused work here
- **Canonical handoff format**: `task: dispatch` + `# Task for N0X` anchors fixed Haiku 2/9 -> 9/9
- **Gemini no longer hanging**: flash-lite 2026-04-28 completes in 31-180s (prior: 25min+ hang on 2026-04-15)

## 8F Decomposition Lift Analysis

| Model | Mode A Avg | Mode B Avg | Delta | Lift Source |
|-------|-----------|-----------|-------|-------------|
| Opus | 10.0 | N/A | 0 | No lift needed -- already perfect |
| Sonnet | 10.0 | N/A | 0 | No lift needed -- already perfect |
| Haiku | 9.0 | 9.0 | 0 | No lift -- already high; B fixes F2 gaps |
| Gemini flash-lite | 6.3 | 7.9 | +1.7 | F2/F4 pre-compiled; F7/F8 tooling applied |
| Ollama llama3.1:8b | N/A | 7.0 vs C=1.0 | +6.0 | Mode C nearly total failure; B rescues all 9 tasks |
| Codex GPT-4.1 | N/A | 9.5 | N/A | Code-focused subset only; no A baseline |
| qwen3:14b | N/A | 0.0 | N/A | 600s timeout; thinking-budget exhaustion prevents F5+ |
| cex-student (FT) | N/A | 0.0 | N/A | Fine-tuned model not yet viable for 8F tasks |

## Anti-Patterns (What Fails)

| Failure | Root Cause | Impact | Mitigation |
|---------|-----------|--------|------------|
| Haiku old 2/6 result | Non-standard handoff format | False routing to higher tier | Use canonical handoff anchors |
| Gemini T09 TIMEOUT | Cross-ref audit exceeds model reasoning depth | 0/10, 301s timeout | Route T09 to cloud models only |
| Gemini Mode A F7 fail | Cannot self-score without structural tools | F7=0 on 5/6 tasks | Mode B pre-compiles F7 gates |
| Ollama Mode C | Raw prompt insufficient for 8F compliance | 5/6 tasks score 0 | Always use Mode B for Ollama |
| PowerShell && syntax | Gemini runs in PS context; && invalid | Handoff step 3 fails silently | Split into separate commands |
| Early process kill | Batch runner sleep 10 too short | Kills before compile+commit | 120s commit-wait loop with git log polling |
| qwen3:14b timeout | Thinking-budget loop exhausts 600s | F5+ never reached; 0/3 tasks | BLOCKED: qwen3 unsuitable for 8F |
| cex-student timeout | Fine-tuned model lacks reasoning depth | F5+ never reached; 0/1 tasks | DEFERRED: needs better base model or training data |

## Application -- Routing Truth Table

| Task Type | Opus A | Sonnet A | Haiku A | Haiku B | Gemini A | Gemini B | Codex B | Ollama B | Ollama C |
|-----------|--------|----------|---------|---------|----------|----------|---------|----------|----------|
| T01 Simple KC | 10 | 10 | 9 | 9 | 7 | 8 | 8 | 7 | 6 |
| T02 System prompt | 10 | 10 | 9 | 9 | 6 | 8 | -- | 7 | 0 |
| T03 Agent scaffold | 10 | 10 | 9 | 9 | 7 | 9 | -- | 7 | 0 |
| T04 Scoring rubric | 10 | 10 | 9 | 9 | 6 | 8 | -- | 7 | 0 |
| T05 Pipeline template | 10 | 10 | 9 | 9 | 6 | 8 | 10 | 7 | 0 |
| T06 Full workflow | 10 | 10 | 9 | 9 | 6 | 7 | -- | 7 | 0 |
| T07 Fix broken | 10 | 10 | 9 | 9 | -- | 7 | 10 | 7 | -- |
| T08 Score evolve | 10 | 10 | 9 | 9 | -- | 8 | 10 | 7 | -- |
| T09 Cross-ref audit | 10 | 10 | 9 | 9 | -- | TIMEOUT | -- | 7 | -- |

Legend: score/10. -- = not tested. TIMEOUT = exceeded 300s limit.

**Routing decision matrix (updated):**
- **Quality-first**: Opus or Sonnet Mode A (10/10, identical results)
- **Cost-first**: Haiku Mode A for all tasks (9/10, ~10x cheaper than Opus)
- **Code tasks on budget**: Codex GPT-4.1 Mode B for T05/T07/T08 (9.5 avg, free tier)
- **Free tier general**: Gemini Mode B for T01-T08 (7.9 avg, free); skip T09
- **Free tier local**: Ollama Mode B for all 9 tasks (7.0, requires CPU time)
- **Never**: Gemini Mode A (6.3 avg, wastes free-tier quota); Ollama Mode C (1.0 avg); qwen3:14b (timeout); cex-student (not viable)

## Known Issues (Batch Runner)

| Issue | Script | Fix Applied |
|-------|--------|-------------|
| PowerShell && not valid | run_gemini_mode_b.sh handoff step 3 | Split into separate git add + git commit commands |
| Early kill (sleep 10) | run_gemini_mode_a.sh | Fixed in Mode B runners: 120s commit-wait loop |
| Background & redundancy | bash script.sh & with run_in_background | Remove trailing & when using tool backgrounding |
| gitignored experiment dir | .cex/experiments/ | Use git add -f to stage |

## References

- [\[spec_stress_test_decompose\]] -- experiment spec + methodology (87 planned runs)
- [\[spec_8f_decompose\]] -- 8F decomposition pipeline design
- p02_fc_cex_model_fallback -- fallback chain config
- p08_adr_runtime_coverage_n05 -- routing architecture ADR
- p01_kc_claude_model_capabilities_2026 -- model capability reference
- Source: `.cex/experiments/stress_decompose/results/stress_results.tsv` (78 data rows)
- Batch runners: `run_gemini_mode_a.sh`, `run_gemini_mode_b.sh`, `run_codex_mode_b.sh`
- Related benchmark: [[p01_kc_benchmark_tool_vs_llm]]

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p02_fc_cex_model_fallback | downstream | 0.36 |
| p08_adr_runtime_coverage_n05 | downstream | 0.30 |
| p01_kc_claude_model_capabilities_2026 | sibling | 0.28 |
| [[p01_kc_ollama_deployment_guide]] | sibling | 0.28 |
| [[p01_kc_spawn_config]] | sibling | 0.26 |
| p01_kc_token_efficiency_gap_map | sibling | 0.26 |
| p02_fb_model_cascade | downstream | 0.25 |
