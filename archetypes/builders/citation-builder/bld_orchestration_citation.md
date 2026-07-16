---
kind: collaboration
id: bld_collaboration_citation
pillar: P12
llm_function: COLLABORATE
purpose: How citation-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Citation"
version: "1.0.0"
author: n03_builder
tags: [citation, builder, examples]
tldr: "Golden and anti-examples for citation construction, demonstrating ideal structure and common pitfalls."
domain: "citation construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [citation construction, collaboration citation, citation, builder, examples, "### crew: rag quality", my role, crew compositions, grounded knowledge, handoff protocol]
density_score: 0.90
related:
  - citation-builder
  - bld_collaboration_builder
---
# Collaboration: citation-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what is the verifiable source for this claim?"
I do not distill knowledge. I do not configure retrieval pipelines.
I create structured references so artifacts can trace claims to verifiable sources.
## Crew Compositions
### Crew: "Evidence-Grounded Knowledge"
```
  1. citation-builder -> "source attribution and provenance"
  2. knowledge-card-builder -> "distilled facts grounded by citations"
  3. context-doc-builder -> "domain context with source references"
```
### Crew: "RAG Quality"
```
  1. rag-source-builder -> "indexable sources"
  2. citation-builder -> "provenance for retrieved content"
  3. retriever-config-builder -> "search configuration"
```
## Handoff Protocol
### I Receive
- seeds: source URL, source material, claim to attribute
- optional: reliability assessment, domain context
### I Produce
- citation artifact (.md, max 2KB) with complete provenance
- committed to: `P01_knowledge/examples/p01_cit_{topic}.md`
### I Signal
- signal: complete (with quality from QUALITY_GATES)
- if quality < 7.0: signal retry with failure reasons
## Builders I Depend On
None — independent builder (layer 0). Citations reference external sources.
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| knowledge-card-builder | KCs ground claims in cited sources |
| context-doc-builder | Context docs reference citations |
| rag-source-builder | Sources are formalized as citations |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_knowledge_card]] | sibling | 0.40 |
| [[bld_orchestration_rag_source]] | sibling | 0.39 |
| bld_collaboration_context_doc | sibling | 0.34 |
| [[citation-builder]] | upstream | 0.31 |
| bld_collaboration_builder | sibling | 0.29 |
