---
id: p01_kc_mission_token_routing
kind: knowledge_card
pillar: P01
nucleus: N01
title: "MISSION_BENCH: Token-vs-Quality Routing Playbook"
version: 1.0.0
created: "2026-06-15"
author: n01_intelligence
domain: token-economics
quality: null
tags: [routing-playbook, token-economics, mission-bench, frontier, graduation, topology-routing]
tldr: "Single-shot generation: D (Sonnet native) or E (decompose+thin) for most tasks -- 38-52% of Opus-full cost at equal quality. Thin-boot (B) wins T1/T2/T4 vs full-boot (A) but FAILS T3 (orchestration). Full /mission earns its tokens on multi-artifact complex missions: governance gates catch the 30-50% structural failure rate that single-shot misses."
when_to_use: "Selecting topology for a generation task; deciding whether to use full /mission or leaner path; routing decisions after graduation (A.5 thin-boot, autoroute)"
keywords: [topology routing, token efficiency, frontier score, graduation delta, orchestration fail, pattern decompose]
long_tails:
  - "which topology cheapest for knowledge card generation"
  - "does thin-boot hurt quality cex mission benchmark"
  - "when does full mission pay off vs native agent"
  - "orchestration workflow topology routing cex"
  - "graduation B vs A frontier shift evidence"
axioms:
  - "NEVER use topology C (decompose) for T1-class factual/research tasks -- Haiku F6 fails synthesis consistently (q=1.2 both rounds)"
  - "NEVER use topology B or D for T3-class orchestration/workflow tasks -- both fail both rounds consistently (B q=1.6, D q=1.2)"
  - "NEVER use topology E for T4-class abstract/governance tasks -- thin-boot strips pattern vocabulary (q=1.1 both rounds)"
  - "FOR T1 (factual): default to E (frontier 19.60) or D (frontier 17.75); E saves 52% vs A"
  - "FOR T3 (orchestration): default to E if cost matters, else A; avoid B and D"
  - "FOR T4 (abstract/pattern): default to C (decompose, most reliable both rounds q=6.0-6.3)"
  - "IF task class unknown AND budget matters: E (frontier 11.43) beats A (6.28) by 82% at 49% of cost"
  - "ALWAYS run >=2 rounds for T2 (agent/structural) -- variance too high for single-round decisions"
linked_artifacts:
  primary: "p07_bm_mission_bench"
  related:
    - "[[p07_efw_mission_bench]]"
    - "[[p01_kc_stress_test_decompose_results]]"
    - "[[p01_kc_token_optimization_map]]"
density_score: null
related:
  - kc_admin_vocabulary
  - bld_feedback_default
  - bld_feedback_few_shot_example
---

<!-- 8F PIPELINE ===
F1 CONSTRAIN: kind=knowledge_card, pillar=P01, nucleus=N01, max_bytes=8192
F2 BECOME: knowledge-card-builder (12 ISOs), Analytical Envy -- routing recommendation vs >=2 alternatives
F2b SPEAK: intelligence vocabulary loaded
F3 INJECT: p07_bm_mission_bench.md (just produced), mission_bench.tsv (raw data), bm2 topology prior
F3c GROUND: benchmark artifact (2026-06-15, n=40 real cells), eval_framework (2026-06-15)
F4 REASON: 6 sections -- routing table, 1-line answer, /mission value cases, graduation verdict, bm2 build, anti-patterns
F6 PRODUCE: 4,900B, 6 sections, density target 0.88
F7 GOVERN: frontmatter valid, quality=null, ASCII-only
F8 COLLABORATE: saved, compiled, committed [N01][ANALYZE]
=== -->

## Routing Table (task class -> efficient-frontier topology)

Source: p07_bm_mission_bench, 40 real cells (n=8 per topology: 4 tasks x 2 rounds).

| Task Class | Example Kind | Recommended | Alt (cost) | AVOID | Evidence |
|-----------|-------------|-------------|------------|-------|---------|
| Factual/research | knowledge_card (T1) | E decompose+thin | D native | C=2.35 (fails) | E frontier 19.60, D 17.75; C q=1.2 both rounds |
| Structural | agent (T2) | D native | E decompose+thin | A=full (expensive) | D frontier 24.64; run 2 rounds (high variance all topologies) |
| Orchestration | workflow (T3) | E decompose+thin | C decompose | B,D (structural fail) | E frontier 11.72; B q=1.6 and D q=1.2 both rounds |
| Abstract/governance | pattern (T4) | C decompose | B graduated | E (consistently fails) | C frontier 11.75, reliable both rounds; E q=1.1 both rounds |

Qualification: these recommendations apply to single-artifact generation with retries acceptable.
For governed multi-artifact pipelines (full /mission), governance gates change the calculus -- see below.

---

## The 1-Line Answer: "token vs outputs"

**For single-artifact generation: tokens_in is overhead, not quality. D and E deliver equal
quality to A at 38-52% of A's cost. The remaining quality gap is bimodal failure (structural
pass/fail), not a smooth dose-response -- more tokens_in does not prevent structural failures.**

Evidence: A (34,260 tok_in, $0.751) vs D (2,931 tok_in, $0.285): quality 4.80 vs 4.19 (9% gap),
frontier 6.28 vs 15.00 (D wins by 2.4x). The 31,329 additional tokens A sends buys 0.61 quality
points on average -- an extremely low marginal return at $0.466/point.

---

## When Full /mission Earns Its Tokens (vs Leaner Path)

Full /mission (F1->F8 governed, quality gate, retry, compile, commit) earns its token cost when:

| Scenario | Why /mission wins | Leaner path misses |
|---------|------------------|--------------------|
| >=3 artifacts in one wave | Governance gates catch 30-50% structural failures PER ARTIFACT | Single-shot fails silently; N retries compound cost but deliver no governance |
| T3-class orchestration (workflow/pipeline) | Only A or E pass both rounds; F7 retry catches the ~50% fail rate | Single-shot D/B consistently fail T3; no retry mechanism |
| Quality floor required (q>=6.0) | F7 GOVERN retries bring floor to 6.0+; single-shot mean is 3.96-4.80 | Single-shot has 30-50% cells at q=1.1-1.6 (structural fail); no floor guarantee |
| Cross-artifact wikilinks/dependencies | F3 INJECT loads prior artifacts; F7 checks wikilink targets | Single-shot ignores existing corpus; hallucination risk on references |
| Multi-nucleus coordination | F4 REASON plans wave structure; handoffs carry context | Solo nucleus misses cross-pillar dependencies |

Full /mission is WASTE when:
- Single artifact, factual, retries acceptable -> use E or D (frontier 11-20x)
- Proof of concept / draft that goes to manual review before publishing
- Cost-constrained batch where F7 governance floor is not required

---

## Graduation Verdict: A -> B (thin-boot A.5)

| Metric | A (pre-graduation) | B (graduated) | Delta |
|--------|-------------------|--------------|-------|
| Tokens_in | 34,260 | 24,033 | -29.8% (-10,227 tok) |
| Quality | 4.80 | 4.04 | -15.8% |
| Cost | $0.751 | $0.594 | -20.9% |
| Frontier | 6.28 | 6.75 | +7.5% |

Per-task graduation picture:
- T1 factual: B wins frontier (+23%) -- thin-boot retains enough context for factual KC
- T2 structural: B wins frontier (+32%) -- structural artifacts need less context
- T3 orchestration: B LOSES frontier (-58%) -- B q=1.6 consistently; thin-boot strips orchestration context
- T4 abstract: B wins frontier (+34%) -- abstract patterns work with thin context

**Verdict: GRADUATE B as the default for T1/T2/T4. Route T3 (orchestration) tasks to A or E.**
Net gain for mixed batches skewing T1/T2/T4: -21% cost, +7.5% frontier. Thin-boot pays off.

The graduation cost saving is real: 10,227 tokens/spawn. At 100 spawns/day that is 1.02M tokens/day saved.
At Opus pricing that is ~$2.05/day or ~$750/year.

---

## Building on Benchmark-2 Prior Art

[[p01_kc_stress_test_decompose_results]] (benchmark-2, April 2026) found:
- "Decompose NOT cheaper for small heterogeneous batch"
- "Mentor-student cheapest+fastest"
- "Producer-rail fixed self-score (F7 gate absent)"

How MISSION_BENCH updates these findings:

| Benchmark-2 finding | MISSION_BENCH update | Evidence |
|--------------------|---------------------|---------|
| C not cheaper than B | FALSIFIED: C ($0.518) < B ($0.594) | H5 falsified; Haiku F6 cost offsets Opus F1-F4 |
| Decompose not cheaper | Qualified: C cheapest per-quality for T4; E best frontier overall | Task-class dependency revealed |
| Mentor-student cheapest | D (Sonnet native) is cheapest; E is best frontier | D not available in bm2; E adds thin-boot win |
| Producer-rail fixed self-score | F7 gate absence still hits single-shot (1.1-1.6 fail cells) | Confirms bm2: F7 is mandatory, not optional |

Net update: bm2 conclusion "decompose not cheaper" was context-specific to the bm2 task set.
On the MISSION_BENCH task set, C is cheaper AND E (decompose+thin) has best overall frontier.
The routing answer is task-class-dependent, not topology-global.

---

## Anti-Patterns

| Anti-pattern | Cost | Better path |
|-------------|------|------------|
| Using A (full-boot Opus) for factual KC generation | $0.751/artifact vs $0.285-0.365 for equal quality | Route to D or E (frontier 17-20 vs A's 7.96 on T1) |
| Using C (decompose) for knowledge card tasks | Consistently fails (q=1.2 both rounds) | Route T1-class to E or D; never use C for factual synthesis |
| Using B or D for workflow/pipeline builds | Structural fail both rounds | Route T3 to E (frontier 11.72) or A (6.22); B=2.61, D=4.56 |
| Running only 1 round on T2 (agent/structural) | Variance up to 5.7 pts round-to-round; winner can flip | Always run >=2 rounds; governance retry in /mission substitutes |
| Interpreting proxy quality (7.4-8.3) as real | Overestimates by 3-5 points; governance not applied | Use real cex_score runs; proxy biases decisions toward over-confidence |
| Concluding full /mission is not worth it | Single-shot floor is q=3.96-4.80; governed floor is q>=6.0 | Full /mission earns tokens via F7 governance + retry + wikilink validation |

---

## FLANCHOR Validation (N07 consolidation, 2026-06-15)

Real-data follow-up p07_bm_flanchor scored 14 of THIS session's full-8F-lifecycle artifacts
with the SAME cex_score: full-lifecycle quality floors at **8.0-8.4** (vs single-shot 3.96-4.80),
meeting the predicted q>=6.0 governance floor with NO structural collapses. The **single-shot
caveat is RETIRED**: the governance premium is TASK-CLASS-dependent -- SMALL for T1 factual
(+15%, so D/E still win the frontier) but LARGE for T3/T4 (governance erases the single-shot
structural failures -> full /mission justified). All playbook conclusions above HOLD, now evidenced.


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p08_ac_verification | downstream | 0.21 |
| p03_sp_n03_creation_nucleus | downstream | 0.19 |
| [[kc_admin_vocabulary]] | sibling | 0.19 |
| [[bld_feedback_default]] | downstream | 0.18 |
| p11_fb_cost_budget | downstream | 0.18 |
| [[bld_feedback_few_shot_example]] | downstream | 0.18 |
| p06_val_n07 | downstream | 0.18 |
| p07_rt_8f_govern | downstream | 0.18 |
