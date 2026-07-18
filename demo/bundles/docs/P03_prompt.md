---
kind: instruction
id: bld_instruction_knowledge_card
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for knowledge_card
pattern: 3-phase pipeline (research -> compose -> validate)
quality: null
title: "Instruction Knowledge Card"
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
8f: "F6_produce"
keywords:
  - "knowledge card construction"
  - "instruction knowledge card"
  - "knowledge_card"
  - "builder"
  - "examples"
  - "python _tools/validate_kc.py <file>"
  - "p01_kc_[a-z][a-z0-9_]+"
  - "quick reference"
  - "key concepts"
  - "strategy phases"
density_score: 0.90
related:
  - knowledge-card-builder
---
# Instrucoes: Como Produzir um knowledge_card
## Fase 1: PESQUISA
1. Identifique o topico: qual fato ou padrao atomico unico precisa ser capturado?
2. Reuna fontes: documentacao oficial, URLs, referencias de codigo ou conhecimento especializado consolidado
3. Extraia fatos-chave -- pontos de dado concretos (numeros, datas, nomes, medidas), nao opinioes ou afirmacoes vagas
4. Determine o tipo de KC:
   - domain_kc: conhecimento externo sobre uma ferramenta, API, protocolo ou dominio
   - meta_kc: padrao interno ou licao aprendida operando este sistema
5. Verifique knowledge_card existentes via brain_query [SE MCP] para o mesmo topico -- evite duplicatas
6. Avalie a densidade de informacao: e possivel atingir densidade >= 0.80 (tabelas, codigo, bullets concretos em vez de prosa de enchimento)?
## Fase 2: COMPOSICAO
1. Leia o SCHEMA.md -- fonte da verdade para todos os campos de frontmatter e restricoes de corpo
2. Leia o OUTPUT_TEMPLATE.md -- preencha o template seguindo exatamente as restricoes do SCHEMA
3. Preencha o frontmatter: 14 campos obrigatorios + 5 campos estendidos da CEX (null e aceitavel para campos recomendados)
4. Defina quality: null -- nunca se autopontue
5. Escreva o corpo seguindo a estrutura do tipo de KC:
   - domain_kc: Referencia Rapida, Conceitos-Chave, Fases da Estrategia, Regras de Ouro, Fluxo, Comparativo, Referencias
   - meta_kc: Resumo Executivo, Tabela de Especificacao, Padroes, Antipadroes, Aplicacao, Referencias
6. Prefira formatos de alta densidade: tabelas e blocos de codigo em vez de paragrafos
7. Mantenha cada bullet com 80 caracteres ou menos
8. Inclua ao menos uma URL externa na secao de Referencias
9. Escreva os axiomas no frontmatter como regras ALWAYS / NEVER / IF-THEN -- pelo menos um e obrigatorio
10. Mantenha o corpo entre 200 e 5120 bytes
## Fase 3: VALIDACAO
1. Execute `python _tools/validate_kc.py <file>` se disponivel -- esta e uma ferramenta automatizada ativa
2. Gates HARD (todos devem passar):
   - o frontmatter YAML e interpretado sem erros
   - o id corresponde ao padrao `p01_kc_[a-z][a-z0-9_]+`
   - kind == knowledge_card
   - quality == null
   - densidade >= 0.80
   - pelo menos 3 fatos concretos presentes (numeros, datas, entidades nomeadas)
   - o corpo esta entre 200 e 5120 bytes
   - nenhum caminho interno no corpo (records/, .claude/, /home/)
   - nenhuma frase de enchimento ("este documento aborda", "como mencionado acima")
3. Gates SOFT (pontue cada um contra o QUALITY_GATES.md):
   - o tldr contem dado concreto, nao descricao generica
   - os axiomas estao na forma ALWAYS / NEVER / IF-THEN
   - pelo menos 4 secoes com pelo menos 3 linhas nao vazias cada
   - keywords e long_tails presentes para busca
4. Confira os limites de escopo:
   - e um fato atomico pesquisavel, nao uma visao geral ampla de dominio (context_doc)?
   - nao e a definicao de um termo (glossary_entry)?
   - nao e um arquivo de configuracao de embedding?
   - os fatos sao concretos (numeros, datas, nomes) em vez de afirmacoes vagas?
5. Se um gate HARD falhar: corrija imediatamente e execute o validador novamente
6. Se a pontuacao < 8.0: expanda secoes rasas, substitua prosa por tabelas ou blocos de codigo, remova enchimento

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_knowledge_knowledge_card]] | a montante | 0.37 |
| [[knowledge-card-builder]] | a montante | 0.36 |
| p01_kc_knowledge_best_practices | a montante | 0.32 |
| [[bld_prompt_input_schema]] | irmao | 0.30 |
| [[bld_prompt_instruction]] | irmao | 0.28 |
