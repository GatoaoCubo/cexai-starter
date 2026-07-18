---
id: config_prompt_template_builder
kind: config
pillar: P09
llm_function: CONSTRAIN
domain: prompt_template
version: 1.0.0
created: "2026-03-26"
updated: "2026-03-26"
author: builder
tags: [config, prompt-template, P03, naming, constraints]
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Prompt Template"
tldr: "Exemplos-modelo e antiexemplos para a construção de prompt template, demonstrando a estrutura ideal e as armadilhas mais comuns."
8f: "F1_constrain"
keywords: [config prompt template, config, prompt-template, naming, constraints, "p03_pt_{topic_slug}.md", "{topic_slug}", p03_pt_knowledge_card_production.md, p03_pt_research_synthesis.md, p03_pt_code_review_checklist.md]
density_score: 0.90
related:
  - bld_memory_prompt_template
  - prompt-template-builder
---
# Config -- prompt-template-builder

## Convenção de Nomenclatura
**Padrão**: `p03_pt_{topic_slug}.md`
| Componente | Regra |
|---|---|
| `p03` | Prefixo de pillar -- sempre P03 para a camada de prompt |
| `pt` | Abreviação de kind -- sempre `pt` para prompt_template |
| `{topic_slug}` | Minúsculo, com underscore, 2-5 palavras descrevendo o propósito do template |
| `.md` | Sempre markdown |

**Exemplos válidos**:
- `p03_pt_knowledge_card_production.md`
- `p03_pt_research_synthesis.md`
- `p03_pt_code_review_checklist.md`
- `p03_pt_marketing_copy_generator.md`

**Exemplos inválidos**:
- `prompt_template_knowledge.md` -- falta o prefixo de pillar
- `p03_knowledge_card.md` -- falta a abreviação de kind `pt`
- `p03_pt_KnowledgeCard.md` -- maiúsculas não permitidas
- `p03_pt_k.md` -- topic_slug curto demais (mínimo 2 caracteres após pt_)

## Caminhos de Arquivo
| Contexto | Caminho |
|---|---|
| Artefatos do pool | `artifacts/prompts/p03_pt_{topic_slug}.md` |
| Rascunho / WIP | `artifacts/drafts/p03_pt_{topic_slug}.md` |
| Referência do builder | `archetypes/builders/prompt-template-builder/` |

## Limites de Tamanho
| Limite | Valor | Escopo |
|---|---|---|
| max_bytes | 8192 | Por arquivo de artefato |
| max_variables | 20 | Por template (limite prático; sem teto rígido no schema) |
| max_body_lines | 80 | Recomendado; mantém os templates fáceis de escanear |
| min_variables | 1 | Um template com zero variáveis é um user_prompt, não um template |

## Regras de Sintaxe de Variável
### Tier-1: Mustache (default)
```
{{variable_name}}
```
Use para: todos os templates novos. Compatível com Mustache, Handlebars, bibliotecas de prompt da Anthropic e a maioria dos renderizadores do CEX.

**Blocos condicionais** (Mustache):
```
{{#boolean_var}}
  Content shown when boolean_var is true
{{/boolean_var}}
```
**Iteração de lista** (Mustache):
```
{{#items}}
  - {{.}}
{{/items}}
```

### Tier-2: Bracket (fallback)
```
[VARIABLE_NAME]
```
Use para: templates que visam sistemas onde `{{}}` é sintaxe reservada (ex.: templates Vue.js, alguns shell scripts, templates HTML do Go).

### Misturando Tiers
NUNCA misture a sintaxe tier-1 e tier-2 no mesmo template. Defina `variable_syntax` como `mustache` ou `bracket` e use exclusivamente essa opção.

## Regras de Incremento de Versão
| Tipo de mudança | Incremento de versão |
|---|---|
| Adicionar nova variável opcional | patch (1.0.0 -> 1.0.1) |
| Adicionar nova variável obrigatória | minor (1.0.0 -> 1.1.0) |
| Remover ou renomear variável | major (1.0.0 -> 2.0.0) |
| Mudar a estrutura do corpo do template | minor (1.0.0 -> 1.1.0) |
| Corrigir erro de digitação ou formatação | patch (1.0.0 -> 1.0.1) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_prompt_template]] | downstream | 0.40 |
| [[bld_knowledge_prompt_template]] | upstream | 0.38 |
| [[prompt-template-builder]] | upstream | 0.36 |
| [[bld_orchestration_prompt_template]] | upstream | 0.36 |
