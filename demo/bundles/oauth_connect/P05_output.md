---
kind: output_template
id: bld_output_template_oauth_app_config
pillar: P05
llm_function: PRODUCE
purpose: Template com variáveis para a produção de oauth_app_config
quality: null
title: "Output Template Oauth App Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags:
  - "oauth_app_config"
  - "builder"
  - "output_template"
tldr: "Template com variáveis para a produção de oauth_app_config"
domain: "construção de oauth_app_config"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords:
  - "oauth_app_config construction"
  - "oauth_app_config"
  - "builder"
  - "output_template"
  - "| filename following naming rules      |"
  - "| must match exact url registered      |"
  - "| space-separated permissions          |"
  - "user dashboard"
  - "related artifacts"
  - "callback scope"
density_score: 0.85
related:
  - bld_config_app_directory_entry
---
```yaml
---
id: p09_oauth_{{name}}.yaml
name: {{app_name}} <!-- Nome legível do app OAuth -->
description: {{app_description}} <!-- Propósito resumido do app -->
client_id: {{client_id}} <!-- Emitido pela CEX durante o registro -->
client_secret: {{client_secret}} <!-- Segredo confidencial para autenticação de API -->
redirect_uri: {{redirect_uri}} <!-- URL de callback pós-autenticação -->
scope: {{scope}} <!-- Permissões solicitadas (ex.: "read write") -->
quality: null
```

| Campo           | Descrição                             | Exemplo                          |
|-----------------|--------------------------------------|-----------------------------------|
| `id`            | Nome do arquivo seguindo as regras de nomenclatura | `p09_oauth_user_dashboard.yaml`  |
| `redirect_uri`  | Deve corresponder exatamente à URL registrada     | `https://app.example.com/callback` |
| `scope`         | Permissões separadas por espaço                    | `read_balance trade_orders`      |

```bash
# Exemplo de comando CLI para registrar o app
cex-cli oauth register \
  --name "User Dashboard" \
  --redirect-uri "https://app.example.com/callback" \
  --scope "read_balance trade_orders"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_app_directory_entry | upstream | 0.36 |
| ex-oauth-app-config-shopify | upstream | 0.35 |
| bld_collaboration_app_directory_entry | downstream | 0.34 |
| bld_collaboration_marketplace_app_manifest | downstream | 0.34 |
| bld_config_app_directory_entry | downstream | 0.31 |
