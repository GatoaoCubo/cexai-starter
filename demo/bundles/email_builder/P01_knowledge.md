---
kind: knowledge_card
id: bld_knowledge_card_prompt_template
pillar: P01
llm_function: INJECT
purpose: Conhecimento de dominio para a producao de prompt_template -- fatos atomicos e pesquisaveis
sources: prompt-template-builder MANIFEST.md + SCHEMA.md, LangChain, Mustache, Jinja2
quality: null
title: "Knowledge Card Prompt Template"
version: "1.0.0"
author: n03_builder
tags: [prompt_template, builder, examples]
tldr: "Exemplos-modelo e antiexemplos para a construção de prompt template, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de prompt template"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords: [atomic searchable facts, prompt template construction, knowledge card prompt template, prompt_template, builder, examples, "{{variable}}", "p03_pt_{slug}", user, [variable]]
density_score: 0.90
related:
  - bld_memory_prompt_template
  - prompt-template-builder
---
# Conhecimento de Domínio: prompt_template

## Resumo Executivo
Prompt templates são moldes de texto parametrizados nos quais a estrutura fixa e o conteúdo dinâmico são separados por meio de slots tipados `{{variable}}` preenchidos no momento da invocação. O mesmo template produz N prompts distintos ao substituir diferentes valores de variável -- esse é o contrato de reuso central. Eles se diferenciam de system prompts (identidade fixa, sem slots), user prompts (tarefas de uso único), few-shot examples (exemplos fixos) e meta-prompts (que geram outros prompts) por serem moldes reutilizáveis com slots de variável declarados e tipados.

## Tabela de Especificação
| Propriedade | Valor |
|----------|-------|
| Pillar | P03 (prompts) |
| Kind | `prompt_template` (literal exato) |
| Padrão de ID | `p03_pt_{slug}` |
| Frontmatter obrigatório | 14 campos |
| Quality gates | 8 HARD + 10 SOFT |
| Corpo máximo | 4096 bytes |
| Densidade mínima | >= 0.80 |
| Campo quality | sempre `null` |
| Mínimo de variáveis | 1 (ao menos um slot `{{variable}}`) |
| Ponto de injeção | `system` ou `user` |
| Sintaxe Tier-1 | `{{variable}}` (compatível com Mustache) |
| Sintaxe Tier-2 | `[VARIABLE]` (quando há conflito com Mustache) |

## Padrões
| Padrão | Aplicação |
|---------|-------------|
| Sintaxe uniforme | Todo {{}} Mustache OU todo [] bracket -- nunca misturados em um mesmo template |
| Variáveis tipadas | Declarar o tipo (string, list, integer, boolean, object) para validação |
| Obrigatório vs opcional | Variáveis obrigatórias não têm default; opcionais carregam um valor default |
| Ponto de injeção | Declarar system ou user -- determina onde o template se encaixa na conversa |
| Composabilidade | Template projetado para ser incorporado em templates maiores via partials |
| Idempotência | O mesmo template + as mesmas variáveis DEVEM sempre produzir o mesmo prompt renderizado |
| Correspondência variável-corpo | Toda `{{variable}}` no corpo deve estar declarada na seção Variables |
| Pipeline de renderização | Template -> substituição de variável -> prompt renderizado -> chamada ao LLM |

## Antipadrões
| Antipadrão | Por que falha |
|-------------|-------------|
| Nenhuma `{{variable}}` no corpo | Não é um template -- é um prompt fixo |
| Variável não declarada no corpo | Variável presente no corpo mas ausente da seção Variables |
| Sintaxe mista ({{}} e []) | Inconsistente; ferramentas não conseguem extrair todas as variáveis com confiança |
| Conteúdo fixo em slots de variável | Slots devem ser apenas placeholders vazios |
| injection_point não declarado | O consumidor não sabe onde posicionar o texto renderizado |
| Variáveis sem constraints | Sem type/enum/regex, qualquer valor é aceito -- frágil |
| Template com efeitos colaterais | Templates devem ser transformação pura de texto, sem efeitos colaterais |

## Aplicação
1. Identifique o contrato de reuso: o que varia entre invocações?
2. Extraia as variáveis: nome, tipo, obrigatória/opcional, constraints
3. Escolha o tier de sintaxe: `{{variable}}` (tier-1) ou [VARIABLE] (tier-2)
4. Defina o injection_point: system ou user
5. Escreva o corpo do template com todos os slots de variável como placeholders vazios
6. Forneça ao menos um exemplo de invocação completo com todos os slots preenchidos
7. Declare o formato de saída (o que o template renderizado produz)
8. Valide: todas as variáveis do corpo declaradas, 8 HARD + 10 SOFT gates, corpo <= 4096 bytes

## Referências
- prompt-template-builder SCHEMA.md v1.0.0
- LangChain PromptTemplate / ChatPromptTemplate
- Especificação Mustache (templates logic-less)
- Documentação do motor de templates Jinja2

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_prompt_template]] | downstream | 0.57 |
| [[prompt-template-builder]] | downstream | 0.57 |
| [[bld_orchestration_prompt_template]] | downstream | 0.50 |
