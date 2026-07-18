---
id: p03_ins_prompt_template
kind: instruction
pillar: P03
version: 1.0.0
created: 2026-03-27
updated: 2026-03-27
author: instruction-builder
title: Prompt Template Builder Instructions
target: "agente prompt-template-builder"
phases_count: 4
prerequisites:
  - "A entrada descreve um prompt com ao menos um slot dinâmico (um valor que muda a cada invocação)"
  - "O motor de renderização de destino é conhecido ou inferível (mustache, bracket, jinja2, langchain, dspy)"
  - "O domínio do template é identificável (ex.: research, code, marketing, knowledge)"
validation_method: checklist
domain: prompt_template
quality: null
tags: [instruction, prompt-template, P03, parameterization, reusable]
idempotent: true
atomic: false
rollback: "Apagar o arquivo .md produzido. Sem efeitos colaterais -- templates são inertes até serem renderizados."
dependencies: []
logging: true
tldr: "Extrair os slots de variável, compor um template mustache reutilizável com frontmatter completo, validar os 8 HARD gates e então entregar."
8f: "F6_produce"
keywords: [prompt template builder instructions, extract variable slots, validate all, hard gates, then deliver, instruction, prompt-template, parameterization, reusable, "{{variable}}"]
density_score: 0.93
llm_function: REASON
related:
  - prompt-template-builder
  - bld_memory_prompt_template
---
## Contexto
Um **prompt_template** é um molde reutilizável: um corpo de prompt onde valores dinâmicos são representados como placeholders nomeados (`{{variable}}`). O mesmo template produz muitos prompts distintos ao substituir diferentes valores no momento da invocação. Este builder opera na camada de prompt -- acima das definições de identidade (system_prompt) e abaixo da execução ao vivo (P04).

**Entradas**
| Campo | Tipo | Descrição |
|---|---|---|
| `raw_prompt` | string | O prompt ou esboço de prompt fornecido por quem chama |
| `target_engine` | string | `mustache` (default) ou `bracket` (somente quando `{{}}` conflita com o sistema de destino) |
| `domain` | string | Área de assunto que o template atende (ex.: `code_review`, `summarization`, `research`) |
| `composable` | boolean | True se este template foi projetado para ser incorporado dentro de um template maior |

**Saída**
Um único arquivo `.md` em conformidade com SCHEMA.md e OUTPUT_TEMPLATE.md. Contém frontmatter YAML (16 campos) + 5 seções obrigatórias no corpo: Purpose, Variables Table, Template Body, Quality Gates, Examples.

**Regras de fronteira**
- Se a entrada não tem nenhum slot de variável -> é um `user_prompt` fixo, não um template. Rejeitar e explicar.
- Se a entrada define a identidade/persona de um agente -> é um `system_prompt`. Rotear para lá.
- Se a entrada gera ou aprimora outros prompts -> é um `meta_prompt`. Rotear para lá.

## Fases

### Fase 1: Analisar -- Extrair Variáveis
Varra o `raw_prompt` e identifique todo valor que vai diferir entre invocações.
```
FOR each token or phrase in raw_prompt:
  IF the value is domain-specific, caller-supplied, or context-dependent:
    mark as candidate variable
  ELSE (always the same regardless of invocation):
    mark as literal text
IF candidate_variables.count == 0:
  RETURN error: "No dynamic slots found. This is a fixed prompt, not a template."
FOR each candidate variable:
  name        <- snake_case descriptor (e.g. topic, audience, word_limit)
  type        <- string | list | integer | boolean | object
  required    <- true if omitting breaks the prompt; false otherwise
  default     <- concrete value for optional vars; null for required vars
  description <- one sentence stating the variable's purpose
variable_syntax:
  USE "mustache"  by default  ->  {{variable_name}}
  USE "bracket"   only when target system reserves {{ }} -> [VARIABLE_NAME]
composable:
  true  if this template will be embedded in a larger template
  false otherwise (default)
```
Entregável: registro de variáveis com name, type, required, default e description para cada slot.

### Fase 2: Classificar -- Checagem de Fronteira
Confirme que o artefato é `prompt_template` e não um kind irmão.
```
IF prompt defines agent role, values, or personality:
  RETURN "This is a system_prompt — route to system-prompt builder."
IF prompt is invoked once with no variable substitution:
  RETURN "This is a user_prompt — no template needed."
IF prompt's purpose is to generate or refine other prompts:
  RETURN "This is a meta_prompt — route to meta-prompt builder."
IF variables.count >= 1 AND body will be rendered repeatedly:
  PROCEED as prompt_template
```
Entregável: `kind: prompt_template` confirmado, com justificativa de uma linha.

### Fase 3: Compor -- Construir o Artefato
Monte o frontmatter e as 5 seções obrigatórias do corpo usando OUTPUT_TEMPLATE.md como guia estrutural.
```
ID generation:
  id = "p03_pt_" + topic_slug
  topic_slug: lowercase, underscores, describes template purpose
  pattern must match: ^p03_pt_[a-z][a-z0-9_]+$
Frontmatter (all 16 fields from SCHEMA.md):
  id, kind, pillar, title, version, created, updated, author,
  variables (list of objects), variable_syntax, composable,
  domain, quality (= null), tags, tldr, keywords, density_score
Body sections (in this order):
  ## Purpose
    One paragraph: what this template produces and its reuse scope.
  ## Variables Table
    Markdown table with columns: name | type | required | default | description
    One row per variable from Phase 1.
  ## Template Body
    Fenced code block containing the parameterized prompt text.
    Apply syntax: mustache -> {{variable_name}}, bracket -> [VARIABLE_NAME]
    Every variable from the table must appear at least once here.
    No hard-coded values where a variable slot was identified.
  ## Quality Gates
    Table: gate | status | notes
    Fill H01-H08 status as PASS or FAIL with one-line note each.
  ## Examples
    At least one filled example:
      - Variables block (yaml): concrete values for each variable
      - Rendered Output block: the actual prompt text after substitution
```
Entregável: arquivo `.md` completo, com frontmatter + 5 seções de corpo.

### Fase 4: Validar -- Checagem de Gates
Rode todos os quality gates antes de entregar.
```
HARD gates (all must pass — fix before delivering):
  H01: id matches ^p03_pt_[a-z][a-z0-9_]+$
  H02: all frontmatter required fields present (id, kind, title, variables, quality)
  H03: no `{{var}}` in template body that is absent from variables list
  H04: no variable in variables list that is absent from template body
  H05: file size <= 8192 bytes
  H06: variable_syntax is "mustache" or "bracket" (not mixed)
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt-template-builder]] | related | 0.48 |
| [[bld_knowledge_prompt_template]] | upstream | 0.47 |
| [[bld_orchestration_prompt_template]] | related | 0.47 |
| [[schema_prompt_template_builder]] | downstream | 0.45 |
| [[bld_memory_prompt_template]] | downstream | 0.39 |
