---
kind: architecture
id: bld_architecture_decision_record
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of decision_record — inventory, dependencies, and architectural position
quality: null
title: "Architecture Decision Record"
version: "1.0.0"
author: n03_builder
tags: [decision_record, builder, examples]
tldr: "Golden and anti-examples for decision record construction, demonstrating ideal structure and common pitfalls."
domain: "decision record construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [component map of decision_record, and architectural position, decision record construction, architecture decision record, decision_record, builder, examples, component inventory, dependency graph, boundary table]
density_score: 0.90
related:
  - decision-record-builder
  - bld_instruction_decision_record
  - bld_knowledge_card_decision_record
  - n00_decision_record_manifest
  - bld_schema_decision_record
---
## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| context | Forces that made the decision necessary | decision_record | required |
| decision | Chosen option and primary rationale | decision_record | required |
| status | Lifecycle state (proposed/accepted/deprecated/superseded) | decision_record | required |
| options | Alternatives considered with pros and cons | decision_record | required (>= 2) |
| consequences | Positive, negative, and neutral effects | decision_record | required |
| supersedes | Reference to older ADR this replaces | decision_record | conditional |
| superseded_by | Reference to newer ADR that replaces this | decision_record | conditional |
| related_to | References to architecturally related ADRs | decision_record | optional |
| deciders | Named individuals or roles who ratified the decision | decision_record | optional |
| date_decided | Date the decision was finalized | decision_record | optional |
| law | Inviolable system rule derived from accepted ADR | P08 | external consumer |
| pattern | Reusable prescriptive solution implementing ADR's choice | P08 | external consumer |
| agent | Runtime component subject to a decision's constraints | P02 | external consumer |

## Dependency Graph
```
context       --produces--> decision
options       --produces--> decision
decision      --produces--> consequences
status        --governs-->  decision
supersedes    --links-->    decision
superseded_by --links-->    decision
related_to    --links-->    decision
decision      --informs-->  law
decision      --informs-->  pattern
decision      --constrains--> agent
```

## Boundary Table
| decision_record IS | decision_record IS NOT |
|-------------------|----------------------|
| Permanent record of a single significant architectural choice | A law (inviolable — use invariant-builder) |
| Documents context, options, rationale, and consequences | A pattern (reusable prescription — use pattern-builder) |
| Has lifecycle: proposed -> accepted -> deprecated/superseded | A diagram (use diagram-builder) |
| Revisable: future teams can create superseding ADRs | A knowledge card (use knowledge-card-builder) |
| Keeps history: deprecated ADRs kept, never deleted | An implementation guide (use instruction-builder) |

## Layer Map
| Layer | Components | Purpose |
|-------|-----------|---------|
| evidence | context, options | Information needed to evaluate the decision |
| decision | decision, status, date_decided, deciders | The choice, timing, and who ratified it |
| effects | consequences | What changes as a result |
| links | supersedes, superseded_by, related_to | Traversable decision history chain |
| consumers | law, pattern, agent | Downstream artifacts shaped by accepted decisions |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[decision-record-builder]] | related | 0.65 |
| [[bld_prompt_decision_record]] | upstream | 0.52 |
| [[bld_knowledge_decision_record]] | upstream | 0.50 |
| n00_decision_record_manifest | related | 0.50 |
| [[bld_schema_decision_record]] | upstream | 0.48 |
