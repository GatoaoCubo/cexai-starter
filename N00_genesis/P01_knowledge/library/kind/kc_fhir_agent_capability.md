---
id: kc_fhir_agent_capability
kind: knowledge_card
8f: F3_inject
title: HL7 FHIR R5 AI Agent Capability Declaration
version: 1.0.0
quality: null
pillar: P01
tldr: "AI agent capability declaration for HL7 FHIR R5 with SMART scopes and PHI handling"
when_to_use: "When building AI agents that interact with healthcare FHIR systems under HIPAA/GDPR constraints"
keywords: [fhir r, ai agent capability declaration, agent capability declaration, health card, hooks integration, transparency extension, smart fhir, clinical decision, decision support, downstream]
tags: [fhir, smart-on-fhir, cds-hooks, phi, hipaa, capability, healthcare, agent]
long_tails:
  - "what capabilities must an AI agent declare to talk to a FHIR R5 system"
  - "how do SMART on FHIR scopes and CDS Hooks apply to an AI agent"
density_score: 0.98
related:
  - fhir-agent-capability-builder
  - bld_knowledge_card_fhir_agent_capability
  - bld_tools_fhir_agent_capability
  - bld_instruction_fhir_agent_capability
  - healthcare_vertical_fhir_workflows
---

**HL7 FHIR R5 AI Agent Capability Declaration**

This card defines the technical capabilities required for AI agents to interact with FHIR R5 systems securely and effectively. Key components include:

1. **SMART on FHIR Scopes**  
   - OAuth 2.0 scopes for read/write access to FHIR resources  
   - Support for SMART Health Card standards  
   - Dynamic client registration capabilities

2. **PHI Handling**  
   - Compliance with HIPAA and GDPR regulations  
   - Anonymization techniques for protected health information  
   - Access control based on role-based permissions

3. **CDS Hooks Integration**  
   - Support for clinical decision support hooks  
   - Real-time interaction with EHR systems  
   - Context-aware recommendation generation

4. **AI Transparency Extension**  
   - Implementation of AI Transparency Extension for FHIR  
   - Metadata tracking for model inputs/outputs  
   - Audit trail for AI-generated clinical recommendations

5. **Security Requirements**  
   - TLS 1.2+ encryption for data in transit  
   - Token-based authentication with JWT support  
   - Regular security vulnerability assessments

**Use Cases**:  
- Clinical decision support systems  
- Patient data analysis tools  
- AI-powered diagnostic assistants  
- Interoperability testing frameworks

**Implementation Notes**:  
- Must include FHIR version 5.0+ compatibility  
- Requires SMART on FHIR implementation  
- Should support both RESTful and messaging interfaces

## How to use
Load this card at F3 INJECT when an agent must read or write FHIR resources. Act on it as follows:
- Configure OAuth 2.0 / SMART on FHIR scopes for least-privilege read/write before any resource call.
- Apply HIPAA/GDPR PHI handling: anonymize, enforce role-based access, and keep an audit trail for every AI-generated recommendation.
- Use CDS Hooks for real-time, context-aware EHR interaction rather than polling.
- Always require TLS 1.2+ and JWT-based auth; pair with `kc_healthcare_vertical` for the regulatory frame and `healthcare_vertical_fhir_workflows` for end-to-end flows.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[fhir-agent-capability-builder]] | downstream | 0.53 |
| [[bld_knowledge_card_fhir_agent_capability]] | sibling | 0.48 |
| [[bld_tools_fhir_agent_capability]] | downstream | 0.46 |
| [[bld_instruction_fhir_agent_capability]] | downstream | 0.45 |
| [[healthcare_vertical_fhir_workflows]] | related | 0.43 |
