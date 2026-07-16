---
kind: tools
id: bld_tools_opportunity_matrix
pillar: P04
llm_function: CALL
purpose: Tools available for opportunity_matrix production
quality: null
title: "Tools Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, tools]
tldr: "Tool registry for opportunity matrix builder: CEX pipeline tools (compile, score, retrieve), file system ops (Read/Write/Edit/Glob/Grep), and the real generator + capability wiring for scored supplier-cost x market-demand buy/sourcing decisions."
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F5_call"
keywords: [opportunity_matrix construction, tools opportunity matrix, cex pipeline tools, file system ops, opportunity_matrix, builder, tools, sourcing_opportunity generator, capability wiring, production tools]
density_score: 0.85
related:
  - bld_tools_roi_calculator
  - opportunity-matrix-builder
---
## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile artifact after production | F8 COLLABORATE |
| cex_score.py | Score artifact quality (5D dimensions) | F7 GOVERN |
| cex_retriever.py | Retrieve similar opportunity_matrix artifacts for reuse | F3 INJECT |
| cex_doctor.py | Validate builder health, check ISO completeness | F7 GOVERN |

## Runtime Reference (the real generator this builder documents)
| Component | Path | Note |
|-----------|------|------|
| Generator | `_tools/capability_generators/sourcing_opportunity.py` | `@register("opportunity_matrix")`; offline-deterministic, never raises |
| Capability wiring | `_tools/cex_run_capability.py` | slug `sourcing_opportunity` -> (N06, opportunity_matrix, P11, analyze) |
| Frozen I/O shape | `apps/dashboard_web/lib/molds.ts` | MOLD_SOURCING_OPPORTUNITY (9 inputs, 8 sections) |
| Contract summary | `apps/dashboard_web/lib/capability_contracts_v1.0.md` | Section 15 |
| CLI entry | `.claude/commands/sourcing.md` | `/sourcing <catalog_dir\|sources> [params]` |
| Offline pytest | `_tools/tests/test_capgen_sourcing.py` | shape + honesty checks (read-only reference; do not edit) |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | Structural YAML + frontmatter validation | Post-production |
| cex_hooks.py | Pre-commit ASCII and schema checks | Pre-commit |

## Domain-Rigor References
- `_docs/specs/contract/n01_sourcing_rigor.md` -- S1-S5 invariants (triangulation, provenance, freshness, gate, honest-null)
- `_docs/specs/contract/n06_unit_econ.md` -- cited for the general cost->price->take-rate->margin discipline (its own LTV/CAC section bundle targets other kinds, not this one)
- `_docs/specs/contract/n06_benchmark.md` -- cited for the weighted-ranking-surface principle (opp_score); its own section bundle targets competitor_benchmark
- `_docs/specs/contract/n03_schema.md` -- closed type vocabulary for the input_contract

## CEX Pipeline Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile .md artifact to .yaml | After Write (F8) |
| cex_score.py | Peer-review quality scoring | After production (F7) |
| cex_retriever.py | Discover similar artifacts by TF-IDF | During F3 INJECT |
| cex_doctor.py | Health check builder ISOs | Before dispatch |

## Data Sources
| Source | Content | When to use |
|--------|---------|-------------|
| SCHEMA.md | Field definitions, ID pattern, constraints | Every production run |
| OUTPUT_TEMPLATE.md | Exact frontmatter + body structure | Every production run |
| QUALITY_GATES.md | H01-H08 HARD gates | Every validation run |
| KNOWLEDGE.md | Domain concepts for opportunity matrix | When designing structure |
| MEMORY.md | Common mistakes, anti-patterns | When stuck or producing a variant |

## Tool Permissions
| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Properties
| Property | Value |
|----------|-------|
| Kind | `tools` |
| Pillar | P04 |
| Domain | opportunity matrix construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_roi_calculator]] | sibling | 0.52 |
| [[opportunity-matrix-builder]] | related | 0.45 |
| sourcing | related | 0.40 |
| p08_adr_opportunity_matrix_kind | upstream | 0.38 |
| [[bld_prompt_opportunity_matrix]] | related | 0.35 |
