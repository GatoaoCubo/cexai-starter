---
id: edtech_vertical_lms_market
kind: edtech_vertical
8f: F1_constrain
pillar: P01
nucleus: N06
domain: edtech
title: "EdTech Vertical — LMS Market Analysis"
version: "1.0.0"
quality: null
tags: [edtech, lms, ferpa, coppa, vertical, market_analysis]
author: N06_contrib_stress_test
created: "2026-04-19"
compliance: [FERPA, COPPA, GDPR]
focus_area: lms_integration
target_demographic: K12_higher_ed
keywords: [edtech vertical, lms market analysis, edtech, ferpa, coppa, vertical, market_analysis, guardrail, content_filter, market overview]
density_score: 1.0
updated: "2026-04-22"
related:
  - edtech-vertical-builder
---

## Market Overview

| Dimension | Value |
|-----------|-------|
| Global EdTech market (2024) | $254B |
| LMS segment (2024) | $22B |
| CAGR (2024-2029) | 19.4% |
| Top regions | NA (38%), APAC (31%), EMEA (22%) |
| Dominant delivery | SaaS (73%), on-prem (27%) |

## Key Players

| Vendor | Segment | Market Share | Compliance Focus |
|--------|---------|-------------|-----------------|
| Canvas (Instructure) | Higher Ed | 35% | FERPA, LTI 1.3 |
| Moodle | K-12 / SMB | 28% | GDPR, FERPA |
| Blackboard (Anthology) | Enterprise Edu | 18% | FERPA, SOC2 |
| Google Classroom | K-12 | 12% | COPPA, FERPA |
| Schoology (PowerSchool) | K-12 | 7% | FERPA, COPPA |

## Domain Vocabulary (Seed for N08_edtech vocabulary KC)

| Term | Definition | CEX Equivalent |
|------|-----------|----------------|
| LMS | Learning Management System — centralized platform for course delivery | workflow kind |
| LTI 1.3 | Learning Tools Interoperability — OAuth2-based tool launch standard | interface kind |
| xAPI (Tin Can) | Learning activity tracking standard (successor to SCORM) | event_schema kind |
| SIS | Student Information System — roster/grade data store | db_connector kind |
| FERPA | Family Educational Rights and Privacy Act — US student data law | compliance_checklist kind |
| COPPA | Children's Online Privacy Protection Act — <13 data rules | guardrail kind |
| IMS Global | Consortium defining LTI, QTI, Caliper standards | domain_vocabulary kind |
| Caliper | IMS learning analytics framework | eval_metric kind |

## Compliance Requirements

### FERPA (US)
- Records covered: grades, enrollment, financial aid, disciplinary
- Consent model: opt-out for directory info; opt-in for PII disclosure
- Data minimization: only collect records necessary for stated educational purpose
- Breach notification: within 60 days to affected parties
- CEX hook: `guardrail` kind enforces PII field masking in student data pipelines

### COPPA (US — under 13)
- Parental consent: verifiable, explicit, prior to data collection
- Data types blocked: precise geolocation, behavioral advertising, full name+address combo
- Operator obligations: delete on request within 30 days
- CEX hook: `content_filter` kind blocks COPPA-violating data fields at ingestion

### LTI 1.3 Integration Pattern
```
Platform (LMS) → OIDC Connect → Tool Provider (CEX)
  1. Platform sends id_token (JWT, signed RS256)
  2. Tool validates iss, aud, nonce, deployment_id
  3. Tool returns resource link + context claims
  4. OAuth2 service access token for Names+Roles, Grade Passback
```

## CEX Kind Mapping

| EdTech Need | CEX Kind | Pillar | Notes |
|-------------|---------|--------|-------|
| Course content delivery | `workflow` | P12 | Sequential lesson flow |
| Grade passback API | `api_client` | P04 | LTI Advantage Grade Services |
| Student roster sync | `db_connector` | P04 | SIS integration (OneRoster) |
| Learning activity tracking | `event_schema` | P06 | xAPI statement format |
| FERPA compliance gate | `compliance_checklist` | P07 | Pre-processing validation |
| Adaptive content router | `router` | P02 | Mastery-based branching |
| Assessment rubric | `scoring_rubric` | P07 | Standards-aligned grading |
| Parent consent workflow | `workflow` + `guardrail` | P11+P12 | COPPA consent chain |

## New Builders/Kinds This Vertical Needs

| Proposed Kind | Rationale | Priority |
|---------------|-----------|----------|
| `lti_provider` | LTI 1.3 tool registration + launch config | HIGH |
| `student_data_policy` | FERPA/COPPA field-level policy artifact | HIGH |
| `adaptive_learning_path` | Mastery-gated content sequence | MEDIUM |
| `assessment_rubric` | Caliper-aligned grading instrument | MEDIUM |
| `sis_connector` | OneRoster 2.0 roster sync protocol | MEDIUM |

## Existing Builder Relevance

| Builder | Relevance | Use Case |
|---------|-----------|----------|
| `api_client-builder` | HIGH | LTI Advantage API client |
| `compliance_checklist-builder` | HIGH | FERPA/COPPA audit artifact |
| `workflow-builder` | HIGH | Course enrollment flow |
| `guardrail-builder` | HIGH | Student PII protection |
| `event_schema-builder` | MEDIUM | xAPI statement schema |
| `scoring_rubric-builder` | MEDIUM | Standards-aligned assessment |
| `db_connector-builder` | MEDIUM | SIS/OneRoster integration |

## Moat Assessment (N06 Lens -- Strategic Greed)

| Factor | Score | Rationale |
|--------|-------|-----------|
| Compliance complexity | 9/10 | FERPA+COPPA+LTI = high barrier |
| Market size | 8/10 | $22B LMS, 19% CAGR |
| CEX differentiation | 8/10 | Typed guardrails beat generic AI |
| Switching cost | 7/10 | LMS deeply embedded in institutions |
| Revenue model fit | 8/10 | SaaS per-student pricing, district deals |

## CEXAI EdTech Pricing Model (Strategic Greed)

| Tier | Annual price | Target buyer | Volume metric |
|------|-------------:|--------------|---------------|
| EdTech Starter | $4,900/yr | K-12 single school (<2,000 students) | up to 2,000 student records |
| EdTech Growth | $24,000/yr | District (10-50 schools) | up to 50,000 student records |
| EdTech District | $96,000/yr | Large district (100+ schools) | up to 500,000 student records |
| EdTech State/Higher Ed | Custom ($250K+/yr) | State agencies, R1 universities | Unlimited + dedicated CSM + FERPA attestation |

### Pricing Rationale (every $ has a WHY)
- $4,900 floor: matches Schoology Essentials ($5,000) but bundles FERPA-attested AI; below the $5K procurement threshold for purchase orders without committee.
- $24,000 mid-tier: per-student equivalent of $0.48/student/year -- lower than ClassDojo Plus per-student ($1/student/yr) but higher unit value via AI artifacts.
- $96,000 district tier: matches Canvas district floor ($75K-150K) within range; 30% margin even after 3PAO pen-test annual cost ($25K).
- Custom state tier: GSA Schedule eligible after FedRAMP Moderate ATO (12-18mo investment); state contracts averaging $250K-$2M/yr.

### Competitive Pricing Matrix (EdTech)

| Vendor | Free | Mid-tier | Enterprise | AI Compliance Premium |
|--------|------|---------|-----------|----------------------|
| Canvas (Instructure) | None | $75K-$150K/yr (district) | $500K+/yr | +15-20% for AI features |
| Moodle | OSS | $30K-$80K/yr (hosting) | Custom | None (community-driven) |
| Google Classroom | Free | Workspace EDU $5/user/yr | Custom | $0 incremental |
| Schoology (PowerSchool) | None | $5K-$50K/yr | $500K+/yr | +10-15% for AI |
| **CEXAI EdTech** | **MIT repo + FREE tier** | **$4,900-$96,000/yr** | **$250K+/yr** | **Bundled in tier** |

### Per-Student Unit Economics
- District tier: $96,000 / 50,000 students = $1.92/student/yr
- CAC target: $12,000 (district sales cycle 4-6 months) -> 8x LTV/CAC at 4-yr retention
- Renewal rate target: 92% (FERPA switching cost is high; legal review = 6 months)
- Expansion: +15%/yr via per-student attach + AI premium add-ons

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_qg_edtech_vertical | downstream | 0.49 |
| bld_instruction_edtech_vertical | downstream | 0.44 |
| edtech-vertical-builder | related | 0.42 |
| p01_kc_edtech_vertical | related | 0.42 |
| p10_mem_edtech_vertical_builder | downstream | 0.41 |
