---
kind: instruction
id: bld_instruction_competitive_matrix
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para competitive_matrix
quality: null
title: "Instruction Competitive Matrix"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, instruction]
tldr: "Processo de produção passo a passo para competitive_matrix"
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [competitive_matrix construction, instruction competitive matrix, competitive_matrix, builder, instruction, related artifacts, phase step, customer requirements, sales battle, propositions differentiators]
density_score: 0.85
related:
  - competitive-matrix-builder
---
## Fase 1: PESQUISA
1. Identificar os concorrentes-alvo e suas ofertas de produto/serviço.
2. Coletar dados de funcionalidades a partir de especificações públicas, avaliações de clientes e demos de vendas.
3. Mapear os requisitos do cliente para battle cards de vendas e avaliações de procurement.
4. Analisar modelos de precificação, SLAs e capacidades de integração.
5. Documentar propostas de valor únicas e diferenciais.
6. Validar as fontes de dados quanto a precisão e relevância.

## Fase 2: COMPOSIÇÃO
1. Definir a estrutura da matriz: linhas = funcionalidades, colunas = concorrentes + nós mesmos.
2. Preencher as linhas com funcionalidades priorizadas (ex.: escalabilidade, segurança).
3. Preencher as colunas com os benchmarks competitivos (ex.: sim/não, escalas de avaliação).
4. Alinhar os dados com o SCHEMA.md (ex.: categorias de funcionalidade, campos de metadados).
5. Usar o OUTPUT_TEMPLATE.md para formatar cabeçalhos, rodapés e anotações.
6. Inserir propostas de valor e diferenciais em colunas dedicadas.
7. Adicionar métricas específicas de procurement (ex.: TCO, tempo de implementação).
8. Fazer referência cruzada com os templates de battle card de vendas para consistência.
9. Finalizar com legendas claras e notas para os avaliadores.

## Fase 3: VALIDAÇÃO
- [ ] Todas as funcionalidades mapeadas aos requisitos do cliente (Fase 1, Passo 3).
- [ ] Fontes de dados citadas e verificadas quanto a precisão (Fase 1, Passo 6).
- [ ] Alinhamento com o schema confirmado (Fase 2, Passo 4).
- [ ] Formatação do template compatível com OUTPUT_TEMPLATE.md (Fase 2, Passo 5).
- [ ] Stakeholders confirmam a usabilidade para cenários de vendas/procurement.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_instruction_playground_config | sibling | 0.35 |
| bld_instruction_planning_strategy | sibling | 0.29 |
| bld_instruction_judge_config | sibling | 0.28 |
| bld_instruction_eval_framework | sibling | 0.26 |
| [[competitive-matrix-builder]] | upstream | 0.26 |
