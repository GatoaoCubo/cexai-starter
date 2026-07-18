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
# Conhecimento de Dominio: knowledge_card
## Resumo Executivo
Artefatos knowledge_card sao fatos atomicos pesquisaveis -- a menor unidade de recuperacao em um sistema de conhecimento. Cada card responde a UMA pergunta sobre UM topico com densidade >= 0.80 (mais de 80% de dado concreto, sem enchimento). Os cards sao recuperados via busca hibrida (BM25 + vetor) usando os campos do frontmatter. Eles se diferenciam de model cards (especificacoes de LLM), learning records (experiencia interna) e context docs (contexto de dominio).
## Tabela de Especificacao
| Propriedade | Valor |
|----------|-------|
| Pillar | P01 (knowledge) |
| Campos de frontmatter | 14 obrigatorios + 5 estendidos |
| Gates de qualidade | 10 HARD + 20 SOFT |
| Corpo maximo | 5120 bytes |
| Corpo minimo | 200 bytes |
| Densidade minima | >= 0.80 |
| Faixa ideal de tamanho | 50-80 linhas (conceito unico), 80-120 (multiplos padroes) |
| Dimensoes de pontuacao | D1 Frontmatter, D2 Densidade, D3 Axiomas, D4 Estrutura, D5 Formato |
## Padroes
- **Superficie de recuperacao**: os campos de frontmatter direcionam a descoberta na busca
| Campo | Papel na recuperacao | Padrao |
|-------|---------------|---------|
| tldr | Match primario (BM25 + embedding) | Especifico: "Executar CLI via subprocess, retry 3x" |
| tags | Filtragem por faceta, clustering | 3-7 tags, misturando dominio + tecnica |
| keywords | Reforco de match exato no BM25 | 2-5 termos que o usuario realmente digitaria |
| long_tails | Busca semantica/vetorial | Frases completas: "como lidar com refresh concorrente de token" |
| when_to_use | Gatilho de ativacao do agente | Contexto especifico, nao "quando necessario" |
- **Hierarquia de densidade** (do mais ao menos informativo por token): tabelas > blocos de codigo > bullets > diagramas ASCII > paragrafos
- **Duas estruturas de corpo**: domain_kc (conhecimento externo: Referencia Rapida, Conceitos-Chave, Estrategia, Regras de Ouro, Fluxo, Referencias) e meta_kc (interno ao sistema: Resumo Executivo, Tabela de Especificacao, Padroes, Antipadroes, Aplicacao, Referencias)
- **Gate de densidade**: densidade = linhas_de_dado / linhas_nao_vazias_totais; < 0.80 = o card falha independentemente da demais qualidade
- **Forma do axioma**: ALWAYS/NEVER/IF-THEN com condicao + acao + consequencia
## Antipadroes
| Antipadrao | Por que falha |
|-------------|-------------|
| tldr vago ("Como usar a CLI") | Sem sinal de busca; retorna errado no BM25 |
| Corpo em prosa | Densidade baixa; converta para tabelas, bullets, codigo |
| Residuo de template (`{{placeholder}}`) | Campos nao preenchidos; parece incompleto |
| Eco do frontmatter no corpo | O corpo repete title/tldr; nao agrega profundidade |
| Monolito gigante (300+ linhas) | Divida em 2+ cards atomicos focados |
| densidade < 0.80 | O card falha independentemente das demais pontuacoes de qualidade |
## Aplicacao
1. Defina UM topico: qual pergunta unica este card responde?
2. Escreva o frontmatter: os 14 campos obrigatorios com valores especificos e otimizados para busca
3. Selecione a estrutura do corpo: domain_kc (externo) ou meta_kc (interno)
4. Escreva um corpo denso: tabelas primeiro, bullets em segundo, paragrafos somente quando necessario
5. Verifique a densidade: linhas_de_dado / total >= 0.80
6. Valide: <= 5120 bytes, >= 200 bytes, axiomas na forma ALWAYS/NEVER/IF-THEN
## Referencias
- validate_kc.py v2.0: validador de gates 10 HARD + 20 SOFT
- _schema.yaml v4.0: definicoes canonicas de campos para knowledge_card
- 721 knowledge cards reais: padroes empiricos (corpo p95 = 4274 bytes)
- Information retrieval: busca hibrida BM25 + vetor para recuperacao densa

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| p01_kc_knowledge_best_practices | irmao | 0.41 |
| [[knowledge-card-builder]] | a jusante | 0.39 |
| p01_kc_creation_best_practices | irmao | 0.38 |
| [[bld_prompt_knowledge_card]] | a jusante | 0.38 |
| [[bld_orchestration_knowledge_card]] | a jusante | 0.32 |
