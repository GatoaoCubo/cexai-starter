---
id: kc_pitch_deck
kind: knowledge_card
8f: F3_inject
title: Pitch Deck
version: 1.0.0
quality: null
pillar: P01
tldr: "Structured investor presentation framework: problem, solution, traction, and funding ask slides"
when_to_use: "When creating a concise slide deck to pitch a business to investors, partners, or enterprise stakeholders"
keywords: [pitch deck, value proposition, user growth, revenue, metrics, data-driven, audience-centric, conciseness, clarity, pitch_deck, funding_ask]
long_tails:
  - "how do I structure an investor pitch deck"
  - "how do I sequence problem solution traction and ask slides"
primary_8f: F6_produce
slots:
  PROBLEM: "the pain the venture solves, with data"
  SOLUTION: "the differentiated product answer"
  TRACTION: "metrics that prove validation"
  ASK: "funding or resources requested and use of funds"
  AUDIENCE: "investors | partners | enterprise stakeholders"
density_score: 0.9
related:
  - p10_mem_pitch_deck_builder
  - bld_instruction_pitch_deck
  - bld_knowledge_card_pitch_deck
  - pitch-deck-builder
  - p05_qg_pitch_deck
---

# Pitch Deck

A pitch deck is a concise presentation used to communicate the value proposition of a business to potential investors, partners, or customers. It follows a structured framework to effectively convey key information:

1. **Problem**  
   Clearly define the problem your product or service solves. Use data or anecdotes to highlight its significance and urgency.

2. **Solution**  
   Present your product/service as the innovative solution to the identified problem. Focus on unique value propositions and differentiation.

3. **Traction**  
   Demonstrate progress and validation through metrics (e.g., user growth, revenue, partnerships) to build credibility.

4. **Ask**  
   Specify the funding or resources requested, including usage of funds and expected outcomes. Be transparent about financial needs.

**Design Tips**:  
- Use clean visuals, minimal text, and consistent branding.  
- Prioritize storytelling over dense text.  
- Include charts, graphs, and customer testimonials for impact.  

**Key Principles**:  
- **Conciseness**: Keep slides focused and avoid clutter.  
- **Clarity**: Use simple language and avoid jargon.  
- **Data-Driven**: Back claims with metrics and evidence.  
- **Audience-Centric**: Tailor content to the specific stakeholders (investors vs. clients).

### How to use
```text
Role: you are the PRODUCE agent at 8F step F6 drafting an investor deck.
Load this card to turn a venture into a tight, persuasive slide sequence.
- Build exactly four core slides in order: PROBLEM, SOLUTION, TRACTION, ASK.
- Lead each slide with one claim; back it with a metric, not adjectives.
- Tailor depth to AUDIENCE (investors want returns; clients want outcomes).
- Apply the Design Tips: clean visuals, minimal text, storytelling over clutter.
```

### Procedure
```text
1. State the PROBLEM with data that shows its size and urgency.
2. Present the SOLUTION and its unique value proposition.
3. Prove TRACTION with growth, revenue, or partnership metrics.
4. Make the ASK: amount requested plus concrete use of funds.
5. Tighten every slide for conciseness, clarity, and a single message.
6. Tailor the framing to the AUDIENCE before presenting.
```

### Slots
```text
PROBLEM  = <PROBLEM>    # pain solved, with data
SOLUTION = <SOLUTION>   # differentiated product answer
TRACTION = <TRACTION>   # validation metrics
ASK      = <ASK>        # funding requested + use of funds
AUDIENCE = <AUDIENCE>   # investors | partners | enterprise
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_mem_pitch_deck_builder]] | downstream | 0.32 |
| [[bld_instruction_pitch_deck]] | downstream | 0.29 |
| [[bld_knowledge_card_pitch_deck]] | sibling | 0.28 |
| [[pitch-deck-builder]] | downstream | 0.23 |
| [[p05_qg_pitch_deck]] | downstream | 0.23 |
