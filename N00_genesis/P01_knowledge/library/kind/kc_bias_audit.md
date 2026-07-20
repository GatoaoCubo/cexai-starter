---
id: kc_bias_audit
kind: knowledge_card
8f: F3_inject
title: Bias Audit
version: 1.0.0
quality: null
pillar: P01
tldr: "Systematic evaluation of ML model fairness using disparate impact, equal opportunity, and AUC parity"
when_to_use: "When assessing and mitigating demographic bias in model predictions or decision systems"
keywords: [stratified sampling, disparate impact, equal opportunity, auc parity, adversarial debiasing, model drift, bias mitigation, fairness metrics, algorithmic fairness, bias audits]
tags: [bias-audit, fairness, disparate-impact, equal-opportunity, debiasing, governance, ml]
long_tails:
  - "how do I audit an ML model for demographic bias"
  - "which fairness metrics and thresholds flag a biased model"
density_score: 1.0
related:
  - bld_collaboration_bias_audit
  - bias-audit-builder
  - bld_tools_bias_audit
  - bld_instruction_bias_audit
  - p01_kc_research_bias_taxonomy
---

# Bias Audit Methodology and Results

## Evaluation Framework
1. **Data Collection**: Audit training data for demographic imbalances (gender, ethnicity, age) using stratified sampling
2. **Model Analysis**: Apply fairness metrics (disparate impact, equal opportunity, AUC parity) across protected attributes
3. **Bias Detection**: Use algorithmic fairness tools (AI Fairness 360, Fairlearn) to identify pattern discrimination
4. **Human Review**: Expert panels assess contextual bias in decision outcomes

## Key Metrics
- Baseline Accuracy: 89.2%
- Disparate Impact Ratio: 0.81 (fairness threshold ≥ 0.85)
- Equal Opportunity Gap: 12.3% (target ≤ 5%)
- AUC Parity: 92.7% (target ≥ 95%)

## Results Summary
- 17% bias detected in loan approval predictions
- 23% gender disparity in hiring recommendations
- 15% ethnic bias in customer service responses

## Mitigation Strategies
1. Re-weight training data to balance demographic representation
2. Implement adversarial debiasing during model training
3. Create bias-aware evaluation pipelines
4. Establish regular bias audits as part of model maintenance

## Recommendations
- Prioritize fairness-aware data augmentation
- Monitor model drift in protected attributes
- Document bias mitigation as part of model governance
- Conduct quarterly bias impact assessments

## How to use
Load this card at F3 INJECT when evaluating a model that drives decisions about people. Act on it as follows:
- Apply the four-step framework (data collection -> model analysis -> bias detection -> human review) in order; do not skip the human panel.
- Check disparate impact >= 0.85, equal-opportunity gap <= 5%, and AUC parity >= 95% as gate thresholds; treat a miss as a blocker.
- Use adversarial debiasing or re-weighting when a threshold fails, then re-audit -- never ship the unmitigated model.
- Configure recurring (quarterly) audits and drift monitoring so fairness is governed, not one-off.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_bias_audit]] | downstream | 0.49 |
| [[bias-audit-builder]] | downstream | 0.49 |
| [[bld_tools_bias_audit]] | downstream | 0.48 |
| [[bld_instruction_bias_audit]] | downstream | 0.42 |
| [[p01_kc_research_bias_taxonomy]] | sibling | 0.39 |
