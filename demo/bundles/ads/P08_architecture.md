---
kind: architecture
id: bld_architecture_prompt_template
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of prompt_template — inventory, dependencies, and architectural position
quality: null
title: "Architecture Prompt Template"
version: "1.0.0"
author: n03_builder
tags: [prompt_template, builder, examples]
tldr: "Golden and anti-examples for prompt template construction, demonstrating ideal structure and common pitfalls."
domain: "prompt template construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [component map of prompt_template, and architectural position, prompt template construction, architecture prompt template, prompt_template, builder, examples, "{{variable}}", component inventory, dependency graph]
density_score: 0.90
related:
  - prompt-template-builder
  - bld_memory_prompt_template
---
# Arquitetura: prompt_template no CEX
## Inventário de Componentes
| Nome | Papel | Dono | Status |
|------|------|-------|--------|
| bloco de frontmatter | Cabeçalho de metadados (id, kind, pillar, domain, variables, syntax_tier, etc.) | prompt-template-builder | ativo |
| variable_declarations | Slots de variável tipados, com nomes, tipos, defaults e descrições | author | ativo |
| template_body | Texto parametrizado com placeholders `{{variable}}` ou [VAR] | author | ativo |
| syntax_tier | Nível de sintaxe de interpolação (tier-1 Mustache, tier-2 bracket) | author | ativo |
| rendering_context | Contexto de runtime necessário para preencher as variáveis (fontes de dados, APIs) | author | ativo |
| example_fills | Preenchimentos concretos de variável demonstrando uso válido do template | author | ativo |
## Grafo de Dependências
```
type_def        --produces-->  prompt_template  --consumed_by-->  renderer
knowledge_card  --produces-->  prompt_template  --produces-->     filled_prompt
prompt_template --signals-->   render_error
```
| De | Para | Tipo | Dado |
|------|----|------|------|
| type_def (P06) | prompt_template | data_flow | definições de tipo para restrições de variável |
| knowledge_card (P01) | prompt_template | data_flow | fatos de domínio injetados como valores de variável |
| prompt_template | renderer (LangChain/DSPy/Mustache) | consumes | template consumido pelo motor de renderização |
| prompt_template | filled_prompt | produces | prompt concreto após a substituição de variáveis |
| prompt_template | render_error (P12) | signals | emitido quando o preenchimento de variável falha na validação |
| system_prompt (P03) | prompt_template | dependency | a identidade do sistema pode restringir o escopo do template |
## Tabela de Fronteira
| prompt_template É | prompt_template NÃO É |
|--------------------|------------------------|
| Um molde reutilizável com slots `{{variable}}` para múltiplas invocações | Uma instrução de tarefa única (action_prompt P03) |
| Estrutura separada do conteúdo via parametrização | Uma definição de identidade de sistema fixa (system_prompt P03) |
| Renderizado por motores LangChain, DSPy, Mustache ou Jinja2 | Uma receita passo a passo sem variáveis (instruction P03) |
| Tipado por variável, com defaults e restrições de validação | Uma mensagem de usuário bruta, sem estrutura |
| Invocado múltiplas vezes com diferentes preenchimentos de variável | Um prompt de uso único, descartado após a execução |
| Produz prompts preenchidos -- não respostas diretas do LLM | Um meta-prompt que gera outros prompts |
## Mapa de Camadas
| Camada | Componentes | Propósito |
|-------|------------|---------|
| Tipos | type_def | Fornece definições de tipo para restrições de variável |
| Definição | frontmatter, variable_declarations, syntax_tier | Especifica a identidade do template e os slots de variável |
| Template | template_body, example_fills | O texto parametrizado e os exemplos de uso |
| Renderização | rendering_context, renderer | Preenchimento em runtime e execução do motor de template |
| Saída | filled_prompt, render_error | Prompt concreto produzido ou erro sinalizado |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt-template-builder]] | upstream | 0.53 |
| [[bld_knowledge_prompt_template]] | upstream | 0.50 |
| [[bld_memory_prompt_template]] | downstream | 0.49 |
| [[bld_orchestration_prompt_template]] | upstream | 0.42 |
