---
id: p06_vs_artifact_output
kind: validation_schema
8f: F1_constrain
pillar: P06
title: "Validation Schema -- Artifact Output"
version: 1.1.0
created: 2026-04-17
author: n03_engineering
domain: artifact-construction
quality: null
tags: [validation-schema, artifact, frontmatter, density, N03, 8F, quality-gate]
tldr: "Validation rules for every artifact produced by N03. Enforces frontmatter contract, density target, structural requirements, and kind-specific constraints at F7 GOVERN."
keywords: [yaml frontmatter, semver pattern, iso date, density_score, canonical path, placeholder text, ascii-rule violations]
density_score: 0.93
updated: "2026-07-17"
related:
  - p06_iface_engineering_nucleus_n03
  - p07_gt_n03
  - p11_qg_builder_nucleus
  - bld_schema_validation_schema
---

# Validation Schema: Artifact Output

## Purpose

Applied at **F7 GOVERN** for every artifact produced by N03.
This schema defines what makes an artifact VALID before it can be saved, compiled, and signaled.
It is the machine-readable companion to the quality checklist a builder self-checks against.

## External Prior Art

This is CEX's own instance of a pattern with real precedent elsewhere, not an
arbitrary house rule:

- **Hard gate = JSON Schema's `required` keyword.** "The `required` keyword
  takes an array of ... strings ... if those properties are not present, the
  JSON data is considered invalid" (json-schema.org/understanding-json-schema/
  reference/object). Layer 1 below (FM-01..FM-10) is this repo's `required`
  list for artifact frontmatter -- same hard-fail semantics, YAML instead of
  JSON.
- **System-side, post-generation validation + bounded retry = Guardrails AI's
  `Guard`.** This kind's own boundary (kinds_meta.json, in `.cex/`: "contract
  enforced by the SYSTEM after generation ... LLM does not see it") plus the
  bounded retry in Error Recovery Protocol below (max 2) mirrors Guardrails
  AI's `Guard.parse` (validates LLM output after it is produced) and its
  `num_reasks` argument (bounded re-ask of the LLM when validation fails) --
  guardrailsai.com/docs/concepts/guard.

## Layer 1: Frontmatter Validation (HARD gates -- all must pass)

| Rule | Check | Error if Fail |
|------|-------|--------------|
| FM-01 | YAML frontmatter block present (--- delimiters) | MissingFrontmatterError |
| FM-02 | `id` field present and non-empty | MissingFieldError: id |
| FM-03 | `kind` field matches a value in kinds_meta.json | UnknownKindError |
| FM-04 | `pillar` field matches kind's canonical pillar | PillarMismatchError |
| FM-05 | `title` field present, length 5-120 chars | TitleLengthError |
| FM-06 | `version` matches semver pattern `\d+\.\d+\.\d+` | VersionFormatError |
| FM-07 | `quality: null` (never self-scored) | SelfScoringError |
| FM-08 | `tags` is a non-empty list | MissingTagsError |
| FM-09 | `tldr` present, length 20-300 chars | TldrLengthError |
| FM-10 | `created` matches ISO date `\d{4}-\d{2}-\d{2}` | DateFormatError |

## Layer 2: Body Validation (SOFT gates -- score against thresholds)

| Rule | Check | Weight | Basis |
|------|-------|--------|-------|
| BD-01 | Body byte count in range [512, max_bytes for kind] | 20% | internal: kinds_meta.json (in `.cex/`), max_bytes per kind (design choice, not externally sourced) |
| BD-02 | At least one H2 section heading present | 10% | internal structural minimum (design choice, not externally sourced) |
| BD-03 | density_score >= 0.85 (tables/code/structure ratio) | 15% | see 8f-reasoning.md (in `.claude/rules/`) F6 PRODUCE ("density target >= 0.85") |
| BD-04 | No placeholder text (TODO, FIXME, TBD, {{.*}}) in final output | 10% | cf. SonarSource rule S1135 "Track uses of TODO tags" (same placeholder-tag pattern) |
| BD-05 | At least one concrete example (code block, table row, or YAML block) | 15% | cf. JSON Schema's `examples` keyword ("array of examples that validate against the schema") |
| BD-06 | Cross-references use canonical path format (not colloquial names) | 10% | see ubiquitous-language.md (in `.claude/rules/`), canonical-reference rule |
| BD-07 | No duplicate sections (H2 headings unique) | 5% | cf. markdownlint rule MD024 "no-duplicate-heading" |
| BD-08 | No ASCII-rule violations in embedded code (.py, .ps1, .sh) | 15% | see ascii-code-rule.md (in `.claude/rules/`), source of this check |

## Layer 3: Kind-Specific Validation

Applied in addition to L1+L2 based on resolved `kind`:

### input_schema
- fields table required (columns: name, type, required, default, description)
- validation_rules section required
- examples section required

### knowledge_card
- definition section required
- application section required
- >= 3 body sections

### agent / agent_card
- capabilities list required
- tools list required
- nucleus field in frontmatter

### workflow
- steps table required
- trigger field in frontmatter

### scoring_rubric
- dimensions table required (columns: name, weight, description)
- weights must sum to 100

## Density Score Calculation

```
density_score = (structured_bytes / total_body_bytes)
structured_bytes = bytes in: tables + code_blocks + lists + yaml_blocks
threshold: >= 0.85
```

## Validation Modes

| Mode | When | Gates Applied |
|------|------|--------------|
| STRICT | Production builds (compile=true) | L1 + L2 + L3 |
| SOFT | Dry runs | L1 only |
| AUDIT | cex_doctor.py scan | L1 + L2 (no L3) |
| FAST | Signal writes | FM-01..FM-04 only |

## Pass/Fail Thresholds

| Outcome | Condition |
|---------|-----------|
| PASS | All L1 gates pass + L2 score >= 0.80 |
| WARN | All L1 gates pass + L2 score in [0.70, 0.80) |
| FAIL | Any L1 gate fails OR L2 score < 0.70 |
| RETRY | FAIL + retry_count < 2 (return to F6 PRODUCE) |
| REJECT | FAIL + retry_count >= 2 (escalate to N07) |

## Error Recovery Protocol

```
FAIL -> F6 PRODUCE retry (max 2 times)
WARN -> save artifact, log warning, continue to F8
REJECT -> write error to .cex/runtime/signals/signal_n03_fail_{timestamp}.json
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_iface_engineering_nucleus_n03]] | sibling | 0.27 |
| [[p07_gt_n03]] | downstream | 0.26 |
| [[p11_qg_builder_nucleus]] | downstream | 0.26 |
| [[bld_schema_validation_schema]] | related | 0.22 |
