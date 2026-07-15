---
id: p01_kc_whitepaper_practical_solutions
kind: knowledge_card
pillar: P01
title: "Whitepaper Annex D: Practical Engineering Solutions to the 10 Failure Modes"
version: 1.0.0
quality: null
created: 2026-04-29
updated: 2026-04-29
author: n03_engineering
domain: cex_architecture
tags: [whitepaper, annex, failure-modes, solutions, 8f, evidence]
tldr: "Each of the 10 failure modes from whitepaper Section 1 mapped to a concrete CEXAI tool, command, architecture pattern, and live evidence. Inventive Pride: prove every claim."
related:
  - p01_ctx_whitepaper_technical_deepdive
  - p01_faq_cex_common_questions
  - p01_kc_cex_distribution_model
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_crew, cex_evolve. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.
# Annex D: Practical Engineering Solutions

> **Companion to `docs/WHITEPAPER_CEXAI_CAPABILITIES.md` Section 0.** The whitepaper enumerates ten
> structural failure modes of LLMs in production. This annex maps each to the
> CEXAI tool, command, and architectural pattern that solves it -- with real
> output captured from the running system. Every claim runnable today.

## D.1 Hallucination (Confabulation)
**Problem.** Confident fluent text regardless of accuracy. Intrinsic
(contradicts source) + extrinsic (unsupported) variants both common.
**Solution.** F3c GROUND sub-step + structural binary scoring + 12-pillar typed
knowledge injecting verified KCs before generation.
**Example.**
```bash
python _tools/cex_8f_runner.py "create knowledge card about React hooks" --dry-run
```
F3 INJECT loads builder-KC + domain KCs; F3c GROUND records source path +
retrieval confidence. F7 awards points for citation tables and wikilink
density, not for prose fluency.
**Pattern.** `F3 INJECT -> F3c GROUND -> F7 GOVERN`. P01 substrate, P11 gate.
**Evidence.** `cex_8f_runner.py:412` enforces builder-KC injection at F3.
`cex_score.py:37` rewards structural patterns; fluency gets zero points.

## D.2 Context Rot
**Problem.** Token 10000 has different attention than token 100. Long prompts
silently degrade. "Lost in the middle" is invisible to users.
**Solution.** Mode B decomposition: 1M-context Opus runs F1-F4 (~2K tokens),
then a cheap model runs F6 only on the compiled prompt_package (~3K tokens).
No model ever sees the full 50K-token soup.
**Example.**
```bash
python _tools/cex_8f_runner.py "task" --mode B --model haiku --execute
```
Stage 1 writes `.cex/runtime/packages/pp_<task>.md`. Stage 2 dispatches Haiku
with that one tight prompt. Stage 3 validates with zero-token tools.
**Pattern.** Mode auto-detection by tier: `opus/sonnet/haiku -> A`,
`flash/gpt -> B`. Codified in `.cex/config/nucleus_models.yaml`.
**Evidence.** `cex_router_v2.py:340` `get_mode()` returns `"A"` or `"B"`.
STRESS_TEST_DECOMPOSE: Haiku 9/9 Mode A; flash 7.9/10 Mode B average.

## D.3 Amnesia
**Problem.** Every session starts from zero. Yesterday's analysis is gone.
**Solution.** Every artifact compiled, indexed, and retrieved on demand.
Knowledge persists in the repo; the next conversation hydrates it.
**Example.**
```bash
python _tools/cex_compile.py --all          # .md -> typed .yaml
python _tools/cex_index.py --stats          # SQLite index
python _tools/cex_retriever.py --query "..." # TF-IDF retrieval
```
Live: `Builders: 119 | Total files: 1428 | Avg density: 0.89`. Those 1428 ISOs
are typed, addressable, version-controlled knowledge any nucleus loads at F3.
**Pattern.** P10 ships seven memory kinds -- working_memory, episodic_memory,
[[kc_entity_memory|entity_memory]], knowledge_index, prompt_cache, memory_summary, prospective_memory
-- each with its own consolidation and lifecycle policy.
**Evidence.** `git log` over WHITEPAPER_ANNEXES shows every annex committed as
a typed artifact, not a clipboard paste.

## D.4 Quality Drift
**Problem.** Same prompt, different quality between runs. Provider updates
regress silently.
**Solution.** Mandatory F7 gate runs deterministic `score_structural()` on
every artifact. Quality below 8.0 blocks publication.
**Example.**
```bash
python _tools/cex_score.py --structural artifact.md
python _tools/cex_doctor.py
```
Live: `Result: 119 PASS | 0 WARN | 0 FAIL | Avg density: 0.89 | Oversized: 0`.
The scorer is pure Python on bytes -- cannot drift with model versions because
it does not call models.
**Pattern.** Three-layer scoring (structural / semantic / LLM council) with
binary 10-point gates. Layer 3 fires only when 1+2 sum >= 8.5.
**Evidence.** `cex_score.py:37` -- count-based. Re-running next month returns
the same score. Doctor reports 7 gates per builder, none use LLM inference.

## D.5 Prompt Brittleness
**Problem.** Reorder a sentence, change a synonym, output collapses.
**Solution.** Twelve ISOs per kind decouple identity (BECOME), schema
(CONSTRAIN), examples (GOVERN), output template (PRODUCE). Composed
deterministically, not hand-tuned.
**Example.**
```bash
ls archetypes/builders/knowledge-card-builder/
# bld_architecture, bld_collaboration, bld_config, bld_eval, bld_examples,
# bld_feedback, bld_knowledge, bld_manifest, bld_model, bld_orchestration,
# bld_prompt, bld_schema  (12 files, one per pillar)
```
Same shape for every kind. F2 BECOME loads all 12; F6 PRODUCE composes.
**Pattern.** 1:1 ISO/pillar mapping. A kind builder is a record, not a string.
Re-render is reproducible.
**Evidence.** 119 builders x 12 ISOs = 1428 files. Doctor: `expected 1428`,
match. Adding a kind = `cex_kind_register.py` + `cex_materialize.py`, no
copy-paste.

## D.6 Vendor Lock-in
**Problem.** Prompts tuned for Claude break on GPT. ChatGPT instructions do
not transfer to Gemini.
**Solution.** Same artifacts, same 8F pipeline, four runtimes via boot
polymorphism. The prompt_package is a Markdown file; any model that reads
Markdown can execute Stage 2.
**Example.**
```bash
ls boot/n03*.ps1
# n03.ps1 (Claude) | n03_codex.ps1 (GPT) | n03_gemini.ps1 (Gemini)
# n03_ollama.ps1 (local) | n03_litellm.ps1 (proxy)
```
35 boot scripts (5 runtimes x 7 nuclei). One YAML routes them.
**Pattern.** `cex_router_v2.py` reads `nucleus_models.yaml` fallback chain;
primary fails, next runtime is tried. Same handoff format, same output.
**Evidence.**
```text
$ python _tools/cex_router_v2.py --kind knowledge_card --signature production_kc
backend: opus | fallback: ollama/qwen3:14b + human_review
```
Fallback chain is data, not code. SMOKE_GRID: 6/6 Ollama-only nuclei produce
clean artifacts -- zero proprietary lock-in path.

## D.7 Output Chaos
**Problem.** Free-text output. No schema. No type contracts. Every consumer
writes their own parser.
**Solution.** 125 typed kinds. Every artifact has frontmatter validated against
`_schema.yaml`. Pre-commit hook rejects malformed frontmatter.
**Example.**
```bash
python -c "import json; m=json.load(open('.cex/kinds_meta.json')); print(len(m))"
# 125
python _tools/cex_compile.py path/to/artifact.md   # .md -> typed .yaml
python _tools/cex_doctor.py                        # rejects schema violations
```
Required fields: `id`, `kind`, `pillar`, `version`, `quality` (must be `null`
-- H04 invariant), `tags`.
**Pattern.** P06 (schema) defines `input_schema`, `output_schema`,
`validation_schema`, `interface`, `type_def`, `enum_def`. F1 loads, F7 enforces.
**Evidence.** Doctor: `No frontmatter: 0 files`. Universal H01-H06 (parses, id
matches, kind matches, quality null, required fields, body <= max_bytes) block
publication on violation.

## D.8 Sycophancy
**Problem.** Models agree with users when wrong. RLHF teaches that agreement
correlates with positive feedback. Self-assessment inflates scores.
**Solution.** Hard rule: `quality: null`. Authors do not score their own work.
F7c COUNCIL routes scoring to a separate cross-provider crew.
**Example.**
```bash
python _tools/cex_crew.py run cross_provider_council \  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
    --charter <path> --execute
```
Council is `consensus`, 4 roles, each judge running the same `scoring_rubric`
on a different LLM provider. Output: `consensus_score` (mean) +
`divergence_score` (stddev) + per-judge dissent. Blocked when
`divergence_score > 0.3`; outliers surfaced, not suppressed.
**Pattern.** Producer/scorer separation via `.claude/rules/raci-matrix.md`:
N03 builds, N05 scores, N07 governs. P11 owns the gate.
**Evidence.** `cex_hooks.py` pre-commit rejects non-null `quality:` from the
producing nucleus. `crews list` shows `cross_provider_council [consensus, 4
roles]`. Honesty mechanic is wired, not aspirational.

## D.9 Multi-Agent Coordination Failure
**Problem.** N agents invent N synonyms. Handoffs lose information. System
drifts toward incoherence.
**Solution.** Ubiquitous Language protocol: F2b SPEAK loads a controlled
vocabulary KC at every nucleus boot. The [[p03_pc_cex_universal|prompt_compiler]] at
`N00_genesis/P03_prompt/layers/p03_pc_cex_universal.md` maps any phrase (any
language) to canonical `{kind, pillar, nucleus, verb}` tuples.
**Example.**
```bash
python _tools/cex_intent_resolver.py "make me a landing page"
# kind=landing_page pillar=P05 nucleus=N02 verb=create
python _tools/cex_intent_resolver.py "criar uma landing page"
# kind=landing_page pillar=P05 nucleus=N02 verb=create
```
EN and PT-BR both resolve to the same canonical tuple. Handoffs use the
canonical taxonomy; no agent translates.
**Pattern.** Prompt compiler loaded at F1 by every nucleus. Domain overlays in
`N0X/P01_knowledge/kc_<domain>_vocabulary.md`. Hierarchy in
`.claude/rules/ubiquitous-language.md`.
**Evidence.** 26 composable crews list with `[topology, role count]`. Every
role binds to a typed agent in `capability_registry.json`, not free-form
description.

## D.10 Knowledge Entropy
**Problem.** Best prompts die in chat threads. Architectural decisions lost in
DMs. Nothing compounds.
**Solution.** Every conversation produces typed artifacts that compile into the
searchable repo. AutoResearch (`cex_evolve.py`) closes the loop by improving
low-scoring artifacts on a budget.
**Example.**
```bash
python _tools/cex_evolve.py sweep --target 8.5 --max-rounds 2  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
python _tools/cex_evolve.py auto path/to/artifact.md --budget 50000  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```
Karpathy AutoResearch loop: program.md (strategy) + target.md (artifact) +
score.py (immutable metric). LLM escalates only when deterministic tools fail.
**Pattern.** F8 always saves + compiles + commits + signals. Every artifact
enters the index; every future F3 retrieves it. Knowledge accumulates by
construction.
**Evidence.** `git log` over WHITEPAPER_ANNEXES shows typed annexes
(knowledge_card, context_doc) that future builds will inject as related
artifacts. Mission output IS the next mission's substrate.

## D.11 Cross-Reference Map

| Failure | Tool | Pillar | 8F | WP |
|---------|------|--------|----|----|
| Hallucination | cex_8f_runner + retriever | P01+P11 | F3c+F7 | 1.1 |
| Context rot | cex_8f_runner --mode B | P10+P03 | F1-F4/F6 | 1.2 |
| Amnesia | cex_compile + cex_index | P10 | F8 | 1.3 |
| Quality drift | cex_score + cex_doctor | P11+P07 | F7 | 1.4 |
| Prompt brittleness | 12 ISOs / kind | P02-P12 | F2 | 1.5 |
| Vendor lock-in | cex_router_v2 + boot/*.ps1 | P09+P12 | F5 | 1.6 |
| Output chaos | kinds_meta + cex_compile | P06 | F1 | 1.7 |
| Sycophancy | crew cross_provider_council | P11+P12 | F7c | 1.8 |
| Coordination | prompt_compiler + resolver | P03+P02 | F1+F2b | 1.9 |
| Knowledge entropy | cex_evolve + cex_index | P10+P11 | F8 | 1.10 |

Every cell maps to a runnable command and a real file path.

## Related Artifacts

| Artifact | Relationship |
|----------|--------------|
| p01_ctx_whitepaper_technical_deepdive | upstream (Annex C: diagrams + transcripts) |
| [[p01_faq_cex_common_questions]] | related |
| [[p01_kc_cex_distribution_model]] | related |
