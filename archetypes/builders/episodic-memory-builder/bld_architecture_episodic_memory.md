---
quality: null
quality: null
kind: architecture
id: bld_architecture_episodic_memory
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of episodic_memory -- inventory, dependencies, architectural position
title: "Architecture Episodic Memory"
version: "1.0.0"
author: n03_builder
tags: [episodic_memory, builder, architecture]
tldr: "episodic_memory is P10's long-term temporal store, receiving promotions from working_memory and feeding memory_summary."
domain: "episodic memory construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F1_constrain"
keywords: [architectural position, episodic memory construction, architecture episodic memory, episodic_memory is p, s long-term temporal store, episodic_memory, builder, architecture, component inventory, memory flow]
density_score: 0.90
related:
  - episodic-memory-builder
  - bld_collaboration_episodic_memory
  - bld_architecture_working_memory
  - p01_kc_episodic_memory
  - working-memory-builder
---
## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| episode_schema | Fields each stored episode has | episodic_memory | required |
| retrieval_config | How past episodes are surfaced | episodic_memory | required |
| episode_count | Max episodes in store | episodic_memory | required |
| decay_policy | How episodes age and are pruned | episodic_memory | required |
| owner | Agent or nucleus that owns this store | episodic_memory | required |
| promotion_sources | working_memory stores that feed this | episodic_memory | recommended |
| working_memory | Short-term task state that promotes to here | P10 | producer |
| entity_memory | Long-term entity facts -- distinct store | P10 | sibling |
| memory_summary | Compressed output from episodic store | P10 | consumer |
| retrieval_engine | System that queries episodic store at inference | P10 runtime | consumer |

## P10 Memory Flow
```
[working_memory]  --promote_on_complete-->  [episodic_memory]
                                                   |
                                           [memory_summary]
                                           (compression)
                                                   |
                                       [agent context injection]
```

## Boundary Table
| episodic_memory IS | episodic_memory IS NOT |
|--------------------|------------------------|
| Long-term, temporally indexed episode store | Short-term task state (that is working_memory) |
| Past interaction history (what happened) | Entity facts (what is true about an entity) |
| Indexed by time + retrieval keys | Compressed context output (that is memory_summary) |
| Grows over time, pruned by decay policy | In-session state (that is session_state) |
| Autobiographical LLM interactions | General knowledge (that is knowledge_card) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[episodic-memory-builder]] | downstream | 0.61 |
| [[bld_orchestration_episodic_memory]] | downstream | 0.51 |
| bld_architecture_working_memory | sibling | 0.44 |
| [[kc_episodic_memory]] | downstream | 0.44 |
| working-memory-builder | downstream | 0.41 |
