---
kind: collaboration
id: bld_collaboration_prompt_template
pillar: P03
llm_function: COLLABORATE
purpose: Como o prompt-template-builder trabalha em crews com outros builders
pattern: cada builder deve conhecer seu PAPEL em uma equipe, o que RECEBE e o que PRODUZ
quality: null
title: "Collaboration Prompt Template"
version: "1.0.0"
author: n03_builder
tags: [prompt_template, builder, examples]
tldr: "Exemplos-modelo e antiexemplos para a construção de prompt template, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de prompt template"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords: [prompt template construction, collaboration prompt template, prompt_template, builder, examples, "{{variables}}", "### crew: rag-augmented prompt pipeline", "### crew: few-shot template pack", my role, crew compositions]
density_score: 0.90
related:
  - prompt-template-builder
---
# Collaboration: prompt-template-builder

## Meu Papel em Crews
Eu sou um ESPECIALISTA. Respondo a UMA pergunta: "qual é o molde reutilizável que gera este prompt quando preenchido?"
Eu produzo templates parametrizados com `{{variables}}` -- não prompts fixos, não identidades, não instructions sem slots de variável.

## Composições de Crew

### Crew: "Agent Prompt Stack"
```
  1. system-prompt-builder    -> "fixed identity and persona for the agent"
  2. prompt-template-builder  -> "reusable mold with {{variables}} for dynamic invocations"
  3. response-format-builder  -> "output structure spec injected into the prompt"
```

### Crew: "RAG-Augmented Prompt Pipeline"
```
  1. rag-source-builder       -> "external sources to pull context from at runtime"
  2. context-doc-builder      -> "domain context injected into the template"
  3. prompt-template-builder  -> "template with {{context}} and {{query}} slots"
  4. quality-gate-builder     -> "gates that validate the template before deployment"
```

### Crew: "Few-Shot Template Pack"
```
  1. few-shot-example-builder -> "concrete examples embedded in the template body"
  2. prompt-template-builder  -> "template wrapping examples with {{input}} slot"
  3. validation-schema-builder -> "schema validating filled-template outputs post-generation"
```

## Protocolo de Handoff

### Eu Recebo
- seeds: domínio da tarefa, nomes de variável, propósito do prompt, framework de destino (LangChain/DSPy/Mustache/Jinja2)
- opcional: few-shot examples, conteúdo de context doc, identidade de system prompt, spec de response format, schema de type-def

### Eu Produzo
- artefato prompt_template (frontmatter YAML + corpo Mustache/bracket, máx. 4096 bytes)
- commitado em: `cex/P03/examples/p03_pt_{name}.md`

### Eu Sinalizo
- signal: complete (com a pontuação de qualidade vinda de QUALITY_GATES)
- se quality < 8.0: signal de retry com os motivos da falha

## Builders dos Quais Dependo
- type-def-builder: fornece schemas de variável tipados que mapeiam para os slots `{{variable}}`
- few-shot-example-builder: fornece exemplos embutidos no corpo do template
- context-doc-builder: fornece o contexto de domínio injetado como um slot do template

## Builders Que Dependem de Mim
| Builder | Por quê |
|---------|-----|
| system-prompt-builder | Pode embutir slots de template dentro de system prompts para identidade dinâmica |
| quality-gate-builder | Os gates referenciam a estrutura do template para validar os hard gates H01-H08 |
| response-format-builder | O response format costuma ser injetado como uma variável dentro do template |
| agent-package-builder | Empacota o template junto com seus irmãos em uma unidade implantável |
| knowledge-card-builder | Usa as saídas de template renderizadas como prompts para a produção de cards |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_response_format]] | sibling | 0.41 |
| [[bld_orchestration_action_prompt]] | sibling | 0.41 |
| [[prompt-template-builder]] | related | 0.39 |
| [[bld_orchestration_prompt_version]] | sibling | 0.39 |
| [[bld_orchestration_few_shot_example]] | sibling | 0.36 |
