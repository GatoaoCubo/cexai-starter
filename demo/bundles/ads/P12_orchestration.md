---
kind: collaboration
id: bld_collaboration_prompt_template
pillar: P03
llm_function: COLLABORATE
purpose: How prompt-template-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Prompt Template"
version: "1.0.0"
author: n03_builder
tags: [prompt_template, builder, examples]
tldr: "Golden and anti-examples for prompt template construction, demonstrating ideal structure and common pitfalls."
domain: "prompt template construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords: [prompt template construction, collaboration prompt template, prompt_template, builder, examples, "{{variables}}", "### crew: rag-augmented prompt pipeline", "### crew: few-shot template pack", my role, crew compositions]
density_score: 0.90
related:
  - prompt-template-builder
---
# Colaboração: prompt-template-builder
## Meu Papel nas Equipes
Eu sou um ESPECIALISTA. Eu respondo a UMA pergunta: "qual é o molde reutilizável que gera este prompt quando preenchido?"
Eu produzo templates parametrizados com `{{variables}}` -- não prompts fixos, não identidades, não instruções sem slots de variável.
## Composições de Equipe
### Equipe: "Agent Prompt Stack"
```
  1. system-prompt-builder    -> "fixed identity and persona for the agent"
  2. prompt-template-builder  -> "reusable mold with {{variables}} for dynamic invocations"
  3. response-format-builder  -> "output structure spec injected into the prompt"
```
### Equipe: "RAG-Augmented Prompt Pipeline"
```
  1. rag-source-builder       -> "external sources to pull context from at runtime"
  2. context-doc-builder      -> "domain context injected into the template"
  3. prompt-template-builder  -> "template with {{context}} and {{query}} slots"
  4. quality-gate-builder     -> "gates that validate the template before deployment"
```
### Equipe: "Few-Shot Template Pack"
```
  1. few-shot-example-builder -> "concrete examples embedded in the template body"
  2. prompt-template-builder  -> "template wrapping examples with {{input}} slot"
  3. validation-schema-builder -> "schema validating filled-template outputs post-generation"
```
## Protocolo de Handoff
### Eu Recebo
- seeds: domínio da tarefa, nomes de variável, propósito do prompt, framework alvo (LangChain/DSPy/Mustache/Jinja2)
- opcional: exemplos few-shot, conteúdo de context doc, identidade de system prompt, spec de response format, schema de type-def
### Eu Produzo
- artefato prompt_template (frontmatter YAML + corpo Mustache/bracket, max 4096 bytes)
- commitado em: `cex/P03/examples/p03_pt_{name}.md`
### Eu Sinalizo
- signal: complete (com nota de qualidade vinda do QUALITY_GATES)
- se quality < 8.0: signal retry com os motivos da falha
## Builders dos Quais Eu Dependo
- type-def-builder: fornece schemas de variável tipados que mapeiam para slots `{{variable}}`
- few-shot-example-builder: fornece exemplos embutidos no corpo do template
- context-doc-builder: fornece contexto de domínio injetado como slot do template
## Builders Que Dependem de Mim
| Builder | Por que |
|---------|-----|
| system-prompt-builder | Pode embutir slots de template dentro de system prompts para identidade dinâmica |
| quality-gate-builder | Gates referenciam a estrutura do template para validar os gates hard H01-H08 |
| response-format-builder | O response format é frequentemente injetado como uma variável dentro do template |
| agent-package-builder | Empacota o template junto com seus irmãos em uma unidade implantável |
| knowledge-card-builder | Usa as saídas renderizadas do template como prompts para produção de cards |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_response_format]] | sibling | 0.41 |
| [[bld_orchestration_action_prompt]] | sibling | 0.41 |
| [[prompt-template-builder]] | related | 0.39 |
| [[bld_orchestration_prompt_version]] | sibling | 0.39 |
| [[bld_orchestration_few_shot_example]] | sibling | 0.36 |
