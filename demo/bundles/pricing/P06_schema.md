---
kind: schema
id: bld_schema_content_monetization
pillar: P06
llm_function: CONSTRAIN
purpose: "Schema formal -- UNICA FONTE DE VERDADE para a config content_monetization"
pattern: "CONFIG deriva disto. TEMPLATE renderiza isto."
quality: null
title: "Schema Content Monetization"
version: "1.0.0"
author: n03_builder
tags: [content_monetization, builder, examples]
tldr: "Exemplos de referencia e antiexemplos para a construcao de content_monetization, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construcao de content_monetization"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [schema formal, construcao de content_monetization, schema content monetization, content_monetization, builder, examples, schema da config, centavos cents, tier inteiro, signature_algo const]
density_score: 0.90
related:
  - bld_schema_usage_report
  - bld_schema_dataset_card
  - bld_schema_quickstart_guide
  - bld_schema_reranker_config
---

# Schema: content_monetization

## Schema da Config (o YAML que toda empresa preenche)

### identity (obrigatorio)
| Campo | Tipo | Obrigatorio | Exemplo |
|-------|------|----------|---------|
| empresa | string | SIM | "ACME" |
| domain | string | SIM | "ai_tools" |
| currency | enum(BRL,USD,EUR) | SIM | "BRL" |
| currency_unit | enum(centavos,cents) | SIM | "centavos" |
| country | enum(BR,US,EU,UK,LATAM) | SIM | "BR" |

### pricing (obrigatorio)
| Campo | Tipo | Obrigatorio | Padrao |
|-------|------|----------|---------|
| strategy | enum(freemium,tiered,usage,credit_pack,hybrid) | SIM | "tiered" |
| tiers | list[tier_object] | SIM | - |
| tier.name | string | SIM | "pro" |
| tier.price_monthly | integer (centavos/cents) | SIM | 4990 |
| tier.price_yearly | integer | NAO | 49900 |
| tier.credits_monthly | integer | SIM | 1000 |
| tier.features | list[string] | SIM | ["research", "publish"] |
| floor_margin_pct | float (0.0-1.0) | SIM | 0.30 |
| trial_days | integer | NAO | 7 |

### credits (obrigatorio)
| Campo | Tipo | Obrigatorio | Padrao |
|-------|------|----------|---------|
| pipeline_costs | map[string,int] | SIM | {research: 50} |
| packs | list[pack] | NAO | - |
| overdraft_policy | enum(block,notify_then_block,allow_negative) | SIM | "block" |
| rollover | boolean | NAO | false |

### checkout (obrigatorio)
| Campo | Tipo | Obrigatorio | Padrao |
|-------|------|----------|---------|
| provider | enum(stripe,hotmart,kiwify,monetizze,eduzz,digistore24) | SIM | "stripe" |
| webhook_url | string (URL) | SIM | - |
| webhook_secret_env | string (ENV_VAR) | SIM | "CHECKOUT_WEBHOOK_SECRET" |
| idempotency | boolean | SIM | true |
| success_redirect | string (URL) | SIM | - |
| cancel_redirect | string (URL) | SIM | - |
| mock_mode | boolean | NAO | true |

### checkout_ds24 (quando provider=digistore24)
| Campo | Tipo | Padrao |
|-------|------|---------|
| ds24_product_id | string | - |
| ds24_api_key_env | ENV_VAR | "DS24_API_KEY" |
| ipn_url | URL | - |
| ipn_passphrase_env | ENV_VAR | "DS24_IPN_PASSPHRASE" |
| ipn_format | const | "form-encoded" |
| ipn_response | const | "OK" |
| signature_algo | const | "sha512" |
| merchant_of_record | enum(ds24,self) | "ds24" |
| eu_vat_included | boolean | true |

### checkout_hotmart (quando provider=hotmart)
| Campo | Tipo | Padrao |
|-------|------|---------|
| hotmart_product_id | string | - |
| hotmart_token_env | ENV_VAR | "HOTMART_TOKEN" |
| hottok_env | ENV_VAR | "HOTMART_HOTTOK" |
| webhook_format | const | "json" |
| signature_algo | const | "sha256_hmac" |

### courses (opcional)
| Campo | Tipo | Obrigatorio | Padrao |
|-------|------|----------|---------|
| enabled | boolean | SIM | false |
| modules | list[module_object] | COND | - |
| module.title | string | SIM | - |
| module.lessons | list[lesson_object] | SIM | - |
| module.drip_days | integer | NAO | 0 |
| certification | boolean | NAO | false |
| completion_threshold | float (0.0-1.0) | NAO | 0.80 |

### ads (opcional)
| Campo | Tipo | Padrao |
|-------|------|---------|
| platforms | list[enum(meta,google,tiktok,linkedin)] | - |
| monthly_budget | int (centavos) | - |
| pixel_env | ENV_VAR | "META_PIXEL_ID" |

### emails (opcional)
| Campo | Tipo | Padrao |
|-------|------|---------|
| provider | enum(resend,sendgrid,ses,mailchimp) | "resend" |
| api_key_env | ENV_VAR | "EMAIL_API_KEY" |
| sequences | list[sequence] | - |

### validation (obrigatorio)
margin_check: true, webhook_test: true, mock_before_live: true

## Regras
1. Precos em centavos/cents (inteiros). 2. floor_margin >= 0.30.
3. Segredos: apenas ENV_VAR. 4. mock_mode: true em desenvolvimento. 5. Minimo de 1 tier.

## Related Artifacts
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| bld_schema_social_publisher | sibling | 0.54 |
| bld_schema_usage_report | sibling | 0.51 |
| [[bld_schema_dataset_card]] | sibling | 0.50 |
| bld_schema_quickstart_guide | sibling | 0.50 |
| bld_schema_reranker_config | sibling | 0.49 |
