---
kind: knowledge_card
id: bld_knowledge_card_safety_policy
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for safety_policy production
quality: null
title: "Knowledge Card Safety Policy"
version: "1.1.0"
author: n06_hybrid_review
tags: [safety_policy, builder, knowledge_card, anthropic_hhh, openai_moderation, perspective_api, eu_ai_act]
tldr: "Domain knowledge for safety_policy production -- includes Anthropic HHH, OpenAI moderation taxonomy, Perspective API categories, EU AI Act articles..."
domain: "safety_policy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F3_inject"
keywords: [safety_policy construction, knowledge card safety policy, openai moderation taxonomy, perspective api categories, eu ai act articles, and commercial enforcement protocol, safety_policy]
density_score: 0.92
related:
  - bld_output_template_safety_policy
  - bld_knowledge_card_content_filter
  - n06_audit_safety_policy_builder
  - bld_output_template_content_filter
  - n06_audit_content_filter_builder
---
## Domain Overview
AI safety policies define which behaviors an AI system must never produce, which require human review, and which may proceed with logging. They span three risk layers: (1) absolute prohibitions (CSAM, CBRN synthesis routes), (2) context-dependent restrictions (explicit content, political persuasion), and (3) monitored behaviors (sensitive topics, off-topic use). Effective policies name real harm categories from established taxonomies, cite applicable legal frameworks with article numbers, and specify a commercial response for every trigger (block, flag, degrade, escalate).

Safety policies are distinct from: guardrails (runtime enforcement at inference), bias audits (demographic fairness of outputs), and compliance frameworks (regulatory mapping). Safety policies define WHAT is prohibited; guardrails enforce it; bias audits measure whether enforcement is equitable.

## Harm Category Taxonomies

### Anthropic HHH Framework (Helpful, Harmless, Honest)
| Category | Subcategory | Policy Default |
|----------|-------------|----------------|
| Harmful | Violence, CSAM, CBRN, self-harm, illegal services | BLOCK unconditionally |
| Harmful | Harassment, hate speech, explicit adult | BLOCK or RESTRICT by context |
| Dishonest | Deception, manipulation, false claims | BLOCK or WARN |
| Unhelpful | Off-topic refusals, excessive hedging | LOG -- quality issue, not safety |

### OpenAI Moderation API Categories (GPT-4 taxonomy)
| Category | Subcategory | Default Action |
|----------|-------------|----------------|
| hate | - | FLAG >= 0.7, BLOCK >= 0.9 |
| hate/threatening | - | BLOCK >= 0.5 |
| harassment | - | FLAG >= 0.7 |
| harassment/threatening | - | BLOCK >= 0.5 |
| self-harm | - | FLAG >= 0.5, notify support |
| self-harm/intent | - | BLOCK + crisis resource |

### Perspective API Categories (Jigsaw/Google)
| Attribute | Description | Threshold (block) |
|-----------|-------------|-------------------|
| TOXICITY | Rude or disrespectful comment | 0.90 |
| SEVERE_TOXICITY | Very hateful or aggressive | 0.80 |
| IDENTITY_ATTACK | Negative comment about protected group | 0.80 |
| INSULT | Inflammatory or negative personal comment | 0.90 |
| PROFANITY | Swear words, obscene, vulgar | 0.95 (context-dependent) |
| THREAT | Wish or intent to inflict harm | 0.85 |

## Legal Frameworks

| Jurisdiction | Law | Article | Requirement | Trigger for safety_policy |
|-------------|-----|---------|-------------|--------------------------|
| EU | AI Act (2024) | Art. 9 | Risk management system for high-risk AI | Mandatory if system classifies as high-risk |
| EU | AI Act | Art. 13 | Transparency and provision of information | Disclose when AI generates content |
| EU | AI Act | Art. 61 | Post-market monitoring | Ongoing incident collection and reporting |
| EU | AI Act | Art. 79 | Supervisory authority reporting | 15-day report for serious incidents |
| Colorado | SB 22-169 (2024) | Sec. 6-1-1702 | Bias audit for high-risk AI affecting consequential decisions | Employment, housing, credit, education, healthcare |
| New York City | Local Law 144 (2023) | LL144 | Annual bias audit + public summary for automated employment tools | HR/recruitment AI |

## Commercial Enforcement Protocol
Every harm category in a safety policy MUST specify product behavior:

| Severity | Trigger | Product Action | Revenue Impact | Audit Trail |
|----------|---------|----------------|----------------|-------------|
| Critical | CSAM, CBRN, self-harm/instructions | BLOCK + 403 + session terminate | $0 (correct) | Mandatory + NCMEC/legal |
| High | hate/threatening, violence/graphic | BLOCK + human review queue | 24h SLA cost ~$0.50 | Incident log |
| Medium | harassment, self-harm (non-intent) | FLAG + continue with warning | Retain revenue | Moderation log |
| Low | profanity, flirtation | LOG + continue | No impact | Audit log |
| Borderline | Context-dependent categories | DEGRADE (reduce capability, e.g., no image gen) | Partial retention | Decision log |

## Key Concepts
| Concept | Definition | Source |
|---------|------------|--------|
| Absolute prohibition | Content that must never be produced regardless of context | Anthropic Usage Policy |
| Context-dependent restriction | Content allowed in some contexts (adult platform, medical provider) | OpenAI Usage Policy |
| Human-in-the-loop | Flagged content sent to human moderator before delivery | EU AI Act Art. 14 |
| Safety by design | Safety constraints built into model fine-tuning, not post-hoc filters | NIST AI RMF |
| Red-teaming | Adversarial testing to discover policy gaps before deployment | MITRE ATLAS |
| Incident response | Documented procedure for safety failures: contain, assess, report, remediate | NIST AI RMF IR |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_safety_policy]] | downstream | 0.55 |
| [[bld_knowledge_card_content_filter]] | sibling | 0.51 |
| [[n06_audit_safety_policy_builder]] | downstream | 0.39 |
| [[bld_output_template_content_filter]] | downstream | 0.36 |
| [[n06_audit_content_filter_builder]] | downstream | 0.32 |
