---
quality: null
id: bld_memory_constitutional_rule
kind: knowledge_card
pillar: P11
title: "Constitutional Rule Builder -- Memory"
version: 1.0.0
quality: null
tags: [builder, constitutional_rule, memory]
llm_function: INJECT
author: builder
tldr: "Constitutional Rule feedback: context persistence, recall triggers, and state management"
8f: "F3_inject"
keywords: [constitutional rule feedback, context persistence, recall triggers, and state management, builder, constitutional_rule, memory, session patterns, common mistakes, basis reference
constitutional]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - kc_constitutional_rule
  - bld_architecture_constitutional_rule
---
# Memory: constitutional_rule
## Session Patterns
- Bypass test first: before writing any constitutional_rule, ask "is there ANY bypass scenario?" If yes -> guardrail, not constitutional_rule.
- One rule, one prohibition: never bundle multiple prohibitions. A rule that says "never X or Y" should be two rules.
- Concrete principles: "never deny being an AI when sincerely asked" is good. "Be honest" is not a constitutional rule -- it is a value.
- Detection is mandatory: a constitutional rule without a detection method is not enforceable.
## Common Mistakes
- Writing bypass_policy with a value: immediately downgrades to guardrail. If you catch yourself writing ANY bypass, stop and reclassify.
- Overlapping with guardrail: constitutional rules cover absolute prohibitions; guardrails cover operational safety with approved exceptions.
- Multiple prohibitions in one principle: split into separate constitutional_rule artifacts.
- Missing concrete examples: "this rule would be violated if someone asked for X" must be stated explicitly.
## CAI Basis Reference
Constitutional AI (Anthropic, 2022) defined a set of principles for LLM safety training:
1. Harm avoidance: do not help with violence, CSAM, weapons of mass destruction
2. Honesty: do not deceive, do not deny AI identity
3. Autonomy: do not manipulate, preserve user's right to decide
4. Legality: do not assist with illegal actions
These map to the constitutional_basis enum values in this builder.
## Absoluteness Test
"Could a security researcher, law enforcement agent, or operator legitimately need to bypass this?"
If YES to any role -> guardrail. If NO to all roles -> constitutional_rule.

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
| [[kc_constitutional_rule]] | sibling | 0.47 |
| [[bld_architecture_constitutional_rule]] | sibling | 0.44 |
| [[bld_knowledge_constitutional_rule]] | sibling | 0.39 |
