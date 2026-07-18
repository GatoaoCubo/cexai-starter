---
kind: config
id: bld_config_content_monetization
pillar: P09
llm_function: CONSTRAIN
purpose: "Convencoes de nomenclatura, caminhos de arquivo, limites de tamanho, restricoes operacionais"
pattern: "CONFIG restringe o SCHEMA, nunca o contradiz"
effort: high
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Content Monetization"
version: "1.0.0"
author: n03_builder
tags: [content_monetization, builder, examples]
tldr: "Exemplos de referencia e antiexemplos para a construcao de content_monetization, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construcao de content_monetization"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [convencoes de nomenclatura, caminhos de arquivo, limites de tamanho, restricoes operacionais, construcao de content_monetization, config content monetization, content_monetization, builder, examples, "content_monetization_config_{empresa}.yaml"]
density_score: 0.90
related:
  - bld_architecture_content_monetization
  - bld_config_research_pipeline
---
# Config: Regras de Producao de content_monetization

## Convencao de Nomenclatura
| Escopo | Convencao | Exemplo |
|-------|-----------|---------|
| Arquivo de config | `content_monetization_config_{empresa}.yaml` | `content_monetization_config_acme.yaml` |
| Template | `tpl_content_monetization.md` | P11_feedback/templates/ |
| Exemplos | `ex_content_monetization_{model}.md` | `ex_content_monetization_saas.md` |
| Instancia | `content_monetization_config.md` | _instances/{co}/N06_commercial/ |
| ID de frontmatter | `p04_cli_content_monetization_{slug}` | `p04_cli_content_monetization_acme` |

## Limites de Tamanho
| Artefato | Tamanho Maximo | Motivo |
|----------|---------|-----------|
| Config YAML | 4096 bytes | Config densa, editavel por humanos |
| Template | 4096 bytes | Limite de especificacao do builder |
| Exemplo | 4096 bytes | Limite de especificacao do builder |
| Instruction | 6144 bytes | Estendido para o pipeline de 9 passos |

## Restricoes de Precificacao
| Regra | Valor | Motivo |
|------|-------|-----------|
| Margem minima (piso) | 30% | Abaixo disso, os custos de pipeline de LLM corroem o lucro |
| Quantidade minima de tiers | 1 | Precisa de ao menos um tier gratuito ou pago |
| Quantidade maxima de tiers | 5 | Mais tiers = paralisia de decisao |
| Formato de preco | centavos/cents (inteiro) | Evita arredondamento em float (R$49,90 = 4990) |
| Trial maximo | 30 dias | Trials mais longos reduzem a conversao |
| Pacote de creditos minimo | 100 creditos | Pacotes menores tem overhead de transacao alto |

## Restricoes do Sistema de Creditos
| Regra | Valor | Motivo |
|------|-------|-----------|
| Custo minimo de pipeline | 1 credito | Operacoes de custo zero anulam o proposito do credito |
| Custo maximo de pipeline | 1000 creditos | Uma unica operacao nao pode esvaziar a conta |
| Padrao de saldo negativo (overdraft) | block | Saldos negativos geram disputas de cobranca |
| Padrao de rollover | false | Rollover complica o reconhecimento de receita |

## Restricoes de Checkout
| Regra | Hotmart (BR) | Digistore24 (INT) |
|------|-------------|-------------------|
| Autenticacao | Bearer OAuth2 (HOTMART_TOKEN) | Chave de API (DS24_API_KEY) via header |
| Formato do webhook | JSON | form-encoded (NAO JSON) |
| Assinatura | HMAC sha256 (HOTMART_HOTTOK) | sha512 (DS24_IPN_PASSPHRASE) |
| Resposta | HTTP 200 | string exata "OK" |
| Chave de idempotencia | transaction_id | order_id |
| MoR | vendedor | DS24 (VAT da UE automatico) |
| Padrao de mock | true | true |
| Tentativas maximas | 5, backoff exponencial | reenvia ate receber "OK" |

## Regras de Posicionamento de Arquivos
| Tipo de Artefato | Diretorio | Pillar |
|--------------|-----------|--------|
| Template | P11_feedback/templates/ | P04 |
| Exemplos | P11_feedback/examples/ | P04 |
| Compilado | P11_feedback/compiled/ | P04 |
| Ferramenta do nucleus | N06_commercial/P04_tools/ | P04 |
| KCs do nucleus | N06_commercial/P01_knowledge/ | P01 |
| Config da empresa | _instances/{co}/N06_commercial/ | instancia |

## Variaveis de Ambiente
| Variavel | Plataforma | Finalidade |
|----------|----------|---------|
| HOTMART_TOKEN | Hotmart | Bearer token OAuth2 |
| HOTMART_HOTTOK | Hotmart | Segredo HMAC sha256 do webhook |
| DS24_API_KEY | Digistore24 | Autenticacao de API (X-DS-API-KEY) |
| DS24_IPN_PASSPHRASE | Digistore24 | Verificacao sha512 do IPN |
| DS24_SANDBOX_MODE | Digistore24 | Alternador de sandbox |
| STRIPE_SECRET_KEY | Stripe | Chave de API de fallback global |

## Regras de Seguranca
1. Segredos: NUNCA em texto puro → apenas ENV_VAR. Rotacionar a cada 90 dias.
2. PCI: nunca armazenar numeros de cartao -- o provedor tokeniza.
3. Arquivos de config: NUNCA commitar chaves reais → padrao `.env.example`.
4. Modo mock: aplicado no CI/CD -- chaves reais sao bloqueadas em ambientes de teste.
5. Passphrase do IPN / hottok: nunca logar -- usados apenas para verificacao de assinatura.

## Related Artifacts
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_architecture_content_monetization]] | upstream | 0.36 |
| [[bld_prompt_content_monetization]] | upstream | 0.33 |
| bld_config_social_publisher | sibling | 0.32 |
| [[bld_config_research_pipeline]] | sibling | 0.29 |
| [[bld_knowledge_content_monetization]] | upstream | 0.28 |
