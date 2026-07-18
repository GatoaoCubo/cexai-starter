---
kind: tools
id: bld_tools_content_monetization
pillar: P11
llm_function: CALL
purpose: "Ferramentas, APIs e fontes de dados para o pipeline de monetizacao de conteudo"
quality: null
title: "Tools Content Monetization"
version: "1.0.0"
author: n03_builder
tags: [content_monetization, builder, examples]
tldr: "Exemplos de referencia e antiexemplos para a construcao de content_monetization, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construcao de content_monetization"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F7_govern"
keywords: [construcao de content_monetization, tools content monetization, content_monetization, builder, examples, provedores de pagamento, hotmart club, outros provedores, provedores de e-mail, react email]
density_score: 0.90
related:
  - bld_architecture_content_monetization
---
# Ferramentas: content-monetization-builder

## Provedores de Pagamento

### Plataforma A -- Hotmart (BR)
| Aspecto | Detalhe |
|--------|--------|
| Base da API | https://developers.hotmart.com/docs/en/ |
| Autenticacao | Bearer token OAuth2 (client_credentials) → HOTMART_TOKEN |
| Endpoints | /payments/api/v1/sales, /club/api/v1/modules, /affiliation |
| Webhook | JSON, HMAC sha256 via header X-Hotmart-Hottok |
| Eventos | PURCHASE_COMPLETE, PURCHASE_CANCELED, PURCHASE_REFUNDED, PURCHASE_CHARGEBACK, SUBSCRIPTION_CANCELLATION, SWITCH_PLAN |
| Sandbox | hotmart.com/developer (ambiente de teste) |
| Custo | varia por categoria de produto |
| Mercado | Infoprodutos BR/LATAM, 500 mil+ afiliados |
| Area de membros | Hotmart Club (entrega de curso nativa) |

### Plataforma B -- Digistore24 (Internacional)
| Aspecto | Detalhe |
|--------|--------|
| Base da API | https://www.digistore24.com/api/v1/ |
| Autenticacao | Chave de API via header X-DS-API-KEY → DS24_API_KEY |
| Endpoints | /products, /purchases, /affiliates, /transactions |
| IPN | form-encoded (NAO JSON), assinatura sha512 (DS24_IPN_PASSPHRASE) |
| Resposta do IPN | o corpo precisa ser a string exata "OK" (nao JSON, nao HTML) |
| Eventos | on_payment, on_refund, on_chargeback, on_rebill_resumed, on_rebill_cancelled, on_affiliatelink, on_invoice_created, on_payment_missed |
| Sandbox | modo de produto de teste da DS24 |
| Custo | variavel, DS24 e Merchant of Record |
| Mercado | Dominante em UE/DACH, EUR, VAT da UE automatico |
| Idiomas | 7 nativos: DE, EN, ES, FR, IT, NL, PL |
| Metodos de pagamento | SEPA+Sofort (DE), iDEAL (NL), cartoes+PayPal (global) |
| Area de membros | Area de membros da DS24 ou redirect externo |

### Outros Provedores
| Provedor | Autenticacao | Mercado |
|----------|------|--------|
| Stripe | STRIPE_SECRET_KEY | Global |
| Kiwify | KIWIFY_API_KEY | BR |
| Monetizze | MONETIZZE_TOKEN | BR |
| Eduzz | EDUZZ_API_KEY | BR |

## Provedores de E-mail
| Provedor | API | Autenticacao | Custo | Especialidade |
|----------|-----|------|------|-----------|
| Resend | REST | RESEND_API_KEY | Gratis ate 3 mil/mes, $20/50 mil | Dev-friendly, React Email |
| SendGrid | REST | SENDGRID_API_KEY | Gratis 100/dia, $19.95/50 mil | Escala, templates |
| AWS SES | REST/SMTP | AWS_ACCESS_KEY_ID | $0.10/1000 e-mails | Custo-beneficio em escala |
| Mailchimp | REST | MAILCHIMP_API_KEY | Gratis ate 500 contatos | No-code, automacoes |

## Plataformas de Anuncios
| Plataforma | API | Autenticacao | Orcamento Minimo | Melhor Para |
|----------|-----|------|-----------|----------|
| Meta Ads | Marketing API | META_ACCESS_TOKEN | R$20/dia | Conscientizacao B2C, retargeting |
| Google Ads | REST | GOOGLE_ADS_TOKEN | R$10/dia | Captura de intencao, busca |
| TikTok Ads | Marketing API | TIKTOK_ACCESS_TOKEN | R$50/dia | Gen-Z, conteudo viral |
| LinkedIn Ads | Marketing API | LINKEDIN_TOKEN | $10/dia | B2B, publico profissional |

## Plataformas de Curso
Hotmart Club (nativa), Teachable, Thinkific, area de membros da DS24, LMS proprio.

## Ferramentas de Producao do CEX
| Ferramenta | Finalidade | Quando |
|------|---------|------|
| cex_compile.py | Compilacao .md → .yaml | Apos salvar |
| cex_hooks.py | Validacao pre/pos | Antes do commit |
| cex_doctor.py | Checagem de saude do builder | Apos o build |
| cex_score.py | Pontuacao de qualidade 5D | Peer review |
| signal_writer.py | Sinais entre nucleos | Apos concluir |

## Fontes de Dados
| Fonte | Caminho | Dado |
|--------|------|------|
| Schema | P06/_schema.yaml | Definicoes de campo |
| Kind KC | P01_knowledge/library/kind/ | Conhecimento de dominio |
| Exemplos | P11_feedback/examples/ | Configs de referencia |
| SEED_BANK | archetypes/SEED_BANK.yaml | Seeds de builder |

## Permissoes de Ferramentas

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDO | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| NEGADO | (nenhuma) | Explicitamente bloqueado |
| EFETIVO | Bash, Edit, Glob, Grep, Read, Write | PERMITIDO menos NEGADO |

## Related Artifacts
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_prompt_content_monetization]] | upstream | 0.39 |
| [[bld_knowledge_content_monetization]] | upstream | 0.36 |
| [[bld_architecture_content_monetization]] | upstream | 0.35 |
| p01_kc_content_platform_comparison | upstream | 0.34 |
| [[bld_orchestration_content_monetization]] | downstream | 0.32 |
