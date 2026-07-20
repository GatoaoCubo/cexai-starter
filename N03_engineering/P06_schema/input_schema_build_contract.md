---
id: p06_is_build_contract
kind: input_schema
8f: F1_constrain
pillar: P06
title: "Input Schema -- Build Task Contract"
version: 1.0.0
created: 2026-04-17
author: n03_engineering
domain: artifact-construction
quality: null
tags: [input-schema, build-contract, N03, 8F, task-dispatch, constrain]
tldr: "Canonical input contract for any artifact build task dispatched to N03. Defines kind, pillar, nucleus, verb, quality_target, and execution flags."
when_to_use: "Validate against this (F1 CONSTRAIN) before any N03 build runs. Consult for 'what fields does a build task accept, what are the defaults, and which inputs are coerced/rejected?'"
primary_8f: CONSTRAIN
keywords: [intent, kind, pillar, nucleus, verb, quality_target, domain, output_dir, dry_run, model]
density_score: 0.91
related:
  - p04_cli_n03_build
  - p01_fse_n07_dispatch
---

# Input Schema: Build Task Contract

### How to use

```text
8F verb: CONSTRAIN (F1). A dispatcher validates the incoming build payload against
this schema BEFORE the pipeline runs: apply Validation Rules, then Coercion Rules,
then reject with the matching Error Message on any violation. The Fields table is
the contract; the Examples show a minimal and a full payload. Bind the fields:
```

```yaml
intent: {{intent}}                  # OR kind -- one is required
kind: {{kind}}                      # explicit override; must exist in kinds_meta.json
verb: {{verb}}                      # CREATE | REWRITE | MIGRATE | IMPROVE | VALIDATE
quality_target: {{quality_target}}  # default 9.0, range [0.0, 10.0]
model: {{model}}                    # model tier override (default: mid-tier)
```

## Purpose

Every artifact build dispatched to N03 must conform to this contract. This schema
defines what the build task RECEIVER (N03 / any builder nucleus) accepts as input.
Enforced at F1 CONSTRAIN before any pipeline execution begins.

## Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| intent | string | yes (or kind) | -- | Natural language build request |
| kind | string | no | resolved from intent | Explicit kind override; must exist in kinds_meta.json |
| pillar | enum P01-P12 | no | derived from kind | Pillar override; validated against kind's canonical pillar |
| nucleus | enum n01-n07 | no | n03 | Target nucleus; defaults to N03 for build tasks |
| verb | enum | no | create | Build action: CREATE, REWRITE, MIGRATE, IMPROVE, VALIDATE |
| quality_target | float | no | 9.0 | Minimum acceptable quality score (0.0-10.0) |
| context | string | no | null | Additional context for F3 INJECT; max 5000 chars |
| domain | string | no | null | Domain scope for context injection |
| output_dir | path | no | derived from kind | Override output directory; must be writable |
| dry_run | boolean | no | false | Simulate pipeline without writing any files |
| model | enum | no | mid-tier | Model tier override |
| force | boolean | no | false | Overwrite existing artifact if present |
| compile | boolean | no | true | Run the compile step after write |
| signal | boolean | no | true | Send completion signal |

## Validation Rules

1. `intent` OR `kind` must be provided; both may be present (kind takes precedence)
2. `kind` must resolve to an entry in `.cex/kinds_meta.json`
3. `pillar` if provided must match the canonical pillar for the resolved `kind`
4. `verb` must be one of: CREATE, REWRITE, MIGRATE, IMPROVE, VALIDATE
5. `quality_target` must be in range [0.0, 10.0]; values below 7.0 generate a warning
6. `context` trimmed to 5000 chars if longer; no truncation error raised
7. `output_dir` must be a valid relative path within the repo root

## Coercion Rules

| Input | Coercion |
|-------|---------|
| verb as lowercase | uppercased to SCREAMING_SNAKE |
| quality_target as string | cast to float; non-numeric raises ValidationError |
| compile/signal/dry_run/force as string "true"/"false" | cast to boolean |
| model as null | defaults to the nucleus's configured tier |
| kind with hyphens | normalized to underscores |

## Error Messages

| Field | Error |
|-------|-------|
| intent + kind both null | BuildContractError: intent or kind required |
| kind not in kinds_meta | BuildContractError: unknown kind '{kind}' |
| pillar mismatch | BuildContractError: pillar {pillar} does not match kind {kind} canonical {canonical} |
| verb invalid | BuildContractError: verb must be CREATE/REWRITE/MIGRATE/IMPROVE/VALIDATE |
| quality_target out of range | BuildContractError: quality_target {v} not in [0.0, 10.0] |

## Examples

### Minimal valid input
```yaml
intent: "create a system prompt for the research agent"
```

### Full explicit input
```yaml
kind: system_prompt
pillar: P03
nucleus: n03
verb: CREATE
quality_target: 9.0
domain: research-intelligence
compile: true
signal: true
```

### Rewrite with context
```yaml
kind: knowledge_card
verb: REWRITE
context: "Update to reflect new embedding providers added in Wave 4"
quality_target: 9.5
force: true
```

## Constraints

| Constraint | Value |
|------------|-------|
| Maximum field count | 14 |
| Maximum intent length | 500 chars |
| Maximum context length | 5000 chars |
| Nesting depth | 1 (flat object only) |
| Payload ceiling | 8192 bytes |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p04_cli_n03_build]] | upstream | 0.31 |
| [[p01_fse_n07_dispatch]] | upstream | 0.29 |
