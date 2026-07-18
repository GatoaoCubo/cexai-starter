---
kind: quality_gate
id: p11_qg_content_monetization
pillar: P11
llm_function: GOVERN
purpose: "Exemplos de referencia (golden) e antiexemplos de configs de monetizacao de conteudo"
pattern: "few-shot learning -- o LLM le estes antes de produzir"
quality: null
title: "Gate: content_monetization"
version: 1.0.0
author: n03_engineering
tags: [quality-gate, content-monetization, P11, pricing, billing, credits, governance]
tldr: "Gates para artefatos de monetizacao -- aplicacao de margem, idempotencia de webhook, rastreio de creditos, desenvolvimento mock-first, seguranca de checkout."
domain: content_monetization
created: 2026-03-31
updated: 2026-03-31
8f: "F7_govern"
keywords: [gates para artefatos de monetizacao, aplicacao de margem, idempotencia de webhook, rastreio de creditos, desenvolvimento mock-first, seguranca de checkout, quality-gate]
density_score: 1.0
related:
  - content-monetization-builder
  - bld_schema_content_monetization
---
## Gate de Qualidade

# Gate: content_monetization

## Definicao
| Campo | Valor |
|-------|-------|
| Kind | content_monetization (instancias de cli_tool/workflow) |
| Pillar | P04 (tools) |
| Funcao | CALL (automacao de monetizacao) |
| Limiar | minimo de 8.0 |

## Gates HARD (falha = rejeitar)
| # | Gate | Verificacao |
|---|------|------|
| H1 | 9 estagios completos | Todos os 9 estagios documentados (de PARSE ate DEPLOY) |
| H2 | Aplicacao de margem | floor_margin_pct >= 0.30 e definido explicitamente |
| H3 | Precificacao em inteiros | Todos os precos em centavos/cents, sem float |
| H4 | Zero segredos | Nenhuma chave de API/segredo de webhook em texto puro -- apenas ENV_VAR |
| H5 | Webhook idempotente | idempotency: true e mecanismo de deduplicacao descrito |
| H6 | Modo mock padrao | mock_mode: true em todas as configs fora de producao |

## Gates SOFT (aviso, nao rejeita)
| # | Gate | Verificacao | Peso |
|---|------|------|--------|
| S1 | Multi-tier | Pelo menos 2 tiers de precificacao definidos | 0.8 |
| S2 | Pacotes de creditos | Pacotes pay-as-you-go disponiveis para nao assinantes | 0.7 |
| S3 | E-mails comportamentais | Sequencias de e-mail usam gatilhos comportamentais, nao so tempo | 0.8 |
| S4 | Desconto anual | Precificacao anual com desconto disponivel | 0.5 |
| S5 | Provedor de fallback | Provedor de checkout alternativo documentado | 0.6 |
| S6 | Estrutura de curso | Se cursos habilitados: modulos + aulas + drip definidos | 0.7 |

## Gate de Validacao de Margem (por tier, no momento da config)
| Tipo de Tier | Margem Minima | Motivo |
|-----------|-----------|-----------|
| Free | N/A | Sem receita, mas precisa limitar o uso de creditos |
| Starter/Basic | 30% | Minimo viavel apos os custos de pipeline |
| Pro/Growth | 40% | Deve financiar a escala |
| Enterprise | 50% | Custos de suporte customizado absorvem margem |
| Credit Pack | 35% | Cada unidade precisa cobrir a operacao + overhead |

## Formula de Pontuacao
```
score = (HARD_pass / 8) * 6.0 + (SOFT_weighted / max_weight) * 4.0
```

## Niveis de Qualidade
| Nivel | Pontuacao | Significado |
|------|-------|---------|
| REJECT | < 8.0 | Estagios faltando, sem checagem de margem, ou violacao de seguranca |
| PUBLISH | 8.0-8.9 | Pipeline completo, margens aplicadas, webhooks idempotentes |
| EXEMPLARY | 9.0+ | Funil completo (anuncios→checkout→curso→e-mail), multi-provedor, gatilhos comportamentais |

## Bypass
| Campo | Valor |
|-------|-------|
| conditions | Fluxo de receita critico exigindo lancamento imediato |
| approver | n06-chief |
| audit_trail | Registrar em records/audits/ com justificativa e timestamp |
| expiry | 48h -- precisa passar no gate completo antes de expirar |
| never_bypass | H3 (precificacao em inteiros), H4 (zero segredos), H5 (idempotencia de webhook) |

## Acoes
| Pontuacao | Nivel | Acao |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publicar como exemplar |
| >= 8.0 | PUBLISH | Pronto para producao |
| >= 7.0 | REVIEW | Sinalizar para revisao |
| < 7.0  | REJECT | Retrabalho necessario |

## Exemplos

# Exemplos: content-monetization-builder

## Golden -- SaaS (Stripe, BR)
ENTRADA: "Config de monetizacao para plataforma de pesquisa com IA, BR"
```yaml
identity: { empresa: "ACME", domain: ai_tools, currency: BRL, currency_unit: centavos, country: BR }
pricing:
  strategy: hybrid
  floor_margin_pct: 0.35
  tiers:
    - { name: free, price_monthly: 0, credits_monthly: 50, features: [basic_search] }
    - { name: pro, price_monthly: 9990, credits_monthly: 1000, features: [research, publish] }
credits: { pipeline_costs: { research: 50, publish: 10 }, overdraft_policy: notify_then_block }
checkout: { provider: stripe, webhook_secret_env: STRIPE_WEBHOOK_SECRET, idempotency: true, mock_mode: true }
validation: { margin_check: true, webhook_test: true, mock_before_live: true }
```
POR QUE E BOM: Precificacao hibrida, centavos, segredos via ENV_VAR, idempotente, mock ligado.

## Golden -- Curso (Hotmart, BR)
ENTRADA: "Curso de cuidados com pets, Hotmart, BR"
```yaml
identity: { empresa: "PetVida", domain: pet_education, currency: BRL, currency_unit: centavos, country: BR }
pricing: { strategy: tiered, floor_margin_pct: 0.70, tiers: [{ name: basico, price_monthly: 4990 }, { name: complete, price_monthly: 9990 }] }
checkout: { provider: hotmart, webhook_secret_env: HOTMART_HOTTOK, signature: sha256_hmac, format: json, idempotency: true, mock_mode: true }
courses: { enabled: true, modules: [{ title: "Nutrição", drip_days: 0 }, { title: "Saúde", drip_days: 7 }], certification: true }
validation: { margin_check: true, webhook_test: true, mock_before_live: true }
```
POR QUE E BOM: Foco em curso, webhook Hotmart (JSON/sha256), drip, margens de 70%.

### S_RELATED: Checagem de Cross-Reference (SOFT)
- [ ] Campo de frontmatter `related:` preenchido (3-15 entradas)
- [ ] Secao `## Related Artifacts` presente no corpo do artefato
- [ ] Pelo menos 1 referencia upstream e 1 downstream
- Penalidade: -0.3 se vazio (nao bloqueia, incentiva a conexao)
