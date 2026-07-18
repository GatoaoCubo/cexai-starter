---
kind: instruction
id: bld_instruction_knowledge_card
pillar: P03
llm_function: REASON
purpose: "Processo de producao passo a passo para o knowledge_card"
pattern: "pipeline de 3 fases (pesquisar -> compor -> validar)"
quality: null
title: "Instrucoes: knowledge_card"
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
8f: "F6_produce"
keywords:
  - "knowledge card construction"
  - "instruction knowledge card"
  - "knowledge_card"
  - "builder"
  - "examples"
  - "python _tools/cex_compile.py <file>"
  - "p01_kc_[a-z][a-z0-9_]+"
  - "quick reference"
  - "key concepts"
  - "strategy phases"
density_score: 0.90
related:
  - knowledge-card-builder
---
# Instrucoes: Como Produzir um knowledge_card
## Fase 1: PESQUISAR
1. Identifique o topico: qual fato ou padrao atomico unico precisa ser capturado?
2. Reuna fontes: documentacao oficial, URLs, referencias de codigo, ou conhecimento de especialista ja estabelecido
3. Extraia os fatos-chave -- pontos de dado concreto (numeros, datas, nomes, medidas), nunca opinioes ou afirmacoes vagas
4. Determine o tipo de KC:
   - domain_kc: conhecimento externo sobre uma ferramenta, API, protocolo ou dominio
   - meta_kc: padrao interno ou licao aprendida operando este sistema
5. Confira os knowledge_card existentes via brain_query [SE HOUVER MCP] para o mesmo topico -- evite duplicatas
6. Avalie a densidade de informacao: da para chegar a densidade >= 0.80 (tabelas, codigo, bullets concretos em vez de prosa de enchimento)?
## Fase 2: COMPOR
1. Leia o SCHEMA.md -- a fonte da verdade para todos os campos de frontmatter e restricoes de corpo
2. Leia o OUTPUT_TEMPLATE.md -- preencha o template seguindo exatamente as restricoes do SCHEMA
3. Preencha o frontmatter: os 14 campos obrigatorios + os 5 campos estendidos CEX (null e aceitavel nos campos recomendados)
4. Defina quality: null -- nunca se auto-pontue
5. Escreva o corpo seguindo a estrutura do tipo de KC:
   - domain_kc: Referencia Rapida, Conceitos-Chave, Fases da Estrategia, Regras de Ouro, Fluxo, Comparativo, Referencias
   - meta_kc: Resumo Executivo, Tabela de Especificacao, Padroes, Anti-Padroes, Aplicacao, Referencias
6. Prefira formatos de alta densidade: tabelas e blocos de codigo em vez de paragrafos
7. Mantenha cada bullet com no maximo 80 caracteres
8. Inclua ao menos uma URL externa na secao References
9. Escreva os axiomas do frontmatter como regras SEMPRE / NUNCA / SE-ENTAO -- pelo menos um e obrigatorio
10. Mantenha o corpo entre 200 e 5120 bytes
## Fase 3: VALIDAR
1. Rode `python _tools/cex_compile.py <file>` se disponivel -- esta e uma ferramenta automatizada ativa
2. Portoes HARD (todos precisam passar):
   - o frontmatter YAML parseia sem erro
   - o id casa com o padrao `p01_kc_[a-z][a-z0-9_]+`
   - kind == knowledge_card
   - quality == null
   - densidade >= 0.80
   - pelo menos 3 fatos concretos presentes (numeros, datas, entidades nomeadas)
   - o corpo esta entre 200 e 5120 bytes
   - nenhum caminho interno no corpo (records/, .claude/, /home/)
   - nenhuma frase de enchimento ("este documento cobre", "como mencionado acima")
3. Portoes SOFT (pontue cada um contra o QUALITY_GATES.md):
   - o tldr contem dado concreto, nao descricao generica
   - os axiomas estao na forma SEMPRE / NUNCA / SE-ENTAO
   - pelo menos 4 secoes com pelo menos 3 linhas nao vazias cada
   - keywords e long_tails presentes para busca
4. Confira os limites de escopo:
   - e um fato atomico e pesquisavel, nao uma visao ampla de dominio (isso seria context_doc)?
   - nao e uma definicao de termo (isso seria glossary_entry)?
   - nao e um arquivo de configuracao de embedding?
   - os fatos sao concretos (numeros, datas, nomes) em vez de afirmacoes vagas?
5. Se um portao HARD falhar: corrija imediatamente e rode o validador de novo
6. Se a pontuacao for menor que 8.0: expanda secoes rasas, troque prosa por tabelas ou blocos de codigo, remova enchimento

## Related Artifacts
| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[bld_knowledge_knowledge_card]] | upstream | 0.37 |
| [[knowledge-card-builder]] | upstream | 0.36 |
| p01_kc_knowledge_best_practices | upstream | 0.32 |
| [[bld_prompt_input_schema]] | sibling | 0.30 |
| [[bld_prompt_instruction]] | sibling | 0.28 |
