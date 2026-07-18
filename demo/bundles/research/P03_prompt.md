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
2. Reúna as fontes: documentação oficial, URLs, referências de código ou conhecimento especialista já estabelecido
3. Extraia os fatos-chave -- pontos de dado concretos (números, datas, nomes, medidas), não opiniões ou afirmações vagas
4. Determine o tipo de KC:
   - domain_kc: conhecimento externo sobre uma ferramenta, API, protocolo ou domínio
   - meta_kc: padrão interno ou lição aprendida ao operar este sistema
5. Verifique os knowledge_cards existentes via brain_query [SE MCP] para o mesmo tópico -- evite duplicatas
6. Avalie a densidade de informação: é possível alcançar densidade >= 0.80 (tabelas, código, bullets concretos em vez de prosa de enchimento)?
## Fase 2: COMPOSIÇÃO
1. Leia o SCHEMA.md -- fonte da verdade para todos os campos de frontmatter e restrições de corpo
2. Leia o OUTPUT_TEMPLATE.md -- preencha o template seguindo exatamente as restrições do SCHEMA
3. Preencha o frontmatter: 14 campos obrigatórios + 5 campos estendidos do CEX (null é aceitável para campos recomendados)
4. Defina quality: null -- nunca se autopontue
5. Escreva o corpo seguindo a estrutura do tipo de KC:
   - domain_kc: Referência Rápida, Conceitos-Chave, Fases da Estratégia, Regras de Ouro, Fluxo, Comparativo, Referências
   - meta_kc: Resumo Executivo, Tabela de Especificação, Padrões, Anti-Padrões, Aplicação, Referências
6. Prefira formatos de alta densidade: tabelas e blocos de código em vez de parágrafos
7. Mantenha todo bullet com no máximo 80 caracteres
8. Inclua ao menos uma URL externa na seção de Referências
9. Escreva os axiomas no frontmatter como regras SEMPRE / NUNCA / SE-ENTÃO -- ao menos um é obrigatório
10. Mantenha o corpo entre 200 e 5120 bytes
## Fase 3: VALIDAÇÃO
1. Rode `python _tools/cex_compile.py <file>` se disponível -- esta é uma ferramenta automatizada ativa
2. Gates HARD (todos precisam passar):
   - O frontmatter YAML faz parse sem erros
   - id corresponde ao padrão `p01_kc_[a-z][a-z0-9_]+`
   - kind == knowledge_card
   - quality == null
   - densidade >= 0.80
   - ao menos 3 fatos concretos presentes (números, datas, entidades nomeadas)
   - o corpo está entre 200 e 5120 bytes
   - nenhum caminho interno no corpo (records/, .claude/, /home/)
   - nenhuma frase de enchimento ("this document covers", "as mentioned above")
3. Gates SOFT (pontue cada um contra o QUALITY_GATES.md):
   - o tldr contém dado concreto, não descrição genérica
   - os axiomas estão na forma SEMPRE / NUNCA / SE-ENTÃO
   - ao menos 4 seções com ao menos 3 linhas não vazias cada
   - keywords e long_tails presentes para busca
4. Confira os limites de escopo:
   - é um fato atômico e pesquisável, não uma visão geral ampla de domínio (context_doc)?
   - não é uma definição de termo (glossary_entry)?
   - não é um arquivo de configuração de embedding?
   - os fatos são concretos (números, datas, nomes) em vez de afirmações vagas?
5. Se um gate HARD falhar: corrija imediatamente e rode o validador de novo
6. Se a nota for < 8.0: expanda as seções rasas, substitua prosa por tabelas ou blocos de código, remova o enchimento

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_knowledge_card]] | upstream | 0.37 |
| [[knowledge-card-builder]] | upstream | 0.36 |
| p01_kc_knowledge_best_practices | upstream | 0.32 |
| [[bld_prompt_input_schema]] | sibling | 0.30 |
| [[bld_prompt_instruction]] | sibling | 0.28 |

<!-- cex:domain_contract:start -->
## Domain Contract -- Enforced Rules (real law from the generator)

> Source: `_tools/capability_generators/research.py`'s `domain_contract()` -- read directly from the generator's own module constants (never re-typed by hand, never fabricated). Injected by `_tools/cex_bundle_deepen.py`; re-running regenerates this section idempotently.

**Contract Version**: 1.0.0

### Scope Enum
- competitive
- market
- pricing
- trends

**Default Scope**: competitive

### Scope Dimensions
- **competitive**: Preco, Durabilidade, Avaliacoes, Frete/prazo, Pos-venda, Sazonalidade
- **market**: Demanda, Crescimento, Segmentos, Canais, Regulatorio, Sazonalidade
- **pricing**: Faixa de preco, Anchor, Elasticidade, Concorrencia, Margem tipica
- **trends**: Tendencia macro, Inovacao, Comportamento consumidor, Tech, Regulatorio

### Time Horizon Enum
- ultimos_30d
- ultimos_90d
- ultimos_12m

**Default Time Horizon**: ultimos_90d

### Horizon Days
| Key | Value |
|-----|-------|
| ultimos_30d | 30 |
| ultimos_90d | 90 |
| ultimos_12m | 365 |

### Depth Enum
- rapida
- padrao
- profunda

**Default Depth**: padrao

**Min Sources Per Claim Default**: 3

**Default Region**: Brasil

### Freshness Bands
| Label | Recency Factor | Days Upper Bound | Bound Type |
|-----|-----|-----|-----|
| GREEN (<90d) | 1.0 | 90 | exclusive |
| AMBER (90-365d) | 0.6 | 365 | inclusive |
| RED (>365d) | 0.2 | None | open_ended |

### Confidence Formula Weights
| Key | Value |
|-----|-------|
| source_count | 0.5 |
| agreement | 0.3 |
| recency | 0.2 |

### Veredito Gate Conditions
- Condicao 1 -- confianca: confianca_geral >= 0.70 (S1)
- Condicao 2 -- triangulacao: fontes por achado >= 3, exige credencial (S1)
- Condicao 3 -- frescor: dado mais antigo <= 365 dias (S3)
- Condicao 4 -- cobertura critica: nenhuma dimensao critica sem dado, exige credencial (S4)

**Downstream Chain**: research -> pesquisa_produto -> ads
<!-- cex:domain_contract:end -->
