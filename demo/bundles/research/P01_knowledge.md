---
kind: knowledge_card
id: bld_knowledge_card_knowledge_card
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for knowledge_card production — atomic searchable facts
sources: validate_kc.py v2.0, _schema.yaml v4.0, 721 real knowledge cards
quality: null
title: "Knowledge Card Knowledge Card"
version: "1.0.0"
author: n03_builder
tags:
  - "knowledge_card"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "knowledge card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords:
  - "atomic searchable facts"
  - "knowledge card construction"
  - "knowledge card knowledge card"
  - "knowledge_card"
  - "builder"
  - "examples"
  - "{{placeholder}}"
  - "domain knowledge"
  - "executive summary knowledge"
  - "spec table"
density_score: 0.90
related:
  - knowledge-card-builder
---
# Conhecimento de Domínio: knowledge_card
## Resumo Executivo
Knowledge cards são fatos atômicos e pesquisáveis -- a menor unidade de recuperação em um sistema de conhecimento. Cada card responde UMA pergunta sobre UM tópico com densidade >= 0.80 (mais de 80% de dado concreto, sem enchimento). Os cards são recuperados via busca híbrida (BM25 + vetor) usando os campos do frontmatter. Eles se diferenciam de model cards (specs de LLM), learning records (experiência interna) e context docs (contexto de domínio).
## Tabela de Especificação
| Propriedade | Valor |
|----------|-------|
| Pillar | P01 (knowledge) |
| Campos de frontmatter | 14 obrigatórios + 5 estendidos |
| Gates de qualidade | 10 HARD + 20 SOFT |
| Corpo máximo | 5120 bytes |
| Corpo mínimo | 200 bytes |
| Densidade mínima | >= 0.80 |
| Faixa ideal de tamanho | 50-80 linhas (conceito único), 80-120 (multi-padrão) |
| Dimensões de pontuação | D1 Frontmatter, D2 Densidade, D3 Axiomas, D4 Estrutura, D5 Formato |
## Padrões
- **Superfície de recuperação**: os campos do frontmatter direcionam a descoberta via busca
| Campo | Papel na recuperação | Padrão |
|-------|---------------|---------|
| tldr | Correspondência primária (BM25 + embedding) | Específico: "Execute a CLI via subprocess, retry 3x" |
| tags | Filtragem por faceta, clustering | 3-7 tags, misturando domínio + técnica |
| keywords | Reforço de correspondência exata no BM25 | 2-5 termos que o usuário digitaria literalmente |
| long_tails | Busca semântica/vetorial | Frases completas: "como lidar com refresh concorrente de token" |
| when_to_use | Gatilho de ativação do agente | Contexto específico, não "quando necessário" |
- **Hierarquia de densidade** (do mais ao menos informativo por token): tabelas > blocos de código > bullets > diagramas ASCII > parágrafos
- **Duas estruturas de corpo**: domain_kc (conhecimento externo: Referência Rápida, Conceitos-Chave, Estratégia, Regras de Ouro, Fluxo, Referências) e meta_kc (interno ao sistema: Resumo Executivo, Tabela de Especificação, Padrões, Anti-Padrões, Aplicação, Referências)
- **Gate de densidade**: densidade = linhas_de_dado / total_de_linhas_não_vazias; < 0.80 = o card reprova independente da demais qualidade
- **Forma de axioma**: SEMPRE/NUNCA/SE-ENTÃO com condição + ação + consequência
## Anti-Padrões
| Anti-Padrão | Por que falha |
|-------------|-------------|
| tldr vago ("Como usar a CLI") | Nenhum sinal de busca; retorna errado no BM25 |
| Corpo em prosa | Densidade baixa; converta para tabelas, bullets, código |
| Resíduo de template (`{{placeholder}}`) | Campos não preenchidos; parece incompleto |
| Eco do frontmatter no corpo | O corpo repete title/tldr; não agrega profundidade |
| Monólito gigante (300+ linhas) | Divida em 2+ cards atômicos focados |
| densidade < 0.80 | O card reprova independente das demais notas de qualidade |
## Aplicação
1. Defina UM tópico: que pergunta única este card responde?
2. Escreva o frontmatter: os 14 campos obrigatórios com valores específicos e otimizados para busca
3. Escolha a estrutura de corpo: domain_kc (externo) ou meta_kc (interno)
4. Escreva um corpo denso: tabelas primeiro, bullets em segundo, parágrafos só quando necessário
5. Verifique a densidade: linhas_de_dado / total >= 0.80
6. Valide: <= 5120 bytes, >= 200 bytes, axiomas na forma SEMPRE/NUNCA/SE-ENTÃO
## Referências
- validate_kc.py v2.0: validador de gates 10 HARD + 20 SOFT
- _schema.yaml v4.0: definições canônicas de campo para knowledge_card
- 721 knowledge cards reais: padrões empíricos (corpo p95 = 4274 bytes)
- Recuperação de informação: busca híbrida BM25 + vetor para recuperação densa

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_knowledge_best_practices | sibling | 0.41 |
| [[knowledge-card-builder]] | downstream | 0.39 |
| p01_kc_creation_best_practices | sibling | 0.38 |
| [[bld_prompt_knowledge_card]] | downstream | 0.38 |
| [[bld_orchestration_knowledge_card]] | downstream | 0.32 |
