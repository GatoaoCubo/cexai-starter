---
kind: memory
id: p10_mem_github_issue_template_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for github_issue_template construction
quality: null
title: "Memory Github Issue Template"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [github_issue_template, builder, memory]
tldr: "Learned patterns and pitfalls for github_issue_template construction"
domain: "github_issue_template construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [github_issue_template construction, memory github issue template, github_issue_template, builder, memory, feature, question, title, steps to reproduce, observation
common]
density_score: 0.85
related:
  - github-issue-template-builder
  - kc_github_issue_template
  - bld_instruction_github_issue_template
  - bld_knowledge_card_github_issue_template
  - p05_qg_github_issue_template
---
## Observation
Common issues include missing required fields (e.g., reproduction steps) and inconsistent label usage, leading to incomplete or misclassified reports. Templates often overlook guidance for users to prioritize clarity over verbosity.

## Pattern
Effective templates enforce mandatory fields (title, description, labels) and use structured prompts to guide users. Labels like `bug`, `feature`, or `question` are paired with clear definitions to streamline triage.

## Evidence
Reviewed templates from vuejs/vue and tensorflow/tensorflow demonstrate consistent use of required fields and label-specific instructions.

## Recommendations
- Enforce required fields (e.g., `title`, `steps to reproduce`) via template syntax.
- Use standardized labels with explicit definitions (e.g., `bug`: "Unexpected behavior").
- Include example issues to illustrate expected formatting.
- Avoid markdown in description fields to ensure compatibility with GitHub’s parser.
- Keep templates concise to reduce user friction.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[github-issue-template-builder]] | upstream | 0.38 |
| [[kc_github_issue_template]] | upstream | 0.36 |
| [[bld_instruction_github_issue_template]] | upstream | 0.35 |
| [[bld_knowledge_card_github_issue_template]] | upstream | 0.34 |
| [[p05_qg_github_issue_template]] | downstream | 0.25 |
