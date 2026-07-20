---
id: kc_conformity_assessment
kind: knowledge_card
8f: F3_inject
title: Conformity Assessment for High-Risk AI Systems (EU AI Act Annex IV)
version: 1.0.0
quality: null
pillar: P01
tldr: "EU AI Act Annex IV assessment procedure for high-risk AI: modules A/B/C, CE marking, and declaration"
when_to_use: "When a high-risk AI system requires formal conformity assessment before EU market placement"
keywords: [technical documentation, risk management, conformity assessment modules, ce marking, conformity statement, high-risk systems, moderate-risk systems, notified body]
density_score: 0.84
related:
  - bld_manifest_conformity_assessment
  - bld_knowledge_card_conformity_assessment
  - n00_conformity_assessment_manifest
  - bld_instruction_conformity_assessment
  - p11_fb_conformity_assessment
---

**EU AI Act Annex IV Conformity Assessment**  
*Article 43 · Deadline: August 2026*

High-risk AI systems must undergo conformity assessment per Annex IV, ensuring compliance with the EU AI Act's requirements. Key obligations include:

1. **Technical Documentation**  
   - Detailed records of system design, risk management, and safety measures  
   - Evidence of compliance with transparency, data governance, and human oversight requirements  

2. **Conformity Assessment Modules**  
   - **Module A (Internal Assessment):** Developer self-assessment for low-risk systems  
   - **Module B (External Assessment):** Third-party evaluation for moderate-risk systems  
   - **Module C (Notified Body):** Mandatory for high-risk systems requiring strict oversight  

3. **CE Marking Obligation**  
   - Systems passing assessment must bear the CE mark, indicating compliance with EU safety standards  

4. **Conformity Statement**  
   - Developers must issue a formal declaration confirming compliance with all applicable requirements  

The August 2026 deadline applies to systems developed after 2024, requiring full conformity assessment before market placement. Non-compliance risks financial penalties and restricted market access.

## How to use

You are a compliance builder readying a high-risk AI system for the EU market. Load this
card to pick the right evaluation module and build the evidence pack. Choose by `{{RISK_TIER}}`,
draft the Annex IV documentation, then issue the declaration and apply CE marking -- captured
as a `conformity_assessment` artifact.

## Procedure

1. Classify `{{RISK_TIER}}` (low / moderate / high) per the EU AI Act.
2. Pick the path: A self for low, B third-party for moderate, C notified-body for high.
3. Draft Annex IV docs: design, governance, oversight, safety evidence.
4. Execute the chosen path; close every finding.
5. Sign the declaration; affix CE marking.
6. Archive the evidence pack before placing on market.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_manifest_conformity_assessment]] | downstream | 0.41 |
| [[bld_knowledge_card_conformity_assessment]] | sibling | 0.38 |
| [[bld_instruction_conformity_assessment]] | downstream | 0.30 |
| [[p11_fb_conformity_assessment]] | downstream | 0.25 |
