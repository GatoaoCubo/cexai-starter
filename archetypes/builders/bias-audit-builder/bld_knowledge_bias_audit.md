---
kind: knowledge_card
id: bld_knowledge_card_bias_audit
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for bias_audit production
quality: null
title: "Knowledge Card Bias Audit"
version: "1.1.0"
author: n06_hybrid_review
tags: [bias_audit, builder, knowledge_card, bbq, winobias, stereoset, faact, nyc_ll144, colorado_ai_act, eu_ai_act]
tldr: "Domain knowledge for bias_audit -- includes BBQ/WinoBias/StereoSet benchmarks, NYC LL144, Colorado AI Act, EU AI Act articles, and commercial audit..."
domain: "bias_audit construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F3_inject"
keywords: [bias_audit construction, knowledge card bias audit, stereoset benchmarks, nyc ll, colorado ai act, eu ai act articles, and commercial audit-as-product framing]
density_score: 0.93
related:
  - n06_audit_bias_audit_builder
  - p07_qg_bias_audit
  - kc_bias_audit
  - bld_tools_bias_audit
  - n00_bias_audit_manifest
---
## Domain Overview

This ISO drives a bias audit: measuring fairness across demographic slices.
Bias audits evaluate whether AI systems produce systematically unfair outcomes across protected attributes (race, gender, age, religion, disability, national origin, sexual orientation). The discipline spans three tiers: (1) statistical disparity measurement (demographic parity, equalized odds), (2) benchmark evaluation (BBQ, WinoBias, StereoSet on standardized test sets), and (3) regulatory compliance documentation (NYC LL144, Colorado SB 22-169). Audits are distinct from model evaluations (overall accuracy) and from content filters (which categories are blocked). A bias audit asks: "For users in group A vs group B, does the system treat them equitably?"

## Named Benchmarks

### BBQ (Bias Benchmark for Question Answering)
Parrish et al., ACL 2022. 11 social categories, 58,492 examples.
| Social Category | Ambiguous Context | Disambiguated Context |
|-----------------|------------------|----------------------|
| Age | How old people are perceived | Context specifies age |
| Disability | Abled vs disabled | Explicit disability mentioned |
| Gender identity | Non-binary, trans representation | Explicit gender given |
| Nationality | Country-based stereotypes | Nationality named |
| Physical appearance | Body size, attractiveness | Appearance described |
| Race/ethnicity | Racial stereotypes | Race specified |
Usage: accuracy on BBQ should be >= 0.85 for both groups; disparity < 0.05.

### WinoBias (Gender Bias in Pronoun Resolution)
Zhao et al., NAACL 2018. 3,160 examples in 2 sets (Type 1: syntactic cues; Type 2: semantic).
| Metric | Definition | Target |
|--------|------------|--------|
| Pro-stereotypical accuracy | Correct for gender-conforming occupations | >= 0.90 |
| Anti-stereotypical accuracy | Correct for gender-nonconforming occupations | >= 0.80 |
| Gender parity gap | |pro - anti| | < 0.10 |
Usage: HR/recruitment AI, co-reference resolution systems, any NLP with pronoun handling.

### StereoSet (Stereotype Score)
Nadeem et al., ACL 2021. 4 domains: profession, gender, race, religion.
| Metric | Definition | Target |
|--------|------------|--------|
| SS (Stereotype Score) | % of stereotype-reinforcing selections | < 0.55 (near 0.50 = unbiased) |
| ICAT (Idealized CAT) | Combines LM score with idealized anti-stereotypical behavior | >= 0.80 |
Usage: LLM output evaluation; generative systems; conversational AI.

### BOLD (Bias in Open-Ended Language Generation)
Dhamala et al., FAccT 2021. Prompts for 5 domains: race, gender, religion, political ideology, profession.
Metric: regard score distribution across demographic groups (using Sheng et al. regard classifier).
Target: regard parity < 0.10 across all demographic groups in each domain.

### HolisticBias (Sentence-Level Generation Bias)
Smith et al., EMNLP 2022. 600+ demographic descriptors across 13 axes.
Usage: comprehensive generation audit for instruction-tuned LLMs.

### Winogender (Occupational Gender Stereotypes)
Rudinger et al., NAACL 2018. 720 sentences, 60 occupations.
Metric: co-reference resolution accuracy for "gotcha" gender assignments.
Usage: employment-adjacent AI systems required to audit by NYC LL144.

## Legal Frameworks

| Jurisdiction | Law | Section | Requirement | Audit Deliverable |
|-------------|-----|---------|-------------|-------------------|
| New York City | Local Law 144 (2023) | LL144 Sec. 1 | Annual bias audit for Automated Employment Decision Tools (AEDTs) | Public summary: impact ratio by race/ethnicity and sex |
| Colorado | SB 22-169 AI Act (2024) | Sec. 6-1-1702 | Bias audit for high-risk AI in employment, housing, credit, education, healthcare | Documented mitigation strategy |
| EU | AI Act (2024) | Art. 10(3) | Training data must be free from discriminatory bias for high-risk AI | Data sheet with demographic representation |
| EU | AI Act | Art. 64 | Provide documentation to national authority for bias audit | Technical documentation (Annex IV) |
| Illinois | AIVIA (HB 2557) | Sec. 5 | Annual bias audit + candidate notification for AI video interview tools | Audit report + disclosure notice |
| US Federal | Equal Credit Opportunity Act | 15 U.S.C. 1691 | Disparate impact analysis for credit-related AI | Adverse action notice + statistical analysis |
| US Federal | EEOC Guidance (2023) | AI Hiring | Disparate impact standard applies to AI-assisted hiring | 4/5 rule analysis (adverse impact ratio) |

### NYC Local Law 144 -- Specific Requirements
Applies to: AI tools used to screen, select, or rank candidates for employment or promotion in NYC.
Required public summary fields:
- Category: sex; race/ethnicity (separate breakdowns)
- Impact ratio: (selection rate of monitored group) / (selection rate of reference group)
- Pass threshold: impact ratio >= 0.80 (4/5 EEOC rule)
- Audit must be conducted by independent auditor

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[n06_audit_bias_audit_builder]] | downstream | 0.52 |
| [[p07_qg_bias_audit]] | downstream | 0.42 |
| [[kc_bias_audit]] | sibling | 0.38 |
| [[bld_tools_bias_audit]] | downstream | 0.35 |
| [[n00_bias_audit_manifest]] | sibling | 0.33 |
