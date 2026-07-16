---
id: fintech_vertical_payment_compliance
kind: fintech_vertical
8f: F1_constrain
pillar: P01
nucleus: N06
domain: fintech
title: "FinTech Vertical — Payment Compliance Analysis"
version: "1.0.0"
quality: null
tags: [fintech, payment, pci_dss, aml, kyc, vertical, compliance]
author: N06_contrib_stress_test
created: "2026-04-19"
compliance: [PCI-DSS, AML, KYC, SOX, GDPR]
focus_area: payment_compliance
target_demographic: payment_processors_neobanks_fintechs
keywords: [fintech vertical, payment compliance analysis, fintech, payment, pci_dss, vertical, compliance, compliance_checklist, workflow, guardrail]
density_score: 1.0
updated: "2026-04-22"
related:
  - fintech-vertical-builder
---

## Market Overview

| Dimension | Value |
|-----------|-------|
| Global FinTech market (2024) | $340B |
| Payments segment | $112B (33%) |
| Compliance tech spend | $38B |
| CAGR (2024-2030) | 16.8% |
| Dominant model | API-first, embedded finance |

## Key Players

| Vendor | Segment | Compliance Stack |
|--------|---------|-----------------|
| Stripe | Payment processing | PCI-DSS L1, SOC2, GDPR |
| Adyen | Enterprise acquiring | PCI-DSS L1, PSD2 SCA, AML |
| Plaid | Open banking / data | SOC2, PCI-DSS, CCPA |
| Marqeta | Card issuing | PCI-DSS L1, Reg E |
| Wise | Cross-border | FCA, FinCEN, PSD2, AML |

## Domain Vocabulary (Seed for N08_fintech vocabulary KC)

| Term | Definition | CEX Equivalent |
|------|-----------|----------------|
| PCI-DSS | Payment Card Industry Data Security Standard — 12-control framework | compliance_framework kind |
| AML | Anti-Money Laundering — transaction pattern monitoring | eval_metric kind |
| KYC | Know Your Customer — identity verification protocol | workflow kind |
| SCA | Strong Customer Authentication — PSD2 2FA requirement | guardrail kind |
| SAR | Suspicious Activity Report — FinCEN regulatory filing | audit_log kind |
| Reg E | Electronic Fund Transfer Act — consumer dispute rights | compliance_checklist kind |
| ISO 20022 | Global financial messaging standard (replacing SWIFT MT) | event_schema kind |
| FedNow | US real-time payment rail (launched 2023) | api_client kind |
| Open Banking | API-mandated account data sharing (PSD2, CDR) | api_reference kind |

## Compliance Requirements

### PCI-DSS v4.0 (2024 enforced)
- Scope: any entity storing, processing, or transmitting cardholder data
- 12 requirements: network security, access control, encryption, monitoring
- SAQ A: e-commerce redirect (no CHD in scope) — simplest tier
- SAQ D: full card data handling — strictest, 12 full controls
- CEX hook: `compliance_checklist` kind maps each requirement to pipeline stage

### AML / KYC Framework
| Stage | Process | CEX Kind |
|-------|---------|---------|
| CDD | Customer Due Diligence — identity + risk profile | `workflow` |
| EDD | Enhanced Due Diligence — PEP/sanctions screening | `guardrail` |
| Transaction monitoring | Rule-based + ML anomaly detection | `alert_rule` |
| SAR filing | Automated FinCEN report generation | `audit_log` |
| KYC refresh | Periodic re-verification schedule | `schedule` |

### PSD2 / Open Banking (EU)
- SCA: 2 of 3 factors (knowledge, possession, inherence) for >€30 transactions
- APIs: Berlin Group NextGenPSD2, UK Open Banking, CDR (Australia)
- AISP/PISP: Account Information / Payment Initiation Service Providers
- CEX hook: `api_client` + `guardrail` for SCA enforcement at payment initiation

## CEX Kind Mapping

| FinTech Need | CEX Kind | Pillar | Notes |
|-------------|---------|--------|-------|
| Payment workflow | `workflow` | P12 | Auth → capture → settle |
| PCI-DSS audit | `compliance_checklist` | P07 | 12-control mapping |
| Transaction alerting | `alert_rule` | P09 | AML threshold triggers |
| KYC identity flow | `workflow` + `guardrail` | P11+P12 | CDD/EDD pipeline |
| ISO 20022 message | `event_schema` | P06 | pacs.008 credit transfer |
| Open Banking API | `api_client` | P04 | PSD2 / Berlin Group |
| SAR report | `audit_log` | P08 | FinCEN XML format |
| Rate limiting | `rate_limit_config` | P09 | API quota per partner |

## New Builders/Kinds This Vertical Needs

| Proposed Kind | Rationale | Priority |
|---------------|-----------|----------|
| `payment_workflow` | Auth/capture/settle/refund state machine | HIGH |
| `aml_rule` | Transaction monitoring rule with threshold/pattern | HIGH |
| `kyc_profile` | Customer due diligence artifact with risk tier | HIGH |
| `financial_message` | ISO 20022 message schema variant | MEDIUM |
| `regulatory_report` | SAR/CTR/FBAR template with e-file format | MEDIUM |

## Moat Assessment (N06 Lens -- Strategic Greed)

| Factor | Score | Rationale |
|--------|-------|-----------|
| Compliance complexity | 10/10 | PCI+AML+KYC = top-tier barrier |
| Regulatory velocity | 9/10 | PSD3, Basel IV, DORA incoming |
| Market size | 9/10 | $112B payments, $38B compliance tech |
| CEX differentiation | 9/10 | Typed compliance artifacts beat manual audit |
| Revenue model fit | 9/10 | Per-transaction SaaS, compliance-as-a-service |

## CEXAI FinTech Pricing Model (Strategic Greed)

| Tier | Annual price | Target buyer | Volume metric |
|------|-------------:|--------------|---------------|
| FinTech Starter | $12,000/yr ($1K/mo) | Small fintech / neobank pilot | up to 100K transactions/mo |
| FinTech Growth | $60,000/yr ($5K/mo) | Series A-B fintech | up to 1M transactions/mo |
| FinTech Scale | $240,000/yr ($20K/mo) | PSP/acquirer, neobank | up to 10M transactions/mo |
| FinTech Enterprise | Custom ($500K+/yr) | Stripe-tier, banks, card networks | Unlimited + dedicated AML team |

### Pricing Rationale (every $ has a WHY)
- $12K floor: covers PCI-DSS SAQ A audit fees ($3K-5K) + base AML rule library ($2K) -- positioned 30% below Alloy starter ($18K-25K).
- $60K mid-tier: matches ComplyAdvantage Growth ($50K-100K) but bundles 3 compliance artifacts (PCI checklist + AML rules + KYC workflows) at parity pricing.
- $240K scale tier: 1/8th the cost of NICE Actimize ($2M+ enterprise minimum) -- strategic positioning to capture mid-market.
- Custom enterprise: PSP/bank deals typical $500K-$5M/yr; per-transaction SaaS at $0.001-$0.005/txn for high-volume.

### Competitive Pricing Matrix (FinTech)

| Vendor | Starter | Growth | Enterprise | Compliance Coverage |
|--------|--------|--------|-----------|--------------------|
| Stripe Radar | 5 cents/txn (pay-as-you-go) | 5 cents/txn | Custom | AML, PCI baseline |
| Alloy | $18K-25K/yr | $50K-150K/yr | $500K+/yr | KYC + AML |
| ComplyAdvantage | $35K/yr starter | $50K-100K/yr | $250K+/yr | AML, PEP, sanctions |
| NICE Actimize | (no SMB) | (no mid) | $2M+/yr | Full AML + fraud + AML investigations |
| Sift Science | Pay-per-API call | $50K-100K/yr | $300K+/yr | Fraud + chargeback |
| **CEXAI FinTech** | **$12K/yr** | **$60K/yr** | **$240K-$500K+/yr** | **PCI + AML + KYC + PSD2 SCA** |

### Per-Transaction Unit Economics
- Growth tier: $60K / 12M txns/yr = $0.005/transaction (vs Stripe Radar 5c/txn = 10x cheaper)
- CAC target: $24,000 (FinTech enterprise sales cycle 6-9mo)
- LTV target at 6% annual churn: $60K / 0.06 = $1M
- LTV:CAC = 1,000,000 / 24,000 = 41.7x (target >=3.0)
- Net Revenue Retention target: 130% (compliance scope expansion is natural)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_fintech_vertical | related | 0.37 |
| fintech-vertical-builder | related | 0.37 |
| bld_knowledge_card_fintech_vertical | related | 0.36 |
| p01_qg_fintech_vertical | downstream | 0.33 |
| p10_mem_fintech_vertical_builder | downstream | 0.29 |
