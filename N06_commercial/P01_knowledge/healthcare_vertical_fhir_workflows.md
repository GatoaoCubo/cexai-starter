---
id: healthcare_vertical_fhir_workflows
kind: healthcare_vertical
8f: F1_constrain
pillar: P01
nucleus: N06
domain: healthcare
title: "Healthcare Vertical — FHIR Workflows Analysis"
version: "1.0.0"
quality: null
tags: [healthcare, fhir, hipaa, hl7, interoperability, vertical]
author: N06_contrib_stress_test
created: "2026-04-19"
compliance: [HIPAA, HITECH, ONC, 21st_Century_Cures]
focus_area: fhir_workflows
target_demographic: ehr_vendors_health_systems_payers
keywords: [healthcare vertical, fhir workflows analysis, healthcare, fhir, hipaa, interoperability, vertical, guardrail, audit_log, compliance_checklist]
density_score: 1.0
updated: "2026-04-22"
related:
  - fhir-agent-capability-builder
  - bld_knowledge_card_fhir_agent_capability
  - kc_fhir_agent_capability
  - bld_tools_fhir_agent_capability
  - bld_instruction_fhir_agent_capability
---

## Market Overview

| Dimension | Value |
|-----------|-------|
| Global Healthcare IT market (2024) | $390B |
| EHR segment | $32B |
| Interoperability / FHIR tooling | $4.2B |
| CAGR (2024-2030) | 14.9% |
| Mandate driver | ONC 21st Century Cures Act (2024 enforcement) |

## Key Players

| Vendor | Segment | FHIR Maturity |
|--------|---------|---------------|
| Epic | Enterprise EHR | FHIR R4, SMART on FHIR |
| Cerner (Oracle Health) | Enterprise EHR | FHIR R4, CDS Hooks |
| Athenahealth | Ambulatory | FHIR R4 |
| Veradigm (Allscripts) | Ambulatory / Analytics | FHIR R4 |
| Apple Health | Patient app | FHIR R4 consumer API |

## Domain Vocabulary (Seed for N08_healthcare vocabulary KC)

| Term | Definition | CEX Equivalent |
|------|-----------|----------------|
| FHIR R4 | Fast Healthcare Interoperability Resources v4 — REST API standard | api_reference kind |
| SMART | Substitutable Medical Apps, Reusable Technologies — OAuth2 layer | oauth_app_config kind |
| CDS Hooks | Clinical Decision Support trigger framework | hook kind |
| HL7 v2 | Legacy ADT/ORU/ORM message format (still 80% of hospital traffic) | event_schema kind |
| PHI | Protected Health Information — HIPAA-covered data class | guardrail kind |
| HIPAA | Health Insurance Portability and Accountability Act | compliance_framework kind |
| Prior Auth | Payer approval before procedure — Da Vinci use case | workflow kind |
| IPA | Implementation Guide for Patient Access — ONC mandate | api_client kind |
| PDMP | Prescription Drug Monitoring Program | db_connector kind |

## Compliance Requirements

### HIPAA / HITECH
- PHI categories: 18 identifiers (name, DOB, geo, device IDs, etc.)
- Minimum necessary standard: only access/transmit PHI needed for the task
- BAA: Business Associate Agreement required for any PHI-processing vendor
- Breach notification: 60-day rule for >500 individuals (HHS + media)
- Security Rule: administrative, physical, technical safeguards
- CEX hook: `guardrail` kind enforces PHI field masking; `audit_log` tracks all access

### ONC 21st Century Cures — Information Blocking Rule
- Effective 2022: EHRs CANNOT block access to electronic health information (EHI)
- Patient APIs: SMART on FHIR patient-facing endpoint mandatory for CMS-regulated payers
- Developers: must attest ONC Health IT certification
- Penalty: up to $1M per violation for EHR developers
- CEX hook: `compliance_checklist` audits API openness pre-deployment

### FHIR R4 Integration Pattern
```
Client (app/CEX) → SMART on FHIR auth → EHR FHIR server
  1. Discovery: GET /.well-known/smart-configuration
  2. Auth: OAuth2 PKCE flow (authorization_code or client_credentials)
  3. Launch: EHR-launch or standalone-launch context
  4. Query: GET /Patient/{id}/everything (bundle)
  5. Write: POST/PUT Observation, MedicationRequest, etc.
```

## CEX Kind Mapping

| Healthcare Need | CEX Kind | Pillar | Notes |
|----------------|---------|--------|-------|
| FHIR API client | `api_client` | P04 | SMART on FHIR OAuth2 |
| PHI guardrail | `guardrail` | P11 | 18-identifier masking |
| HL7 v2 message | `event_schema` | P06 | ADT/ORU message schema |
| Prior auth workflow | `workflow` | P12 | Da Vinci PAS guide |
| CDS Hook trigger | `hook` | P04 | patient-view, order-sign |
| HIPAA audit trail | `audit_log` | P08 | PHI access log |
| Care coordination | `dag` | P12 | Multi-provider workflow |
| Clinical decision | `reasoning_strategy` | P08 | Evidence-based branching |

## New Builders/Kinds This Vertical Needs

| Proposed Kind | Rationale | Priority |
|---------------|-----------|----------|
| `fhir_resource` | Typed FHIR R4 resource schema (Patient, Observation, etc.) | HIGH |
| `cds_hook` | CDS Hooks service definition with prefetch template | HIGH |
| `clinical_workflow` | Care pathway with clinical decision nodes | HIGH |
| `phi_policy` | HIPAA minimum-necessary field policy per resource type | HIGH |
| `prior_auth_request` | Da Vinci PAS prior authorization document | MEDIUM |

Note: `fhir_agent_capability` builder already exists in CEX — leverage for N08_healthcare.

## Moat Assessment (N06 Lens -- Strategic Greed)

| Factor | Score | Rationale |
|--------|-------|-----------|
| Compliance complexity | 10/10 | HIPAA+ONC+FHIR = highest barrier in tech |
| Market size | 9/10 | $390B HIT, mandated interoperability |
| CEX differentiation | 9/10 | Typed PHI guardrails + audit logs native |
| Switching cost | 10/10 | EHR integrations are multi-year commitments |
| Revenue model fit | 8/10 | Per-API-call SaaS, compliance attestation fees |

## CEXAI Healthcare Pricing Model (Strategic Greed)

| Tier | Annual price | Target buyer | Volume metric |
|------|-------------:|--------------|---------------|
| Health Starter | $18,000/yr ($1.5K/mo) | Single clinic / specialty practice | up to 5,000 patient records |
| Health Growth | $96,000/yr ($8K/mo) | Multi-site practice or small EHR vendor | up to 100,000 patient records |
| Health Enterprise | $360,000/yr ($30K/mo) | Hospital system, payer, large EHR vendor | up to 5M patient records |
| Health Strategic | Custom ($1M+/yr) | Epic/Cerner-tier, national payers, ACO networks | Unlimited + BAA + HITRUST attestation + SLA |

### Pricing Rationale (every $ has a WHY)
- $18K floor: covers HIPAA BAA legal review ($5K) + 1 SMART on FHIR API setup ($3K) -- 40% below Redox Starter ($30K) but with full PHI guardrails included.
- $96K mid-tier: matches Particle Health Growth ($75K-150K) and 1Up Health ($80K-120K); positioned mid-market with compliance bundle.
- $360K enterprise: 60% below Innovaccer ($600K-1.5M minimum); hospital-tier deals via GPO contract vehicle (Vizient, Premier).
- Custom strategic: ONC certification ($75K-200K cycle) + HITRUST CSF Common ($120K-300K) is recouped within 9-12mo at this tier.

### Competitive Pricing Matrix (Healthcare)

| Vendor | Starter | Growth | Enterprise | FHIR + HIPAA Coverage |
|--------|--------|--------|-----------|----------------------|
| Redox | $30K-60K/yr | $100K-300K/yr | $500K+/yr | FHIR R4 + HL7 v2 routing |
| 1Up Health | $24K/yr | $80K-120K/yr | $300K+/yr | FHIR R4 + Patient Access API |
| Particle Health | $30K/yr | $75K-150K/yr | $400K+/yr | TEFCA + FHIR + records exchange |
| Innovaccer | (no SMB) | $300K/yr | $600K-1.5M/yr | FHIR + ML + analytics |
| Smile Digital Health | $15K-30K/yr | $80K-200K/yr | $400K+/yr | FHIR R4 server + apps |
| **CEXAI Healthcare** | **$18K/yr** | **$96K/yr** | **$360K-$1M+/yr** | **FHIR + HL7 v2 + HIPAA + ONC + CDS Hooks** |

### Per-Patient Unit Economics
- Growth tier: $96K / 100K patients/yr = $0.96/patient/year (industry avg $1.50-3.00)
- CAC target: $36,000 (healthcare enterprise sales cycle 9-12mo, BAA legal review adds 2-3mo)
- LTV target at 4% annual churn: $96K / 0.04 = $2.4M
- LTV:CAC = 2,400,000 / 36,000 = 66.7x (sticky vertical)
- Net Revenue Retention target: 125% (PHI volume grows + new specialties added)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| fhir-agent-capability-builder | downstream | 0.55 |
| bld_knowledge_card_fhir_agent_capability | related | 0.54 |
| kc_fhir_agent_capability | related | 0.50 |
| bld_tools_fhir_agent_capability | downstream | 0.47 |
| bld_instruction_fhir_agent_capability | downstream | 0.47 |
