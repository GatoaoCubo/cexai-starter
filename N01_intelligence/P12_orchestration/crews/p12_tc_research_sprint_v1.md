---
id: p12_tc_research_sprint_v1
kind: team_charter
pillar: P12
llm_function: COLLABORATE
charter_id: research_sprint_template
crew_template_ref: p12_ct_research_sprint.md
mission_statement: "Produce a validated research brief on {{RESEARCH_TOPIC}}, grounded on >= {{MIN_SOURCES}} independent sources, with quality >= {{QUALITY_GATE}}."
quality_gate: 8.5
deadline: "{{DEADLINE}}"
deliverables:
  - "Raw findings KC (knowledge_card P01) -- scout output with >= 5 cited sources"
  - "Structured findings KC (knowledge_card P01) -- analyst output with >= 2 patterns or gaps identified"
  - "Final research brief (knowledge_card P01) -- synthesizer output following p03_pt_research_brief.md, quality >= 8.5"
budget:
  tokens: "{{BUDGET_TOKENS}}"
  wall_clock_seconds: "{{BUDGET_WALL_CLOCK_SECONDS}}"
  usd: "{{BUDGET_USD}}"
domain_focus: "{{RESEARCH_TOPIC}}"
stakeholders: ["n01_intelligence", "n07_orchestrator"]
escalation_protocol: "If any role crosses its token or wall-clock ceiling, or fails 2 consecutive revision cycles, emit signal_{role}_escalate.json to .cex/runtime/signals/. N01 reads and either extends budget (with justification) or kills the crew and archives partial work."
termination_criteria: "ANY of: (1) synthesizer emits a brief that clears p11_qg_research_n01.md and the quality_gate floor; (2) token or wall-clock budget exhausted; (3) deadline passed; (4) 2 consecutive quality-gate rejections on the same artifact (stuck loop)."
quality: null
keywords: [knowledge_card, research brief, a2a-task, token budget, wall-clock, escalation protocol, open_vars, template]
density_score: 0.90
title: "Team Charter Template -- Research Sprint"
version: "1.0.0"
tags: [team_charter, research_sprint, intelligence, template]
tldr: "Fill-in-the-blanks mission contract for the research_sprint crew. Copy this file per instance and replace every {{open_var}} before dispatch."
domain: "research sprint governance"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p12_ct_research_sprint
  - p02_ra_scout
  - p02_ra_analyst
  - p02_ra_synthesizer
  - p11_qg_research_n01
---

## Mission Statement

Produce a validated research brief on **{{RESEARCH_TOPIC}}**, grounded on
>= **{{MIN_SOURCES}}** independent sources, with final quality >=
**{{QUALITY_GATE}}** as measured by `p11_qg_research_n01.md`.

## Open Variables (fill before dispatch)

| Variable | Type | Example | Notes |
|----------|------|---------|-------|
| `{{RESEARCH_TOPIC}}` | string | "open-source agent framework landscape" | Becomes `domain_focus` and the scout's search anchor |
| `{{MIN_SOURCES}}` | integer | `5` | Floor for the scout's raw_findings citation count |
| `{{QUALITY_GATE}}` | float | `8.5` or `9.0` | Overrides the `quality_gate:` frontmatter default (8.5) if different |
| `{{DEADLINE}}` | ISO-8601 datetime | `2026-08-15T18:00:00-03:00` | Hard stop; see Termination Criteria |
| `{{BUDGET_TOKENS}}` | integer | `90000` | Total across all 3 roles (recommend 30000/role ceiling) |
| `{{BUDGET_WALL_CLOCK_SECONDS}}` | integer | `2100` | 3 roles x 700s avg is a reasonable starting point |
| `{{BUDGET_USD}}` | float | `3.00` | Rough estimate at your provider's blended token pricing |

## Deliverables

1. Raw findings KC (`knowledge_card` under P01) -- scout output; >= `{{MIN_SOURCES}}` sources, source URLs required
2. Structured findings KC (`knowledge_card` under P01) -- analyst output; >= 2 patterns or gaps identified
3. Final research brief (`knowledge_card` under P01) -- synthesizer output; follows `p03_pt_research_brief.md`; `quality >= {{QUALITY_GATE}}`

## Success Metrics

- Each deliverable quality >= `{{QUALITY_GATE}}` (floor 8.0 for intermediate deliverables)
- Wall-clock under `{{BUDGET_WALL_CLOCK_SECONDS}}` for the full crew
- Token budget under `{{BUDGET_TOKENS}}` total
- All 3 a2a-task handoff signals present and archived
- Zero unresolved `[unverified]` tags in the final brief

## Budget

- Tokens: `{{BUDGET_TOKENS}}` total (hard ceiling)
- Wall-clock: `{{BUDGET_WALL_CLOCK_SECONDS}}` seconds
- USD: `{{BUDGET_USD}}` (estimate at your provider's blended pricing)

## Configuration

- `domain_focus` / `{{RESEARCH_TOPIC}}`: the market, technology, or question to research
- `{{MIN_SOURCES}}`: raise for a high-stakes brief, lower for an exploratory scan
- `quality_gate`: default 8.5; raise to 9.0 for a brief that ships externally

## Stakeholders

- n01_intelligence (nucleus that owns the crew instance -- executes + monitors)
- n07_orchestrator (dispatches, monitors signals, consolidates on completion)
- Consumer of output: specified per run (any requesting nucleus, or a direct user)

## Escalation Protocol

If any role crosses its token or wall-clock ceiling, or if the same artifact
fails the quality gate twice consecutively, emit
`signal_{role}_escalate.json` to `.cex/runtime/signals/`. N01 reads and
either extends budget (with justification logged) or kills the crew and
archives partial work.

## Termination Criteria

ANY of:
1. Synthesizer emits a brief that clears `p11_qg_research_n01.md` and the `{{QUALITY_GATE}}` floor (normal completion)
2. Token or wall-clock budget exhausted (partial work archived)
3. `{{DEADLINE}}` passed
4. 2 consecutive quality-gate rejections on the same artifact (stuck revision loop)

## Instantiation (copy this file per run)

```bash
# 1. Copy this template and fill every {{open_var}}
cp N01_intelligence/P12_orchestration/p12_tc_research_sprint_v1.md \
   N01_intelligence/P12_orchestration/p12_tc_research_sprint_{{instance_slug}}.md

# 2. Dry run (inspect resolved plan)
python _tools/cex_crew.py show research_sprint

# 3. Live run with the filled-in charter
python _tools/cex_crew.py run research_sprint \
    --charter N01_intelligence/P12_orchestration/p12_tc_research_sprint_{{instance_slug}}.md \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_research_sprint]] | parent | 0.55 |
| [[p02_ra_scout]] | related | 0.40 |
| [[p02_ra_analyst]] | related | 0.40 |
| [[p02_ra_synthesizer]] | related | 0.40 |
| [[p11_qg_research_n01]] | downstream | 0.34 |
