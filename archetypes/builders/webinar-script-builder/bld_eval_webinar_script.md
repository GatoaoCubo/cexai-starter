---
kind: quality_gate
id: p03_qg_webinar_script
pillar: P11
llm_function: GOVERN
purpose: "Define HARD gates and SOFT scoring dimensions for webinar_script quality enforce"
quality: null
title: "Webinar Script Quality Gate"
version: "1.0.0"
author: n02_wave6
tags: [webinar_script, builder, quality_gate]
tldr: "8 hard gates and 5 scored dimensions for webinar_script artifacts. Minimum publish score: 8.0."
domain: "webinar_script construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [webinar_script construction, webinar script quality gate, hard gates and, minimum publish score, webinar_script, builder, quality_gate]
density_score: 0.85
related:
  - bld_instruction_webinar_script
  - bld_schema_webinar_script
  - webinar-script-builder
  - p10_lr_webinar_script_builder
  - p11_qg_quality_gate
---
## Quality Gate
## Definition
| Property | Value |
|---------|-------|
| Kind | quality_gate |
| Target kind | webinar_script |
| Gate count | 8 HARD + 5 SOFT dimensions |
| Publish floor | 8.0 / 10.0 |
| Golden threshold | 9.5 / 10.0 |
| Scorer | cex_score.py |
| Retry limit | 2 retries before REJECT |
## HARD Gates (all must pass -- any failure = BLOCK)
| Gate | ID | Check | Pass Condition | Failure Action |
|------|----|-------|---------------|---------------|
| YAML valid | H01 | frontmatter parses without error | All fields present and typed correctly | Return to F6 |
| ID pattern | H02 | id field matches regex | ^p03_ws_[a-z][a-z0-9_]+$ | Return to F6 |
| Kind correct | H03 | kind field value | Exactly "webinar_script" | Return to F6 |
| Hook present | H04 | First section contains hook | Hook statement in section 1, <= 150 words | Return to F6 |
| Agenda section | H05 | Second section exists | Contains 3+ agenda items and Q&A timing | Return to F6 |
| Value segment | H06 | At least one content segment | Contains speaker content + [SLIDE X] cue | Return to F6 |
## SOFT Scoring Dimensions (weighted to 10.0)
| Dimension | ID | Weight | What Is Scored | Score Criteria |
|-----------|-----|--------|---------------|---------------|
| Hook strength | D01 | 0.25 | Attention capture in first 60 sec | 10=benefit stated in sentence 1, hook framework applied; 7=benefit stated but no framework; 5=vague opener; 3=company bio opener |
| Segment structure | D02 | 0.20 | Timed clarity and flow across segments | 10=all segments timed, [SLIDE] and [SPEAKER NOTE] in every segment; 7=most cues present; 5=some cues missing; 3=unstructured prose |
| Demo narration | D03 | 0.20 | Slide cue completeness and demo precision | 10=step-by-step cues, fallback note, screen cues present; 7=steps present, no fallback; 5=demo section present but vague; 3=no demo narration |
| Q&A preparation | D04 | 0.15 | Seed question quality and facilitator script | 10=3+ seeds, moderator intro, graceful close line; 7=3 seeds, no moderator intro; 5=2 seeds only; 3=no seeds |
| CTA clarity | D05 | 0.20 | Conversion strength of closing CTA | 10=action named, URL present, benefit restated, urgency element; 7=action and URL, no benefit; 5=action only, no URL; 3=vague close |
**Formula**: `score = (D01 * 0.25) + (D02 * 0.20) + (D03 * 0.20) + (D04 * 0.15) + (D05 * 0.20)`
## Actions Table
| Score | Label | Action |
|-------|-------|--------|
| >= 9.5 | GOLDEN | Publish + add to examples as golden reference |
| >= 8.0 | PUBLISH | Publish to artifacts directory |
| >= 7.0 | REVIEW | Return to builder with specific feedback |
| < 7.0 | REJECT | Block publish, mandatory rebuild |
## Bypass Table
Bypass is not available for webinar scripts. Live delivery stakes require all gates.
| Gate | Bypassable | Reason |
|------|-----------|--------|
| H01 YAML | NO | Structural integrity |
| H02 ID | NO | Naming convention |
| H03 Kind | NO | Type safety |
| H04 Hook | NO | Audience retention critical |
| H05 Agenda | NO | Attendee orientation critical |
| H06 Segment | NO | Content delivery required |
## Retry Protocol
1. First failure: return to F6 with specific gate failure listed.
2. Second failure: return to F4 REASON -- rebuild plan may be flawed.
3. Third failure: escalate to REJECT. Do not publish below floor.
## Examples
## Golden Example
**Score**: 9.6 / 10.0 | **Kind**: webinar_script | **ID**: p03_ws_saas_product_demo
**Context**: 60-minute SaaS product demo webinar targeting operations managers. Goal: trial sign-ups.
**Why it scores GOLDEN:**
- Hook states attendee benefit in sentence 1 with a quantified outcome ("cut onboarding time by 50%")
- Agenda lists exactly 3 items with Q&A timing stated upfront
- Each segment has [SLIDE X] cues and [SPEAKER NOTE] instructions
- Demo includes step-by-step narration and a live-fail fallback note
**Excerpt (Hook section)**:
```
## [0:00] HOOK / OPENING (60 sec)
[SLIDE 1: Title Slide]
Speaker: "By the end of this session, you will have a repeatable onboarding workflow
that cuts new-hire ramp time by 50% -- without adding a single headcount to your ops team.
I am going to show you exactly how 140 teams did it last quarter. Let's get started."
[SPEAKER NOTE: Deliver this from memory. No notes. High energy. Pause after "50%".]
```
**Excerpt (Q&A section)**:
```
## [50:00] Q&A FACILITATION (10 min)
[SLIDE 8: Q&A]
Moderator: "We are opening Q&A now. Sarah, first question from the chat --"
Seed Question 1: "How long does implementation typically take for a team of 20?"
Suggested direction: Typical 2-week setup, highlight onboarding specialist support.
Seed Question 2: "Does this integrate with our existing HRIS tools?"
Suggested direction: Native integrations with Workday, BambooHR, ADP -- see integration page.
Seed Question 3: "What happens to our data if we cancel?"
Suggested direction: Full data export, 30-day retention window, no lock-in.
```
## Anti-Example 1: No Hook (Company Bio Opener)
**Score**: 3.8 / 10.0 | **Gate H04**: FAIL | **Why it fails**
**Problematic opening**:
```

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
