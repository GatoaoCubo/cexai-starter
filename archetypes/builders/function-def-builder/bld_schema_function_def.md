---
kind: schema
id: bld_schema_function_def
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema — SINGLE SOURCE OF TRUTH for function_def
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Function Def"
version: "1.0.0"
author: n03_builder
tags:
  - "function_def"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for function def construction, demonstrating ideal structure and common pitfalls."
domain: "function def construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "function def construction"
  - "schema function def"
  - "function_def"
  - "builder"
  - "examples"
  - "^p04_fn_[a-z][a-z0-9_]+$"
  - "## overview"
  - "## parameters"
  - "## returns"
density_score: 0.90
related:
  - bld_schema_input_schema
  - bld_schema_retriever_config
  - bld_schema_unit_eval
  - bld_schema_action_prompt
  - bld_schema_constraint_spec
---

# Schema: function_def
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p04_fn_{name_slug}) | YES | - | Namespace compliance |
| kind | literal "function_def" | YES | - | Type integrity |
| pillar | literal "P04" | YES | - | Pillar assignment |
| version | semver string | YES | "1.0.0" | Artifact versioning |
| created | date YYYY-MM-DD | YES | - | Creation date |
| updated | date YYYY-MM-DD | YES | - | Last update |
| author | string | YES | - | Producer identity |
| name | string | YES | - | Function name (snake_case, verb_noun) |
| description | string <= 200ch | YES | - | What the function does — LLM reads this to decide when to call |
| parameters | object (JSON Schema) | YES | - | Input parameters as JSON Schema with type, properties, required |
| returns | object | YES | - | Return type and structure |
| provider_compat | list[enum: openai, anthropic, gemini, bedrock] | REC | [openai, anthropic] | Tested provider compatibility |
| strict | boolean | REC | false | Strict schema enforcement (OpenAI strict mode) |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "function_def" |
| tldr | string <= 160ch | YES | - | Dense summary |
| examples | list[object] | REC | - | Example invocations with input/output |
| error_types | list[string] | REC | - | Possible error conditions |
## ID Pattern
Regex: `^p04_fn_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.
## Body Structure (required sections)
1. `## Overview` — what the function does, when LLM should call it
2. `## Parameters` — detailed parameter descriptions with types, constraints, examples
3. `## Returns` — return type, structure, possible values
4. `## Examples` — concrete input/output pairs showing correct invocation
## Constraints
- max_bytes: 2048 (body only)
- naming: p04_fn_{name_slug}.md + .json (compiled)
- machine_format: json (compiled artifact)
- id == filename stem
- parameters MUST be valid JSON Schema
- quality: null always
- NO implementation code in body — schema definition only

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_input_schema]] | sibling | 0.58 |
| [[bld_schema_retriever_config]] | sibling | 0.56 |
| [[bld_schema_unit_eval]] | sibling | 0.56 |
| [[bld_schema_action_prompt]] | sibling | 0.55 |
| [[bld_schema_constraint_spec]] | sibling | 0.55 |
