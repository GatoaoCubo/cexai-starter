---
id: p01_dv_vocabulario_venda_pme
kind: domain_vocabulary
pillar: P01
nucleus: N02
version: 1.0.0
quality: null
title: "Vocabulario de Venda PME -- Domain Vocabulary"
domain: vocabulario_venda_pme
bounded_context: dono_de_pme_intake_e_dashboard
governed_agents: [n02_marketing, n03_engineering]
term_count: 19
languages: [pt-br, en]
loaded_at: F2b_SPEAK
created: "2026-07-11"
tags: [vocabulary, venda, pt-br, transmutation, go_online]
tldr: "Crosswalk termo-tecnico -> termo-de-venda para o dono de PME (spec 23_go_online, User Story P2a, FR-004). Aplicado em /intake, /dashboard/research e nas CTAs da landing."
related:
  - p03_pc_cex_universal
  - n07-input-transmutation
---

# Vocabulario de Venda PME -- Domain Vocabulary

Crosswalk PT-BR: termo tecnico (como o sistema pensa) -> termo de venda (como
um dono de PME lê). Carregado em F2b SPEAK antes de qualquer copy tocar uma
superfície pública BR (`/intake`, `/dashboard/research`, CTAs da landing).
Overlay de `p03_pc_cex_universal` -- não redefine termos cross-nucleus. Padrão
do founder: venda BR = PT-BR acentuado (OSS/EN fica como está).

## Cadastro e site

| Termo técnico | Termo de venda | Nota |
|---|---|---|
| tenant | seu negócio / sua marca | conta que representa o cliente no sistema |
| slug | identificador da sua marca | vira o `--tenant SLUG` do bootstrap |
| bootstrap | criar o site | comando que gera o site a partir do briefing |
| onboarding | cadastro inicial | primeira configuração da marca |
| dashboard | painel | área logada de acompanhamento |

## Formulário e dados

| Termo técnico | Termo de venda | Nota |
|---|---|---|
| intake | briefing | formulário-entrevista da marca (`/intake`) |
| answers / form_v1 | respostas do briefing | dados coletados no formulário |
| brand_init.yaml | arquivo da sua marca | gerado a partir das respostas |
| resolve / resolver | processar o briefing | gera o arquivo da marca |

## Pesquisa e IA

| Termo técnico | Termo de venda | Nota |
|---|---|---|
| seed | o que você quer pesquisar | ponto de partida (produto/marca/CNPJ) |
| lane | frente de pesquisa | uma linha de investigação específica |
| capability / caps | recurso de IA | uma habilidade que a IA executa |
| distill | resumo da pesquisa | síntese que a IA produz a partir das fontes |
| research | pesquisa | investigação assistida por IA |

## Limites, fila e catálogo

| Termo técnico | Termo de venda | Nota |
|---|---|---|
| quota | limite de uso | quantidade disponível antes de renovar |
| rate limit | limite de chamadas | teto de pedidos por período |
| waitlist | fila de espera | lista de interessados aguardando acesso |
| webhook | aviso automático | notificação enviada quando algo acontece |
| catalog | catálogo | lista de produtos/serviços da marca |

## Como estender

1. Termo novo aparece numa conversa com o founder ou numa superfície pública.
2. Verificar que não está em `p03_pc_cex_universal` (camada universal).
3. Adicionar linha na categoria certa (ou criar categoria nova).
4. Preencher as 3 colunas: termo técnico, termo de venda, nota.
5. Bump version + atualizar `term_count`.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pc_cex_universal]] | extends (overlay) | 0.80 |
| n07-input-transmutation | feeds_f1_constrain | 0.60 |
