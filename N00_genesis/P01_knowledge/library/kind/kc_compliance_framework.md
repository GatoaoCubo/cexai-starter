---
id: kc_compliance_framework
kind: knowledge_card
8f: F3_inject
title: Compliance Framework
version: 1.0.0
quality: null
pillar: P01
tldr: "Structured approach mapping AI operations to regulations with attestation and continuous monitoring"
when_to_use: "When establishing an organization-wide compliance program spanning multiple regulatory standards"
keywords: [gdpr, ccpa, hipaa, iso/iec 27001, nist ai risk management framework, soc 2, data privacy, bias mitigation, risk assessments, control implementations]
density_score: 0.87
related:
  - bld_knowledge_card_compliance_framework
  - compliance-framework-builder
  - bld_instruction_compliance_framework
  - p11_qg_compliance_framework
  - p10_lr_compliance_framework_builder
---

A compliance framework for AI systems is a structured approach to ensuring alignment with regulatory requirements, ethical standards, and organizational policies. It provides a systematic way to map AI operations to applicable regulations, assess risks, and implement controls.

**Key Components:**
1. **Regulatory Mapping**  
   - Identify relevant laws (e.g., GDPR, CCPA, HIPAA) and industry standards (e.g., ISO/IEC 27001) applicable to AI systems.  
   - Document how system features interact with regulatory requirements (e.g., data privacy, bias mitigation).  

2. **Attestation Process**  
   - Validate compliance through audits, third-party certifications, or internal reviews.  
   - Maintain records of compliance activities, including risk assessments, control implementations, and incident responses.  

3. **Continuous Monitoring**  
   - Regularly update the framework to reflect changes in regulations or system capabilities.  
   - Use automated tools to track compliance metrics and flag potential gaps.  

**Examples of Regulatory Alignment:**  
- GDPR: Ensure data subject rights (e.g., right to be forgotten) are implemented.  
- NIST AI Risk Management Framework: Address governance, data quality, and transparency.  
- SOC 2: Demonstrate controls for security, availability, and privacy.  

This framework enables organizations to demonstrate accountability, reduce legal risks, and build trust with stakeholders.

## How to use

You are a builder or governance lead standing up a compliance program. Load this card
when the task spans multiple regulations at once. Use the three Key Components as the
program's backbone: instantiate a Regulatory Mapping for your `{{APPLICABLE_REGULATIONS}}`,
wire the Attestation Process to your evidence store, and schedule Continuous Monitoring.
Express the result as a `compliance_framework` artifact, not prose.

## Procedure

1. Enumerate `{{APPLICABLE_REGULATIONS}}` for the system's domain and data classes.
2. Build the Regulatory Mapping: each feature -> the requirement(s) it must satisfy.
3. Define the Attestation Process: audits, certifications, and the records to retain.
4. Stand up Continuous Monitoring with automated metrics and gap alerts.
5. Run a baseline assessment; record gaps as remediation items with owners.
6. Re-attest on each regulation change or major system release.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_compliance_framework]] | sibling | 0.43 |
| [[compliance-framework-builder]] | downstream | 0.41 |
| [[bld_instruction_compliance_framework]] | downstream | 0.38 |
| [[p11_qg_compliance_framework]] | downstream | 0.37 |
| [[p10_lr_compliance_framework_builder]] | downstream | 0.35 |
