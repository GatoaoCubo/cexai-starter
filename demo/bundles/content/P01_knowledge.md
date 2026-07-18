---
kind: knowledge_card
id: bld_knowledge_card_knowledge_card
pillar: P01
llm_function: INJECT
purpose: "Conhecimento de dominio para producao de knowledge_card -- fatos atomicos e pesquisaveis"
sources: validate_kc.py v2.0, _schema.yaml v4.0, 721 knowledge cards reais
quality: null
title: "Base de Conhecimento: knowledge_card"
version: "1.0.0"
author: n03_builder
tags:
  - "knowledge_card"
  - "builder"
  - "examples"
tldr: "Exemplos-modelo e anti-exemplos de construcao de knowledge_card, demonstrando estrutura ideal e armadilhas comuns."
domain: "construcao de knowledge_card"
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
Knowledge cards sao fatos atomicos e pesquisaveis -- a menor unidade de recuperacao em um sistema de conhecimento. Cada card responde UMA pergunta sobre UM topico, com densidade >= 0.80 (mais de 80% de dado concreto, sem enchimento). Os cards sao recuperados via busca hibrida (BM25 + vetor) usando os campos do frontmatter. Eles se diferenciam do model card (especificacao de LLM), do learning_record (experiencia interna registrada) e do context_doc (contexto amplo de dominio).
## Tabela de Especificacao
| Propriedade | Valor |
|----------|-------|
| Pilar | P01 (knowledge) |
| Campos de frontmatter | 14 obrigatorios + 5 estendidos |
| Portoes de qualidade | 10 HARD + 20 SOFT |
| Corpo maximo | 5120 bytes |
| Corpo minimo | 200 bytes |
| Densidade minima | >= 0.80 |
| Tamanho ideal | 50-80 linhas (conceito unico), 80-120 (multi-padrao) |
| Dimensoes de pontuacao | D1 Frontmatter, D2 Densidade, D3 Axiomas, D4 Estrutura, D5 Formato |
## Padroes
- **Superficie de recuperacao**: os campos do frontmatter guiam a descoberta na busca
| Campo | Papel na recuperacao | Padrao |
|-------|---------------|---------|
| tldr | Match primario (BM25 + embedding) | Especifico: "Executa a CLI via subprocess, retry 3x" |
| tags | Filtro facetado, agrupamento | 3-7 tags, mix de dominio + tecnica |
| keywords | Reforco de match exato no BM25 | 2-5 termos que o usuario digitaria literalmente |
| long_tails | Busca semantica/vetorial | Frases completas: "como tratar refresh de token concorrente" |
| when_to_use | Gatilho de ativacao do agente | Contexto especifico, nunca "quando necessario" |
- **Hierarquia de densidade** (do que mais informa por token ao que menos informa): tabelas > blocos de codigo > bullets > diagramas ASCII > paragrafos
- **Duas estruturas de corpo**: domain_kc (conhecimento externo: Referencia Rapida, Conceitos-Chave, Estrategia, Regras de Ouro, Fluxo, Referencias) e meta_kc (interno ao sistema: Resumo Executivo, Tabela de Especificacao, Padroes, Anti-Padroes, Aplicacao, Referencias)
- **Portao de densidade**: densidade = linhas_de_dado / linhas_nao_vazias_totais; abaixo de 0.80 o card reprova independente da demais qualidade
- **Forma do axioma**: SEMPRE/NUNCA/SE-ENTAO com condicao + acao + consequencia
## Anti-Padroes
| Anti-Padrao | Por que falha |
|-------------|-------------|
| tldr vago ("Como usar a CLI") | Sem sinal de busca; retorna errado no BM25 |
| Corpo em prosa | Densidade baixa; converter em tabelas, bullets, codigo |
| Residuo de template (`{{placeholder}}`) | Campo nao preenchido; parece incompleto |
| Eco do frontmatter no corpo | Corpo repete title/tldr; adiciona profundidade zero |
| Monolito gigante (300+ linhas) | Dividir em 2 ou mais cards atomicos focados |
| densidade < 0.80 | Card reprovado, independente das demais notas de qualidade |
## Aplicacao
1. Defina UM topico: qual pergunta unica este card responde?
2. Escreva o frontmatter: os 14 campos obrigatorios com valores especificos e otimizados para busca
3. Escolha a estrutura do corpo: domain_kc (externo) ou meta_kc (interno)
4. Escreva um corpo denso: tabelas primeiro, bullets em segundo, paragrafos apenas quando necessario
5. Confira a densidade: linhas_de_dado / total >= 0.80
6. Valide: entre 200 e 5120 bytes, axiomas na forma SEMPRE/NUNCA/SE-ENTAO
## Referencias
- validate_kc.py v2.0: validador com 10 portoes HARD + 20 SOFT
- _schema.yaml v4.0: definicoes canonicas de campo para knowledge_card
- 721 knowledge cards reais: padroes empiricos (corpo no percentil 95 = 4274 bytes)
- Information retrieval: busca hibrida BM25 + vetor para recuperacao densa

## Related Artifacts
| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| p01_kc_knowledge_best_practices | sibling | 0.41 |
| [[knowledge-card-builder]] | downstream | 0.39 |
| p01_kc_creation_best_practices | sibling | 0.38 |
| [[bld_prompt_knowledge_card]] | downstream | 0.38 |
| [[bld_orchestration_knowledge_card]] | downstream | 0.32 |
