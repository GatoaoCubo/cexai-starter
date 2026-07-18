---
kind: instruction
id: bld_instruction_knowledge_card
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para knowledge_card
pattern: pipeline de 3 fases (pesquisar -> compor -> validar)
quality: null
title: "Instruções: Knowledge Card"
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
8f: "F6_produce"
keywords:
  - "construção de knowledge_card"
  - "instruções knowledge card"
  - "knowledge_card"
  - "builder"
  - "examples"
  - "python _tools/cex_compile.py <file>"
  - "p01_kc_[a-z][a-z0-9_]+"
  - "referência rápida"
  - "conceitos-chave"
  - "fases da estratégia"
density_score: 0.90
related:
  - knowledge-card-builder
---
# Instruções: Como Produzir um knowledge_card
## Fase 1: PESQUISAR
1. Identifique o tópico: qual fato ou padrão atômico único precisa ser capturado?
2. Reúna fontes: documentação oficial, URLs, referências de código, ou conhecimento especialista estabelecido
3. Extraia fatos-chave -- pontos de dado concretos (números, datas, nomes, medições), não opiniões ou afirmações vagas
4. Determine o tipo de KC:
   - domain_kc: conhecimento externo sobre uma ferramenta, API, protocolo, ou domínio
   - meta_kc: padrão interno ou lição aprendida operando este sistema
5. Confira os knowledge_cards existentes via brain_query [SE MCP] para o mesmo tópico -- evite duplicatas
6. Avalie a densidade de informação: dá para atingir densidade >= 0.80 (tabelas, código, bullets concretos em vez de prosa de enchimento)?
## Fase 2: COMPOR
1. Leia o SCHEMA.md -- fonte da verdade para todos os campos de frontmatter e restrições de corpo
2. Leia o OUTPUT_TEMPLATE.md -- preencha o template seguindo exatamente as restrições do SCHEMA
3. Preencha o frontmatter: 14 campos obrigatórios + 5 campos estendidos CEX (null é aceitável para campos recomendados)
4. Defina quality: null -- nunca se autoavalie
5. Escreva o corpo seguindo a estrutura do tipo de KC:
   - domain_kc: Referência Rápida, Conceitos-Chave, Fases da Estratégia, Regras de Ouro, Fluxo, Comparativo, Referências
   - meta_kc: Resumo Executivo, Tabela de Especificações, Padrões, Antipadrões, Aplicação, Referências
6. Prefira formatos de alta densidade: tabelas e blocos de código em vez de parágrafos
7. Mantenha todo bullet com 80 caracteres ou menos
8. Inclua ao menos uma URL externa na seção Referências
9. Escreva os axiomas no frontmatter como regras ALWAYS / NEVER / IF-THEN -- ao menos um é obrigatório
10. Mantenha o corpo entre 200 e 5120 bytes
## Fase 3: VALIDAR
1. Rode `python _tools/cex_compile.py <file>` se disponível -- esta é uma ferramenta automatizada ativa
2. Gates HARD (todos precisam passar):
   - o frontmatter YAML faz parse sem erros
   - o id casa com o padrão `p01_kc_[a-z][a-z0-9_]+`
   - kind == knowledge_card
   - quality == null
   - densidade >= 0.80
   - ao menos 3 fatos concretos presentes (números, datas, entidades nomeadas)
   - o corpo está entre 200 e 5120 bytes
   - sem caminhos internos no corpo (records/, .claude/, /home/)
   - sem frases de enchimento ("this document covers", "as mentioned above")
3. Gates SOFT (pontue cada um contra o QUALITY_GATES.md):
   - o tldr contém dado concreto, não descrição genérica
   - os axiomas estão em forma ALWAYS / NEVER / IF-THEN
   - ao menos 4 seções com ao menos 3 linhas não vazias cada
   - keywords e long_tails presentes para busca
4. Confira cruzado os limites de escopo:
   - é um fato atômico pesquisável, não uma visão geral ampla de domínio (context_doc)?
   - não é uma definição de termo (glossary_entry)?
   - não é um arquivo de configuração de embedding?
   - os fatos são concretos (números, datas, nomes) em vez de afirmações vagas?
5. Se um gate HARD falhar: corrija imediatamente e rode o validador de novo
6. Se a nota for < 8.0: expanda seções rasas, substitua prosa por tabelas ou blocos de código, remova enchimento

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_knowledge_card]] | upstream | 0.37 |
| [[knowledge-card-builder]] | upstream | 0.36 |
| p01_kc_knowledge_best_practices | upstream | 0.32 |
| [[bld_prompt_input_schema]] | sibling | 0.30 |
| [[bld_prompt_instruction]] | sibling | 0.28 |
