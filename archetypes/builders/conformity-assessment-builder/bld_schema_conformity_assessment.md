---
kind: schema
id: bld_schema_conformity_assessment
pillar: P06
llm_function: CONSTRAIN
purpose: Data schema defining all required fields for a conformity_assessment artifact
quality: null
title: "Conformity Assessment Builder -- Schema"
version: "1.0.0"
author: wave7_n05
tags: [conformity_assessment, builder, schema]
tldr: "Field definitions and validation rules for EU-AI-Act Annex-IV conformity assessment artifacts"
domain: "conformity_assessment construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [conformity_assessment construction, conformity_assessment, builder, schema, conformity assessment builder, level fields, clinical decision support]
density_score: 0.85
related:
  - bld_instruction_conformity_assessment
  - bld_schema_model_registry
  - bld_collaboration_conformity_assessment
  - p03_constraint_brand_config_n06
  - bld_schema_dataset_card
---
# Conformity Assessment Builder -- Schema

## Top-Level Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| system_name | string | MANDATORY | Full name of the AI system | "MedTriage-v2 Clinical Decision Support" |
| system_version | string | MANDATORY | Version under assessment | "2.1.4" |
| provider_name | string | MANDATORY | Legal name of the provider per Art. 3(3) | "Acme Health AI GmbH" |
| provider_address | string | MANDATORY | Registered address of the provider | "Musterstrasse 1, 10115 Berlin, DE" |
| provider_contact | string | MANDATORY | Contact email or URL for technical queries | "compliance@acmehealth.ai" |
| annex_iii_category | enum | MANDATORY | Which Annex-III category applies | see Annex-III categories below |

## Annex-III Category Enum

| Value | Annex-III Reference | Notified Body Required? |
|-------|--------------------|-----------------------|
| biometric_identification | Annex III(1)(a) | YES (real-time remote) |
| biometric_categorisation | Annex III(1)(b) | NO (internal check) |
| critical_infrastructure | Annex III(2) | NO |
| education_vocational | Annex III(3) | NO |
| employment_workers | Annex III(4) | NO |
| essential_services | Annex III(5) | NO |

## Nested Object: risk_management_system

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| rms.process_description | string | MANDATORY | Description of the iterative RMS process (Art. 9) |
| rms.risks_identified | list[string] | MANDATORY | List of identified risks |
| rms.risk_estimation_method | string | MANDATORY | Method used to estimate and evaluate risks |
| rms.mitigation_measures | list[object] | MANDATORY | Each: {risk_id, measure, residual_risk_level} |
| rms.residual_risk_evaluation | string | MANDATORY | Overall assessment of acceptable residual risk |
| rms.review_schedule | string | MANDATORY | Cadence for post-deployment risk review |

## Nested Object: data_governance_plan

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| dgp.training_datasets | list[object] | MANDATORY | Each: {name, source, size, date_range, license} |
| dgp.validation_datasets | list[object] | MANDATORY | Each: {name, source, size, purpose} |
| dgp.test_datasets | list[object] | MANDATORY | Each: {name, source, size, purpose} |
| dgp.quality_criteria | list[string] | MANDATORY | Data quality criteria applied per Art. 10(3) |
| dgp.bias_mitigation | string | MANDATORY | Bias examination and mitigation measures |
| dgp.known_limitations | list[string] | MANDATORY | Known gaps or limitations in datasets |
| dgp.data_provenance | string | MANDATORY | Data lineage and provenance documentation ref |

## Nested Object: human_oversight_measures

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| hom.override_capability | string | MANDATORY | How humans can override or stop the system (Art. 14) |
| hom.interpretability_tools | list[string] | MANDATORY | Tools or methods for interpretability/explainability |
| hom.operator_training | string | MANDATORY | Training requirements for human overseers |
| hom.monitoring_interface | string | MANDATORY | Description of real-time monitoring dashboard |
| hom.anomaly_alerting | string | MANDATORY | How anomalies are surfaced to human operators |

## Nested Object: accuracy_robustness_cybersecurity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| arc.accuracy_metrics | list[object] | MANDATORY | Each: {metric_name, threshold, achieved, dataset} |
| arc.robustness_measures | string | MANDATORY | Adversarial testing results and fallback spec |
| arc.cybersecurity_controls | string | MANDATORY | Threat model ref and penetration test summary |
| arc.degradation_handling | string | MANDATORY | Graceful degradation procedure |

## Nested Object: post_market_monitoring_plan

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pmm.objectives | list[string] | MANDATORY | Monitoring objectives and KPIs (Art. 72) |
| pmm.data_collection_method | string | MANDATORY | Telemetry or feedback pipeline specification |
| pmm.serious_incident_procedure | string | MANDATORY | SIR reporting procedure per Art. 73 |
| pmm.review_schedule | string | MANDATORY | Periodic review dates |
| pmm.corrective_action_thresholds | list[object] | MANDATORY | Each: {kpi, threshold, action} |
| pmm.report_recipients | list[string] | MANDATORY | Authorities and stakeholders for PMM reports |

## Validation Rules

| Rule | Constraint |
|------|-----------|
| ID pattern | ^p11_ca_[a-z0-9_]+\.md$ |
| kind | must be exactly "conformity_assessment" |
| annex_iii_category | must be one of the enum values above |
| article_43_procedure | must be "internal_check" or "notified_body" |
| notified_body_id | required if and only if article_43_procedure == "notified_body" |
| rms | all sub-fields mandatory, no nulls |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_conformity_assessment]] | upstream | 0.33 |
| [[bld_schema_model_registry]] | sibling | 0.33 |
| [[bld_collaboration_conformity_assessment]] | downstream | 0.32 |
| [[p03_constraint_brand_config_n06]] | related | 0.30 |
| [[bld_schema_dataset_card]] | sibling | 0.30 |
