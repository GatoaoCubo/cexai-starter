---
kind: architecture
id: bld_architecture_compliance_framework
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of compliance_framework -- inventory, dependencies
quality: null
title: "Architecture Compliance Framework"
version: "1.1.0"
author: n05_ops
tags: [compliance_framework, builder, architecture]
tldr: "Component map of compliance_framework -- inventory, dependencies"
domain: "compliance_framework construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [compliance_framework construction, architecture compliance framework, compliance_framework, builder, architecture, component inventory, policy engine, compliance team, rule validator, in development]
density_score: 0.85
related:
  - bld_architecture_sandbox_config
  - bld_architecture_action_paradigm
  - bld_architecture_audit_log
  - bld_architecture_bias_audit
  - bld_architecture_collaboration_pattern
---

## Component Inventory  
| Name | Role | Owner | Status |  
|------|------|-------|--------|  
| Policy Engine | Core compliance logic | Compliance Team | Active |  
| Rule Validator | Validates rules against standards | DevOps | In Development |  
| Audit Logger | Logs compliance events | Security | Active |  
| Data Store | Stores compliance data | DB Team | Active |  
| User Interface | Configures framework | UX Team | In Development |  
| Compliance Reporter | Generates reports | Analytics | Active |  
| Configuration Manager | Manages framework settings | DevOps | Active |  

## Dependencies  
| From | To | Type |  
|------|----|------|  
| Policy Engine | Rule Validator | Validation |  
| Rule Validator | Data Store | Storage |  
| Audit Logger | Data Store | Storage |  
| User Interface | Policy Engine | Control |  
| Compliance Reporter | Audit Logger | Reporting |  

## Architectural Position  
The compliance_framework-builder sits within CEX's P11 Feedback pillar as the external regulatory mapping module. It consumes outputs from threat_model (risk exposure data), incident_report (breach notifications triggering GDPR Art. 33 obligations), and safety_policy (internal rules to cross-reference). It produces compliance attestations consumed by audit processes, legal teams, and external regulators. Covers GDPR, EU AI Act, NIST AI RMF, ISO 42001, HIPAA, and sector-specific regulations. Does NOT enforce runtime safety (guardrail) or detect threats (threat_model).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_sandbox_config]] | sibling | 0.32 |
| [[bld_architecture_action_paradigm]] | sibling | 0.32 |
| [[bld_architecture_audit_log]] | sibling | 0.32 |
| [[bld_architecture_bias_audit]] | sibling | 0.31 |
| [[bld_architecture_collaboration_pattern]] | sibling | 0.31 |
