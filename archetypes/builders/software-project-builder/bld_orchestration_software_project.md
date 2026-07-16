---
id: bld_sp_collaboration_software_project
kind: collaboration
pillar: P11
title: "Collaboration — Software Project Builder"
version: 1.0.0
created: 2026-03-31
updated: 2026-03-31
author: n03_engineering
domain: software-engineering
quality: null
tags: [builder, collaboration, software-project, cross-nucleus]
tldr: "Cross-nucleus collaboration: N03 receives specs from N01/N02/N04 and produces executable code. N03→N05 for deploy ops. N03→N07 for CEX tool maintenance."
8f: "F7_govern"
keywords: [software project builder, cross-nucleus collaboration, receives specs from n, and produces executable code, for deploy ops, for cex tool maintenance, builder, collaboration, software-project, cross-nucleus]
density_score: 0.88
llm_function: COLLABORATE
related:
  - p12_dr_software_project
  - p01_kc_n03_software_engineering
  - bld_collaboration_supabase_data_layer
  - bld_collaboration_social_publisher
---
# Collaboration

This ISO describes a software project: its repository layout, modules, and build graph.

## N03 Receives From (Inputs)

| Source | What | Example |
|--------|------|---------|
| N01 (Intelligence) | Pipeline spec + config | "implement research pipeline in Python" |
| N02 (Marketing) | Publisher spec + config | "implement social publisher runtime" |
| N04 (Knowledge) | Schema + migrations | "deploy Supabase migrations" |
| N06 (Commercial) | Integration spec | "build Stripe billing connector" |
| N07 (Admin) | CEX tool requirements | "add --batch flag to 8F runner" |

## N03 Sends To (Outputs)

| Target | What | Example |
|--------|------|---------|
| N05 (Operations) | Deploy artifacts | Dockerfile, CI/CD, monitoring config |
| N04 (Knowledge) | Migration files | SQL migrations for new features |
| N07 (Admin) | Updated tools | New/improved _tools/cex_*.py |
| All nuclei | Executable projects | src/ + tests/ + Dockerfile |

## Handoff Protocol

```yaml
# .cex/runtime/handoffs/n03_task.md
task: implement research pipeline
source_nucleus: N01
builder_spec: archetypes/builders/research-pipeline-builder/
instance_config: _instances/codexa/N01_intelligence/research_pipeline_config.md
output_type: pipeline_runner
expected_files:
  - src/research_pipeline/pipeline.py
  - src/research_pipeline/stages/
  - tests/test_pipeline.py
  - Dockerfile
  - .github/workflows/ci.yml
```

## Collaboration Matrix

```
N01 ──spec──→ N03 ──code──→ N05 (deploy)
N02 ──spec──→ N03 ──code──→ N05 (deploy)
N04 ──schema─→ N03 ──migration→ N04 (execute)
N06 ──spec──→ N03 ──code──→ N05 (deploy)
N07 ──req───→ N03 ──tool──→ N07 (integrate)
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_dr_software_project]] | downstream | 0.49 |
| [[p01_kc_n03_software_engineering]] | upstream | 0.35 |
| [[bld_collaboration_supabase_data_layer]] | sibling | 0.34 |
| [[bld_collaboration_social_publisher]] | sibling | 0.31 |
