---
id: kc_compliance_checklist
kind: knowledge_card
8f: F3_inject
title: Compliance Checklist
version: 1.0.0
quality: null
pillar: P01
tldr: "Actionable checklist of regulatory controls for SOC2, GDPR, and HIPAA compliance verification"
when_to_use: "When auditing a system against specific regulatory frameworks with discrete pass/fail items"
keywords: [data encryption, data flow diagrams, incident response protocols, business associate agreements, electronic health record access, data protection impact assessments, data subject rights, lawful basis for data processing]
tags: [compliance, soc2, gdpr, hipaa, checklist, audit, governance]
long_tails:
  - "what controls do I check for SOC2, GDPR, and HIPAA compliance"
  - "how do I run a pass/fail regulatory audit on a system"
density_score: 1.0
related:
  - p01_kc_data_residency
  - p01_kc_ai_compliance_gdpr
  - bld_instruction_compliance_checklist
  - bld_knowledge_card_compliance_checklist
  - p11_qg_compliance_checklist
---

# Compliance Checklist

## SOC2
- [ ] Verify data encryption in transit and at rest
- [ ] Confirm third-party vendor agreements
- [ ] Audit access controls and permissions
- [ ] Validate incident response protocols
- [ ] Ensure system and data availability metrics

## GDPR
- [ ] Implement data subject rights processes
- [ ] Conduct data protection impact assessments
- [ ] Maintain detailed data flow diagrams
- [ ] Establish data breach notification procedures
- [ ] Ensure lawful basis for data processing

## HIPAA
- [ ] Validate HIPAA-compliant data storage
- [ ] Confirm business associate agreements
- [ ] Audit electronic health record access
- [ ] Enforce minimum-necessary access to PHI
- [ ] Verify breach notification procedures within required timelines

## How to use
Load this card at F3 INJECT when auditing a system for regulatory readiness. Act on it as follows:
- Run each box as a discrete pass/fail control; a single unchecked item blocks the compliance sign-off.
- Apply only the frameworks in scope (SOC2 / GDPR / HIPAA) for the deployment; do not over-audit.
- Attach evidence (config, logs, agreements) to every checked item so the audit is reproducible.
- Pair with `kc_ai_compliance_gdpr` and `p09_kc_data_residency` for framework-specific depth.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_data_residency]] | sibling | 0.36 |
| [[p01_kc_ai_compliance_gdpr]] | sibling | 0.34 |
| [[bld_instruction_compliance_checklist]] | downstream | 0.31 |
| [[bld_knowledge_card_compliance_checklist]] | sibling | 0.30 |
| [[p11_qg_compliance_checklist]] | downstream | 0.29 |
