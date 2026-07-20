---
id: p04_skill_n06
kind: skill
pillar: P04
nucleus: n06
title: "Skill N06: Sales Skills (Discovery / Objection-Handling / Closing)"
version: 1.0.0
quality: null
tags: [n06, commercial, skill, discovery, objection_handling, closing]
tldr: "N06 skill set: structured discovery, ROI-anchored objection-handling, and conversion-optimized closing sequences"
density_score: 0.88
related:
  - nucleus_def_n06
  - kc_commercial_vocabulary
  - p07_sr_commercial_n06
updated: "2026-07-20"
---

# Skill N06: Sales Skills

## Skill Registry

| Skill | Pillar Domain | Conversion Impact | Primary Metric |
|-------|---------------|-------------------|---------------|
| discovery | pre-sale diagnosis | +18% SQL-to-demo rate | discovery score 0-10 |
| objection_handling | mid-funnel defense | -31% lost deals | objection-close rate |
| closing | deal finalization | +24% win rate | close velocity (days) |

Numbers above are industry-pattern illustrations, not guarantees -- replace
them with your own cohort data once you have enough deal volume to measure.

---

## Skill 1: Discovery

**Purpose**: Diagnose buyer pain, quantify urgency, map stakeholders -- before any solution is proposed.

**Trigger**: Any inbound lead above your qualification threshold, or SQLs from the marketing-qualified pipeline.

**Revenue Impact**: Deals with structured discovery close at roughly 2x the rate of unstructured pitches (Gong 2024 cohort data).

### Discovery Framework (MEDDPICC)

| Element | Question Prompt | Revenue Signal |
|---------|----------------|---------------|
| Metrics | "What does success look like in numbers?" | Quantified pain = higher ACV |
| Economic Buyer | "Who controls this budget?" | Identifies true deal velocity |
| Decision Criteria | "What does your ideal solution need to do?" | Feature-to-value mapping |
| Decision Process | "How does your team evaluate vendors?" | Multi-thread vs. single-thread risk |
| Paper Process | "What does the contract approval path look like?" | Legal/procurement lag forecast |
| Identify Pain | "What's the cost of NOT solving this?" | Urgency calibration |
| Champion | "Who internally wants this solved most?" | Internal champion = faster close |
| Competition | "Are you evaluating alternatives?" | Win/loss positioning |

### Activation

```yaml
trigger: new_sql OR demo_requested
steps:
  - run_discovery_questionnaire: true
  - score_meddpicc: true
  - qualify_threshold: 6/8  # minimum to advance to demo
  - log_discovery_score: true
output: discovery_score, pain_quantification, stakeholder_map
```

### Conversion Target

- Discovery score >= 6/8 before advancing to demo stage
- Pain quantification (in your currency or in %) present in most advanced deals
- cost_model confirmed before pricing discussion

---

## Skill 2: Objection Handling

**Purpose**: Neutralize blockers with data, not persuasion. Convert objections into deal accelerators.

**Trigger**: Any deal stage where the buyer raises price, timing, or competitive concerns.

**Revenue Impact**: Structured objection-handling meaningfully reduces lost deals vs. ad-hoc responses -- track your own delta once you have baseline data.

### Objection Response Library

| Objection | Root Cause | Response Framework | Data Point (illustrative) |
|-----------|-----------|-------------------|------------|
| "Too expensive" | Cost vs. value gap | Show LTV:CAC ratio + payback period | "Customers your size typically see a multi-x return within a year" |
| "Not the right time" | Urgency deficit | Quantify cost of delay | "Each quarter delayed costs roughly {{DELAY_COST_ESTIMATE}} in lost efficiency/revenue" |
| "A competitor is cheaper" | Commodity framing | Reframe on TCO + outcomes | "Lower price + lower retention = higher 3yr cost; here's the comparison" |
| "Need to think about it" | Missing stakeholder | Identify unmapped buyer | "What would make this a clear yes? Let me get you that data." |
| "We built it internally" | Build vs. buy bias | TCO + opportunity cost | "Internal tools cost several x in eng time; here's the amortized comparison" |
| "Budget is frozen" | Timing/budget cycle | Reframe as next quarter pipeline | "Let's lock terms now so you can activate on day 1 of next quarter." |

### Activation

```yaml
trigger: deal_stage >= 2 AND objection_logged
steps:
  - classify_objection: true
  - load_response_library: true
  - attach_proof_point: true  # case study, metric, or reference
  - log_objection_close_rate: true
output: objection_category, recommended_response, proof_point, follow_up_task
conversion_target: "{{OBJECTION_TO_ADVANCEMENT_RATE}}"  # illustrative default: 0.55
```

---

## Skill 3: Closing

**Purpose**: Convert qualified opportunities into signed contracts using structured close sequences.

**Trigger**: Late-stage deal (champion confirmed, economic buyer engaged, legal/paper process known).

**Revenue Impact**: Structured close sequences tend to shorten the average sales cycle vs. open-ended follow-up.

### Close Sequence (7-Step)

| Step | Action | Timing | Revenue Signal |
|------|--------|--------|---------------|
| 1 | Mutual action plan sent | Day 0 | Shared commitment speeds close |
| 2 | Commercial proposal with ROI model | Day 2 | Anchored value before price discussion |
| 3 | Champion alignment call | Day 4 | Internal champion confirmed live |
| 4 | Economic buyer demo / exec briefing | Day 6 | EB engaged = deal unstuck |
| 5 | Legal / MSA kickoff | Day 8 | Paper process started early |
| 6 | Pricing negotiation + T&Cs finalized | Day 12 | Final objection resolution window |
| 7 | Signature + kickoff scheduled | Day 14 | Deal closed |

### Closing Variants

| Variant | When | Tactic |
|---------|------|--------|
| Trial-to-paid | Freemium conversion | Usage-triggered upgrade nudge near the quota limit |
| End-of-quarter push | Quota pressure | Time-limited pricing with exec approval |
| Multi-year lock | Churn prevention | Discount for a multi-year commit |
| Expansion close | Upsell trigger | Usage data + seat expansion ROI model |

### Activation

```yaml
trigger: deal_stage == 4 AND champion_confirmed == true
steps:
  - send_mutual_action_plan: true
  - attach_roi_model: true
  - schedule_eb_touchpoint: true
  - monitor_paper_process: true
  - set_close_date_target: "+14 days"
output: mutual_action_plan, roi_model, close_date_forecast
conversion_target: "{{STAGE4_TO_CLOSE_RATE}}"  # illustrative default: 0.68
cost_model: tracked per deal in CRM; CAC charged at close
revenue_impact: forecast updated daily from stage x probability x deal value
```

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[nucleus_def_n06]] | upstream |
| [[kc_commercial_vocabulary]] | upstream (shared vocabulary for discovery/objection/close terms) |
| [[p07_sr_commercial_n06]] | downstream (scoring rubric gates skill-output quality) |
