---
id: kc_discovery_questions
kind: knowledge_card
8f: F3_inject
title: MEDDIC/BANT Discovery Question Bank
version: 1.0.0
quality: null
pillar: P01
tldr: "MEDDIC/BANT question bank for sales discovery across buyer personas and deal stages"
when_to_use: "When preparing structured discovery calls to qualify leads and uncover decision criteria"
keywords: [kpis, roi metrics, rfp criteria, procurement policies, technical integrations, infrastructure, strategic goals]
density_score: 0.89
related:
  - p10_mem_discovery_questions_builder
  - kc_competitive_matrix
  - bld_knowledge_card_discovery_questions
  - bld_instruction_discovery_questions
  - p01_qg_discovery_questions
---

**MEDDIC Framework Questions**  
**Metrics**:  
- What key performance indicators (KPIs) do you track for this function?  
- How do you measure success in your current workflow?  

**Economic Impact**:  
- What budget constraints exist for this initiative?  
- What are the potential cost savings or revenue opportunities?  

**Decision Criteria**:  
- What specific outcomes must this solution deliver?  
- Are there any compliance or regulatory requirements to consider?  

**Identify Decision Maker**:  
- Who holds the final authority to approve this purchase?  
- Are there any stakeholders with veto power?  

**Champion**:  
- Who will advocate for this solution within your organization?  
- What challenges might hinder adoption?  

**BANT Framework Questions**  
**Budget**:  
- What is the allocated budget for this project?  
- Are there any cost constraints or preferred pricing models?  

**Authority**:  
- Who owns the budget and decision-making process?  
- Are there any procurement policies or approval hierarchies?  

**Need**:  
- What specific problems are you trying to solve?  
- How does this align with your strategic goals?  

**Timeline**:  
- What is the expected timeline for implementation?  
- Are there any critical deadlines or milestones?  

*Buyer Personas & Deal Stages*  
**IT Manager (Evaluation Stage)**:  
- What technical integrations are required?  
- How will this solution impact existing infrastructure?  

**Procurement Officer (Negotiation Stage)**:  
- What RFP criteria are prioritized?  
- Are there any preferred vendors or contracts?  

**C-Level Executive (Decision Stage)**:  
- How does this align with our overall business strategy?  
- What ROI metrics will be used to evaluate success?

## How to use

You are an account executive prepping a discovery call. Load this bank to assemble a
question set matched to the `{{BUYER_PERSONA}}` and `{{DEAL_STAGE}}`. Open with Metrics and
Need, qualify with Budget and Authority, and close by confirming Decision Criteria and a
Champion. Capture answers back into the deal record so later stages inherit context.

## Procedure (run discovery)

1. Identify the `{{BUYER_PERSONA}}` and current `{{DEAL_STAGE}}` before the call.
2. Pull the matching MEDDIC + BANT questions plus the persona-specific set.
3. Lead with Metrics and Need to surface the pain; quantify with Economic Impact.
4. Qualify Budget, Authority, and Timeline to confirm the deal is real.
5. Lock Decision Criteria and name a Champion who will advocate internally.
6. Log every answer to the CRM so negotiation and decision stages reuse it.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_mem_discovery_questions_builder]] | downstream | 0.30 |
| [[kc_competitive_matrix]] | sibling | 0.29 |
| [[bld_knowledge_card_discovery_questions]] | sibling | 0.27 |
| [[bld_instruction_discovery_questions]] | downstream | 0.26 |
| [[p01_qg_discovery_questions]] | downstream | 0.26 |
