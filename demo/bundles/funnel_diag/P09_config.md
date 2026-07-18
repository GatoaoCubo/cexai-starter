---
kind: config
id: bld_config_funnel_diag
pillar: P09
llm_function: CONSTRAIN
purpose: Nomenclatura, caminhos, limites de tamanho e restrições operacionais do funnel_diag
pattern: CONFIG restringe o SCHEMA, nunca o contradiz
effort: medium
max_turns: 20
disallowed_tools: []
fork_context: fork
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, config]
tldr: "Nomenclatura p11_tc_funnel_diag_{{slug}}.md, limite de 5120 bytes de corpo, e as exceções de borda mais comuns (dado parcial, estágio ausente)."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F1_constrain"
keywords: [convenção de nomenclatura, limites de tamanho, casos de borda, funnel_diag]
density_score: 0.88
related:
  - bld_schema_funnel_diag
---
# Config: Regras de Produção do funnel_diag

## Convenção de Nomenclatura
| Escopo | Convenção | Exemplo |
|---|---|---|
| Arquivo de artefato | `p11_tc_funnel_diag_{{slug}}.md` | `p11_tc_funnel_diag_saas_b2b_acme.md` |
| Diretório do builder | kebab-case | `funnel-diagnostic-builder/` |
| Campos de frontmatter | snake_case | `biggest_leak`, `prioritization_method` |
| Slug do diagnóstico | minúsculo, underscores | `saas_b2b_acme`, `ecommerce_loja_x` |

Regra: id deve ser igual ao nome do arquivo sem extensão (gate H02).

## Caminhos
- Saída: `N06_commercial/P11_feedback/tool_cards/p11_tc_funnel_diag_{{slug}}.md`
- Compilado: `N06_commercial/P11_feedback/compiled/p11_tc_funnel_diag_{{slug}}.yaml`

## Limites de Tamanho
- Corpo: 400-5120 bytes
- Total (frontmatter + corpo): até ~6500 bytes
- Título: 5-100 caracteres
- tldr: <=160 caracteres, deve conter o vazamento principal

## Requisitos do Corpo
- Exatamente 5 seções fixas (Mapa do Funil, Métricas por Estágio, Análise de Vazamento, Fixes Priorizados, Suposições)
- Pelo menos 1 tabela por seção (exceto Suposições, que é lista)
- Os 5 estágios do framework aparecem nas seções 1 e 2, mesmo que como lacuna

## Restrições Específicas do Domínio
| Restrição | Valor |
|---|---|
| Limite | Diagnóstico + priorização (nunca execução da correção) |
| Dependências | Dados do usuário (analytics/CRM); nenhuma chamada live |
| Função 8F primária | F6_produce |
| Tamanho máximo do artefato | 5120 bytes (corpo) |

## Casos de Borda
| Cenário | Tratamento |
|---|---|
| Usuário fornece dado de só 2-3 estágios | Diagnóstico parcial rotulado; os demais estágios entram como `[A CONFIRMAR]`, nunca são omitidos |
| Nenhum benchmark disponível para o setor | Usa o benchmark mais próximo disponível, rotulado `estimado`, nunca apresentado como medido |
| Números contraditórios entre fontes | Sinaliza a contradição explicitamente; não escolhe uma fonte silenciosamente |
| Usuário pede só "o pior estágio", sem ranking de fixes | Ainda assim aplica ICE/RICE internamente para justificar qual é "o pior" -- resposta curta, método continua explícito |

## Propriedades
| Propriedade | Valor |
|---|---|
| Kind | `config` |
| Pilar | P09 |
| Domínio | diagnóstico de funil (funnel_diag) |
| Pipeline | 8F (F1-F8) |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_funnel_diag]] | sibling | 0.44 |
| [[bld_tools_funnel_diag]] | sibling | 0.34 |
