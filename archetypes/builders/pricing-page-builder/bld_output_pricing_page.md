---
kind: output_template
id: bld_output_template_pricing_page
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for pricing_page production
quality: null
title: "Output Template Pricing Page"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [pricing_page, builder, output_template]
tldr: "Template with vars for pricing_page production"
domain: "pricing_page construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [pricing_page construction, output template pricing page, pricing_page, builder, output_template, most popular, start free, get pro, contact sales, pricing tiers table]
density_score: 0.85
related:
  - n00_pricing_page_manifest
  - bld_instruction_subscription_tier
  - bld_instruction_pricing_page
  - bld_schema_pricing_page
  - kc_pricing_page
---
```yaml
---
id: p05_pp_{{name}}.md
kind: pricing_page
pillar: P05
quality: null
title: {{title}}
description: {{description}}
pricing_model: {{flat|tiered|freemium}}
currency: {{USD|EUR|BRL}}
tags: [pricing_page, {{product_name}}, {{tier_style}}]
tldr: "{{one_sentence_summary}}"
domain: pricing_page construction
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
author: {{author_name}}
---
```

<!-- GUIDANCE:
  - name: lowercase slug, e.g. "acme_saas" -> id becomes p05_pp_acme_saas.md
  - pricing_model: flat (single price), tiered (3+ tiers), freemium (free + paid)
  - currency: ISO 4217 code. Default USD for SaaS
  - Most Popular tier: mark with badge in table (see golden example)
  - CTA per tier: action-oriented verb ("Start Free", "Get Pro", "Contact Sales")
-->

<!-- Pricing Tiers Table -->
| Tier | Price (`{{currency}}`) | Features |
|------|----------------------|----------|
| Basic | `{{basic_price}}` | `{{basic_features}}` |
| Pro | `{{pro_price}}` | `{{pro_features}}` |
| Enterprise | `{{enterprise_price}}` | `{{enterprise_features}}` |

<!-- API Pricing Example -->
```json
{
  "endpoint": "/v1/pricing",
  "rate_limit": "{{rate_limit}}",
  "cost_per_call": "{{cost_per_call}}"
}
```

<!-- Additional Notes -->
`{{notes}}` <!-- Key terms, discounts, or usage policies -->

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[n00_pricing_page_manifest]] | related | 0.35 |
| [[bld_instruction_subscription_tier]] | upstream | 0.34 |
| [[bld_instruction_pricing_page]] | upstream | 0.33 |
| [[bld_schema_pricing_page]] | downstream | 0.33 |
| [[kc_pricing_page]] | upstream | 0.30 |
