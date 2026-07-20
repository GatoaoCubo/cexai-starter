---
id: p11_qg_artifact
kind: quality_gate
pillar: P11
title: "Gate: Artifact Quality Validation"
version: 1.0.0
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
domain: artifact-quality-operations
quality: null
tags: [quality_gate, artifact, operations, N05, frontmatter, compilation]
tldr: "Artifact quality gate covering frontmatter validity, YAML compilation, density scoring, kind compliance, and cross-reference integrity."
related:
  - kind-builder
  - bld_config_default
  - p11_qg_kind_builder
  - bld_instruction_kind
---

## Definition

| Property | Value |
|----------|-------|
| Metric | artifact_quality_score |
| Threshold | 0.90 |
| Operator | >= |
| Scope | All artifacts (.md files with frontmatter) across all pillars and nuclei |

## Hard Gates

| gate_id | description | threshold | block |
|---------|-------------|-----------|-------|
| ART01 | Valid YAML frontmatter (parseable, no syntax errors) | 100% | true |
| ART02 | Required frontmatter fields present (id, kind, pillar, title, version, quality, tags, tldr) | 100% | true |
| ART03 | `kind` value exists in kinds_meta.json registry | 100% | true |
| ART04 | `quality` is null in source artifacts (peer-review assigns score) | 100% | true |
| ART05 | YAML compilation succeeds via `cex_compile.py` | 100% | true |
| ART06 | UTF-8 encoding (no cp1252, no BOM in body) | 100% | true |
| ART07 | `id` is unique across the entire repository | 100% | true |
| ART08 | `pillar` matches the parent directory P{01-12}_* | 100% | true |
| ART09 | All wikilinks (double-bracket cross-references) resolve to existing artifacts | 100% | true |
| ART10 | Density score >= 0.85 | >= 0.85 | true |

## Soft Gates

| gate_id | description | max_penalty | weight |
|---------|-------------|-------------|--------|
| SA03 | tldr field is concise, accurate, and non-generic | 0.10 | 0.40 |
| SA04 | Tags are relevant and consistent with kind taxonomy | 0.10 | 0.25 |
| SA05 | Version follows semver and increments on edits | 0.10 | 0.20 |
| SA06 | Domain-specific content (not generic filler applicable to any nucleus) | 0.10 | 0.15 |

## Validation Commands

```bash
# ART01-02: Frontmatter validation
python _tools/cex_hooks.py --check <file>

# ART03: Kind registry check
python -c "import json; k=json.load(open('.cex/kinds_meta.json')); print('VALID' if '<kind>' in k else 'INVALID')"

# ART05: Compilation
python _tools/cex_compile.py <file>

# ART06: Encoding check
python _tools/cex_sanitize.py --check <file>

# Full batch validation
python _tools/cex_doctor.py
```

## Scoring Formula

`artifact_score = (SA03 * 0.40) + (SA04 * 0.25) + (SA05 * 0.20) + (SA06 * 0.15)`

Pass condition: all 10 hard gates ART01-ART10 PASS AND `artifact_score >= 0.90`.
ANY hard-gate FAIL forces total = 0 regardless of soft-gate score.

## Anti-Sycophancy Clause (F7c COUNCIL)

A producer nucleus MUST NOT score its own artifact. Score MUST come from a
peer nucleus or `cex_score.py --apply` deterministic checks. If self-scoring
is detected (frontmatter `quality:` non-null on save), trigger BLOCK.

When `artifact_score >= 9.0` from a single judge: REQUIRE F7c COUNCIL with
N=3 cross-provider judges. Block publication if `divergence_score > 0.3`
(stddev of scores). Surface dissent rationales -- do NOT auto-suppress lone
outliers.

## Actions
| Score | Tier | Action | FAIL trigger |
|-------|------|--------|--------------|
| >= 9.5 | GOLDEN | Exemplar artifact -- reference for builders | F7c divergence > 0.3 -> downgrade to PUBLISH |
| >= 8.0 | PUBLISH | Ready for runtime use | any hard gate fail -> REJECT |
| >= 7.0 | REVIEW | Needs refinement before publish | F6 retry budget exhausted -> escalate to N07 |
| < 7.0  | REJECT | Rework frontmatter, content, or structure | 3+ rejects in session -> quarantine producer |

## Boundary

Quality barrier with numeric score. NOT a validator (P06, technical pass/fail)
nor a scoring_rubric (P07, defines criteria).

## 8F Pipeline Function

Primary function: **GOVERN**

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kind-builder]] | upstream | 0.27 |
| [[bld_config_default]] | upstream | 0.26 |
| [[p11_qg_kind_builder]] | sibling | 0.26 |
| [[bld_instruction_kind]] | upstream | 0.26 |
