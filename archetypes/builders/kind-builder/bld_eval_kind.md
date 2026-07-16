---
kind: quality_gate
id: p11_qg_kind_builder
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of builder package scaffolding
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: kind_builder"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, kind-builder, meta-builder, architecture, iso, P11]
tldr: "Gates for builder packages: validates 13-file completeness, frontmatter consistency, quality:null, naming, sub-agent."
domain: "kind_builder -- meta-builder that produces complete 13-ISO builder packages for any CEX kind"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
density_score: 0.92
related:
  - bld_schema_kind
  - kind-builder
  - bld_instruction_kind
  - bld_architecture_kind
  - bld_schema_quality_gate
---
## Quality Gate
# Gate: kind_builder
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All builder packages at archetypes/builders/{kind}-builder/ |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | Directory contains exactly 13 bld_*.md files | "Incomplete package: {N}/13 ISOs found" |
| H02 | All 13 files have parseable YAML frontmatter | "ISO {file} has invalid YAML frontmatter" |
| H03 | All 13 files have quality: null in frontmatter | "ISO {file} has quality != null (never self-score)" |
| H04 | All file names match bld_{iso_type}_{kind}.md pattern | "File {file} does not match naming pattern" |
| H05 | Sub-agent file exists at .claude/agents/{kind}-builder.md | "Sub-agent definition missing" |
| H06 | bld_manifest has >= 4 capabilities listed | "Manifest has fewer than 4 capabilities" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Internal consistency | 1.5 | Schema fields match template vars match gate checks |
| Boundary clarity | 1.0 | IS/IS NOT boundaries in schema, KC, and architecture |
| Domain specificity | 1.5 | Content is specific to the target kind, not generic builder text |
| Cross-referencing | 1.0 | Related kinds from same pillar are mentioned and differentiated |
| Golden example quality | 1.0 | Golden example passes all HARD gates listed in quality_gate ISO |
| Instruction completeness | 1.0 | 3 phases with >= 5 steps each, covering research/compose/validate |
Weight sum: 1.5+1.0+1.5+1.0+1.0+1.0+0.5+0.5+0.5+0.5 = 9.0
Normalize: multiply final by 10/9 to reach 10.0 scale.
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish as reference builder for future kind-builder runs |
| >= 8.0 | PUBLISH | Builder is functional, ready for dispatch |
| >= 7.0 | REVIEW | Flag for manual review before first use |
| < 7.0 | REJECT | Return to kind-builder with failure report |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Experimental kind with no established domain knowledge yet |
| approver | N07 orchestrator approval required; quality: null still mandatory |
## Examples
# Examples: kind-builder
## Golden Example
INPUT: "Create builder for kind: env_config (P09, GOVERN)"
OUTPUT (manifest ISO only -- showing quality standard for all 13):
```yaml
---
id: env-config-builder
kind: type_builder
pillar: P09
parent: null
domain: env_config
llm_function: GOVERN
version: 1.0.0
```
WHY THIS IS GOLDEN:
- quality: null (H01 pass -- never self-scored)
- kind: type_builder (H02 pass -- correct meta-kind)
- All required frontmatter fields present (H03 pass)
- 6 capabilities listed, each specific to the domain (H04 pass)
## Complete Package Checklist (all 13 files for env-config-builder)
| # | File | Exists | quality: null | Domain content |
|---|------|--------|---------------|----------------|
| 1 | bld_manifest_env_config.md | YES | YES | env_config identity + 6 capabilities |
| 2 | bld_schema_env_config.md | YES | YES | 15+ frontmatter fields + 4 body sections |
| 3 | bld_system_prompt_env_config.md | YES | YES | 13 rules for env_config production |
| 4 | bld_instruction_env_config.md | YES | YES | 3-phase process with 20+ steps |
| 5 | bld_output_template_env_config.md | YES | YES | YAML template + 4 body section templates |
| 6 | bld_examples_env_config.md | YES | YES | Golden + anti with gate analysis |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
