---
id: p01_kc_whitepaper_glossary
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n04
title: "Whitepaper Annex F: Glossary"
version: "1.0.0"
quality: null
tags: [glossary, whitepaper, annex, vocabulary, cexai, knowledge, n04, P01]
domain: knowledge management
type: glossary_collection
status: active
created: "2026-04-29"
updated: "2026-04-29"
author: n04_knowledge
tldr: "Whitepaper annex F: 32 canonical CEXAI terms with one-line definitions and cross-references to whitepaper sections. Compounds the vocabulary already established in docs/glossary.md and docs/vocabulary.md without contradiction."
keywords: [eight_function_pipeline, mode_a, mode_b, prompt_package, kind, builder, iso, pillar, nucleus, sin_lens, gdp, decision_manifest, structural_score, density_target, frontmatter, wikilink, grid, crew, swarm, dispatch, exchange, sovereignty, tf_idf_retriever, prompt_compiler]
density_score: null
related:
  - kc_knowledge_vocabulary
  - p01_kc_concept_graph
  - p01_kc_whitepaper_faq
  - p02_mm_cex_architecture_n04
  - p01_faq_cex_common_questions
  - p01_gl_knowledge_card
  - p01_gl_rag
  - p01_gl_embedding
  - glossary-entry-builder
  - n00_glossary_entry_manifest
---

## Definition

Whitepaper annex F. Concise, alphabetical glossary covering every term used in `docs/WHITEPAPER_CEXAI_CAPABILITIES.md` that a reader new to CEXAI might not recognize. Each entry is one to two lines and links to the whitepaper section where the term first appears. This annex extends -- never contradicts -- the canonical sources `docs/glossary.md` (system-wide vocabulary) and `docs/vocabulary.md` (controlled vocabulary registry).

## Scope

This annex targets readers of the whitepaper specifically. Term selection prioritizes density: if a term appears more than once in the whitepaper or is named in a section header, it is included. Three categories of term are excluded: (1) generic English words, (2) terms already in the reader's prior knowledge of LLM systems, (3) terms exhaustively defined in `docs/glossary.md` (cross-referenced instead of repeated).

## Glossary (Alphabetical)

| Term | One-line Definition | Whitepaper Section |
|------|---------------------|--------------------|
| **8F Pipeline** | Eight-function reasoning protocol (CONSTRAIN -> COLLABORATE) every CEXAI task passes through; not optional middleware. | §3 |
| **Amnesia** | Failure mode: LLMs have no memory across sessions; prior brilliant analysis is gone tomorrow. | §1.3 |
| **Builder** | A 12-file instruction set (one per pillar) at `archetypes/builders/{kind}-builder/` that teaches an LLM to produce one specific kind. | §2.1 |
| **Compounding** | The thesis that intelligence grows multiplicatively when shared: every new artifact enriches every future artifact's context. | §7.7 |
| **Confabulation** | OWASP LLM09:2025 industry term for hallucination; intrinsic (contradicts source) or extrinsic (unsupported claim). | §1.1 |
| **Context Rot** | Performance degradation as context grows; the 10,000th token receives less attention than the 100th. | §1.2 |
| **Crew** | A multi-role team (sequential / hierarchical / consensus topology) producing one coherent deliverable via handoffs. | §6.5 |
| **Decision Manifest** | YAML file in `.cex/runtime/decisions/` recording all subjective choices a user made; nuclei read it to skip re-asking. | §3 (GDP) |
| **Density Target** | Minimum information density (>= 0.85) an artifact must satisfy at F6 PRODUCE; structural metric, not semantic. | §3.1 (F6) |
| **Density Score** | Computed information density of a finished artifact; one of the 10 structural-score checks. | §6.3 |
| **Dispatch** | Multi-runtime spawn mechanism (`Task tool: dispatch`) that launches nuclei across 5 backends with 7 modes. | §6.6 |
| **Exchange** | The X in CEXAI: typed artifacts flow git-natively between nuclei, runtimes, and instances. No platform intermediary. | §2.3 |
| **F1-F8** | The eight functions of the 8F pipeline: CONSTRAIN, BECOME, INJECT, REASON, CALL, PRODUCE, GOVERN, COLLABORATE. | §3.1 |
| **Fractal Principle** | The same 12-pillar structure repeats at every level: genesis archetype, every nucleus, every builder. | §2.2 |
| **Frontmatter** | YAML header at the top of every artifact declaring id, kind, pillar, version, quality, tags, related. Machine-readable contract. | §2.1 |
| **GDP (Guided Decision Protocol)** | Co-pilot mode: user decides WHAT (subjective), nuclei execute HOW (technical) using the decision manifest. | §3 (mode A pre-step) |
| **Grid** | Dispatch mode running up to 6 nuclei in parallel on independent tasks (no inter-nucleus handoffs during the wave). | §6.6 |
| **Hard Gate (H01-H06)** | Six universal validation checks every artifact must pass: YAML valid, id matches filename, kind matches, quality null, required fields, body size. | §2.1 |
| **Hook** | Mandatory boundary check (pre-commit, pre-save, post-save, validate-all) executed by `cex_hooks.py`; not opt-in. | §6.7 |
| **ISO** | One of 12 builder instruction files mapped 1:1 to pillars (e.g., `bld_eval_agent.md` is the P07 ISO of agent-builder). | §2.1, App. B |
| **Kind** | One of 125 artifact types in `.cex/kinds_meta.json`; replaces "type" to avoid programming-language conflicts. | §2.1 |
| **Knowledge Entropy** | Failure mode: best prompts die in chat threads, decisions die in DMs; nothing compounds without typing. | §1.10 |
| **Lost in the Middle** | Documented LLM failure where information mid-prompt is ignored more than information at the start or end. | §1.2 |
| **Mode A** | Monolithic 8F: one capable model (Opus, Sonnet) runs F1 through F8 autonomously. | §3.3 |
| **Mode B** | Decomposed 8F: Stage 1 Opus plans (F1-F4), Stage 2 cheap model generates (F6), Stage 3 tools validate (F7-F8). | §3.3 |
| **Nucleus** | A specialized AI department with sin lens, 12-pillar fractal directory, sub-agents, memory, and quality gates. Not a chatbot. | §4 |
| **Peer Review** | Quality scoring rule: a nucleus never scores its own output; a different nucleus assigns the score to prevent sycophancy. | §2.1, §6.3 |
| **Pillar** | One of 12 taxonomic axes (P01 Knowledge ... P12 Orchestration) every artifact lives in exactly one. | §2.2 |
| **Prompt Brittleness** | Failure mode: tiny wording changes cause large output changes because there is no structural prompt-output contract. | §1.5 |
| **Prompt Compiler** | Universal pattern table (`N00_genesis/P03_prompt/layers/p03_pc_cex_universal.md`) that maps any-language user phrase to `{kind, pillar, nucleus, verb}`. | §3.1 (F1) |
| **Prompt Package** | Mode B Stage 1 output: a portable Markdown file containing builder identity, assembled context, plan, and fill template; runtime-agnostic. | §3.3 |
| **Quality Drift** | Failure mode: same prompt yields different quality across runs (model updates, load, temperature) -- invisible without explicit gates. | §1.4 |
| **RLHF Sycophancy** | Reinforcement-Learning-from-Human-Feedback artifact: models learn agreement correlates with reward; a structural risk. | §1.8 |
| **Runtime Sovereignty** | Property that the same artifacts, pipeline, and gates run unchanged on Claude / GPT / Gemini / Ollama. | §5 |
| **Signal** | JSON file in `.cex/runtime/signals/` written at F8 by a finishing nucleus; tracked by `cex_signal_watch.py` for wave sync. | §6.6 |
| **Sin Lens** | Decision heuristic per nucleus (Envy, Lust, Pride, Gluttony, Wrath, Greed, Sloth) that biases ambiguous choices. | §4 |
| **Structural Score** | A 10-point deterministic quality metric computed by `cex_doctor.py` + `cex_score.py` at zero token cost. | §6.3 |
| **Swarm** | Dispatch mode running N parallel builders of the same kind in worktree-isolated copies; trades coherence for breadth. | §6.6 |
| **Sycophancy** | LLM tendency to agree with users / inflate self-scores; mitigated by peer review and F7c COUNCIL. | §1.8, §6.3 |
| **TF-IDF Retriever** | Zero-token corpus search (`cex_retriever.py`) using term-frequency / inverse-document-frequency; replaces LLM-as-search. | §6.5 |
| **Tier (Model Tier)** | Capability classification: `full_8f`, `f6_generation`, `preflight_aux`, `unsupported`. Auto-detected by `cex_router_v2.py`. | §5.2 |
| **Vendor Lock-in** | Failure mode: prompts tuned for one provider break on another; intelligence is non-portable until typed. | §1.6 |
| **Wikilink** | `[\[artifact_id\]]` reference; resolved by `cex_index.py` and validated by structural score check 7. | §6.3, §6.5 |

## Disambiguation

- **Kind vs Type**: kind is CEXAI taxonomy; type is generic programming. The kind named `type_def` (P06) exists to define custom programming types -- it is itself a kind.
- **Pillar vs Nucleus**: pillars are taxonomic axes (every nucleus exercises all 12). Nuclei are organizational units. Not orthogonal: every artifact has a pillar AND a nucleus.
- **Builder vs ISO**: a builder is the whole 12-file directory; an ISO is one file inside it. The kind `instruction` is sometimes synonymous with ISO.
- **Mode A vs Mode B**: Mode A = one model runs all 8 functions. Mode B = three stages, three executors. Both produce identical artifacts.
- **Crew vs Grid vs Swarm**: crew = N roles, 1 deliverable, handoffs. Grid = N nuclei, N deliverables, parallel. Swarm = N copies of same builder, N variants, isolated.

## Cross-Reference

The canonical system-wide glossary is `docs/glossary.md` (235 lines, 23 entries with the {definition, input, output, owner, example, anti-pattern} schema). The controlled vocabulary registry is `docs/vocabulary.md`. The metaphor-to-industry-term mapping is `_docs/specs/spec_metaphor_dictionary.md`. The 125-kind registry is `.cex/kinds_meta.json`. This annex compresses; it does not replace.

## Related Terms

- See `docs/glossary.md` for full schema entries.
- See `kc_knowledge_vocabulary.md` for N04's controlled vocabulary (21 RAG/knowledge terms).
- See `p01_kc_concept_graph.md` for term-relationship structure.
- See `p01_kc_whitepaper_faq.md` for the companion FAQ annex.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_knowledge_vocabulary]] | upstream | 0.55 |
| [[p01_kc_whitepaper_faq]] | sibling | 0.50 |
| [[p01_kc_concept_graph]] | sibling | 0.45 |
| [[p02_mm_cex_architecture_n04]] | related | 0.40 |
| [[p01_faq_cex_common_questions]] | related | 0.35 |
