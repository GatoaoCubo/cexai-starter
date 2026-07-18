---
kind: output_template
id: bld_output_template_content_monetization
pillar: P05
llm_function: PRODUCE
purpose: "Template com {{vars}} para producao de config de monetizacao de conteudo"
pattern: "deriva do SCHEMA -- sem campos extras"
quality: null
title: "Output Template Content Monetization"
version: "1.0.0"
author: n03_builder
tags:
  - "content_monetization"
  - "builder"
  - "examples"
tldr: "Exemplos de referencia e antiexemplos para a construcao de content_monetization, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construcao de content_monetization"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords:
  - "template com"
  - "construcao de content_monetization"
  - "output template content monetization"
  - "content_monetization"
  - "builder"
  - "examples"
  - "## template de arquivo de artefato"
  - "output template"
  - "template de arquivo de config"
  - "config de monetizacao de conteudo"
density_score: 0.90
related:
  - bld_schema_content_monetization
  - content-monetization-builder
---
# Output Template: content_monetization

## Template de Arquivo de Config
```yaml
# Config de Monetizacao de Conteudo -- {{empresa}}
# Gerado por content-monetization-builder v1.0.0

identity:
  empresa: "{{empresa}}"
  domain: "{{domain}}"
  currency: "{{currency}}"           # BRL, USD, EUR
  currency_unit: "{{currency_unit}}" # centavos, cents
  country: "{{country}}"             # BR, US, EU

pricing:
  strategy: "{{strategy}}"           # freemium, tiered, usage, credit_pack, hybrid
  floor_margin_pct: {{floor_margin}}  # >= 0.30
  trial_days: {{trial_days}}          # 0 = sem trial
  tiers:
    {{#each tiers}}
    - name: "{{this.name}}"
      price_monthly: {{this.price_monthly}}     # centavos
      price_yearly: {{this.price_yearly}}       # centavos (opcional)
      credits_monthly: {{this.credits_monthly}}
      features: [{{this.features}}]
    {{/each}}

credits:
  unit_name: "{{credit_unit_name}}"
  pipeline_costs:
    {{#each pipeline_costs}}
    {{@key}}: {{this}}
    {{/each}}
  packs:
    {{#each packs}}
    - name: "{{this.name}}"
      credits: {{this.credits}}
      price: {{this.price}}           # centavos
    {{/each}}
  overdraft_policy: "{{overdraft_policy}}" # block, notify_then_block, allow_negative
  rollover: {{rollover}}

checkout:
  provider: "{{checkout_provider}}"   # stripe, hotmart, kiwify, monetizze, eduzz
  webhook_url: "{{webhook_url}}"
  webhook_secret_env: "{{WEBHOOK_SECRET_ENV}}"
  idempotency: true
  success_redirect: "{{success_url}}"
  cancel_redirect: "{{cancel_url}}"
  mock_mode: true                     # SEMPRE true ate validar

courses:
  enabled: {{courses_enabled}}
  {{#if courses_enabled}}
  modules:
    {{#each modules}}
    - title: "{{this.title}}"
      lessons:
        {{#each this.lessons}}
        - { title: "{{this.title}}", type: "{{this.type}}", duration_min: {{this.duration}} }
        {{/each}}
      drip_days: {{this.drip_days}}
    {{/each}}
  certification: {{certification}}
  completion_threshold: {{completion_threshold}}
  {{/if}}

ads:
  enabled: {{ads_enabled}}
  {{#if ads_enabled}}
  platforms: [{{ad_platforms}}]
  monthly_budget: {{ad_budget}}       # centavos
  target_cpa: {{target_cpa}}          # centavos
  pixel_env: "{{PIXEL_ENV}}"
  {{/if}}

emails:
  provider: "{{email_provider}}"      # resend, sendgrid, ses, mailchimp
  api_key_env: "{{EMAIL_API_KEY_ENV}}"
  sequences:
    {{#each sequences}}
    - name: "{{this.name}}"
      trigger: "{{this.trigger}}"
      emails:
        {{#each this.emails}}
        - { delay_hours: {{this.delay}}, template: "{{this.template}}" }
        {{/each}}
    {{/each}}

validation:
  margin_check: true
  webhook_test: true
  mock_before_live: true
```

## Template de Arquivo de Artefato
```markdown
---
id: {{artifact_id}}
kind: cli_tool
pillar: P11
title: "{{title}}"
version: "1.0.0"
created: "{{date}}"
author: "content-monetization-builder"
domain: content_monetization
quality: null
tags: [content-monetization, pricing, {{domain}}]
---
# {{title}}
## Pipeline (9 estagios)
## Estrategia de Precificacao
## Sistema de Creditos
## Integracao de Checkout
## Gates de Qualidade
```

## Related Artifacts
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_schema_content_monetization]] | downstream | 0.32 |
| [[bld_prompt_content_monetization]] | upstream | 0.29 |
| [[content-monetization-builder]] | downstream | 0.29 |
