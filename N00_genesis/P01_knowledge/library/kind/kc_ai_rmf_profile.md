---
id: kc_ai_rmf_profile
kind: knowledge_card
8f: F3_inject
title: AI RMF Profile
version: 1.0.0
quality: null
pillar: P01
language: English
tldr: "NIST AI RMF implementation profile mapping 13 GenAI risk categories to GOVERN/MAP/MEASURE/MANAGE functions"
when_to_use: "When building a risk management profile for AI systems aligned with NIST AI 600-1 standards"
keywords: [ai risk management, genai, risk appetite, bias audits, diverse training data, penetration testing, secure apis, data anonymization, access controls]
density_score: 1.0
related:
  - ai-rmf-profile-builder
  - bld_instruction_ai_rmf_profile
  - bld_knowledge_card_ai_rmf_profile
  - p11_qg_ai_rmf_profile
  - p01_kc_atom_24_nist_vocabulary
---

# AI RMF Profile (NIST AI RMF Artifact)

## Overview
This artifact implements the NIST AI Risk Management Framework (AI RMF) profile, compliant with AI 600-1 standards. It provides structured guidance for managing GenAI risks through four core functions:

## 4 Core Functions
1. **GOVERN**  
   - Establish governance policies and accountability  
   - Define risk appetite and decision-making authority  
   - Integrate AI risk management into organizational strategy  

2. **MAP**  
   - Identify AI systems and their operational contexts  
   - Map risk categories to specific AI capabilities  
   - Develop risk scenarios and impact assessments  

3. **MEASURE**  
   - Quantify risk exposure using standardized metrics  
   - Monitor AI system performance and bias patterns  
   - Track compliance with regulatory requirements  

4. **MANAGE**  
   - Implement risk mitigation strategies  
   - Continuously improve AI systems through feedback loops  
   - Maintain documentation for audit and review  

## 13 GenAI Risk Categories
- Data Privacy  
- Model Bias  
- Intellectual Property  
- Security Vulnerabilities  
- Operational Reliability  
- Ethical Implications  
- Regulatory Compliance  
- System Interoperability  
- Human-AI Collaboration  
- Environmental Impact  
- Job Displacement Risks  
- Data Integrity  
- Transparency & Explainability  

## Action-ID Mappings
Each risk category is linked to specific remediation actions:  
- **Data Privacy**: ACTION-001 (Data Anonymization), ACTION-002 (Access Controls)  
- **Model Bias**: ACTION-003 (Bias Audits), ACTION-004 (Diverse Training Data)  
- **Security Vulnerabilities**: ACTION-005 (Penetration Testing), ACTION-006 (Secure APIs)  

## Compliance
This profile aligns with NIST Special Publication 600-1 (AI Risk Management) and provides a structured approach to:  
- Identify, assess, and mitigate AI-related risks  
- Ensure ethical and compliant AI system development  
- Support continuous improvement through measurement and feedback

### How to use this card

```text
ROLE: you are N05/governance building a NIST-aligned risk profile for an AI system.
8F: INJECT this card at F3 to FRAME an ai_rmf_profile and feed its quality gate.
You must run all four functions; never ship a profile missing MANAGE mitigations.
Action: run the four functions as a loop -- GOVERN (set policy + risk appetite),
MAP (identify the system + which of the 13 categories apply), MEASURE (quantify
exposure + monitor bias), MANAGE (apply mitigations + keep audit docs). For each
applicable risk category, attach its Action-ID remediations.
```

### Procedure (build the profile)

```text
Step 1  GOVERN   -- set governance policy, risk appetite, decision authority.
Step 2  MAP      -- identify the system + which of the 13 categories apply.
Step 3  MEASURE  -- quantify exposure with metrics; monitor performance + bias.
Step 4  MANAGE   -- apply mitigations; attach each Action-ID; keep audit docs.
Step 5  REVIEW   -- loop on feedback; re-MEASURE after each mitigation lands.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[ai-rmf-profile-builder]] | downstream | 0.51 |
| [[bld_instruction_ai_rmf_profile]] | downstream | 0.43 |
| [[bld_knowledge_card_ai_rmf_profile]] | sibling | 0.41 |
| [[p11_qg_ai_rmf_profile]] | downstream | 0.36 |
