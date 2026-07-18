---
kind: knowledge_card
id: bld_knowledge_card_competitive_matrix
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para produção de competitive_matrix
quality: null
title: "Knowledge Card Competitive Matrix"
version: "1.1.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, knowledge_card]
tldr: "Gartner MQ, Forrester Wave, G2 Grid, feature-parity grid, battle card, diretrizes anti-FUD"
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [competitive_matrix construction, knowledge card competitive matrix, gartner mq, forrester wave, feature-parity grid, battle card, anti-fud guidelines, competitive_matrix, builder, knowledge_card]
density_score: 0.85
related:
  - competitive-matrix-builder
  - bld_schema_competitive_matrix
  - analyst-briefing-builder
---
## Visão Geral do Domínio
Matrizes competitivas são artefatos analíticos estruturados usados em battle cards de vendas e avaliações de compras (procurement). Elas comparam produtos em dimensões quantificáveis para apoiar decisões de go/no-go. Três frameworks de analistas moldam o padrão da indústria: Gartner Magic Quadrant (2 eixos: capacidade de execução x completude de visão), Forrester Wave (pontuação ponderada por critérios em Oferta Atual, Estratégia e Presença de Mercado) e G2 Grid (avaliações verificadas de usuários plotadas em Satisfação x Presença de Mercado).

Battle cards são derivados por concorrente: 1 página com nos-vs-eles por capacidade, pares de objeção-contra-argumento e a razão de vitória/derrota (win/loss rationale). As diretrizes anti-FUD regem como responder as alegações de mercado de concorrentes com dados verificáveis.

## Conceitos-Chave
| Conceito | Definição | Fonte |
|---------|-----------|--------|
| Feature parity grid | Tabela comparando Sim/Não/Parcial/Roadmap entre fornecedores para cada capacidade | Boas práticas de sales enablement |
| Gartner Magic Quadrant | Plotagem em 2 eixos: Capacidade de Execução (y) x Completude de Visão (x); quatro quadrantes | Metodologia Gartner MQ |
| Forrester Wave | Pontuação ponderada nas dimensões Oferta Atual, Estratégia e Presença de Mercado | Metodologia Forrester Wave |
| G2 Grid | Posicionamento baseado em avaliações de usuários: Satisfação (y) x Presença de Mercado (x) | Metodologia G2 Grid |
| Battle card | 1 página por concorrente: funcionalidades, preço, objeções, razões de vitória | Padrão de sales enablement |
| TCO (Custo Total de Propriedade) | Custo de ciclo de vida completo: licença + implementação + treinamento + suporte + migração | Metodologia Gartner TCO |
| Anti-FUD | Respostas factuais e com fonte citada a alegações de medo/incerteza/dúvida do concorrente | Ética de inteligência competitiva |
| Win/Loss rationale | Razão orientada a dados de por que negócios são ganhos ou perdidos contra um concorrente específico | Inteligência competitiva derivada do CRM |
| Feature weighting | Atribuição de pesos de prioridade a capacidades com base nos requisitos do comprador | Modelo Kano + matrizes de pontuação de RFP |
| Roadmap item | Funcionalidade ainda não lançada; sempre rotulada com o trimestre-alvo (Q# AAAA) | Convenção de gestão de produto |

## Padrões da Indústria
- Gartner Magic Quadrant (posicionamento por capacidade de execução x completude de visão)
- Forrester Wave (pontuação ponderada multi-critério com briefings de fornecedores)
- G2 Grid (posicionamento por avaliação verificada de usuários -- não opinião de analista)
- IDC MarketScape (2 eixos similar ao MQ, mas com pontuações de capacidade)
- SCIP (Strategic and Competitive Intelligence Professionals) -- diretrizes éticas
- Battlecard.io / Klue / Crayon (convenções de estrutura de battle card)

## Padrões Comuns
1. Feature parity grid: linhas = capacidades, colunas = nos + concorrentes; valores = Sim/Não/Parcial/Roadmap Q# AAAA.
2. Posicionamento estilo Gartner: posicionar fornecedores em uma matriz 2x2 com justificativa para cada eixo.
3. Battle card por concorrente: nos vs eles em 5-8 capacidades-chave, 2-3 pares de objeção-contra-argumento.
4. Tabela de comparação de preços: camadas entrada/intermediária/enterprise + modelo de precificação (por usuário/fixo/uso).
5. Seção anti-FUD: listar as 3 principais alegações do concorrente com contra-argumento factual e fonte primária.
6. Atualidade dos dados: toda alegação datada; sinalizar itens com mais de 12 meses como potencialmente desatualizados.

## Armadilhas
- Valores de capacidade vagos: "Rápido" vs "Lento" (usar "< 100ms de latência p99" vs "> 500ms de latência p99").
- Itens de roadmap apresentados como já disponíveis: sempre marcar roadmap com Q# AAAA.
- Ausência de anti-FUD: se concorrentes fazem alegações nos seus negócios, ignorá-las é um risco de perda.
- Dependência de um único analista: cruzar Gartner com avaliações de usuários do G2 e o Forrester Wave.
- Dados desatualizados: inteligência competitiva degrada rápido; datar toda alegação.
- Superlativos sem citação: "líder de mercado" é FUD sem uma citação de analista ou benchmark.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[competitive-matrix-builder]] | related | 0.47 |
| bld_knowledge_card_analyst_briefing | sibling | 0.41 |
| [[bld_schema_competitive_matrix]] | downstream | 0.38 |
| analyst-briefing-builder | downstream | 0.33 |
