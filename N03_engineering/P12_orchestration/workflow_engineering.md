---
id: p12_wf_builder_8f_pipeline
kind: workflow
8f: F8_collaborate
pillar: P12
title: 8F Construction Pipeline
version: 2.0.0
created: 2026-03-30
updated: 2026-03-30
author: builder_agent
steps_count: 9
execution: sequential
agent_groups: [builder_nucleus]
timeout: 120
retry_policy: per_step
depends_on: []
signals: [intent_parsed, constrained, identity_loaded, knowledge_injected, plan_ready, tools_ready, artifact_produced, validated, complete]
domain: meta-construction
quality: null
tags: [workflow, 8F, pipeline, N03, collaborate]
tldr: The 8F pipeline as an executable workflow -- 9 steps from intent to indexed artifact.
when_to_use: "Run when constructing ANY typed artifact (this workflow IS N03's core loop). Consult for 'what are the 9 steps from intent to a compiled, indexed artifact?'"
primary_8f: COLLABORATE
keywords: [artifact, schema.yaml, kinds_meta.json, builder isos, knowledge context, llm plans construction, frontmatter]
density_score: 0.90
related:
  - bld_architecture_chain
  - p10_lr_chain_builder
---

# 8F Construction Pipeline

## Purpose
Transforms human intent into a validated, compiled, indexed artifact.
This workflow IS the core of N03 -- every artifact in the entire taxonomy
is produced by running these 9 steps.

### Inputs (bind per run)

```yaml
user_text: {{user_text}}       # the natural-language intent entering Step 1
kind: {{kind}}                 # resolved target kind (drives F1-F6 ISO + KC loads)
max_retries: {{max_retries}}   # default 2 -- F6 retry budget on F7 soft-fail
```

### How to use

```text
8F verb: COLLABORATE (F8 is the terminal step; the run spans F1-F8). Execute the
9 Steps in sequence -- each emits its named Signal and gates the next. F6 retries
up to max_retries on an F7 soft-fail; an F7 hard-fail aborts. Bind {{kind}} after
Step 1 resolves intent.
```

## Steps

### Step 1: PARSE_INTENT
- **Input**: user_text (natural language string)
- **Action**: Classify intent into verb + objects + kinds
- **Output**: classified_kinds list with (kind, pillar, function) tuples
- **Signal**: intent_parsed
- **Depends**: none
- **Failure**: If 0 kinds resolved, suggest closest matches

### Step 2: LOAD_CONSTRAINTS [Runner.F1]
- **Input**: kind name from Step 1
- **Action**: Read _schema.yaml + kinds_meta.json
- **Output**: max_bytes, naming convention, required frontmatter fields
- **Signal**: constrained
- **Depends**: Step 1

### Step 3: LOAD_IDENTITY [Runner.F2]
- **Input**: kind name
- **Action**: Load builder ISOs from archetypes/builders/{{kind}}-builder/
- **Output**: Builder system prompt (manifest + instructions + architecture)
- **Signal**: identity_loaded
- **Depends**: Step 2

### Step 4: INJECT_KNOWLEDGE [Runner.F3]
- **Input**: kind name
- **Action**: Load kc_{{kind}}.md + builder KC + domain KCs + examples
- **Output**: Knowledge context (up to 7KB budget)
- **Signal**: knowledge_injected
- **Depends**: Step 3

### Step 5: REASON_PLAN [Runner.F4]
- **Input**: Constraints + identity + knowledge
- **Action**: LLM plans construction (sections, references, approach)
- **Output**: Construction plan (100-200 words)
- **Signal**: plan_ready
- **Depends**: Step 4
- **Temperature**: 0.3

### Step 6: LOAD_TOOLS [Runner.F5]
- **Input**: kind name
- **Action**: Parse bld_tools, scan for existing similar artifacts
- **Output**: Available tools list + existing artifact warnings
- **Signal**: tools_ready
- **Depends**: Step 5

### Step 7: PRODUCE_ARTIFACT [Runner.F6]
- **Input**: Plan + tools + knowledge + constraints
- **Action**: LLM generates complete artifact (frontmatter + body)
- **Output**: Artifact markdown text
- **Signal**: artifact_produced
- **Depends**: Step 6
- **Temperature**: 0.7
- **Retry**: Up to 2x on quality failure (Step 8 feedback)

### Step 8: VALIDATE [Runner.F7]
- **Input**: Artifact text + constraints
- **Action**: Run quality gates H01-H07
- **Output**: pass/fail + score + issue list
- **Signal**: validated
- **Depends**: Step 7
- **On soft fail**: Return to Step 7 with issues (max 2 retries)
- **On hard fail**: Abort with error signal

### Step 9: SAVE_COMPILE_INDEX [Runner.F8]
- **Input**: Validated artifact
- **Action**: Write .md, compile to .yaml, rebuild the search index
- **Output**: File path + compiled flag + indexed flag
- **Signal**: complete
- **Depends**: Step 8

## Quality Gates (Step 8 detail)

| Gate | Check | Severity |
|------|-------|----------|
| H01 | Valid YAML frontmatter with required fields | HARD |
| H02 | Kind matches requested kind | HARD |
| H03 | Naming follows convention | WARN |
| H04 | References resolve | WARN |
| H05 | Density >= 0.80 | SOFT |
| H06 | Size <= max_bytes | SOFT |
| H07 | Schema required fields present | HARD |

## Signals

- **On step complete**: Each step emits named signal
- **On workflow complete**: complete signal with quality score
- **On error**: error signal with step number and failure reason

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_chain]] | upstream | 0.40 |
| [[p10_lr_chain_builder]] | upstream | 0.34 |
