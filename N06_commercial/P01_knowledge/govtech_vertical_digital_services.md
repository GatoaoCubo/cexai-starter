---
id: govtech_vertical_digital_services
kind: govtech_vertical
8f: F1_constrain
pillar: P01
nucleus: N06
domain: govtech
title: "GovTech Vertical — Digital Services Analysis"
version: "1.0.0"
quality: null
tags: [govtech, digital_government, fedramp, accessibility, vertical]
author: N06_contrib_stress_test
created: "2026-04-19"
compliance: [FedRAMP, FISMA, Section508, ATO, NIST-800-53]
focus_area: digital_services
target_demographic: federal_agencies_state_local_govtech_vendors
keywords: [govtech vertical, digital services analysis, govtech, digital_government, fedramp, accessibility, vertical, compliance_checklist, content_filter, market overview]
density_score: 1.0
updated: "2026-04-22"
related:
  - bld_knowledge_card_govtech_vertical
  - govtech-vertical-builder
  - p01_qg_govtech_vertical
  - bld_instruction_govtech_vertical
  - bld_tools_govtech_vertical
---

## Market Overview

| Dimension | Value |
|-----------|-------|
| Global GovTech market (2024) | $667B |
| US Federal IT spending | $74B/yr |
| AI in government (2024-2030 CAGR) | 22.4% |
| Mandate driver | Executive Order 14110 on Safe AI (Oct 2023) |
| Procurement cycle | 12-24 months (SAM.gov / GSA Schedule) |

## Key Players

| Vendor | Segment | Certification |
|--------|---------|--------------|
| Palantir | Data analytics, defense | FedRAMP High, DoD IL5 |
| Salesforce Government Cloud | CRM, case mgmt | FedRAMP High |
| Microsoft Azure Government | Cloud infrastructure | FedRAMP High, DoD IL6 |
| AWS GovCloud | Cloud infrastructure | FedRAMP High, ITAR |
| Tyler Technologies | State/local ERP, courts | StateRAMP |

## Domain Vocabulary (Seed for N08_govtech vocabulary KC)

| Term | Definition | CEX Equivalent |
|------|-----------|----------------|
| FedRAMP | Federal Risk and Authorization Management Program — cloud security | compliance_framework kind |
| ATO | Authority to Operate — security authorization document | conformity_assessment kind |
| FISMA | Federal Information Security Modernization Act | compliance_checklist kind |
| Section 508 | Accessibility law for federal electronic content | content_filter kind |
| SAM.gov | System for Award Management — federal procurement portal | partner_listing kind |
| GSA Schedule | Government-wide acquisition contract vehicle | enterprise_sla kind |
| NIST SP 800-53 | Security control catalog (1000+ controls) | safety_policy kind |
| CDM | Continuous Diagnostics and Mitigation — DHS cyber program | monitoring kind |
| FedRAMP IL | Impact Level — Low/Moderate/High/DoD IL4/IL5/IL6 | rbac_policy kind |

## Compliance Requirements

### FedRAMP Authorization
| Level | Data Type | Controls | Timeline |
|-------|-----------|----------|---------|
| Low | Public, non-sensitive | 125 controls | 6-12 months |
| Moderate | CUI, PII | 325 controls | 12-18 months |
| High | Law enforcement, health | 421 controls | 18-36 months |

- Process: 3PAO assessment → Agency ATO or JAB P-ATO → FedRAMP marketplace listing
- Key controls: AC (access), AU (audit), CM (config), IA (identity), SC (communication)
- CEX hook: `compliance_checklist` maps NIST 800-53 controls to pipeline stages

### Section 508 / WCAG 2.1
- Level AA mandatory for all federal digital services
- Key requirements: keyboard nav, screen reader, color contrast 4.5:1, captions
- Testing: aXe, NVDA, JAWS, automated + manual
- CEX hook: `content_filter` kind enforces accessible output format constraints

### FedRAMP Continuous Monitoring
```
Monthly: vulnerability scans, POA&M updates
Annually: security assessment, penetration test
Real-time: SIEM log ingestion, CDM dashboard feeds
CEX role: audit_log + alert_rule kinds for continuous monitoring artifacts
```

## CEX Kind Mapping

| GovTech Need | CEX Kind | Pillar | Notes |
|-------------|---------|--------|-------|
| FedRAMP compliance | `compliance_framework` | P07 | Control mapping artifact |
| ATO package | `conformity_assessment` | P07 | SSP, SAR, POA&M |
| NIST 800-53 controls | `safety_policy` | P11 | Per-control policy |
| Section 508 audit | `content_filter` | P11 | Accessibility gate |
| Procurement vehicle | `enterprise_sla` | P11 | GSA Schedule terms |
| Audit log | `audit_log` | P08 | FISMA audit trail |
| RBAC for IL levels | `rbac_policy` | P09 | Role per clearance |
| Continuous monitoring | `alert_rule` + `schedule` | P09 | CDM feeds |

## New Builders/Kinds This Vertical Needs

| Proposed Kind | Rationale | Priority |
|---------------|-----------|----------|
| `fedramp_control` | Individual NIST 800-53 control implementation statement | HIGH |
| `ato_package` | Authority to Operate documentation set (SSP+SAR+POA&M) | HIGH |
| `procurement_vehicle` | GSA Schedule / GWAC contract vehicle artifact | MEDIUM |
| `clearance_policy` | Personnel security / clearance requirement definition | MEDIUM |
| `508_audit` | WCAG 2.1 AA accessibility audit artifact | MEDIUM |

## Procurement Model (N06 Lens)

| Vehicle | Mechanism | Timeline | Revenue Scale |
|---------|-----------|---------|---------------|
| GSA MAS Schedule | Listed vendor, on-demand | 6-18 months setup | $100K-$10M/yr |
| IDIQ | Indefinite Delivery contracts | 2-5 year base + options | $1M-$500M |
| OTA (Other Transaction) | R&D prototype, non-FAR | 3-6 months | $500K-$50M |
| SBIR/STTR | Small business R&D grants | 6-12 months | $150K-$2M |

## Moat Assessment (N06 Lens -- Strategic Greed)

| Factor | Score | Rationale |
|--------|-------|-----------|
| Procurement barrier | 10/10 | FedRAMP = 12-36 month moat |
| Market size | 9/10 | $74B federal IT alone |
| CEX differentiation | 8/10 | Typed audit trails + NIST control mapping |
| Revenue stability | 10/10 | Multi-year government contracts |
| Competition | 7/10 | Established players, but AI gap is real |

## CEXAI GovTech Pricing Model (Strategic Greed)

| Tier | Annual price | Target buyer | Volume metric |
|------|-------------:|--------------|---------------|
| Civic Starter | $36,000/yr ($3K/mo) | Small city / county agency, NGO, civic-tech vendor | StateRAMP Low equivalent |
| Civic Growth | $180,000/yr ($15K/mo) | State agency, large county, federal pilot | StateRAMP/FedRAMP Moderate |
| Civic Federal | $720,000/yr ($60K/mo) | Federal agency, ATO holder, GSA Schedule | FedRAMP Moderate authorized |
| Civic Strategic | Custom ($1.5M+/yr) | DoD, intel community, multi-agency platform | FedRAMP High + DoD IL5/IL6 |

### Pricing Rationale (every $ has a WHY)
- $36K floor: 70% below Palantir Foundry SMB ($120K-300K) -- positioned for civic-tech vendors and state pilot phase.
- $180K growth tier: matches Tyler Technologies state implementations ($150K-500K); below Salesforce Government Cloud floor ($200K).
- $720K federal tier: ATO-authorized vendors typically charge $500K-$2M/yr; positioned as price-disrupter for AI-augmented compliance.
- Custom strategic: DoD IL5/IL6 deals routinely $1M-$50M/yr (Palantir USAF $130M, Anduril $100M+); CEXAI captures 1-3% of those budgets.

### Procurement-Aligned Pricing
- GSA Schedule add-on: 7.5% IFF (Industrial Funding Fee) baked into list price.
- FAR 52.215-21 Pricing terms: "best price" obligation across federal customers; CEXAI standardizes pricing per procurement vehicle.
- Multi-year contract discount: 5% off Year 2, 10% off Year 3 (incentivizes long-term commitment for budget predictability).

### Competitive Pricing Matrix (GovTech)

| Vendor | SMB | Mid-tier | Federal | Compliance Coverage |
|--------|-----|---------|---------|---------------------|
| Palantir Foundry | $120K-300K/yr | $500K-2M/yr | $5M-50M/yr | FedRAMP High + DoD IL5 |
| Salesforce Government Cloud | $200K/yr | $500K-1.5M/yr | $2M+/yr | FedRAMP High |
| Microsoft Azure Government | (consumption) | (consumption) | $5M+/yr commit | FedRAMP High + IL6 |
| Tyler Technologies | $50K-150K/yr | $150K-500K/yr | (no federal) | StateRAMP |
| Booz Allen / Carahsoft | (consulting) | $500K-2M/yr | $5M+/yr | Full federal stack |
| **CEXAI GovTech** | **$36K/yr** | **$180K-$720K/yr** | **$1.5M+/yr** | **FedRAMP + NIST 800-53 + Section 508** |

### Per-User Unit Economics (federal pilot)
- Federal tier: $720K / 200 federal users/agency = $3,600/seat/year (vs Palantir $5K-15K/seat/yr)
- CAC target: $144,000 (federal sales cycle 12-24mo, SAM.gov + GSA registration)
- LTV target at 2% annual churn (multi-year contracts): $720K / 0.02 = $36M
- LTV:CAC = 36,000,000 / 144,000 = 250x (long government contracts dominate)
- Net Revenue Retention target: 110% via task order expansion within IDIQ vehicles

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_knowledge_card_govtech_vertical | related | 0.47 |
| govtech-vertical-builder | related | 0.38 |
| p01_qg_govtech_vertical | downstream | 0.38 |
| bld_instruction_govtech_vertical | downstream | 0.33 |
| bld_tools_govtech_vertical | downstream | 0.29 |
