---
kind: output_template
id: bld_output_template_agentic_rag
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for agentic_rag production
quality: null
title: "Output Template Agentic Rag"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [agentic_rag, builder, output_template]
tldr: "Template with vars for agentic_rag production"
domain: "agentic_rag construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [agentic_rag construction, output template agentic rag, agentic_rag, builder, output_template, agent configuration, knowledge sources, execution workflow, tool plan, related artifacts]
density_score: 0.85
related:
  - bld_knowledge_card_agentic_rag
  - bld_instruction_agentic_rag
  - p01_qg_agentic_rag
  - kc_query_optimizer
  - bld_tools_agentic_rag
---
```yaml
---
id: p01_ar_{{name}}.md
kind: agentic_rag
quality: null
title: "{{title}}"
version: "1.0.0"
agent_type: "{{agent_type}}"  # e.g. self_rag | crag | rag_fusion | adaptive | react
knowledge_source: "{{knowledge_source}}"  # e.g. vector_store | graph_store | web | hybrid
created: "{{created}}"
updated: "{{updated}}"
author: "{{author}}"
domain: "{{domain}}"
tags: [{{tags}}]
tldr: "{{tldr}}"
---

## Overview
<!-- Purpose: what domain problem does this agentic RAG solve? -->
<!-- Scope: which documents / data sources / APIs are in retrieval scope? -->

## Agent Configuration
| Parameter | Value | Notes |
|---|---|---|
| agent_type | {{agent_type}} | self_rag / crag / rag_fusion / adaptive / react |
| plan_strategy | {{plan_strategy}} | react / cot / direct |
| max_reflection_iterations | {{max_reflection_iterations}} | Terminate loop after N re-queries |
| reflection_trigger | {{reflection_trigger}} | Condition: similarity < threshold, contradictory evidence |

## Knowledge Sources
| Source | Type | Access | Format |
|---|---|---|---|
| {{source_name}} | vector_store / graph_store / web | API / local | {{format}} |

## Execution Workflow
1. **Retrieve**: query {{knowledge_source}} with top-k={{top_k}}, similarity metric={{metric}}
2. **Reflect**: score retrieved docs -- if relevance < {{threshold}}, trigger re-query
3. **Re-query**: {{corrective_strategy}} (sub-query decomposition / web fallback / abort)
4. **Generate**: synthesize answer from verified retrieved context
5. **Validate**: cross-check generated claims against source passages

## Tool Plan
| Tool | Phase | Purpose |
|---|---|---|
| retrieve_vector | Retrieve | Dense similarity search |
| retrieve_graph | Retrieve | Graph neighborhood traversal |
| generate_subquery | Re-query | Decompose into sub-questions |
| reflect_plan | Reflect | Score retrieved doc relevance |
| rerank_results | Retrieve | Cross-encoder reranking |

## Compliance
<!-- Regulatory requirements: data residency, PII handling, audit trail -->
<!-- Ethical: bias evaluation, source attribution policy -->
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_agentic_rag]] | upstream | 0.35 |
| [[bld_instruction_agentic_rag]] | upstream | 0.29 |
| [[p01_qg_agentic_rag]] | downstream | 0.27 |
| [[kc_query_optimizer]] | upstream | 0.25 |
| [[bld_tools_agentic_rag]] | upstream | 0.23 |
