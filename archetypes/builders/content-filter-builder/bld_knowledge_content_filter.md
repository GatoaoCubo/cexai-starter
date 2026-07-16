---
kind: knowledge_card
id: bld_knowledge_card_content_filter
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for content_filter production
quality: null
title: "Knowledge Card Content Filter"
version: "1.1.0"
author: n06_hybrid_review
tags: [content_filter, builder, knowledge_card, perspective_api, openai_moderation, csam, dsa, coppa]
tldr: "Domain knowledge for content_filter production -- includes named harm categories (Perspective API, OpenAI Moderation, CSAM), real enforcement actio..."
domain: "content_filter construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F3_inject"
keywords: [content_filter construction, knowledge card content filter, perspective api, openai moderation, real enforcement actions, and dsa, gdpr legal framework]
density_score: 0.92
related:
  - bld_tools_content_filter
---
## Domain Overview

This ISO defines a content filter -- the moderation rules that gate output or input.
Content filter pipelines enforce organizational harm policies by intercepting text, images, audio, and structured data at ingestion (pre-LLM) and output (post-LLM) stages. They operate in sequential stages: fast rule-based triage (< 5ms) -> ML classifier scoring (< 50ms) -> optional human review queue (async). Each stage assigns a harm category and confidence score; enforcement actions (block, flag, degrade, log) are triggered by configured thresholds per category.

Content filters differ from: safety policies (define WHAT is prohibited), guardrails (constrain model BEHAVIOR), and output validators (verify schema/format). Filters execute at the data-plane level; guardrails execute at the model level.

## Named Harm Category Taxonomies

### Perspective API (Jigsaw/Google) -- production taxonomy
| Attribute | Description | Block Threshold | Flag Threshold |
|-----------|-------------|-----------------|----------------|
| TOXICITY | Rude, disrespectful, unreasonable | 0.90 | 0.70 |
| SEVERE_TOXICITY | Hateful, aggressive, explicit | 0.80 | 0.60 |
| IDENTITY_ATTACK | Negative comment about race, religion, gender, nationality | 0.80 | 0.65 |
| INSULT | Inflammatory, negative personal comment | 0.90 | 0.75 |
| PROFANITY | Obscene, vulgar | 0.95 | 0.85 |
| THREAT | Wish or intent to physically harm | 0.85 | 0.70 |

### OpenAI Moderation API -- production taxonomy (2023-11)
| Category | Action |
|----------|--------|
| hate | FLAG >= 0.7, BLOCK >= 0.9 |
| hate/threatening | BLOCK >= 0.5 |
| harassment | FLAG >= 0.7 |
| harassment/threatening | BLOCK >= 0.5 |
| self-harm | FLAG + notify support |
| self-harm/intent | BLOCK + crisis resource link |

### CSAM Detection (absolute prohibition -- no threshold)
| Tool | Method | Regulatory mandate |
|------|--------|--------------------|
| PhotoDNA (Microsoft) | Hash matching against NCMEC database | PROTECT Act (US) |
| Google CSAI Match | Hash matching | EU Regulation 2021/1232 |
| NCMEC CyberTipline | Mandatory reporting | 18 U.S.C. 2258A |
Action: BLOCK + terminate session + file NCMEC report within 24h (mandatory, no exceptions).

## Legal Frameworks

| Jurisdiction | Law | Article | Content Filter Requirement |
|-------------|-----|---------|---------------------------|
| EU | Digital Services Act (DSA) 2023 | Art. 34 | Large platforms must assess and mitigate systemic risks from harmful content |
| EU | DSA | Art. 16 | Notice-and-action mechanisms for illegal content |
| EU | AI Act (2024) | Art. 52 | Disclose AI-generated content (deep fakes, synthetic media) |
| EU | GDPR | Art. 5(1)(c) | Data minimization: filter logs must not retain PII beyond operational need |
| US | COPPA (FTC Rule 312.3) | Sec. 312.3 | Operators of child-directed services must not collect PII from under-13 users |
| US | CDA Section 230 | Sec. 230(c)(2) | Good Samaritan protection for filtering objectionable material (requires active filtering) |
| US | PROTECT Act | 18 U.S.C. 2258A | Mandatory reporting of CSAM to NCMEC |

## Enforcement Action Taxonomy
Every harm category MUST map to exactly one of these actions:

| Action | Product Behavior | When to Use |
|--------|-----------------|-------------|
| BLOCK | 403 response; content not delivered | sexual/minors, CSAM, severe threats |
| FLAG | Content held; routed to human review queue | borderline hate, harassment, self-harm |
| DEGRADE | Request fulfilled with reduced capability (no image gen, no code exec) | medium toxicity, insults |
| LOG | Request fulfilled; audit record written | low profanity, flirtation |
| ESCALATE | Route to senior moderator + notify legal | repeat offenders, potential legal violations |

## Key Concepts
| Concept | Definition | Source |
|---------|------------|--------|
| Pre-inference filter | Blocks harmful prompt before LLM processes it | OpenAI Moderation API |
| Post-inference filter | Scans LLM output before delivery to user | AWS Comprehend Detect Toxic Content |
| Hash matching | Fingerprint of known-bad content (exact match, no ML) | PhotoDNA, NCMEC |
| Semantic similarity | Vector distance from known-bad embeddings | Jigsaw Perspective |
| False positive rate | Legitimate content incorrectly blocked; target < 1% for non-critical | Google AI Blog |
| Latency budget | Pre-inference: < 5ms. Post-inference: < 50ms. Total pipeline: < 100ms | AWS WAF |

## Industry Standards
- Google Jigsaw: Perspective API (8 production attributes, available via REST)
- OpenAI: Moderation API (11 categories, free with API key)
- Microsoft: PhotoDNA (CSAM hash matching), Azure Content Moderator
- AWS: Comprehend Detect Toxic Content, Rekognition Content Moderation

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_knowledge_card_safety_policy | sibling | 0.54 |
| bld_output_template_safety_policy | downstream | 0.48 |
| n06_audit_content_filter_builder | downstream | 0.35 |
| [[bld_tools_content_filter]] | downstream | 0.33 |
