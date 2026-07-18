---
kind: knowledge_card
id: bld_knowledge_card_knowledge_card
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para a produção de knowledge_card -- fatos atômicos pesquisáveis
sources: validate_kc.py v2.0, _schema.yaml v4.0, 721 knowledge_cards reais
quality: null
title: "Knowledge Card Knowledge Card"
version: "1.0.0"
author: n03_builder
tags:
  - "knowledge_card"
  - "builder"
  - "examples"
tldr: "Exemplos ideais e anti-exemplos para a construção de knowledge_card, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de knowledge_card"
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
Knowledge_cards são fatos atômicos pesquisáveis -- a menor unidade de retrieval em um sistema de conhecimento. Cada card responde a UMA pergunta sobre UM tópico com densidade >= 0.80 (mais de 80% de dado concreto, sem enchimento). Os cards são recuperados via busca híbrida (BM25 + vetorial) usando os campos do frontmatter. Eles se diferenciam de model_card (especificações de LLM), learning_record (experiência interna do sistema) e context_doc (contexto de domínio).
## Tabela de Especificações
| Propriedade | Valor |
|----------|-------|
| Pilar | P01 (knowledge) |
| Campos de frontmatter | 14 obrigatórios + 5 estendidos |
| Gates de qualidade | 10 HARD + 20 SOFT |
| Corpo máximo | 5120 bytes |
| Corpo mínimo | 200 bytes |
| Densidade mínima | >= 0.80 |
| Tamanho ideal | 50-80 linhas (conceito único), 80-120 (multi-padrão) |
| Dimensões de pontuação | D1 Frontmatter, D2 Densidade, D3 Axiomas, D4 Estrutura, D5 Formato |
## Padrões
- **Superficie de retrieval**: os campos do frontmatter direcionam a descoberta na busca
| Campo | Papel no retrieval | Padrão |
|-------|---------------|---------|
| tldr | Match primário (BM25 + embedding) | Específico: "Executar CLI via subprocess, retry 3x" |
| tags | Filtragem por faceta, clustering | 3-7 tags, misturando domínio + técnica |
| keywords | Reforço de match exato no BM25 | 2-5 termos que o usuário literalmente digitaria |
| long_tails | Busca semântica/vetorial | Frases completas: "como lidar com refresh concorrente de token" |
| when_to_use | Gatilho de ativação do agente | Contexto específico, não "quando necessário" |
- **Hierarquia de densidade** (do mais para o menos informativo por token): tabelas > blocos de código > bullets > diagramas ASCII > parágrafos
- **Duas estruturas de corpo**: domain_kc (conhecimento externo: Referência Rápida, Conceitos-Chave, Estratégia, Regras de Ouro, Fluxo, Referências) e meta_kc (interno ao sistema: Resumo Executivo, Tabela de Especificações, Padrões, Antipadrões, Aplicação, Referências)
- **Gate de densidade**: densidade = linhas_de_dado / total_de_linhas_nao_vazias; < 0.80 = o card falha independente do resto da qualidade
- **Forma do axioma**: SEMPRE/NUNCA/SE-ENTÃO com condição + ação + consequência
## Antipadrões
| Antipadrão | Por que falha |
|-------------|-------------|
| tldr vago ("Como usar a CLI") | Sem sinal de busca; retorna errado no BM25 |
| Corpo em prosa | Densidade baixa; converta para tabelas, bullets, código |
| Resíduo de template (`{{placeholder}}`) | Campos não preenchidos; parece incompleto |
| Eco do frontmatter no corpo | O corpo repete title/tldr; não agrega profundidade |
| Monolito gigante (300+ linhas) | Divida em 2+ cards atômicos focados |
| densidade < 0.80 | O card falha independente das demais pontuações de qualidade |
## Aplicação
1. Defina UM tópico: qual pergunta única este card responde?
2. Escreva o frontmatter: os 14 campos obrigatórios com valores específicos, otimizados para busca
3. Escolha a estrutura de corpo: domain_kc (externo) ou meta_kc (interno)
4. Escreva um corpo denso: tabelas primeiro, bullets em segundo, parágrafos so quando necessário
5. Confira a densidade: linhas_de_dado / total >= 0.80
6. Valide: <= 5120 bytes, >= 200 bytes, axiomas na forma SEMPRE/NUNCA/SE-ENTÃO
## Referências
- validate_kc.py v2.0: validador de gates 10 HARD + 20 SOFT
- _schema.yaml v4.0: definições canônicas de campos para knowledge_card
- 721 knowledge_cards reais: padrões empíricos (corpo p95 = 4274 bytes)
- Recuperação de informação: busca híbrida BM25 + vetorial para retrieval denso

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| p01_kc_knowledge_best_practices | irmão | 0.41 |
| [[knowledge-card-builder]] | a jusante | 0.39 |
| p01_kc_creation_best_practices | irmão | 0.38 |
| [[bld_prompt_knowledge_card]] | a jusante | 0.38 |
| [[bld_orchestration_knowledge_card]] | a jusante | 0.32 |
