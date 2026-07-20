---
id: p12_tc_deep_research_v1
kind: team_charter
pillar: P12
llm_function: COLLABORATE
charter_id: deep_research_template
crew_template_ref: p12_ct_deep_research.md
mission_statement: "Produce a fact-validated research brief on {{RESEARCH_TOPIC}}, grounded on >= {{MIN_SOURCES}} independent sources, with overall claim confidence >= {{CONFIDENCE_FLOOR}} and final quality >= {{QUALITY_GATE}}."
quality_gate: 9.0
deadline: "{{DEADLINE}}"
deliverables:
  - "Raw findings KC (knowledge_card P01) -- scout output with >= 5 cited sources"
  - "Structured analysis KC (knowledge_card P01) -- analyst output with patterns/gaps identified, quality >= 8.5"
  - "Validation report -- fact_checker output with per-claim confidence scores, overall >= {{CONFIDENCE_FLOOR}}"
  - "Final research brief (analyst_briefing P05) -- writer output, executive summary + findings + recommendations, quality >= {{QUALITY_GATE}}"
budget:
  tokens: "{{BUDGET_TOKENS}}"
  wall_clock_seconds: "{{BUDGET_WALL_CLOCK_SECONDS}}"
  usd: "{{BUDGET_USD}}"
domain_focus: "{{RESEARCH_TOPIC}}"
stakeholders: ["n01_intelligence", "n07_orchestrator"]
escalation_protocol: "If any role crosses its token or wall-clock ceiling, or fails 2 consecutive revision cycles, emit signal_{role}_escalate.json to .cex/runtime/signals/. N01 reads and either extends budget (with justification) or kills the crew and archives partial work."
termination_criteria: "ANY of: (1) writer emits a brief that clears p11_qg_research_n01.md and the quality_gate floor; (2) fact_checker overall confidence stays below {{CONFIDENCE_FLOOR}} after 2 consecutive analyst revisions (stuck loop -- escalate, do not force-pass); (3) token or wall-clock budget exhausted; (4) deadline passed."
quality: null
keywords: [knowledge_card, analyst_briefing, validation_report, confidence_floor, a2a-task, token budget, wall-clock, escalation protocol, open_vars, template]
density_score: 0.90
title: "Team Charter Template -- Deep Research"
version: "1.0.0"
tags: [team_charter, deep_research, intelligence, template]
tldr: "Fill-in-the-blanks mission contract for the deep_research crew. Copy this file per instance and replace every {{open_var}} before dispatch."
domain: "deep research governance"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p12_ct_deep_research
  - p02_ra_scout
  - p02_ra_deep_analyst
  - p02_ra_fact_checker
  - p02_ra_research_writer
---

## Mission Statement

Produce a fact-validated research brief on **{{RESEARCH_TOPIC}}**, grounded on
>= **{{MIN_SOURCES}}** independent sources, with overall claim confidence >=
**{{CONFIDENCE_FLOOR}}** (fact_checker-attested) and final quality >=
**{{QUALITY_GATE}}** as measured by `p11_qg_research_n01.md`.

## Open Variables (fill before dispatch)

| Variable | Type | Example | Notes |
|----------|------|---------|-------|
| `{{RESEARCH_TOPIC}}` | string | "on-device LLM inference costs" | Becomes `domain_focus` and the scout's search anchor |
| `{{MIN_SOURCES}}` | integer | `5` | Floor for the scout's raw_findings citation count |
| `{{CONFIDENCE_FLOOR}}` | float | `0.65` | fact_checker blocks the writer below this overall confidence |
| `{{QUALITY_GATE}}` | float | `9.0` or `9.5` | Overrides the `quality_gate:` frontmatter default (9.0) if different |
| `{{DEADLINE}}` | ISO-8601 datetime | `2026-08-15T18:00:00-03:00` | Hard stop; see Termination Criteria |
| `{{BUDGET_TOKENS}}` | integer | `140000` | Total across all 4 roles (recommend 35000/role ceiling) |
| `{{BUDGET_WALL_CLOCK_SECONDS}}` | integer | `2400` | 4 roles x 600s avg is a reasonable starting point |
| `{{BUDGET_USD}}` | float | `4.50` | Rough estimate at your provider's blended token pricing |

## Deliverables

1. Raw findings KC (`knowledge_card` under P01) -- scout output; >= `{{MIN_SOURCES}}` sources, source URLs required
2. Structured analysis KC (`knowledge_card` under P01) -- analyst output; patterns/gaps identified, quality >= 8.5
3. Validation report -- fact_checker output; per-claim confidence scores, overall >= `{{CONFIDENCE_FLOOR}}`
4. Final research brief (`analyst_briefing` under P05) -- writer output; follows executive-summary-first structure; `quality >= {{QUALITY_GATE}}`

## Success Metrics

- Each deliverable quality >= `{{QUALITY_GATE}}` (floor 8.0 for intermediate deliverables)
- fact_checker overall confidence >= `{{CONFIDENCE_FLOOR}}` before the writer proceeds
- Wall-clock under `{{BUDGET_WALL_CLOCK_SECONDS}}` for the full crew
- Token budget under `{{BUDGET_TOKENS}}` total
- All 4 a2a-task handoff signals present and archived
- Zero unresolved `[LOW CONFIDENCE]` tags left unaddressed in the final brief

## Budget

- Tokens: `{{BUDGET_TOKENS}}` total (hard ceiling)
- Wall-clock: `{{BUDGET_WALL_CLOCK_SECONDS}}` seconds
- USD: `{{BUDGET_USD}}` (estimate at your provider's blended pricing)

## Configuration

- `domain_focus` / `{{RESEARCH_TOPIC}}`: the topic, technology, or question to research
- `{{MIN_SOURCES}}`: raise for a high-stakes brief, lower for an exploratory scan
- `{{CONFIDENCE_FLOOR}}`: default 0.65; raise to 0.80 for claims that will ship externally
- `quality_gate`: default 9.0; raise to 9.5 for a brief that ships externally

## Stakeholders

- n01_intelligence (nucleus that owns the crew instance -- executes + monitors)
- n07_orchestrator (dispatches, monitors signals, consolidates on completion)
- Consumer of output: specified per run (any requesting nucleus, or a direct user)

## Escalation Protocol

If any role crosses its token or wall-clock ceiling, or if the same artifact
fails a revision cycle twice consecutively, emit `signal_{role}_escalate.json`
to `.cex/runtime/signals/`. N01 reads and either extends budget (with
justification logged) or kills the crew and archives partial work.

## Termination Criteria

ANY of:
1. writer emits a brief that clears `p11_qg_research_n01.md` and the `{{QUALITY_GATE}}` floor (normal completion)
2. fact_checker overall confidence stays below `{{CONFIDENCE_FLOOR}}` after 2 consecutive analyst revisions (stuck loop -- escalate, never force-pass)
3. Token or wall-clock budget exhausted (partial work archived)
4. `{{DEADLINE}}` passed

## Instantiation (copy this file per run)

```bash
# 1. Copy this template and fill every {{open_var}}
cp N01_intelligence/P12_orchestration/crews/p12_tc_deep_research_v1.md \
   N01_intelligence/P12_orchestration/crews/p12_tc_deep_research_{{instance_slug}}.md

# 2. Dry run (inspect resolved plan)
python _tools/cex_crew.py show deep_research

# 3. Live run with the filled-in charter
python _tools/cex_crew.py run deep_research \
    --charter N01_intelligence/P12_orchestration/crews/p12_tc_deep_research_{{instance_slug}}.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_deep_research]] | parent | 0.55 |
| [[p02_ra_scout]] | related | 0.38 |
| [[p02_ra_deep_analyst]] | related | 0.38 |
| [[p02_ra_fact_checker]] | related | 0.38 |
| [[p02_ra_research_writer]] | related | 0.38 |
