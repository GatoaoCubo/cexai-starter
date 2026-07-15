---
quality: null
id: bld_rules_constitutional_rule
kind: knowledge_card
pillar: P11
title: "Constitutional Rule Builder -- Rules"
version: 1.0.0
quality: null
tags: [builder, constitutional_rule, rules]
llm_function: COLLABORATE
author: builder
tldr: "Constitutional Rule feedback: workflow coordination, handoffs, and lifecycle management"
8f: "F3_inject"
keywords: [constitutional rule feedback, workflow coordination, and lifecycle management, builder, constitutional_rule, rules, absolute rules, soft rules, boundary rules, the bypass test]
density_score: 0.81
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_manifest_constitutional_rule
  - bld_rules_process_manager
  - bld_rules_value_object
  - guardrail-builder
  - kc_constitutional_rule
---
# Rules: constitutional_rule
## Absolute Rules (HARD -- never violate)
1. bypass_policy MUST be "none" -- any other value means this is a guardrail, not a constitutional rule.
2. core MUST be true -- constitutional rules apply to all agents and cannot be scoped away.
3. severity MUST be critical -- constitutional rules are always the highest severity.
4. One rule, one prohibition -- never bundle multiple prohibitions in a single artifact.
5. Principle must be concrete and testable -- abstract values ("be helpful") are not rules.
6. quality: null always -- never self-score.
## Soft Rules (RECOMMEND)
1. detection_method should be specified to make enforcement practical.
2. Cite a cai_reference or external ethical framework (EU AI Act, NIST AI RMF) for grounding.
3. Violation examples: 2 minimum, prefer 3 covering different attack surfaces.
4. Rationale should address the most compelling "edge case" argument and rebut it.
## Boundary Rules
1. THIS BUILDER handles: constitutional_rule (P11) -- absolute, no bypass
2. NOT this builder: guardrail (soft, has bypass) -> guardrail-builder
3. NOT this builder: quality_gate (output quality) -> quality-gate-builder
4. NOT this builder: permission (access control) -> permission-builder
5. NOT a kind: safety_policy (document) -- there is no safety-policy-builder in CEX
## The Bypass Test (MANDATORY before building)
"Is there ANY legitimate scenario where this rule should be bypassed?"
- YES: use guardrail-builder instead
- NO: proceed with constitutional-rule-builder
## CEX-Specific Rules
1. id pattern: p11_cr_{slug} -- always prefix p11_cr_
2. Pillar: always P11 (Feedback)
3. Producing nucleus: N07 (Orchestrator) -- core rules come from the orchestrator level
4. max_bytes: 2048
5. Publish threshold: >= 8.0 (higher than standard 7.0 for safety-critical artifacts)

## Orchestration Checklist

- Verify workflow topology matches dependency graph
- Validate handoff protocol between upstream and downstream
- Cross-reference with dispatch rules for routing correctness
- Test wave sequencing with dry-run before live dispatch

## Orchestration Pattern

```yaml
# Workflow validation
topology: verified
handoffs: validated
routing: checked
sequencing: tested
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope orchestration
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_manifest_constitutional_rule]] | sibling | 0.35 |
| bld_rules_process_manager | sibling | 0.34 |
| bld_rules_value_object | sibling | 0.32 |
| [[guardrail-builder]] | related | 0.32 |
| [[kc_constitutional_rule]] | sibling | 0.32 |
