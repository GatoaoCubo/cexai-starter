---
kind: quality_gate
id: p05_qg_press_release
pillar: P11
llm_function: GOVERN
purpose: "Define hard gates and soft scoring dimensions for press_release quality enforcem"
quality: null
title: "Press Release Quality Gate"
version: "1.0.0"
author: n02_wave6
tags: [press_release, builder, quality_gate]
tldr: "8 hard gates and 5 scored dimensions; minimum 8.0 to publish, 9.5 for golden status"
domain: "press_release construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [press_release construction, press release quality gate, hard gates and, scored dimensions, to publish, for golden status, press_release]
density_score: 0.85
related:
  - bld_schema_press_release
---
## Quality Gate
## Definition
| Property | Value |
|---|---|
| Kind | press_release |
| Pillar | P05 |
| Scorer | cex_score.py |
| Quality floor | 8.0 (PUBLISH threshold) |
| Quality target | 9.0 |
| Golden threshold | 9.5 |
| Max retries | 2 (return to F6 PRODUCE) |
## HARD Gates (all must pass; one failure = REJECT)
| Gate | ID | Check | Pass condition | Failure action |
|---|---|---|---|---|
| YAML valid | H01 | Frontmatter parses without error | No YAML syntax errors | Fix frontmatter, re-run |
| ID pattern | H02 | ID matches regex | ^p05_pr_[a-z][a-z0-9_]+.md$ | Rename artifact |
| Kind correct | H03 | kind field value | kind == "press_release" | Correct kind |
| Headline | H04 | Headline present, character count | Present AND <= 80 chars | Shorten or add headline |
| Dateline | H05 | Dateline format | City in CAPS + AP state abbr + date | Fix dateline format |
| Lede 5Ws | H06 | Lede answers who/what/when/where/why | All 5 Ws detectable in lede | Rewrite lede |
## SOFT Scoring (5 dimensions, weighted to 1.0)
| Dimension | ID | Weight | What is scored | 10/10 example |
|---|---|---|---|---|
| AP style adherence | D01 | 0.25 | Style compliance: attribution verb, number rules, title format, date format, no Oxford comma | Zero AP violations; "said" used; titles before names |
| Headline quality | D02 | 0.25 | Hook strength, active voice, specificity, keyword relevance | Active verb, concrete number or name, no puffery |
| Quote authenticity | D03 | 0.20 | Attribution completeness, quote naturalness, avoidance of marketing-speak | Full name + title + "said"; quote sounds like a human said it |
| Boilerplate completeness | D04 | 0.15 | Company description, third person, present tense, 50-100 words | Covers: what company does, founded when, key differentiator |
| Contact block completeness | D05 | 0.15 | Name, title, email, phone all present | All four fields, phone with area code |

Score formula: (D01 x 0.25) + (D02 x 0.25) + (D03 x 0.20) + (D04 x 0.15) + (D05 x 0.15) = score out of 10.
## Actions by Score
| Score range | Status | Action |
|---|---|---|
| >= 9.5 | GOLDEN | Archive as exemplar in bld_examples_press_release.md |
| >= 8.0 | PUBLISH | Approved for wire service submission |
| >= 7.0 | REVIEW | Return to human editor for revision pass |
| < 7.0 | REJECT | Return to F6 PRODUCE (max 2 retries) |
## Bypass Table
| Bypass condition | Allowed | Notes |
|---|---|---|
| User waives embargo line | YES | User must explicitly confirm "FOR IMMEDIATE RELEASE" intent |
| User waives phone in contact | YES | Email-only contact acceptable if user confirms |
| Headline exceeds 80 chars | NO | Hard gate, no bypass permitted |
| Missing boilerplate | NO | Hard gate, no bypass permitted |
| Missing lede 5Ws | NO | Hard gate, no bypass permitted |
## Examples
## Golden Example
Score: 9.6/10. All H01-H08 gates pass. No AP style violations.

---

FOR IMMEDIATE RELEASE

DATALOOP LAUNCHES AI-POWERED PIPELINE THAT CUTS DATA PREP TIME BY 70%

SAN FRANCISCO, Calif., April 14, 2026 -- DataLoop Inc. today launched
DataLoop Accelerate, an AI-powered data preparation platform that reduces
the time data teams spend on pipeline configuration from hours to minutes,
available immediately to enterprise customers.

DataLoop Accelerate uses large language model inference to automatically
detect schema mismatches, resolve null values, and generate transformation
scripts from natural language descriptions. The platform integrates with
Snowflake, Databricks, and BigQuery out of the box, with no custom
connectors required. Pricing starts at $2,500 per month for teams of up to
20 data engineers.

Early access customers report a 70 percent reduction in data preparation
time across production pipelines. Meridian Analytics, a DataLoop customer
since 2024, reduced its weekly pipeline maintenance from 16 hours to fewer
than five after deploying Accelerate in January 2026.

"Data engineering teams spend more than half their time on undifferentiated
preparation work that adds no analytical value," said Priya Nair, Chief
Executive Officer at DataLoop Inc. "Accelerate changes that equation so
teams can focus on the insights, not the plumbing."

###

About DataLoop Inc.:
DataLoop Inc. builds AI-powered data infrastructure tools for enterprise
analytics teams. Founded in 2021 and headquartered in San Francisco,
DataLoop serves more than 300 enterprise customers across financial
services, healthcare, and technology verticals. The company has raised
$47 million in venture funding and employs 110 people.

Media Contact:
James Ortega
Head of Communications, DataLoop Inc.
james.ortega@dataloop.io
(415) 555-0182

---
### Why this is golden
| Element | Assessment |
|---|---|
| Headline | 63 chars, active voice, concrete "70%" hook, ALL CAPS |
| Dateline | CITY in caps, "Calif." abbreviation, correct date format |
| Lede | 35 words, answers who/what/when/where/why |
| Body | Two solid paragraphs, specific pricing and integration details |
| Quote | Human-sounding, attributed with full name and spelled-out title |
| ### mark | Present |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
