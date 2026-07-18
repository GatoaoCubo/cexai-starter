---
kind: output_template
id: bld_output_template_subscription_tier
pillar: P05
llm_function: PRODUCE
purpose: "Template com variáveis para a produção de subscription_tier"
quality: null
title: "Output Template Subscription Tier"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [subscription_tier, builder, output_template]
tldr: "Template com variáveis para a produção de subscription_tier"
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [construção de subscription_tier, output template subscription tier, subscription_tier, builder, output_template, nome do tier, nível do tier, related artifacts, funcionalidades e preço]
density_score: 0.85
related:
  - kc_subscription_tier
---
```yaml
---
id: p11_st_{{name}}.yaml
name: {{subscription_tier_name}}
description: {{tier_description}}
features:
  - {{feature_1}}
  - {{feature_2}}
pricing: {{price}}
tier_level: {{level}}
quality: null
---
```

<!-- id: nome de arquivo gerado seguindo o padrao p11_st_[a-z][a-z0-9_]+.yaml -->
<!-- name: nome do tier legivel por humanos (ex.: "Premium") -->
<!-- description: explicacao breve dos beneficios do tier -->
<!-- features: array de 2-5 bullets descrevendo as funcionalidades incluidas -->
<!-- pricing: valor numerico ou "Free" -->
<!-- tier_level: valor numerico (1=mais baixo, 5=mais alto) -->
<!-- quality: sempre null -->

| Nome do Tier | Funcionalidades | Preço | Nível do Tier |
|-------------|---------------------------|----------|------------|
| Basic       | 10 chamadas de API/dia    | $9.99    | 1          |
| Pro         | 100 chamadas de API/dia, suporte | $49.99   | 3          |
| Enterprise  | Ilimitado, equipe dedicada | Custom   | 5          |

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_subscription_tier]] | upstream | 0.33 |
| [[kc_subscription_tier]] | upstream | 0.30 |
| n00_pricing_page_manifest | related | 0.28 |
| bld_instruction_pricing_page | upstream | 0.27 |
