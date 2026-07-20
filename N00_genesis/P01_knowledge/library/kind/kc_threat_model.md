---
id: kc_threat_model
kind: knowledge_card
8f: F3_inject
title: Threat Model
version: 1.0.0
quality: null
pillar: P01
tldr: "Structured identification of assets, threats, vulnerabilities, risks, and mitigations for AI systems"
when_to_use: "When assessing security risks like data breaches, model poisoning, or output bias"
keywords: [threat model, data breach, model poisoning, bias in outputs, vulnerabilities, mitigation strategies, risk assessment, encryption, access controls]
density_score: 0.98
related:
  - bld_knowledge_card_threat_model
  - threat-model-builder
  - bld_instruction_threat_model
  - kc_ai_rmf_profile
  - bld_knowledge_card_dataset_card
---

# Threat Model
A structured approach to identifying, assessing, and mitigating risks in AI systems.

## Key Components
- **Assets**: Identify critical data, systems, and services.
- **Threats**: Potential malicious actions (e.g., data breaches, model poisoning).
- **Vulnerabilities**: Weaknesses in systems or processes.
- **Risks**: Likelihood and impact of threats exploiting vulnerabilities.
- **Mitigation Strategies**: Controls to reduce risks (e.g., encryption, access controls).

## Risk Assessment
- **Criteria**: Use qualitative (low/medium/high) or quantitative (probability × impact) metrics.
- **Prioritization**: Focus on high-impact risks first.

## Examples
- **Data Breach**: Unauthorized access to sensitive data.
- **Model Poisoning**: Manipulating training data to degrade model performance.
- **Bias in Outputs**: Systematic errors in AI decisions due to flawed data.

## How to use this card

```text
Role: you are N05/security reasoning about the risk surface of an AI system.
Action: walk the five components in order -- enumerate Assets, then the Threats
against each, the Vulnerabilities they exploit, the resulting Risk (likelihood x
impact), and a Mitigation per high risk. Score each risk low/medium/high and
prioritize the high-impact ones first. Use this card to FRAME a threat_model
artifact; pair it with kc_ai_rmf_profile for governance-grade risk profiling.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_threat_model]] | sibling | 0.32 |
| [[threat-model-builder]] | downstream | 0.23 |
| [[bld_instruction_threat_model]] | downstream | 0.22 |
| [[kc_ai_rmf_profile]] | sibling | 0.22 |
| [[bld_knowledge_card_dataset_card]] | sibling | 0.22 |
