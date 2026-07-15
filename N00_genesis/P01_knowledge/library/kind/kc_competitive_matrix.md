---
id: kc_competitive_matrix
kind: knowledge_card
8f: F3_inject
title: Competitive Matrix
version: 1.0.0
quality: null
pillar: P01
tldr: "Side-by-side comparison of competitors across features, pricing, support, and market presence"
when_to_use: "When mapping competitive landscape to identify gaps, threats, and differentiation opportunities"
keywords: [market share, brand reputation, r&d investment, product lifecycle management, strategic alliances, environmental initiatives, green certifications, carbon footprint metrics, competitive_matrix, differentiation]
long_tails:
  - "how do I compare competitors side by side across features and pricing"
  - "how do I find gaps in competitor offerings to exploit"
primary_8f: F4_reason
slots:
  COMPETITOR: "rival brand under comparison"
  AXIS: "comparison dimension such as pricing or support"
  SOURCE: "citation backing each matrix cell"
  DIFFERENTIATION: "gap this product exploits"
density_score: 0.92
related:
  - sales_playbook_n06
  - kc_discovery_questions
  - p01_kc_pillar_brief_p03_prompt_en
  - p01_kc_competitive_positioning
  - p01_kc_pillar_brief_p02_model_en
---

# Competitive Matrix

## Product Features
- What unique features differentiate your product from competitors?
- How do your features align with customer pain points?
- Are there any gaps in competitor offerings that we can exploit?

## Pricing
- What is your pricing strategy compared to market benchmarks?
- How do you balance cost-effectiveness with value proposition?
- Are there any hidden costs or premium features that competitors lack?

## Customer Support
- What support channels do you offer (chat, phone, email)?
- How quickly do you resolve customer issues compared to competitors?
- Do you have dedicated account management for enterprise clients?

## Market Presence
- What is your market share in key regions/industries?
- How does your brand reputation compare to competitors?
- Are you actively expanding into new markets or segments?

## User Feedback
- What are common customer complaints about competitors?
- How do users rate your product vs. alternatives in independent reviews?
- Are there any recurring requests for new features?

## Innovation
- How do you stay ahead with R&D investment and new features?
- What emerging technologies are you integrating that competitors haven't?
- How do you handle product lifecycle management compared to industry standards?

## Partnerships
- What strategic alliances or integrations do you have?
- How do these partnerships create competitive advantages?
- Are there any exclusive partnerships that competitors lack?

## Sustainability
- What environmental initiatives do you prioritize?
- How does your sustainability approach compare to industry leaders?
- Are there any green certifications or carbon footprint metrics?

### How to use
```text
Role: you are the INJECT agent at 8F step F3/F4 building competitive intel.
Load this card to turn a raw competitor list into a decision-ready matrix.
- Treat each H2 above as a comparison axis; answer every question per competitor.
- Fill one COMPETITOR column at a time so axes stay consistent across rivals.
- Cite a SOURCE for every claim; an unsourced matrix is opinion, not intel.
- Flag the gaps your product can exploit; that is the matrix's payoff.
```

### Procedure
```text
1. List the COMPETITOR set to compare (3-6 rivals is a workable matrix).
2. Adopt the H2 sections above as the AXES (features, pricing, support, ...).
3. For each competitor, answer every axis question with a sourced fact.
4. Mark cells where rivals are weak or silent (exploitable gaps).
5. Derive 1-3 DIFFERENTIATION opportunities from those gaps.
6. Hand the matrix to N06 sales_playbook / positioning as upstream evidence.
```

### Slots
```text
COMPETITOR      = <COMPETITOR>       # rival brand under comparison
AXIS            = <AXIS>             # comparison dimension (one H2 above)
SOURCE          = <SOURCE>           # citation backing each cell
DIFFERENTIATION = <DIFFERENTIATION>  # gap this product exploits
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| sales_playbook_n06 | downstream | 0.30 |
| kc_discovery_questions | sibling | 0.28 |
| p01_kc_pillar_brief_p03_prompt_en | sibling | 0.28 |
| [[p01_kc_competitive_positioning]] | sibling | 0.28 |
| p01_kc_pillar_brief_p02_model_en | sibling | 0.28 |
