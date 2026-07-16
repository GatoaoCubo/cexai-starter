---
kind: knowledge_card
id: bld_knowledge_card_conformity_assessment
pillar: P01
llm_function: INJECT
purpose: Domain knowledge reference for EU AI Act Annex-IV conformity assessment concepts
quality: null
title: "Conformity Assessment Builder -- Knowledge Card"
version: "1.0.0"
author: wave7_n05
tags: [conformity_assessment, builder, knowledge_card]
tldr: "EU-AI-Act high-risk AI system concepts, Annex III categories, Annex IV requirements, key standards"
domain: "conformity_assessment construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [conformity_assessment construction, annex iii categories, annex iv requirements, key standards, conformity_assessment, builder, knowledge_card, conformity assessment builder, knowledge card, domain overview
the]
density_score: 0.85
---
# Conformity Assessment Builder -- Knowledge Card

## Domain Overview

The EU Artificial Intelligence Act (Regulation 2024/1689, "EU AI Act") establishes a
risk-based regulatory framework for AI systems placed on or put into service in the EU.
High-risk AI systems -- defined by Annex III -- must undergo a conformity assessment
procedure under Article-43 before market placement.

The Aug-2026 deadline applies to existing high-risk systems under transitional provisions
(EU AI Act Art. 113(2)). New systems must comply from the Act's application date (Aug 2026
for most high-risk provisions).

**This builder specializes in**: producing the Annex-IV technical documentation package
required by Article 11, supporting the Article-43 conformity procedure.
## Key Concepts

| Concept | Definition | EU AI Act Reference |
|---------|-----------|-------------------|
| Conformity assessment | Procedure verifying a high-risk AI system meets requirements before market placement | Art. 43 |
| Annex III | Exhaustive list of 8 high-risk AI application areas | Annex III |
| Annex IV | Required content of technical documentation for high-risk AI | Annex IV |
| Risk-management-system (RMS) | Iterative process: identify, estimate, evaluate, mitigate, monitor AI risks | Art. 9 |
| Data governance | Requirements for training/validation/test data quality, bias, provenance | Art. 10 |
| Human-oversight | Measures enabling humans to monitor, override, and correct AI outputs | Art. 14 |
## Annex-III High-Risk Categories

| # | Category | Examples | NB Required? |
|---|----------|---------|-------------|
| 1(a) | Biometric identification (real-time remote) | Live facial recognition in public spaces | YES |
| 1(b) | Biometric categorisation by sensitive attributes | Emotion detection, sexual orientation inference | NO |
| 2 | Critical infrastructure safety | AI in power grids, water systems, transport | NO |
| 3 | Education and vocational training | Exam scoring AI, student assessment tools | NO |
| 4 | Employment and workers management | CV screening, performance monitoring, task allocation | NO |
| 5 | Essential private/public services | Credit scoring, benefits eligibility, emergency dispatch | NO |

**Note**: Annex III categories are exhaustive. If the system does not fit any category,
it is NOT high-risk under Annex III and this builder does not apply.
## Annex-IV Technical Documentation Requirements

| Section | Content Required | Key Article |
|---------|-----------------|-------------|
| 1 | General description: intended purpose, version, provider | Art. 11 |
| 2 | Development elements: design logic, training data, testing methodology | Art. 10, 11 |
| 3 | Monitoring and control: record-keeping, human oversight, instructions | Art. 12-14 |
| 4 | Risk management system: full RMS documentation | Art. 9 |
| 5 | Lifecycle changes: post-market monitoring plan, change management | Art. 72 |
| 6 | Standards and specifications: harmonised standards applied | Art. 40-41 |
| 7 | EU Declaration of Conformity reference | Art. 47 |
## Article-43 Conformity Procedure

| Procedure | When | Process |
|-----------|------|---------|
| Internal conformity check (Annex VI) | All high-risk systems EXCEPT real-time remote biometric ID | Provider performs conformity check internally |
| Notified body assessment (Annex VII) | Real-time remote biometric identification (Annex III(1)(a)) | Third-party NB reviews technical documentation |
| Notified body (elective) | Any high-risk system if provider chooses | Provider may elect NB review for credibility |
## Industry Standards Mapping

| Standard | Version | Relevance to Conformity Assessment |
|----------|---------|-------------------------------------|
| EU AI Act 2024/1689 | 2024 | Primary regulation -- all requirements |
| ISO/IEC 42001 | 2023 | AI management system -- supports RMS implementation |
| ISO 31000 | 2018 | Risk management principles -- basis for Art. 9 RMS |
| NIST AI RMF | 1.0 (2023) | AI risk framework -- supplementary to EU RMS |
| ISO/IEC 27001 | 2022 | Information security -- supports Art. 15 cybersecurity |
| IEEE 2857-2024 | 2024 | Privacy engineering for ML -- supports data governance |
## Deadline Map

| Provision | Applicable Date | Who Is Affected |
|-----------|----------------|----------------|
| Prohibited AI systems ban | Feb 2025 | All providers |
| GPAI model obligations | Aug 2025 | GPAI providers |
| High-risk AI (Annex III) -- new systems | Aug 2026 | Providers placing new systems |
| High-risk AI (Annex III) -- existing systems | Aug 2026 [AUG-2026-DEADLINE] | Providers of already-deployed systems |
| High-risk AI (Annex I -- product safety) | Aug 2027 | Providers of AI embedded in regulated products |
| Full Act application | Aug 2026 | All actors |
