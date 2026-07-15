---
quality: null
id: kc_lens_technical
kind: knowledge_card
8f: F3_inject
kc_type: meta_kc
pillar: P01
nucleus: n04
version: 1.1.0
created: "2026-04-21"
updated: "2026-05-02"
author: n04_knowledge
title: "Lens: Technical -- CEX as Multi-Agent Engineering Infrastructure"
domain: didactic_engine
subdomain: lens_system
tags: [lens, technical, DDD, CI-CD, agents, developer]
tldr: "Direct mapping of CEX concepts to industry-standard engineering terms. No metaphors -- exact equivalents from DDD, CI/CD, MLOps, multi-agent frameworks. For developers who want the real terminology."
keywords: [multi-agent orchestration framework, bounded contexts, autonomous agent, workflow orchestrator, schema type, code generator, config file, artifact, configuration wizard, loss function, dspy compilation, bm25, hybrid retrieval]
density_score: 0.91
related:
  - vocabulary_cex_rosetta
  - n00_mentor_context
  - p02_mm_cex_architecture_n04
  - p06_td_cex_artifact_type_n03
  - p01_faq_cex_common_questions
  - kc_crew_template
  - p01_kc_quality_gate
  - p01_kc_embedding_config
  - p01_kc_agent
---

# Lens: Technical

> Unlike the other lenses (factory, city, biology, game), this lens maps CEX concepts directly to industry-standard equivalents. No analogy -- the actual terms.

## Core Mapping

| CEX Concept | Technical Equivalent |
|-------------|---------------------|
| CEX system | Multi-agent orchestration framework (300 schemas, 12 bounded contexts, 8 agents) |
| 8F pipeline | 8-stage build pipeline: Constrain->Become->Inject->Reason->Call->Produce->Govern->Collaborate |
| 12 pillars | DDD bounded contexts (P01 Knowledge -> P12 Orchestration) |
| nucleus ([[kc_agent]]) | Autonomous agent with specialized role, domain, tools, sin-driven objective |
| N07 orchestrator | Workflow orchestrator (Temporal/Airflow); dispatches + consolidates, never builds |
| kind | Schema type / artifact class (125 registered; naming, max bytes, pillar, builder) |
| builder | Code generator: 12 ISOs per kind (1:1 with pillars); schema + context -> artifact |
| ISO | Config file per concern (model, prompt, knowledge, tools, output, schema, eval, arch, config, memory, feedback, orchestration) |
| artifact | .md + YAML frontmatter following kind schema; compiled to .yaml |
| GDP | Configuration wizard: collect subjective preferences before autonomous generation |
| sin lens | Optimization objective / loss function (envy=coverage, lust=creativity, pride=craft) |
| quality gate (F7) (p01_kc_quality_gate) | CI gate: 7 hard gates + 5D scoring; min 8.0; max 2 retries |
| signal (F8) | Event / webhook: JSON payload with nucleus id, status, quality score |
| handoff | Task spec / work item: Markdown brief with artifact refs + constraints |
| dispatch | Task queue: solo (1), grid (N parallel), swarm (N same-kind) |
| wave | Pipeline stage: sequential group; gate required before next stage |
| grid | Parallel execution pool (max 6 agents, isolated sessions) |
| RAG ([[kc_embedding_config]]) | TF-IDF + Haiku reranking on the full repo doc corpus; Phase 0 MCP for external context; hybrid retrieval (dense + sparse) fused via RRF |

## Top 20 Kinds: Industry Equivalents

| Kind | Industry Equivalent |
|------|---------------------|
| `knowledge_card` | Structured KB article (schema-enforced, compiled to YAML) |
| `agent` | Autonomous agent def (CrewAI Agent / LangGraph node) |
| `prompt_template` | Parameterized prompt / DSPy signature (Mustache slots) |
| `system_prompt` | LLM system message / RLHF instruction set |
| `workflow` | DAG / state machine (Airflow DAG, GitHub Actions) |
| `quality_gate` | CI gate: 7 hard gates + 5D rubric |
| `knowledge_index` | TF-IDF / vector search index (repo-wide doc corpus) |
| `guardrail` | Policy enforcement / content filter (halts before F6) |
| `env_config` | 12-factor environment config (keys, limits, routing) |
| `entity_memory` | Persistent entity store (shared across sessions + agents) |
| `crew_template` ([[kc_crew_template]]) | Multi-agent workflow: N roles + topology + handoff protocol |
| `decision_record` | Architecture Decision Record (ADR) |
| `chain` | Prompt chain with conditional routing (LangChain equivalent) |
| `router` | Load balancer / intent classifier (kind + domain) |
| `scoring_rubric` | Evaluation rubric for F7 GOVERN 5-dimension scoring |

## 5 Developer Entry Points

1. **DDD.** 12 pillars = 12 bounded contexts. Cross-pillar refs are explicit artifact IDs. Each context owns its schema + builder registry.
2. **CI/CD.** 8F is a typed build pipeline: F7 gate (min 8.0), retry budget = 2, F8 compiles `.md` to `.yaml`.
3. **Typed registry.** 125 kinds with JSON schema + naming rule + max bytes. `cex_doctor.py` = corpus-wide linter.
4. **Sin = loss function.** Sin lens = RLHF behavioral prior. N05 (Wrath) maximizes rejection. N07 (Sloth) minimizes direct work, delegates all.
5. **Self-indexing RAG.** Phase 0: MCP (N07). Phase 1: TF-IDF. Phase 2: Haiku rerank. F8 re-indexes each artifact -- every build compounds the corpus.

## Worked Example: CI Gate Implementation as F7

A developer asks "How does CEX enforce quality?" The technical lens shows the actual mechanism:

```python
# F7 GOVERN at the code level (cex_score.py + cex_doctor.py)
def f7_govern(artifact_path: Path) -> GovernResult:
    # 1. Hard gates (BLOCKING -- fail = halt build)
    H = [
        check_frontmatter_parses,    # H01
        check_id_matches_filename,   # H02
        check_kind_in_taxonomy,      # H03
        check_quality_is_null,       # H04
        check_required_fields,       # H05
        check_body_under_max_bytes,  # H06
    ]
    # 2. 5D rubric (scoring -- min 8.0)
    D = [d1_density, d2_completeness, d3_correctness, d4_provenance, d5_taxonomy_alignment]
    # 3. Retry budget = 2 (config-driven via .cex/config/nucleus_models.yaml)
```

This is identical to how a CI pipeline gates a PR: lint -> test -> coverage -> review. The only difference is that CEX's gate runs against a Markdown artifact instead of source code, and the rubric is 5-dimensional instead of pass/fail.

For external comparisons:
- GitHub Actions `if:` conditional == 8F F1 CONSTRAIN.
- CodeClimate quality score == 8F F7 5D rubric.
- LangChain `OutputParserException` retry == 8F F7 retry budget.

## Edge Cases (when industry mapping does not transfer)

| Case | Why the mapping breaks | Reality |
|------|------------------------|---------|
| Sin lens != hyperparameter | Sin biases optimization, but cannot be tuned numerically | Behavioral prior (RLHF-adjacent), not a scalar |
| ISO != single config file | Each ISO is a Markdown spec + YAML compiled | Closer to a Helm chart or k8s manifest, but Markdown-first |
| Decompose mode != distillation | Stage 1 (Opus) plans, Stage 2 (Haiku) generates | Closer to "speculative decoding" + "constrained decoding" |
| Self-assimilating != fine-tuning | F8 commits artifact + index update; not a weight update | Retrieval-time learning (RAG corpus growth), not parameter learning |
| Knowledge Gluttony != optimization metric | "Hoard knowledge" is a process directive, not a loss to minimize | Closer to a cron job ("compound the corpus daily") |

For these cases, switch to [[kc_lens_factory]] (procedural metaphor) or [[kc_lens_biology]] (compound learning analogy).

## Sources

- `_docs/specs/spec_metaphor_dictionary.md`: industry term column (canonical mapping table; this lens is a specialization).
- `CLAUDE.md`: nucleus defs, 8F pipeline, pillar structure, dispatch modes.
- DDD: Evans (2003), "Domain-Driven Design" -- bounded contexts, ubiquitous language; pillars map 1:1.
- CrewAI (Joao Moura, 2024): role + goal + backstory + tools + delegation; identical to CEX [[kc_crew_template]] structure.
- LangGraph (Harrison Chase et al., 2024): nodes + edges + state; CEX nuclei as nodes, signals as state transitions.
- Temporal (Maxim Fateev): durable workflows, retry budgets; CEX 8F retry == Temporal Activity retry policy.
- DSPy (Khattab et al., Stanford 2023): "compile" prompts from declarative signatures -- CEX `prompt_compiler` kind is the equivalent.
- BM25 reference: Robertson & Zaragoza (2009), "The Probabilistic Relevance Framework: BM25 and Beyond".
- 12-factor app (Heroku, 2011): config separation; CEX `env_config` kind is direct lift.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| vocabulary_cex_rosetta | related | 0.35 |
| n00_mentor_context | related | 0.34 |
| [[p02_mm_cex_architecture_n04]] | related | 0.34 |
| p06_td_cex_artifact_type_n03 | downstream | 0.33 |
| [[p01_faq_cex_common_questions]] | related | 0.30 |
