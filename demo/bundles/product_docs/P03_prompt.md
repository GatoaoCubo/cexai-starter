---
kind: instruction
id: bld_instruction_knowledge_card
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para knowledge_card
pattern: pipeline de 3 fases (pesquisar -> compor -> validar)
quality: null
title: "Instruction Knowledge Card"
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
# Instruções: Como Produzir um knowledge_card
## Fase 1: PESQUISA
1. Identifique o tópico: qual fato ou padrão atômico único precisa ser capturado?
2. Reúna fontes: documentação oficial, URLs, referências de código ou conhecimento especializado já estabelecido
3. Extraia os fatos-chave -- pontos de dado concretos (números, datas, nomes, medidas), não opiniões ou afirmações vagas
4. Determine o tipo de KC:
   - domain_kc: conhecimento externo sobre uma ferramenta, API, protocolo ou domínio
   - meta_kc: padrão interno ou lição aprendida operando este sistema
5. Verifique os knowledge_cards existentes via brain_query [SE MCP] para o mesmo tópico -- evite duplicatas
6. Avalie a densidade de informação: é possível atingir densidade >= 0.80 (tabelas, código, bullets concretos em vez de prosa de enchimento)?
## Fase 2: COMPOSIÇÃO
1. Leia o SCHEMA.md -- fonte da verdade para todos os campos de frontmatter e restrições de corpo
2. Leia o OUTPUT_TEMPLATE.md -- preencha o template seguindo exatamente as restrições do SCHEMA
3. Preencha o frontmatter: 14 campos obrigatórios + 5 campos estendidos do CEX (null é aceitável para campos recomendados)
4. Defina quality: null -- nunca se autopontue
5. Escreva o corpo seguindo a estrutura do tipo de KC:
   - domain_kc: Referência Rápida, Conceitos-Chave, Fases da Estratégia, Regras de Ouro, Fluxo, Comparativo, Referências
   - meta_kc: Resumo Executivo, Tabela de Especificações, Padrões, Antipadrões, Aplicação, Referências
6. Prefira formatos de alta densidade: tabelas e blocos de código em vez de parágrafos
7. Mantenha todo bullet com no máximo 80 caracteres
8. Inclua ao menos uma URL externa na seção de Referências
9. Escreva os axiomas no frontmatter como regras SEMPRE / NUNCA / SE-ENTÃO -- ao menos um obrigatório
10. Mantenha o corpo entre 200 e 5120 bytes
## Fase 3: VALIDAÇÃO
1. Rode `python _tools/cex_compile.py <file>` se disponível -- esta é uma ferramenta automatizada ativa
2. Gates HARD (todos devem passar):
   - o frontmatter YAML faz parse sem erros
   - id casa com o padrão `p01_kc_[a-z][a-z0-9_]+`
   - kind == knowledge_card
   - quality == null
   - density >= 0.80
   - ao menos 3 fatos concretos presentes (números, datas, entidades nomeadas)
   - o corpo tem entre 200 e 5120 bytes
   - sem caminhos internos no corpo (records/, .claude/, /home/)
   - sem frases de enchimento ("este documento cobre", "conforme mencionado acima")
3. Gates SOFT (pontue cada um contra o QUALITY_GATES.md):
   - o tldr contem dado concreto, não descrição genérica
   - os axiomas estão na forma SEMPRE / NUNCA / SE-ENTÃO
   - ao menos 4 seções com ao menos 3 linhas não vazias cada
   - keywords e long_tails presentes para busca
4. Confira os limites de escopo:
   - é um fato atômico pesquisável, não uma visão geral ampla de domínio (context_doc)?
   - não é uma definição de termo (glossary_entry)?
   - não é um arquivo de configuração de embedding?
   - os fatos são concretos (números, datas, nomes) em vez de afirmações vagas?
5. Se um gate HARD falhar: corrija imediatamente e rode o validador de novo
6. Se a pontuação < 8.0: expanda seções rasas, substitua prosa por tabelas ou blocos de código, remova enchimento

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_knowledge_knowledge_card]] | a montante | 0.37 |
| [[knowledge-card-builder]] | a montante | 0.36 |
| p01_kc_knowledge_best_practices | a montante | 0.32 |
| [[bld_prompt_input_schema]] | irmão | 0.30 |
| [[bld_prompt_instruction]] | irmão | 0.28 |

<!-- cex:domain_contract:start -->
## Domain Contract -- Enforced Rules (real law from the generator)

> Source: `_tools/capability_generators/product_docs.py`'s `domain_contract()` -- read directly from the generator's own module constants (never re-typed by hand, never fabricated). Injected by `_tools/cex_bundle_deepen.py`; re-running regenerates this section idempotently.

**Contract Version**: 1.0.0

### Optional Sections
- faq
- referencia
- setup

### Section Labels
| Key | Value |
|-----|-------|
| setup | Setup |
| referencia | Referencia de campos |
| faq | FAQ |

### Audience Enum
| Key | Value |
|-----|-------|
| cliente_final | Tutor/cliente final -- sem conhecimento tecnico previo |
| suporte | Equipe de suporte tecnico (nivel 1 e 2) |
| revendedor | Revendedor autorizado -- instalacao e configuracao |
| integrador | Integrador de sistemas -- APIs e extensoes |

**Out Of Scope Statement**: Nao e manual de servico tecnico; para desmontagem/reparo avancado consultar o guia de revendedor ou contatar suporte autorizado

### Default Source Refs
- Manual do fabricante v1.0 (exemplo simulado)

### Source Confidence By Rank
- 0.95
- 0.88
- 0.72
- 0.6

### Source Reliability By Rank
- alta
- alta
- media
- baixa
<!-- cex:domain_contract:end -->
