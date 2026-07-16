---
kind: instruction
id: bld_instruction_audit_log
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for audit_log
quality: null
title: "Instruction Audit Log"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [audit_log, builder, instruction]
tldr: "Step-by-step production process for audit_log"
domain: "audit_log construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [audit_log construction, instruction audit log, audit_log, builder, instruction, trust service criteria, related artifacts, retention policy, audit, downstream]
density_score: 0.85
related:
  - audit-log-builder
  - bld_knowledge_card_audit_log
  - kc_audit_log
  - p10_mem_audit_log_builder
  - n00_audit_log_manifest
---
## Phase 1: RESEARCH  
1. Identify SOC2 Type II audit requirements for log immutability and retention  
2. Map system components requiring audit logging (e.g., user access, configuration changes)  
3. Analyze existing log formats and storage mechanisms for compliance gaps  
4. Evaluate cryptographic hashing requirements for log integrity verification  
5. Determine retention periods aligned with regulatory and organizational policies  
6. Document audit control objectives from SOC2 Trust Service Criteria  

## Phase 2: COMPOSE  
1. Define log schema in bld_schema_audit_log.md with fields: timestamp, actor, action, resource, outcome, hash  
2. Specify immutability via cryptographic hash chaining in log entries  
3. Map SOC2 controls (e.g., CC7.1, CC11.2) to audit log events in bld_knowledge_card_audit_log.md  
4. Write log configuration using bld_output_template_audit_log.md format with YAML anchors  
5. Implement tamper-evident storage (e.g., write-once filesystem, WORM storage anchoring)  
6. Embed log retention policy as a top-level attribute in the artifact  
7. Add metadata for SOC2 attestation scope and audit trail scope  
8. Reference bld_schema_audit_log.md in the artifact's $schema property  
9. Finalize with cryptographic signature of the configuration file  

## Phase 3: VALIDATE  
[ ] [OK] Verify schema compliance using JSON Schema validator  
[ ] [OK] Confirm immutability mechanisms prevent log modification  
[ ] [OK] Validate retention policy aligns with SOC2 Type II requirements  
[ ] [OK] Ensure all mapped controls are represented in log events  
[ ] [OK] Confirm artifact passes SOC2 attestation checklist for audit logs

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[audit-log-builder]] | downstream | 0.55 |
| [[bld_knowledge_card_audit_log]] | upstream | 0.49 |
| [[kc_audit_log]] | upstream | 0.47 |
| [[p10_mem_audit_log_builder]] | downstream | 0.44 |
| [[n00_audit_log_manifest]] | downstream | 0.37 |
