---
kind: tools
id: bld_tools_pipeline_template
pillar: P04
llm_function: CALL
purpose: Tools available for pipeline_template production
quality: null
title: "Tools Pipeline Template"
version: "1.0.0"
author: n03_builder
tags: [pipeline_template, builder, tools, scenario_indexed]
tldr: "Tools available for pipeline_template production"
domain: "pipeline_template construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F5_call"
keywords: [pipeline_template construction, tools pipeline template, pipeline_template, builder, tools, scenario_indexed, production tools, validation tools, external references]
density_score: 0.86
related:
 - bld_tools_data_contract
 - bld_tools_value_object
 - bld_tools_deployment_manifest
 - bld_tools_domain_vocabulary
 - bld_tools_domain_event
---

## Production Tools
| Tool | Purpose | When |
|-------------------|---------------------------------------------------|-------------------|
| cex_compile.py | Compile pipeline_template.yaml to.json | F8 COLLABORATE |
| cex_retriever.py | Find similar pipeline templates (reuse) | F3 INJECT |
| cex_query.py | Discover role_assignment refs for stage binding | F1 CONSTRAIN |
| cex_doctor.py | Validate schema + gate compliance | F7 GOVERN |
| cex_score.py | Peer-review scoring (HARD + SOFT) | F7 GOVERN |
| signal_writer.py | Signal N07 on completion | F8 COLLABORATE |

## Validation Tools
| Tool | Purpose | When |
|---------------------------|----------------------------------------------|------------|
| cex_doctor.py | Confirm scenario in canonical 7-value enum | Pre-commit |
| cex_builder_linter.py | Validate stage order + role names | F7 GOVERN |
| cex_doctor.py | Confirm reviewer + tester in mandatory gates | F7 GOVERN |
| cex_router_v2.py | Validate model_tier values per stage | F7 GOVERN |

## External References
- multi-agent multiagent catalog: github.com/multi-agent-pattern
- SWE-bench revision-loop evaluation methodology
- aider.chat task mode taxonomy (maps to scenario enum)
- Claude Code /build pipeline patterns

## Tool Integration Checklist

- Verify tool name follows snake_case convention
- Validate input/output schema matches interface contract
- Cross-reference with capability_registry for discoverability
- Test tool invocation in sandbox before production use

## Invocation Pattern

```yaml
# Tool invocation contract
name: tool_name
input_schema: validated
output_schema: validated
error_handling: defined
timeout: configured
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_data_contract]] | downstream | 0.45 |
| [[bld_tools_value_object]] | downstream | 0.43 |
| [[bld_tools_deployment_manifest]] | downstream | 0.42 |
| [[bld_tools_domain_vocabulary]] | upstream | 0.41 |
| [[bld_tools_domain_event]] | downstream | 0.41 |
