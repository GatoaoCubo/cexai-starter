---
id: p11_config_revision_loop_policy
kind: env_config
pillar: P11
llm_function: CONSTRAIN
purpose: P09 config knobs for revision_loop_policy builder
quality: null
title: "Config: Revision Loop Policy Builder"
version: "1.0.0"
author: n03_builder
tags: [config, revision_loop_policy, builder, p11, governance]
domain: "revision_loop_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "P09 config knobs for revision_loop_policy builder"
8f: "F1_constrain"
keywords: [revision_loop_policy construction, revision loop policy builder, config, revision_loop_policy, builder, governance, rlp_max_iterations, rlp_quality_floor, rlp_escalation_target, user]
density_score: 0.87
related:
 - n00_revision_loop_policy_manifest
 - rlp_{{name}}
 - bld_memory_revision_loop_policy
 - p11_out_tpl_revision_loop_policy
 - bld_kc_revision_loop_policy
---
## Builder Configuration

### Runtime Defaults

| Config Key | Default | Description |
|------------|---------|-------------|
| `RLP_MAX_ITERATIONS` | `3` | Global default for max revision cycles |
| `RLP_QUALITY_FLOOR` | `8.5` | Score below which revision triggers |
| `RLP_ESCALATION_TARGET` | `user` | Default escalation route |
| `RLP_PRIORITY_ORDER` | `security,quality,implementation` | Default conflict resolution order |
| `RLP_SECURITY_OVERRIDE` | `5` | max_iterations for security_critical scenario |
| `RLP_DOCS_OVERRIDE` | `2` | max_iterations for documentation scenario |

### Environment Variables

```bash
# Override defaults for all new revision_loop_policy artifacts
export RLP_MAX_ITERATIONS=3
export RLP_QUALITY_FLOOR=8.5
export RLP_ESCALATION_TARGET=user

# Headless pipeline mode (no user to escalate to)
export RLP_ESCALATION_TARGET=freeze
```

### Per-Scenario Override Table

| Scenario Key | Default | Description |
|-------------|---------|-------------|
| `security_critical` | 5 | High-stakes security artifacts |
| `documentation` | 2 | Knowledge cards, guides, READMEs |
| `standard` | 3 | All other artifact kinds |
| `experimental` | 1 | Fast-iteration prototypes |

### Quality Thresholds (CEX standards)

| Threshold | Value | When |
|-----------|-------|------|
| Floor (trigger revision) | 8.5 | Below this, a revision cycle starts |
| Publish minimum | 8.0 | CEX system floor (quality_gate) |
| Target | 9.0 | N03 inventive pride target |
| Excellence | 9.5+ | For showcased artifacts |

### Builder Execution Config

```yaml
builder_config:
 kind: revision_loop_policy
 pillar: P11
 max_bytes: 2048
 naming: "p11_rlp_{{name}}.yaml"
 compile_target: yaml
 validate_on_produce: true
 hard_gate_count: 6
 soft_gate_count: 4
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[n00_revision_loop_policy_manifest]] | related | 0.33 |
| [[rlp_{{name}}]] | related | 0.32 |
| [[bld_memory_revision_loop_policy]] | upstream | 0.31 |
| [[p11_out_tpl_revision_loop_policy]] | upstream | 0.31 |
| [[bld_kc_revision_loop_policy]] | upstream | 0.30 |
