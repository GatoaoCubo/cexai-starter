---
id: kc_nps_survey
kind: knowledge_card
8f: F3_inject
title: NPS Survey Configuration
version: 1.0.0
quality: null
pillar: P01
language: en
tldr: "Net Promoter Score survey setup: 0-10 scale, segmentation, cadence, follow-up routing, and response handling"
when_to_use: "When configuring customer satisfaction measurement with promoter/detractor segmentation and follow-up flows"
keywords: [nps survey, detractors, promoters, passives, customer success team, loyalty program, crm system, onboarding, segmentation, cadence]
density_score: 0.96
related:
  - bld_instruction_nps_survey
  - bld_knowledge_card_nps_survey
  - nps-survey-builder
  - bld_output_template_nps_survey
  - nps_survey_n02
---

# NPS Survey Configuration

## Question

| Form | Wording |
|------|---------|
| Standard | "On a scale from 0 to 10, how likely are you to recommend our product to a friend or colleague?" |
| Variant A | "How likely are you to recommend `<PRODUCT_NAME>` to a colleague?" |
| Variant B | "On a scale of 1-10, how likely are you to recommend `<PRODUCT_NAME>`?" |

## Scale

| Band | Range | Anchor label |
|------|-------|--------------|
| Detractors | 0-6 | 0 = "Not at all likely" |
| Passives | 7-8 | -- |
| Promoters | 9-10 | 10 = "Extremely likely" |

## Follow-up
- Send thank-you message with branded logo  
- Offer incentive (e.g., discount code) for promoters  
- Provide resource link for detractors (e.g., support portal)  

## Segmentation
- Target new users with onboarding-specific questions  
- Prioritize high-value customers for follow-up  
- Segment by product usage frequency  

## Cadence
- Primary frequency: Every 3 months  
- Trigger surveys after key interactions (e.g., purchase, support resolution)  
- Avoid more than 1 survey per 90 days  

## Response Routing

| Segment | Route to | Purpose |
|---------|----------|---------|
| Detractors (0-6) | Customer Success Team | recover the relationship |
| Promoters (9-10) | Loyalty Program | amplify advocacy |
| Passives (7-8) | Product Team | improvement insights |
| All responses | CRM system | scoring + trend analysis |

### How to use

```text
ROLE: you are the nps-survey-builder configuring a satisfaction-measurement loop.
- Pick ONE question variant and lock the 0-10 scale + the three segment bands.
- Set cadence (>= 90 days between sends) and the per-segment follow-up + route.
- Wire every response into the CRM so the score and trend are queryable.
Primary 8F verb: CONSTRAIN (this artifact fixes the measurement contract before any send).
```

### Procedure

```text
1. Choose the question variant; substitute the product name slot.
2. Set the scale labels (0 = Not at all likely, 10 = Extremely likely).
3. Bind segment bands: Detractors 0-6, Passives 7-8, Promoters 9-10.
4. Configure cadence: every 3 months, max 1 survey / 90 days, plus event triggers.
5. Attach the follow-up action and route per segment (see Response Routing table).
6. Connect the CRM sink; verify each segment lands in the right downstream owner.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_nps_survey]] | downstream | 0.45 |
| [[bld_knowledge_card_nps_survey]] | sibling | 0.37 |
| [[nps-survey-builder]] | downstream | 0.30 |
| [[bld_output_template_nps_survey]] | downstream | 0.29 |
