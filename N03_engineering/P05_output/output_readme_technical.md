---
id: n03_readme_technical
kind: output_template
8f: F6_produce
pillar: P05
title: "CEX Public README — Architecture & Quickstart"
version: 1.0.0
created: 2026-04-02
author: n03_builder
domain: engineering
quality: null
tags: [readme, architecture, quickstart, public, onboarding]
tldr: "Architecture diagram, 5-step quickstart, and directory map for the CEX public README."
keywords: [iso, 8f pipeline, artifact, builder archetype, nuclei, pillars, quality gates, schema, instruction, manifest]
density_score: 0.91
related:
  - p07_gt_n03
  - p01_kc_cex_tooling_master
  - p12_wf_builder_8f_pipeline
  - bld_schema_output_template
---

# Architecture & Quickstart

## Architecture

```
                         ┌──────────────┐
                         │  Human Goal  │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │ N07 Orchestr │  /plan → /guide → /spec → /grid
                         └──────┬───────┘
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                  ▼
   ┌──────────────┐  ┌──────────────┐   ┌──────────────┐
   │ N01 Intel    │  │ N03 Builder  │   │ N02 Market   │
   │ N04 Knowledge│  │ N05 Ops      │   │ N06 Commerce │
   └──────┬───────┘  └──────┬───────┘   └──────┬───────┘
          │                 │                   │
          ▼                 ▼                   ▼
   ┌────────────────────────────────────────────────┐
   │              8F Pipeline (per artifact)         │
   │  F1 Constrain → F2 Become → F3 Inject →       │
   │  F4 Reason   → F5 Call   → F6 Produce →       │
   │  F7 Govern   → F8 Collaborate                  │
   └──────────────────────┬─────────────────────────┘
                          ▼
   ┌────────────────────────────────────────────────┐
   │            12 Pillars (artifact storage)        │
   │  P01 Knowledge  P02 Model    P03 Prompt        │
   │  P04 Tools      P05 Output   P06 Schema        │
   │  P07 Evals      P08 Arch     P09 Config        │
   │  P10 Memory     P11 Feedback P12 Orchestration │
   └────────────────────────────────────────────────┘
```

**{{KIND_COUNT}} artifact kinds** · **{{BUILDER_COUNT}} builder archetypes** · **8 nuclei** · **12 pillars**

Each builder loads 12 ISOs (one per pillar: knowledge, model, prompt, tools, output, schema,
eval, architecture, config, memory, feedback, orchestration) and produces validated artifacts
through the 8F pipeline with quality-gate enforcement.

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/your-org/cex.git && cd cex

# 2. Install
pip install -r requirements.txt

# 3. Bootstrap your brand identity (~2 min)
claude                          # opens Claude Code
> /init                         # answers 6 questions → brand_config.yaml

# 4. Build your first artifact
> /build knowledge card about React patterns

# 5. Run a full mission (parallel nuclei)
> /mission build landing page for my SaaS
```

---

## Directory Structure

```
cex/
├── archetypes/builders/    # {{BUILDER_COUNT}} builder archetypes (12 ISOs each, 1:1 with pillars)
├── P01-P12_*/              # 12 pillars — artifact storage by domain
├── N00_genesis/            # Template nucleus (fractal mold)
├── N01-N07_*/              # 7 nuclei — each mirrors 12 pillars
├── _tools/                 # Python tools (pipeline, quality, indexing)
├── _spawn/                 # Dispatch scripts (solo/grid)
├── .cex/                   # Runtime state, signals, handoffs
├── boot/                   # Nucleus boot scripts (n01-n07)
├── cex_sdk/                # Python SDK
└── CLAUDE.md               # System entry point
```

| Layer | Count | Purpose |
|-------|-------|---------|
| Kinds | {{KIND_COUNT}} | Typed artifact categories |
| Builders | {{BUILDER_COUNT}} | Specialized artifact factories |
| Pillars | 12 | Domain-organized storage |
| Nuclei | 8 | Autonomous agent clusters |
| Tools | {{TOOL_COUNT}} | Pipeline, quality, indexing |
| Quality gates | {{GATE_COUNT}} | Hard + soft validation |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p07_gt_n03]] | related | 0.30 |
| [[p01_kc_cex_tooling_master]] | upstream | 0.28 |
| [[p12_wf_builder_8f_pipeline]] | upstream | 0.26 |
| [[bld_schema_output_template]] | related | 0.21 |
