---
kind: tools
id: bld_tools_model_card
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for model_card production
quality: null
title: "Tools Model Card"
version: "1.0.0"
author: n03_builder
tags: [model_card, builder, examples]
tldr: "Golden and anti-examples for model card construction, demonstrating ideal structure and common pitfalls."
domain: "model card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [model card construction, tools model card, model_card, builder, examples, production tools, data sources, tool permissions, interim validation, related artifacts]
density_score: 0.90
related:
  - bld_tools_model_provider
  - bld_tools_response_format
  - bld_tools_embedder_provider
  - bld_tools_function_def
---
# Tools: model-card-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing model_cards in pool | Phase 1 (check duplicates) | CONDITIONAL |
| validate_kc.py | Validate KC artifacts (reference pattern) | — | ACTIVE (KC only) |
| validate_artifact.py | Validate any artifact kind via builder gates | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
## Data Sources (APIs)
| Source | URL | Data |
|--------|-----|------|
| Anthropic docs | https://docs.anthropic.com/en/docs/about-claude/models | Claude models specs |
| Anthropic pricing | https://docs.anthropic.com/en/docs/about-claude/pricing | Claude pricing |
| OpenAI docs | https://platform.openai.com/docs/models | GPT models specs |
| OpenAI pricing | https://platform.openai.com/docs/pricing | GPT pricing |
| Google AI | https://ai.google.dev/gemini-api/docs/models | Gemini specs |
| Google pricing | https://ai.google.dev/pricing | Gemini pricing |
| LiteLLM registry | https://github.com/BerriAI/litellm | 2593 models JSON |
| HuggingFace API | https://huggingface.co/api/models/{id} | Model metadata |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation (until validate_artifact.py exists)
Manually check each QUALITY_GATES.md gate against produced artifact.
All 10 HARD gates must pass. SOFT gates contribute to score.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_model_provider]] | sibling | 0.58 |
| [[bld_tools_response_format]] | sibling | 0.45 |
| [[bld_tools_embedder_provider]] | sibling | 0.43 |
| [[bld_tools_function_def]] | sibling | 0.43 |
