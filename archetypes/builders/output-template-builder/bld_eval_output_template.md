---
kind: quality_gate
id: p11_qg_output_template
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of output_template artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: Output Template"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, output-template, reflexive-iso9, naming-drift, recurring-document]
tldr: "Gates ensuring output_template artifacts declare which usage (reflexive vs broader) they serve, follow the canonical id pattern for new work, and disclose naming drift rather than silently blessing it."
domain: "output_template -- reflexive ISO#9 self-typing + broader recurring-output-document scaffold"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F7_govern"
keywords: [naming discrepancy, output template, reflexive usage, quality-gate, output-template, iso9, canonical id pattern]
density_score: 0.87
related:
  - bld_schema_output_template
---
## Quality Gate

# Gate: Output Template
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: output_template` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^bld_output_template_[a-z][a-z0-9_]+$` for NEW reflexive-usage artifacts | Wrong prefix on a NEW ISO#9-typed artifact (FORWARD-ONLY -- does not retroactively invalidate the 18 pre-existing broader-usage instances) |
| H03 | kind equals literal `output_template` | Any other kind value |
| H04 | pillar equals `P05` | Any other pillar (1/18 real instances drifted to P12 -- not repeated in new work) |
| H05 | Quality field is `null` | Any non-null value |
| H06 | `depends_on` equals `[]` | Any populated dependency list |
| H07 | Body states explicitly which usage (reflexive/broader) this instance serves | Ambiguous -- reader cannot tell if this is a blank scaffold or a completed report |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Usage clarity | 1.0 | Reflexive vs broader stated unambiguously, matching the actual body shape | Implied but not stated | Body shape contradicts an explicit usage claim |
| S02 | Naming drift honesty | 1.0 | Broader-usage id disclosed against Convention A/B/C explicitly; reflexive-usage id matches canonical pattern | Convention followed but not disclosed | A 4th, undocumented convention invented silently |
| S03 | depends_on discipline | 0.5 | `[]`, unmodified | -- | Populated without a kinds_meta.json edit |
| S04 | Template-vs-report honesty | 1.0 | A blank scaffold uses `{{var}}` markers throughout; a completed-report instance narrates real content, never fake placeholders | Mixed signals | A "template" with fabricated example data presented as real |
| S05 | Reflexive-case fidelity (when applicable) | 1.0 | Every field in the reflexive template traces to the target kind's own `bld_schema_{{kind}}.md` | Mostly traced, 1-2 gaps | Invented fields with no schema source |
| S06 | Examples + Related Artifacts | 1.0 | At least 2 examples (one per usage where relevant) + Related Artifacts resolving to REAL artifacts | One present | No examples; fabricated wikilinks |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to pool as golden output_template contract |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | The target kind (reflexive case) is itself mid-design and its own schema is not yet stable |
| Approver | Owner agent lead |
| Audit trail | `bypass_reason` + `draft: true` both required in frontmatter |
| Expiry | Draft status expires after 14 days; must reach H-gate compliance or be deprecated |

## Examples

# Examples: output-template-builder
## Golden Example 1 -- Reflexive Usage
INPUT: "Scaffold the ISO#9 output template for a new kind `sourcing_lead`"
OUTPUT (frontmatter only, body omitted for length):
```yaml
id: bld_output_template_sourcing_lead
kind: output_template
pillar: P05
llm_function: PRODUCE
purpose: "Template with {{vars}} that the LLM fills to produce a sourcing_lead artifact"
pattern: "every field here exists in SCHEMA.md -- template derives, never invents"
quality: null
title: "Output Template Sourcing Lead"
version: "1.0.0"
domain: "sourcing lead construction"
depends_on: []
tags: [sourcing_lead, builder, examples]
tldr: "Fill-in-the-blank shape for sourcing_lead artifacts, mirroring bld_schema_sourcing_lead.md exactly."
```
WHY THIS IS GOLDEN:
- id matches canonical pattern `^bld_output_template_[a-z][a-z0-9_]+$` (H02 pass)
- kind: output_template, pillar: P05 (H03/H04 pass)
- quality: null (H05 pass)
- usage stated explicitly as reflexive in the `purpose` field (H07 pass)

## Golden Example 2 -- Broader Usage
INPUT: "Create an output_template scaffold for N05's weekly test-coverage report"
OUTPUT:
```yaml
id: n05_output_test_coverage_report
kind: output_template
pillar: P05
title: "Weekly Test Coverage Report -- Output Scaffold"
version: "1.0.0"
author: "n05_operations"
domain: "test-coverage-reporting"
quality: null
depends_on: []
tags: [output, test-coverage, report, n05]
tldr: "Scaffold for the recurring weekly test-coverage report; follows drift Convention B ({nucleus}_output_{name}) explicitly, disclosed."
```
WHY THIS IS GOLDEN:
- depends_on: [] (H06 pass)
- id explicitly follows Convention B (`{nucleus}_output_{name}`), disclosed in the tldr rather
  than silently presented as canonical (S02 = 10pts)
- usage stated explicitly as a broader recurring-document scaffold (H07 pass)

## Anti-Example -- Silently Blessed Drift (REJECTED)
INPUT: same as Golden Example 2
BAD OUTPUT: an id of `n05_output_test_coverage_report` presented with NO disclosure that
this deviates from the canonical `bld_output_template_{{kind}}` pattern, and no mention of
Convention A/B/C anywhere in the artifact or its authoring notes.
WHY THIS FAILS: S02 = 0pts -- this is precisely "silently blessing the drift" that register
row R-299 explicitly forbids; the convention choice must be disclosed, not just used.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_output_template]] | sibling | 0.44 |
| [[bld_schema_output_template]] | sibling | 0.42 |
| [[bld_knowledge_output_template]] | sibling | 0.40 |
| p11_qg_field_manifest | related | 0.36 |
