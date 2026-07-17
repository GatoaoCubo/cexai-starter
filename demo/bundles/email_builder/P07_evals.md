---
id: p11_qg_prompt_template
kind: quality_gate
pillar: P11
llm_function: GOVERN
domain: prompt_template
version: 1.0.0
created: '2026-03-27'
updated: '2026-07-04'
author: builder
tags:
- eval
- P11
- quality_gate
- examples
quality: null
title: 'Gate: Prompt Template'
tldr: Quality gate for reusable prompt molds with typed {{variables}}, injection points,
  and composable structure.
8f: "F7_govern"
density_score: 0.85
---
## Quality Gate

## Definition
A prompt template is a reusable text mold containing one or more `{{variable}}` placeholders filled at invocation time. It declares where in the conversation it is injected (system or user turn), documents each variable's type and constraints, and provides at least one complete invocation example with all slots filled.
Scope: files with `kind: prompt_template`. Does not apply to system prompts (fixed text, no slots) or instruction files (behavioral rules, no variable slots).
## HARD Gates
Failure on any single gate means REJECT regardless of soft score.
> Renumbered 2026-07-04 (R-262a) to match the canonical H01-H06 sequence in
> `.claude/rules/8f-reasoning.md` and the actual gate order in `_tools/cex_8f_runner.py`
> (H02 id pattern, H03 kind match, H04 quality null, H05 required fields, H06 body size).
> The previous numbering inserted an extra "id == filename stem" gate as its own H03,
> shifting everything down and repurposing H06 for the required-fields check instead of
> body size -- same drift class R-259 found in bld_eval_benchmark.md / bld_eval_guardrail.md.
> `id == filename stem` is folded into H02 below (both are id-validity concerns).
| ID  | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `id` matches namespace `p03_pt_*` AND `id` equals filename stem | `id.startswith("p03_pt_")` is true AND `Path(file).stem == id` |
| H03 | `kind` equals literal `prompt_template` | string equality check |
| H04 | `quality` is null at authoring time | `quality is None` |
| H05 | All enforced frontmatter fields present and non-empty | id, kind, pillar, version, quality, tags, created, tldr all present -- see `bld_schema_prompt_template.md` Recommended tier for the 7 soft-tier fields (title, updated, author, variables, variable_syntax, composable, domain) |
| H06 | Body size within limit | `len(body.encode('utf-8')) <= 8192` (max_bytes per bld_schema_prompt_template.md Constraints) |
## SOFT Scoring
Score each dimension 0 (absent or fails) to 1 (present and passes). Weights are 0.5 or 1.0.
| #  | Dimension | Weight |
|----|-----------|--------|
| 1  | `density_score` field present and >= 0.80 | 1.0 |
| 2  | Every variable has at least one constraint (enum, regex, max_len, or range) | 1.0 |
| 3  | Syntax is uniform throughout (all `{{}}` Mustache or all `[]` bracket, never mixed) | 1.0 |
| 4  | Complete invocation example present with every variable slot filled | 1.0 |
| 5  | Default values documented for all optional variables | 0.5 |
| 6  | Tags list includes `prompt-template` | 0.5 |
**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`
Weight total: 9.0. Each dimension contributes proportionally. Score range: 0.0 to 10.0.
## Actions
| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish to pool as golden; add to curated prompt library |
| PUBLISH | >= 8.0 | Publish to pool; mark production-ready |
| REVIEW | >= 7.0 | Return to author with scored dimension feedback; one revision cycle allowed |
| REJECT | < 7.0 | Block from pool; full rewrite required before re-evaluation |
## Bypass
| Field | Value |
|-------|-------|
| condition | Template is a one-off migration aid with a documented lifespan under 30 days |
| approver | Domain lead must approve in writing before bypass takes effect |
| audit_log | Record in `artifacts/audits/bypasses.md` with date, approver, and reason |
| expiry | 30 days from bypass grant; template must be retired or brought to full compliance |

## Examples

# Examples — prompt-template-builder
## Golden Example
A complete, valid `prompt_template` artifact with 19+ fields.
```yaml
id: p03_pt_knowledge_card_production
kind: prompt_template
pillar: P03
title: "Knowledge Card Production Template"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: knowledge-engine
```
You are a knowledge synthesis expert. Produce a knowledge card for the following topic.
Topic: `{{topic}}`
Domain: `{{domain}}`
Audience level: `{{audience}}`
Maximum sections: `{{max_sections}}`
Include examples: `{{include_examples}}`
Source references: `{{source_refs}}`
Structure your output as follows:
1. TLDR (1 sentence)
2. Core Definition (2-3 sentences, precise, domain-apownte)
3. Key Concepts (up to `{{max_sections}}` bullet points)
4. Relationships (how `{{topic}}` connects to adjacent concepts in `{{domain}}`)
5. Common Misconceptions (2-3 items, audience-calibrated for `{{audience}}`)
{{#include_examples}}
6. Concrete Examples (2-3 examples grounded in `{{domain}}`)
{{/include_examples}}
7. References: `{{source_refs}}`
Calibrate terminology and depth for a `{{audience}}`-level reader in `{{domain}}`.
```

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
