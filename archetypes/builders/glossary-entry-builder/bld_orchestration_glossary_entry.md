---
kind: collaboration
id: bld_collaboration_glossary_entry
pillar: P12
llm_function: COLLABORATE
purpose: How glossary-entry-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Glossary Entry"
version: "1.0.0"
author: n03_builder
tags: [glossary_entry, builder, examples]
tldr: "Golden and anti-examples for glossary entry construction, demonstrating ideal structure and common pitfalls."
domain: "glossary entry construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [glossary entry construction, collaboration glossary entry, glossary_entry, builder, examples, "### crew: onboarding package", my role, crew compositions, content foundation, onboarding package]
density_score: 0.90
related:
  - glossary-entry-builder
---
# Collaboration: glossary-entry-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what does this term mean in this domain?"
I do not distill deep knowledge. I do not document domain scope.
I define terms concisely so all builders share a common vocabulary.
## Crew Compositions
### Crew: "Content Foundation"
```
  1. context-doc-builder -> "domain scope and background"
  2. knowledge-card-builder -> "atomic domain facts"
  3. glossary-entry-builder -> "term definitions for shared vocabulary"
```
### Crew: "Onboarding Package"
```
  1. glossary-entry-builder -> "term definitions for newcomers"
  2. context-doc-builder -> "domain overview"
  3. diagram-builder -> "visual architecture for orientation"
```
## Handoff Protocol
### I Receive
- seeds: term name, domain context
- optional: synonyms, abbreviations, disambiguation notes, related terms
### I Produce
- glossary_entry artifact (.md + .yaml frontmatter, max 3 lines definition)
- committed to: `cex/P01/examples/p01_glossary_{term}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
None — independent builder (layer 0). Terms can be defined standalone.
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| context-doc-builder | References glossary terms in domain documentation |
| knowledge-card-builder | Uses terms as search keywords for discoverability |
| axiom-builder | References precise term definitions in axiom statements |
| knowledge-index-builder | Uses glossary terms for query expansion in search |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_collaboration_context_doc | sibling | 0.45 |
| [[bld_orchestration_knowledge_card]] | sibling | 0.41 |
| [[glossary-entry-builder]] | upstream | 0.39 |
| [[kc_glossary_entry]] | upstream | 0.36 |
| p01_gl_TERM_SLUG | upstream | 0.36 |
