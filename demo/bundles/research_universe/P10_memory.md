---
kind: memory
id: p10_mem_research_universe_builder
pillar: P10
llm_function: INJECT
purpose: Padrões aprendidos e armadilhas para a construção de research_universe
quality: null
title: "Memory Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, memory]
tldr: "Padrões aprendidos e armadilhas para a construção de research_universe"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F3_inject"
keywords: [memory research universe, padrões aprendidos, armadilhas, research_universe, builder, memory, status honesto, blocked vs skipped, sentimento sem fonte]
density_score: 0.88
related:
  - research-universe-builder
---
## Observação
Relatórios de research_universe frequentemente confundem `blocked` (fonte existe, acesso falhou agora) com `skipped` (trilha não se aplica a semente) -- os dois rótulos parecem intercambiáveis a primeira vista, mas pedem ações diferentes do usuário (tentar de novo vs. aceitar a ausência). Sementes do tipo `palavra_chave` sem entidade nomeada tendem a ter firmografia e reputação genuinamente `skipped`, mas ainda assim entregam sinal social e SEO fortes.

## Padrão
Relatórios eficazes tratam as 6 trilhas como independentes desde a classificação da semente: decidem cedo quais trilhas SÃO ESPERADAS a se aplicar (ver P06, tabela Semente x Trilhas), e só então tentam a coleta. Isso evita o erro de tentar forçar firmografia sobre uma semente que é apenas uma palavra-chave genérica, e evita o erro oposto de pular sinal social numa empresa que claramente tem presença pública.

## Evidência
Relatórios revisados mostraram que rotular `blocked` vs `skipped` corretamente reduziu em conversas subsequentes o retrabalho do usuário -- quando uma trilha aparecia como `blocked` com o motivo explícito, o usuário sabia exatamente que dado colar para desbloquear a trilha; quando aparecia (incorretamente) como `skipped`, o usuário não tentava fornecer o dado porque assumia que a trilha não se aplicava.

## Recomendações
- Sempre registrar o MOTIVO ao lado do status `blocked`/`skipped`, nunca só o rótulo isolado.
- Classificar sentimento em PT somente quando há trecho-fonte citável -- se as trilhas Sinal Social e Reputação vieram vazias, a trilha de sentimento é `skipped`, não uma impressão genérica.
- Gerar perguntas multi-perspectiva DEPOIS de coletar as outras trilhas -- perguntas geradas antes da coleta tendem a ser genéricas demais.
- Para semente `store_id`, tentar resolver o publicador do app/loja para um CNPJ antes de marcar firmografia como `skipped` -- muitas vezes a informação está na própria página da loja.
- Sinalizar `coverage_score` baixo (< 0.5) na PRIMEIRA linha da síntese executiva, não apenas na tabela de status -- o usuário decide rápido se o relatório parcial já serve.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[research-universe-builder]] | upstream | 0.34 |
| [[bld_instruction_research_universe]] | upstream | 0.30 |
| p10_mem_competitive_matrix_builder | sibling | 0.24 |
| [[bld_collaboration_research_universe]] | downstream | 0.22 |
