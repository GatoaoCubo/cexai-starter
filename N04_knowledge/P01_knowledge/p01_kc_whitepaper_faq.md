---
id: p01_kc_whitepaper_faq
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n04
title: "Whitepaper Annex F: FAQ"
version: "1.0.0"
quality: null
tags: [faq, whitepaper, annex, vocabulary, cexai, n04, P01, knowledge]
domain: knowledge management
type: faq_collection
status: active
created: "2026-04-29"
updated: "2026-04-29"
author: n04_knowledge
tldr: "Whitepaper annex F: 16 questions an engineer reading the CEXAI whitepaper would ask, with answers grounded in concrete file paths, tools, and stress-test results. Compounds with the 8 questions in docs/faq.md without overlap."
keywords: [langchain_comparison, ollama_offline, runtime_switching, learning_curve, performance_overhead, exchange_format, mode_b, prompt_package, custom_kinds, structural_score, contributing, peer_review]
density_score: null
related:
  - p01_kc_whitepaper_glossary
  - kc_knowledge_vocabulary
  - p01_kc_concept_graph
  - faq-entry-builder
  - p02_mm_cex_architecture_n04
  - contributor_guide_cex
  - changelog_cex_v1
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_crew. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

## Definition

Whitepaper annex F. Sixteen questions an engineer reading `docs/WHITEPAPER_CEXAI_CAPABILITIES.md` is most likely to ask after the first pass. Each answer cites a concrete file path, tool, or whitepaper section so the reader can verify the claim. This annex is additive to `docs/faq.md` (8 questions, beginner-friendly) and `N04_knowledge/P01_knowledge/faq_entry_cex_common_questions.md` (12 questions, contributor onboarding) -- it does not duplicate them.

## Architecture & Comparison

### Q1. How is CEXAI different from LangChain?

LangChain is an orchestration framework: it routes and chains LLM calls. CEXAI is a typed knowledge system: it governs what those calls produce. The whitepaper's gap table (§1.11) makes this explicit: LangChain has opt-in callbacks, no typed knowledge taxonomy, no cross-runtime artifact portability, and frequent breaking changes. CEXAI ships 125 kinds with mandatory schema validation, runtime-agnostic artifacts, and a stable convention-over-configuration API. They are complementary -- you can run LangChain inside an `agent` artifact -- not competitors.

### Q2. How does CEXAI compare to CrewAI / AutoGen / DSPy?

Same category mismatch. CrewAI orchestrates roles, AutoGen orchestrates conversations, DSPy optimizes prompts. None types or persists the produced knowledge. The CEXAI `crew_template` kind (P12) is the equivalent of CrewAI's crew abstraction; the difference is that every role's output is a typed, validated, exchangeable artifact governed by the 8F pipeline. See `archetypes/builders/crew-template-builder/` and `_tools/cex_crew.py`.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

### Q3. Can I use CEXAI on top of an existing LLM provider?

Yes. CEXAI is provider-agnostic. Edit `.cex/config/nucleus_models.yaml` to point each nucleus at any combination of Claude, GPT/Codex, Gemini, or Ollama. The 8F pipeline, builder ISOs, and structural-score checks are identical regardless of provider. Switching providers is a one-line config change, not a rewrite. See whitepaper §5.1.

### Q4. Does CEXAI work offline / air-gapped?

Yes, in two ways. (1) The complete free-tier setup uses Ollama locally -- no API keys, no internet, Mode B with pre-compiled prompt packages. (2) The 88 CLI tools (`_tools/cex_*.py`) are pure Python with no network calls -- routing, validation, retrieval, scoring, compilation all run offline. Whitepaper §5.3 documents the free profile; stress test data (§7.6) shows `llama3.1:8b` is the currently passing local model.

## Pipeline & Performance

### Q5. What is the actual performance overhead of running 8F on every task?

Token-wise, 8F reduces overhead vs raw LLM use. The whitepaper §6.4 gives the budget: producing 30 artifacts costs ~500K tokens raw, ~300K Mode A (40% reduction), ~150K Mode B (70% reduction). The savings come from offloading routing, validation, retrieval, and scoring to deterministic Python (zero tokens). Wall-clock overhead is dominated by the LLM call itself (F4 + F6); the other six functions are sub-second tool calls.

### Q6. How does Mode B actually work end-to-end?

Three stages bridged by the `prompt_package` kind (§3.3). Stage 1: Opus or Sonnet runs F1-F4, produces a `prompt_package` Markdown file at `.cex/runtime/packages/`. Stage 2: a cheap model (Haiku, Gemini Flash, llama3.1:8b) reads the prompt_package and runs F6 only -- no reasoning required, just fill the template. Stage 3: tools (`cex_doctor.py`, `cex_compile.py`) run F7-F8 with zero LLM cost. Run with `python _tools/cex_8f_runner.py "intent" --mode B --model haiku --execute`.

### Q7. How does quality scoring work without LLM calls?

The structural score (§6.3) is 10 deterministic Python checks: frontmatter parses, id matches filename, kind matches target, quality field is null, required fields present, body within byte cap, wikilinks resolve, density >= 0.85, section structure matches builder template, no undeclared vocabulary terms. These catch ~80% of quality defects. Semantic quality (creative coherence, factual accuracy) is assigned by peer review -- a different nucleus scores than the one that produced. See `_tools/cex_doctor.py` and `_tools/cex_score.py`.

### Q8. What if I disagree with a quality score?

Two recourses. (1) Trigger F7c COUNCIL -- multi-provider review where Claude, Gemini, and Ollama independently score; if `divergence_score > 0.3` the score is flagged and rationales are surfaced (`docs/glossary.md` Divergence Score entry, `cex_council.py`). (2) File a `decision_record` (kind, P08) with the dispute, add a `learning_record` (P10) capturing the case; future scoring runs include the new precedent. The system is auditable, not absolute.

## Adoption & Customization

### Q9. How long does it take to get started?

<!-- [N02 narrative sweep 2026-07-14, DP_B]: the engine repo is closed; a reader
     of a distilled tenant repo already has step 1. Removed the "clone the
     engine" instruction. -->
If you're reading this from a distilled tenant repo (like this one), you
already have step 1. Two commands, minutes (whitepaper §7.8): `pip install -r
requirements.txt`, `python _tools/cex_8f_runner.py "create knowledge card
about <topic>" --execute`. The second command runs the full pipeline and
produces a typed, governed artifact. Brand identity is already set for this
tenant -- verify with `python _tools/cex_bootstrap.py --check`.

### Q10. What is the smallest useful CEXAI setup?

One nucleus, one kind, one builder, one pillar. Concretely: clone the repo, keep only `N00_genesis/`, `N03_engineering/`, `archetypes/builders/knowledge_card-builder/`, and `_tools/cex_doctor.py` + `_tools/cex_compile.py`. You lose multi-runtime, crews, swarms, and 6 nuclei -- but you keep the 8F pipeline and zero-token validation. This minimum is ~50MB, single-machine, no API keys (Ollama Mode B). The full repo is ~300MB.

### Q11. What happens if I do not want all 125 kinds?

Nothing breaks. Kinds are loaded lazily by `cex_8f_runner.py` from `.cex/kinds_meta.json`. Unused kinds cost zero runtime. To remove a kind: delete its row from `kinds_meta.json`, delete `archetypes/builders/{kind}-builder/`, delete `N00_genesis/P01_knowledge/library/kind/kc_{kind}.md`. The system continues to work for the remaining kinds.

### Q12. Can I add my own artifact types (custom kinds)?

Yes. The process is documented in `docs/faq.md` Q6 and the contributor guide. Six steps: register in `.cex/kinds_meta.json`, create the knowledge card at `N00_genesis/P01_knowledge/library/kind/`, create the 12-file builder at `archetypes/builders/{kind}-builder/`, add the sub-agent at `.claude/agents/{kind}-builder.md`, add prompt-compiler entries at `N00_genesis/P03_prompt/layers/p03_pc_cex_universal.md`, run `python _tools/cex_doctor.py` to verify wiring. The new-kind registry checklist is in `feedback_new_kind_registry_addendum.md`.

### Q13. Can I add a new nucleus (vertical specialization)?

Yes. Whitepaper §7.3 lists candidate verticals (N08 Healthcare, N09 FinTech, N10 EdTech, N11 Legal, N12 GovTech). The complete bootstrap process is in `.claude/rules/new-nucleus-bootstrap.md`: clone N00 structure, assign a sin lens, create 9 required assets (rule file, nucleus definition, agent card, vocabulary KC, component map, system prompt, two boot scripts, permissions JSON), register routing in `nucleus_models.yaml`. The architecture scales by instantiation, not modification.

## Multi-Runtime & Exchange

### Q14. How does multi-runtime actually work in practice?

One config, four runtimes. `.cex/config/nucleus_models.yaml` declares per-nucleus primary model and fallback chain. `_tools/cex_router_v2.py` reads it at dispatch time, picks Mode A or Mode B by tier (§5.2), invokes the matching boot script (`boot/n0X.ps1` for Claude, `boot/n0X_gemini.ps1` for Gemini, `boot/n0X_codex.ps1` for Codex, `boot/n0X_ollama.ps1` for Ollama, `boot/n0X_litellm.ps1` for the LiteLLM proxy). The 8F pipeline, the builders, the gates, the artifacts, and the wikilink graph are identical across all four. Stress test results (§7.6): Claude/Sonnet/Haiku pass full 8F, Gemini Flash passes Mode B at 7.9 avg, llama3.1:8b passes Mode B at 7/10 across all 9 test tasks.

### Q15. How does the Exchange format work for sharing?

The Exchange is git-native. Every artifact carries its identity in YAML frontmatter (`id`, `kind`, `pillar`, `quality`, `version`, `tags`, `related`); every artifact compiles to portable `.yaml`; every CEXAI instance has the same kind registry. To share: git push your nucleus / kind / artifact; the recipient `git pull`, runs `python _tools/cex_doctor.py`, and the artifact validates. Brand config, secrets, and entity memory stay private (gitignored). N00 Genesis, vertical nuclei, knowledge cards, and builders are the public exchange units. See `docs/glossary.md` Exchange Protocol entry.

### Q16. Can I use just the tools without the full system?

Yes. The 88 tools at `_tools/cex_*.py` are independent Python scripts with documented CLIs. Pick any subset: `cex_doctor.py` validates artifacts, `cex_compile.py` compiles `.md` to `.yaml`, `cex_retriever.py` does TF-IDF search, `cex_intent_resolver.py` maps phrases to kind/pillar tuples, `cex_score.py` computes structural scores. They expect the artifact format (frontmatter + body) but do not require the full nucleus directory tree, the runtime configuration, or the dispatch scripts. The whitepaper §6 lists the principal tools.

## Cross-Reference

- `docs/faq.md` -- 8 beginner questions, public-facing.
- `N04_knowledge/P01_knowledge/faq_entry_cex_common_questions.md` -- 12 questions for new contributors.
- `docs/WHITEPAPER_CEXAI_CAPABILITIES.md` -- the source document this annex serves.
- `kc_whitepaper_glossary.md` -- companion glossary annex (sibling, same `kc_whitepaper_*` family).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_whitepaper_glossary]] | sibling | 0.55 |
| [[kc_knowledge_vocabulary]] | related | 0.40 |
| [[p02_mm_cex_architecture_n04]] | related | 0.40 |
| contributor_guide_cex | related | 0.35 |
