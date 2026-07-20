---
id: kc_usage_report
kind: knowledge_card
8f: F3_inject
title: Usage Analytics Report Specification
version: 1.0.0
quality: null
pillar: P01
tldr: "Standardized analytics report format for billing dashboards -- metrics, trends, anomalies"
when_to_use: "When generating periodic resource utilization reports for CFO or ops dashboards"
keywords: [login frequency, session duration, api call volume, storage utilization, cpu usage, memory usage, error rate, feature adoption, geographic distribution]
density_score: 1.0
related:
  - usage-report-builder
  - n00_usage_report_manifest
  - bld_config_usage_report
  - bld_collaboration_usage_report
  - bld_instruction_usage_report
---

# Usage Analytics Report Specification

## Purpose
Standardized format for billing and CFO dashboards showing system resource utilization patterns.

## Structure
1. **Overview** (10% of report)
2. **Key Metrics** (40% of report)
3. **Trend Analysis** (30% of report)
4. **Anomaly Detection** (15% of report)
5. **Recommendations** (5% of report)

## Data Points
- User activity metrics (login frequency, session duration)
- API call volume by endpoint
- Storage utilization trends
- CPU/memory usage patterns
- Error rate statistics
- Feature adoption rates
- Geographic usage distribution

## Formatting
- Use tables for quantitative data
- Include time-series charts for trend analysis
- Highlight anomalies with color-coding
- Add contextual notes for irregular patterns
- Maintain consistent date formatting (YYYY-MM-DD)

## Usage Guidelines
- Update monthly for recurring subscriptions
- Generate quarterly summaries for CFO analysis
- Include system health indicators in technical reports
- Annotate seasonal variations in usage patterns
- Flag potential fraud patterns for audit review

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[usage-report-builder]] | downstream | 0.36 |
| [[bld_config_usage_report]] | downstream | 0.28 |
| [[bld_collaboration_usage_report]] | downstream | 0.27 |
| [[bld_instruction_usage_report]] | downstream | 0.27 |
