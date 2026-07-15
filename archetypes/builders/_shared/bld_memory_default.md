---
id: bld_memory_default
kind: builder_default
pillar: P10
source: shared
title: "Memory Default: Learning Record Schema"
llm_function: INJECT
version: 1.1.0
quality: null
tags: [memory, learning_record, P10, shared, default]
tldr: "_Shared memory: context persistence, recall triggers, and state management"
8f: "F3_inject"
keywords: [memory default, learning record schema, shared memory, context persistence, recall triggers, and state management, memory, learning_record, shared, default learning record schema]
author: builder
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - bld_eval_default
  - bld_collaboration_memory_type
  - bld_feedback_default
  - bld_architecture_default
  - bld_collaboration_memory_scope
---
# P10 Memory — Default Learning Record Schema
## What to Persist (F3b PERSIST)
After assembling context (F3), declare what new knowledge should survive:
| Type | When | Target kind |
|------|------|-------------|
| New entity discovered | domain entity not in existing KCs | entity_memory |
| Updated fact | existing KC has stale or wrong data | knowledge_card update |
| Session learning | pattern observed across 3+ builds | learning_record |
| User preference | explicit correction or confirmed approach | feedback memory file |
## Learning Record Schema
```yaml
---
id: lr_{kind}_{date}
kind: learning_record
pillar: P10
nucleus: {nucleus}
domain: {kind}
date: {YYYY-MM-DD}
quality: null
---
## Observation
{What was learned or confirmed}
## Evidence
{2-3 concrete examples from this session}
## Impact
{How this changes future builds of this kind}
## Applied From
{Session date, artifact ID that triggered this learning}
```
## Memory Scope Rules
- **Session memory**: context window only -- do not persist
- **Build memory**: persist if the learning changes HOW to build the kind
- **Error memory**: persist if the error is likely to recur (structural, not one-off)
- **Preference memory**: persist user corrections immediately (use Claude memory system)
## When to Override
Override `bld_memory_{kind}.md` when the kind has domain-specific entity types
or lookup tables (e.g., agent builders track capability registries; schema builders
track field type conventions).
## Hard Gates (H01-H07) -- ALL must pass
| Gate | Check | Fail Action |
|------|-------|-------------|
| H01 | Frontmatter present and valid YAML | Return to F6, add frontmatter |
| H02 | `quality: null` in frontmatter (never self-score) | Remove score, set null |
| H03 | Required fields: id, kind, 8f, pillar, title | Add missing fields |
| H04 | Body density >= 0.85 (content lines / total lines) | Add structured data, remove filler |
| H05 | No hallucinated sources (cited paths must exist) | Remove or verify citations |
| H06 | ASCII-only in any generated code blocks | Replace non-ASCII per cex_sanitize rules |
| H07 | Output matches pillar schema constraints | Restructure to match schema |
## Scoring Dimensions (5D)
| Dimension | Weight | Criteria |
|-----------|--------|---------|
| D1 Structural | 30% | Frontmatter complete, naming correct, file in right pillar dir |
| D2 Content | 25% | Density >= 0.85, no filler, tables preferred over prose |
| D3 Accuracy | 20% | No hallucination, sources verified, constraints respected |
| D4 Usefulness | 15% | Actionable, implementable, unambiguous |
| D5 CEX fit | 10% | Kind/pillar/nucleus alignment, 8F stage correctness |
## Memory Persistence Checklist
- Verify memory type matches taxonomy (entity, episodic, procedural, working)
- Validate retention policy aligns with data lifecycle rules
- Cross-reference with memory_scope for boundary correctness
- Check for stale entries that need decay or pruning
## Memory Pattern
```yaml
# Memory lifecycle
type: classified
retention: defined
scope: bounded
decay: configured
```
```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_memory_update.py --check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_default]] | sibling | 0.39 |
| bld_collaboration_memory_type | downstream | 0.38 |
| [[bld_feedback_default]] | sibling | 0.36 |
| [[bld_architecture_default]] | sibling | 0.34 |
| [[bld_orchestration_memory_scope]] | downstream | 0.33 |
