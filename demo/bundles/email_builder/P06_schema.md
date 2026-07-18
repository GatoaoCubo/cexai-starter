---
id: schema_prompt_template_builder
kind: type_def
pillar: P06
llm_function: CONSTRAIN
domain: prompt_template
version: 1.0.0
created: "2026-03-26"
updated: "2026-07-04"
author: builder
tags:
  - "schema"
  - "prompt-template"
  - "P03"
  - "source-of-truth"
quality: null
title: "Schema Prompt Template"
tldr: "Exemplos-modelo e antiexemplos para a construção de prompt template, demonstrando a estrutura ideal e as armadilhas mais comuns."
8f: "F1_constrain"
keywords:
  - "schema prompt template"
  - "schema"
  - "prompt-template"
  - "source-of-truth"
  - "^p03_pt_[a-z][a-z0-9_]+$"
  - "examples:"
  - "| | pillar | enum | yes | — | fixed value:"
  - "frontmatter fields"
  - "variable object"
  - "variable object each"
density_score: 0.90
related:
  - bld_schema_reranker_config
  - bld_schema_benchmark_suite
  - bld_schema_integration_guide
  - bld_schema_sandbox_spec
  - bld_schema_dataset_card
---

# Schema -- prompt-template-builder
> FONTE DE VERDADE. Todos os campos deste arquivo DEVEM aparecer em OUTPUT_TEMPLATE.md. Zero divergência permitida.

## Padrão de ID
Regex: `^p03_pt_[a-z][a-z0-9_]+$`
Regra: o id DEVE ser igual ao stem (nome sem extensão) do arquivo.
Exemplos: `p03_pt_knowledge_card`, `p03_pt_research_synthesis`, `p03_pt_code_review`

> **Status: ENFORCED-AO-VIVO para novos builds 8F (corrigido em 2026-07-04 -- um judge
> refutou por execução a alegação de que o gate estava dormente, e o N07 reproduziu o
> resultado).** O H02 em `_tools/cex_8f_runner.py` extrai a linha de Regex marcada com
> crase nesta seção (extração em ~503-511) e dispara em toda execução 8F deste kind. A
> via `id_pattern` do `_schema.yaml` permanece dormente -- são duas vias, só esta está
> ativa. CONSEQUÊNCIA: vale para todo build NOVO; o corpus anterior a 2026-07-04 estava
> ~55% não conforme (o pior entre os 3 kinds revisados -- benchmark 33%, guardrail 50%)
> -- a varredura de renomeação de id do register R-263 fechou essa lacuna. Evidência:
> nota H02 em `.claude/rules/8f-reasoning.md`; SPEC_R259 Seções 1 + 8.

> **Exceção: corpus derivado de cybersec.** 81 arquivos prompt_template (`N05_operations/
> cybersec/` 77 + `cybersec_distilled/` 4) são pesquisa derivada externamente, com
> nomenclatura própria -- mesmo precedente da contabilidade de hidratação
> (`N05_CYBERSEC_EXEMPT_PREFIXES`, `docs/HYDRATION_MAP.md` Seç. 2). Nunca reconstruídos
> via 8F, então o H02 nunca dispara sobre eles. O R-263 os mantém EXEMPT-DOCUMENTADOS, não
> renomeados -- a varredura cobriu apenas o corpus CORE escrito à mão/de genesis (59
> arquivos, menos 6 retidos para uma decisão de correção de kind sobre o cluster de ISO de
> builder `bld_output_*`).

## Campos do Frontmatter
> Tiering (R-262 sub-lane a, 2026-07-04, método = R-259): população >= 85% entre 150
> artefatos `prompt_template` confirmados em disco -> SIM/enforced (conectado ao
> `frontmatter_required` do `_schema.yaml`); < 85% -> REC, a menos que um consumidor
> comprovado por grep sobreponha essa regra. (n=150, não 139 -- greps ingênuos perdem
> `.cex/` (diretório oculto) + `_courses/` (gitignored, 11 arquivos force-tracked);
> `git ls-files` é a fonte autoritativa -- mesma classe de ponto cego do ancoramento CRLF
> do R-259 e das pegadinhas de arquivo não commitado do R-260.) `title`/`variables` eram
> antes SIM, rebaixados para REC com população de 50,0% / 11,3%. Veja
> `docs/PROJECT_BACKLOG.md` R-262 (sub-lane a) + `docs/SPEC_R259_SCHEMA_PRACTICE_
> RECONCILIATION_2026_07_04.md`.

| Campo | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| id | string | SIM | — | Identificador único. Deve corresponder ao padrão de ID acima |
| kind | enum | SIM | — | Valor fixo: `prompt_template` |
| pillar | enum | SIM | — | Valor fixo: `P03` |
| version | string | SIM | `"1.0.0"` | String semver |
| created | string | SIM | — | Data ISO: YYYY-MM-DD |
| quality | float ou null | SIM | `null` | Pontuação do gate 0.0-1.0; null até a primeira validação |
| tags | list[string] | SIM | `[]` | Tags de pesquisabilidade |
| tldr | string | SIM | — | Resumo de uma frase para descoberta |
| title | string | REC | — | Nome legível do template (50,0% de população; 98,4% entre os artefatos escritos à mão/de curso/de genesis (CORE, n=62) -- a baixa população geral está concentrada em um único lote gerador derivado de cybersec com 77 arquivos, ver dissenso do R-262 (sub-lane a)) |
| updated | string | REC | — | Data ISO: YYYY-MM-DD, atualizada a cada mudança (48,7% de população; 95,2% CORE) |
| author | string | REC | — | Agent_group ou ID de autor humano (44,0% de população; 96,8% CORE) |
| variables | list[object] | REC | — | Lista de definições de variável (ver Objeto de Variável abaixo) (11,3% de população; 27,4% CORE -- baixa mesmo entre artefatos escritos à mão) |
| variable_syntax | enum | REC | `"mustache"` | `"mustache"` ou `"bracket"` (11,3% de população; 27,4% CORE) |
| composable | boolean | REC | `false` | True se o template foi projetado para ser incorporado em templates maiores (12,7% de população; 30,6% CORE) |
| domain | string | REC | — | Domínio semântico: research, marketing, knowledge, code, etc. (39,3% de população; 82,3% CORE -- logo abaixo do limiar de 85% mesmo excluindo o cluster de cybersec; evidência de consumidor também fraca/indireta, mesma ambiguidade que o R-259 encontrou para o `domain` do benchmark) |
| keywords | list[string] | REC | `[]` | Palavras-chave de busca, distintas das tags |
| density_score | float | REC | `null` | Densidade de conteúdo 0.0-1.0; null até ser medida |

## Objeto de Variável
Cada item da lista `variables` DEVE conter:
| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| name | string | SIM | Nome da variável, correspondendo ao slot no corpo do template |
| type | enum | SIM | `string`, `list`, `integer`, `boolean`, `object` |
| required | boolean | SIM | Se a variável deve ser fornecida no momento da renderização |
| default | any ou null | SIM | Valor default; null para variáveis obrigatórias |
| description | string | SIM | Uma frase descrevendo o propósito da variável |

## Estrutura do Corpo
Todo artefato `prompt_template` DEVE conter estas 5 seções, nesta ordem:
1. `## Purpose` -- um parágrafo descrevendo o que o template produz e seu escopo de reuso
2. `## Variables Table` -- tabela markdown listando todas as variáveis com os 5 campos do objeto
3. `## Template Body` -- o texto do prompt parametrizado em um bloco de código fenced
4. `## Quality Gates` -- tabela mostrando o status dos gates H01-H08 para este artefato
5. `## Examples` -- ao menos um exemplo preenchido, com valores de variável e a saída renderizada

## Constraints
| Constraint | Regra |
|---|---|
| max_bytes | 8192 bytes por arquivo |
| variable_syntax | `mustache` é tier-1 (`{{var}}`); `bracket` é tier-2 (`[VAR]`) -- use bracket somente quando o Mustache conflitar com o sistema de destino |
| completude do corpo | Toda `{{var}}` no corpo DEVE estar declarada em `variables`. Toda variável declarada DEVE aparecer no corpo ao menos uma vez |
| unicidade de id | Nenhum outro artefato prompt_template pode compartilhar o mesmo id |
| trava de kind | O campo `kind` DEVE ser `prompt_template` -- nunca sobrescrito |
| quality null | `quality: null` é válido para artefatos em rascunho; deve virar um float antes da submissão ao pool |

## Valores de Enum
### variable_syntax
- `mustache` -- sintaxe `{{variable}}` (Mustache, Handlebars, compatível com Anthropic)
- `bracket` -- sintaxe `[VARIABLE]` (fallback para sistemas onde `{{}}` é reservado)

### variable.type
- `string` -- texto simples
- `list` -- array de itens
- `integer` -- número inteiro
- `boolean` -- true/false
- `object` -- dados estruturados chave-valor

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_reranker_config | related | 0.56 |
| bld_schema_benchmark_suite | related | 0.55 |
| bld_schema_integration_guide | related | 0.54 |
| bld_schema_sandbox_spec | related | 0.53 |
| [[bld_schema_dataset_card]] | related | 0.53 |
