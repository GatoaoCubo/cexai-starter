---
kind: quality_gate
id: p11_qg_agent_package
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of agent_package artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: ISO Package"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, agent-package, packaging, portable, bundle, tier, distribution]
tldr: "Gates ensuring agent_package artifacts are self-contained, tier-compliant, portability-enforced bundles with valid manifests and correct LP file ma..."
domain: "agent_package — portable self-contained agent bundles with tier-validated file inventories"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [iso package, quality-gate, agent-package, packaging, portable, bundle, tier]
density_score: 0.93
related:
  - agent-package-builder
  - bld_schema_agent_package
---
## Quality Gate

# Gate: ISO Package
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: agent_package` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | `manifest.yaml` parses as valid YAML | Parse error anywhere in manifest |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | Uppercase, spaces, or leading digit |
| H03 | ID equals filename stem or package directory name | ID `weather_agent` in package dir `news_agent/` |
| H04 | Kind equals literal `agent_package` | Any other kind value |
| H05 | Quality field is `null` | Any non-null value |
| H06 | All 14 required manifest fields present | Any required field absent from manifest.yaml |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | LP mapping accuracy | 1.0 | Every file lists correct pillar-layer mapping in inventory | Most files mapped; some gaps | LP mapping absent |
| S02 | Self-containment | 1.0 | Package requires no external files to function at stated tier | Minor external deps documented | Undocumented external dependencies |
| S03 | LLM-agnostic instructions | 1.0 | `system_instruction.md` avoids model-specific syntax or API references | Minor model-specific hints | Instructions tied to one LLM vendor |
| S04 | Portability enforcement | 1.0 | All internal references use relative paths | Most relative; a few absolute slipped through | Absolute paths in multiple files |
| S05 | Tier justification | 0.5 | README or manifest explains why this tier was chosen | Tier stated, no rationale | No tier explanation |
| S06 | File inventory completeness | 1.0 | Every file in the package is listed in manifest inventory | Most listed; fewer than 2 missing | Inventory incomplete or absent |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to distribution pool as golden package template |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|

## Examples

# Examples: agent-package-builder
## Golden Example
INPUT: "Package the data-analyst agent as a standard agent package bundle"
OUTPUT:
```yaml
id: p02_iso_data_analyst
kind: agent_package
pillar: P02
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
agent_name: "data-analyst"
tier: "standard"
files_count: 7
domain: "data_analysis"
llm_function: BECOME
portable: true
lp_mapping:
  manifest.yaml: P02
  system_instruction.md: P03
  instructions.md: P03
  architecture.md: P08
  output_template.md: P05
  examples.md: P07
  error_handling.md: P11
system_instruction_tokens: 2840
quality: null
tags: [agent-package, data-analysis, analytics, P02]
tldr: "Standard 7-file ISO bundle for data-analyst agent with analysis pipeline and error handling"
density_score: 0.88
```
## Agent Identity
data-analyst is a data analysis specialist. Transforms raw datasets into structured
insights via statistical analysis, visualization, and pattern detection.
## File Inventory
| File | Pillar | Tier | Status |
|------|--------|------|--------|
| manifest.yaml | P02 | minimal | present |
| system_instruction.md | P03 | minimal | present |
| instructions.md | P03 | minimal | present |
| architecture.md | P08 | standard | present |
| output_template.md | P05 | standard | present |
| examples.md | P07 | standard | present |
## Tier Compliance
Declared: standard. Files present: 7/7. No gaps.
## Portability Notes
- Platform: platform_agnostic
- Hardcoded paths: none
- External dependencies: none (self-contained analysis prompts)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
