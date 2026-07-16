---
kind: output_template
id: bld_output_template_user_journey
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for user_journey production
quality: null
title: "Output Template User Journey"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [user_journey, builder, output_template]
tldr: "Template with vars for user_journey production"
domain: "user_journey construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [user_journey construction, output template user journey, user_journey, builder, output_template, user onboarding, user action, system response, success metric, related artifacts]
density_score: 0.85
related:
  - bld_collaboration_user_journey
  - bld_instruction_user_journey
  - bld_config_user_journey
  - n00_user_journey_manifest
  - p10_mem_user_journey_builder
---
```yaml
---
id: p05_uj_{{name}}.md
title: {{title}} <!-- User journey title, e.g., "User Onboarding" -->
description: {{description}} <!-- Summary of the journey's purpose -->
owner: {{owner}} <!-- Team/individual responsible -->
status: {{status}} <!-- "draft", "review", "approved" -->
quality: null
---
```

| Step | User Action | System Response | Success Metric |
|------|-------------|------------------|----------------|
| 1    | `{{action_1}}` <!-- e.g., "Create account" --> | `{{response_1}}` <!-- e.g., "Send confirmation email" --> | `{{metric_1}}` <!-- e.g., "90% completion rate" --> |
| 2    | `{{action_2}}` <!-- e.g., "Verify email" --> | `{{response_2}}` <!-- e.g., "Display dashboard" --> | `{{metric_2}}` <!-- e.g., "85% conversion rate" --> |

```json
{
  "journey": "{{name}}",
  "steps": [
    {
      "id": "step_1",
      "user_action": "{{action_1}}",
      "system_response": "{{response_1}}"
    }
  ]
}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_user_journey]] | downstream | 0.31 |
| [[bld_instruction_user_journey]] | upstream | 0.31 |
| [[bld_config_user_journey]] | downstream | 0.29 |
| [[n00_user_journey_manifest]] | related | 0.28 |
| [[p10_mem_user_journey_builder]] | downstream | 0.26 |
