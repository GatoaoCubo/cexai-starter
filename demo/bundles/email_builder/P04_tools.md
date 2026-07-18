---
id: tools_prompt_template_builder
kind: tools
pillar: P04
llm_function: CALL
domain: prompt_template
version: 1.0.0
created: "2026-03-26"
updated: "2026-03-26"
author: builder
tags:
  - "tools"
  - "prompt-template"
  - "P03"
  - "data-sources"
quality: null
title: "Tools Prompt Template"
tldr: "Exemplos-modelo e antiexemplos para a construção de prompt template, demonstrando a estrutura ideal e as armadilhas mais comuns."
8f: "F5_call"
keywords:
  - "tools prompt template"
  - "tools"
  - "prompt-template"
  - "data-sources"
  - "prompt_template"
  - "— source of truth for all field definitions -"
  - ". ### grep [fs] — active"
  - "tool registry"
  - "tool descriptions"
  - "data sources"
density_score: 0.90
related:
  - bld_tools_voice_pipeline
  - bld_tools_collaboration_pattern
  - bld_tools_action_paradigm
  - bld_tools_thinking_config
  - bld_tools_naming_rule
---

# Ferramentas -- prompt-template-builder

## Registro de Ferramentas
| Ferramenta | Status | Tag | Propósito |
|---|---|---|---|
| brain_query | CONDICIONAL | [MCP] | Descobrir templates existentes e padrões de variável |
| Read | ATIVA | [FS] | Ler SCHEMA.md, OUTPUT_TEMPLATE.md, exemplos irmãos |
| Glob | ATIVA | [FS] | Encontrar arquivos p03_pt_* existentes no pool |
| Grep | ATIVA | [FS] | Buscar colisões de nome de variável ou reuso de padrão |
| Write | ATIVA | [FS] | Produzir o artefato prompt_template final |
| Edit | ATIVA | [FS] | Corrigir frontmatter ou corpo do template durante a fase VALIDATE |

## Descrições das Ferramentas

### brain_query [MCP] -- CONDICIONAL
Disponível apenas quando o servidor Brain MCP está em execução. Use para:
- Encontrar artefatos `prompt_template` existentes que se sobrepõem ao tópico solicitado
- Recuperar convenções de nomenclatura de variável usadas no pool
- Identificar partials composáveis que poderiam ser referenciados
```
brain_query("prompt template {{topic}} variables")
brain_query("P03 kind:prompt_template domain:{{domain}}")
brain_query("reusable mold {{keyword}} CEX")
```
Trate os resultados como consultivos -- não copie e cole nomes de variável sem validar os tipos.

### Read [FS] -- ATIVA
Ler antes de compor:
- `SCHEMA.md` -- fonte de verdade para todas as definições de campo
- `OUTPUT_TEMPLATE.md` -- estrutura exata de frontmatter e corpo a seguir
- `QUALITY_GATES.md` -- lista de gates para validar
- Arquivos irmãos p03_pt_* como referência de nomenclatura e estilo

### Glob [FS] -- ATIVA
```
artifacts/**/p03_pt_*.md
archetypes/builders/prompt-template-builder/
```
Use para checar colisões de ID antes de atribuir um novo `id`.

### Grep [FS] -- ATIVA
```
grep pattern: "{{variable_name}}"  -- checar se um nome de variável já está padronizado
grep pattern: "kind: prompt_template" -- inventariar templates existentes
```

### Write [FS] -- ATIVA
Ferramenta de entrega final. Escreva o artefato concluído no caminho de destino, sob `artifacts/` ou no caminho de saída especificado por quem chama.

### Edit [FS] -- ATIVA
Use durante a fase VALIDATE para corrigir campos específicos (pontuação de qualidade, data de updated, defaults de variável) sem reescrever o arquivo inteiro.

## Fontes de Dados
| Fonte | Conteúdo | Quando usar |
|---|---|---|
| SCHEMA.md | Definições de campo, padrão de ID, constraints | Toda execução de produção |
| OUTPUT_TEMPLATE.md | Estrutura exata de frontmatter + corpo | Toda execução de produção |
| QUALITY_GATES.md | H01-H08 HARD, S01-S10 SOFT | Toda execução de validação |
| KNOWLEDGE.md | Implementações da indústria, tiers de sintaxe | Ao escolher o variable_syntax |
| MEMORY.md | Erros comuns, antipadrões | Quando travado ou produzindo uma variante |
| pool de arquivos p03_pt_* | Exemplos de referência | Quando houver dúvida sobre o estilo |

## Permissões de Ferramenta

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDAS | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitidas |
| NEGADAS | (nenhuma) | Explicitamente bloqueadas |
| EFETIVAS | Bash, Edit, Glob, Grep, Read, Write | PERMITIDAS menos NEGADAS |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_tools_voice_pipeline | sibling | 0.61 |
| bld_tools_collaboration_pattern | sibling | 0.58 |
| bld_tools_action_paradigm | sibling | 0.57 |
| bld_tools_thinking_config | sibling | 0.56 |
| bld_tools_naming_rule | sibling | 0.53 |
