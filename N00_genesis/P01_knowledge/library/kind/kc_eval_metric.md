---
id: kc_eval_metric
kind: knowledge_card
8f: F3_inject
title: Evaluation Metric Definition
version: 1.0.0
quality: null
pillar: P01
tldr: "Quantitative measure definition for assessing ML model or system performance objectively"
when_to_use: "When defining specific metrics like accuracy, F1, or AUC-ROC for model evaluation"
keywords: [accuracy, precision, recall, f1-score, auc-roc, mean absolute error (mae)]
density_score: 0.96
related:
  - bld_knowledge_card_eval_metric
  - eval-metric-builder
  - p10_mem_eval_metric_builder
  - eval-framework-builder
  - bld_collaboration_eval_metric
---

# Evaluation Metric Definition

An evaluation metric is a quantitative measure used to assess the performance of machine learning models, algorithms, or systems. It provides objective criteria for comparing different approaches and validating results.

## Key Characteristics
- **Objectivity**: Metrics quantify performance without subjective interpretation
- **Comparability**: Enables benchmarking between models
- **Specificity**: Measures particular aspects of performance (e.g., accuracy, precision)
- **Interpretability**: Results should be meaningful to stakeholders

## Common Metrics
- **Accuracy**: Ratio of correct predictions to total predictions
- **Precision**: Ratio of true positives to all predicted positives
- **Recall**: Ratio of true positives to actual positives
- **F1-score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under the receiver operating characteristic curve
- **Mean Absolute Error (MAE)**: Average absolute difference between predicted and actual values

## Use Cases
1. Model selection and hyperparameter tuning
2. Performance validation across datasets
3. Comparative analysis of algorithms
4. Progress tracking during training
5. Stakeholder reporting and justification

## Best Practices
- Choose metrics aligned with business objectives
- Use multiple metrics for comprehensive evaluation
- Validate metrics across different data distributions
- Document metric definitions and calculation methods
- Monitor metric drift over time

## How to use

```text
ROLE: you are defining how a model or system will be judged.
1. Pick the metric class from Common Metrics that matches the task (classification vs regression).
2. State the exact definition + calculation so the score is reproducible.
3. Pair at least two complementary metrics (e.g. precision + recall) to avoid blind spots.
4. Validate across data distributions and monitor for metric drift over time.
Primary 8F verb: INJECT (this card grounds an eval at F3; the running gate lives in P07/P11 kinds).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_eval_metric]] | sibling | 0.44 |
| [[eval-metric-builder]] | downstream | 0.30 |
| [[p10_mem_eval_metric_builder]] | downstream | 0.23 |
| eval-framework-builder | downstream | 0.22 |
| [[bld_collaboration_eval_metric]] | downstream | 0.22 |
