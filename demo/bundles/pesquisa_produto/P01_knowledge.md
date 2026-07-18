---
kind: knowledge_card
id: bld_knowledge_card_knowledge_card
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para a produção de knowledge_card -- fatos atômicos e pesquisáveis
sources: validate_kc.py v2.0, _schema.yaml v4.0, 721 knowledge cards reais
quality: null
title: "Cartão de Conhecimento: Knowledge Card"
version: "1.0.0"
author: n03_builder
tags:
  - "knowledge_card"
  - "builder"
  - "examples"
tldr: "Exemplos ideais e contraexemplos para a construção de knowledge cards, demonstrando estrutura ideal e erros comuns."
domain: "construção de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords:
  - "fatos atômicos pesquisáveis"
  - "construção de knowledge_card"
  - "cartão de conhecimento knowledge card"
  - "knowledge_card"
  - "builder"
  - "examples"
  - "{{placeholder}}"
  - "conhecimento de domínio"
  - "resumo executivo de conhecimento"
  - "tabela de especificações"
density_score: 0.90
related:
  - knowledge-card-builder
---
# Conhecimento de Domínio: knowledge_card
## Resumo Executivo
Cada knowledge_card é um fato atômico e pesquisável -- a menor unidade de retrieval em um sistema de conhecimento. Cada card responde UMA pergunta sobre UM tópico com densidade >= 0.80 (>80% de dado concreto, sem enchimento). Os cards são recuperados via busca híbrida (BM25 + vetor) usando campos de frontmatter. Eles se diferenciam de model_card (especificações de LLM), learning_record (experiência interna) e context_doc (contexto de domínio).
## Tabela de Especificações
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
- **Superfície de retrieval**: os campos de frontmatter conduzem a descoberta na busca
| Campo | Papel no retrieval | Padrão |
|-------|---------------|---------|
| tldr | Match primário (BM25 + embedding) | Específico: "Executa CLI via subprocess, retry 3x" |
| tags | Filtro facetado, clustering | 3-7 tags, misturando domínio + técnica |
| keywords | Reforço de match exato no BM25 | 2-5 termos que o usuário digitaria literalmente |
| long_tails | Busca semântica/vetorial | Frases completas: "como lidar com refresh concorrente de token" |
| when_to_use | Gatilho de ativação do agente | Contexto específico, nunca "quando necessário" |
- **Hierarquia de densidade** (do mais ao menos informativo por token): tabelas > blocos de código > bullets > diagramas ASCII > parágrafos
- **Duas estruturas de corpo**: domain_kc (conhecimento externo: Quick Ref, Key Concepts, Strategy, Golden Rules, Flow, References) e meta_kc (interno ao sistema: Exec Summary, Spec Table, Patterns, Anti-Patterns, Application, References)
- **Gate de densidade**: densidade = data_lines / total_non_empty_lines; < 0.80 = card reprovado independente da demais qualidade
- **Forma do axioma**: ALWAYS/NEVER/IF-THEN com condição + ação + consequência
## Antipadrões
| Antipadrão | Por que falha |
|-------------|-------------|
| tldr vago ("Como usar a CLI") | Sem sinal de busca; retorna errado no BM25 |
| Corpo em prosa | Densidade baixa; converta para tabelas, bullets, código |
| Resíduo de template (`{{placeholder}}`) | Campos não preenchidos; parece incompleto |
| Frontmatter ecoado no corpo | O corpo repete title/tldr; não agrega profundidade |
| Monólito gigante (300+ linhas) | Divida em 2+ cards atômicos focados |
| densidade < 0.80 | Card reprovado independente das demais notas de qualidade |
## Aplicação
1. Defina UM tópico: qual pergunta única este card responde?
2. Escreva o frontmatter: todos os 14 campos obrigatórios com valores específicos e otimizados para busca
3. Escolha a estrutura de corpo: domain_kc (externo) ou meta_kc (interno)
4. Escreva um corpo denso: tabelas primeiro, bullets depois, parágrafos só quando necessário
5. Confira a densidade: data_lines / total >= 0.80
6. Valide: <= 5120 bytes, >= 200 bytes, axiomas em forma ALWAYS/NEVER/IF-THEN
## Referências
- validate_kc.py v2.0: validador de 10 gates HARD + 20 SOFT
- _schema.yaml v4.0: definições canônicas de campo para knowledge_card
- 721 knowledge cards reais: padrões empíricos (corpo p95 = 4274 bytes)
- Information retrieval: busca híbrida BM25 + vetor para retrieval denso

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_knowledge_best_practices | sibling | 0.41 |
| [[knowledge-card-builder]] | downstream | 0.39 |
| p01_kc_creation_best_practices | sibling | 0.38 |
| [[bld_prompt_knowledge_card]] | downstream | 0.38 |
| [[bld_orchestration_knowledge_card]] | downstream | 0.32 |
