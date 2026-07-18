---
kind: knowledge_card
id: bld_knowledge_card_prompt_template
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for prompt_template production — atomic searchable facts
sources: prompt-template-builder MANIFEST.md + SCHEMA.md, LangChain, Mustache, Jinja2
quality: null
title: "Knowledge Card Prompt Template"
version: "1.0.0"
author: n03_builder
tags: [prompt_template, builder, examples]
tldr: "Golden and anti-examples for prompt template construction, demonstrating ideal structure and common pitfalls."
domain: "prompt template construction"
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
Prompt templates são moldes de texto parametrizados onde a estrutura fixa e o conteúdo dinâmico são separados por meio de slots tipados `{{variable}}` preenchidos no momento da invocação. O mesmo template produz N prompts distintos ao substituir diferentes valores de variável -- esse é o contrato central de reuso. Eles se diferenciam de system prompts (identidade fixa, sem slots), user prompts (tarefas únicas), few-shot examples (exemplos fixos) e meta-prompts (que geram outros prompts) por serem moldes reutilizáveis com slots de variável declarados e tipados.
## Tabela de Especificação
| Propriedade | Valor |
|----------|-------|
| Pilar | P03 (prompts) |
| Kind | `prompt_template` (literal exato) |
| Padrão de ID | `p03_pt_{slug}` |
| Frontmatter obrigatório | 14 campos |
| Gates de qualidade | 8 HARD + 10 SOFT |
| Corpo máximo | 4096 bytes |
| Densidade mínima | >= 0.80 |
| Campo quality | sempre `null` |
| Mínimo de variáveis | 1 (pelo menos um slot `{{variable}}`) |
| Ponto de injeção | `system` ou `user` |
| Sintaxe tier-1 | `{{variable}}` (compatível com Mustache) |
| Sintaxe tier-2 | `[VARIABLE]` (quando há conflito com Mustache) |
## Padrões
| Padrão | Aplicação |
|---------|-------------|
| Sintaxe uniforme | Tudo em {{}} Mustache OU tudo em [] colchetes -- nunca misturado no mesmo template |
| Variáveis tipadas | Declare o tipo (string, list, integer, boolean, object) para validação |
| Obrigatória vs opcional | Variáveis obrigatórias não têm default; opcionais carregam valor default |
| Ponto de injeção | Declare system ou user -- determina onde o template cai na conversa |
| Composabilidade | Template projetado para ser embutido em templates maiores via partials |
| Idempotência | O mesmo template + as mesmas variáveis DEVEM sempre produzir o mesmo prompt renderizado |
| Correspondência variável-corpo | Toda `{{variable}}` no corpo deve estar declarada na seção Variables |
| Pipeline de renderização | Template -> substituição de variáveis -> prompt renderizado -> chamada ao LLM |
## Anti-Padrões
| Anti-Padrão | Por que falha |
|-------------|-------------|
| Nenhuma `{{variable}}` no corpo | Não é um template -- é um prompt fixo |
| Variável não declarada no corpo | Variável presente no corpo mas ausente da seção Variables |
| Sintaxe mista ({{}} e []) | Inconsistente; ferramentas não conseguem extrair todas as variáveis de forma confiável |
| Conteúdo fixo em slots de variável | Slots devem ser apenas placeholders vazios |
| injection_point não declarado | O consumidor não sabe onde posicionar o texto renderizado |
| Variáveis sem restrições | Sem type/enum/regex, qualquer valor é aceito -- frágil |
| Template com efeitos colaterais | Templates devem ser transformação pura de texto, sem efeitos colaterais |
## Aplicação
1. Identifique o contrato de reuso: o que varia entre invocações?
2. Extraia as variáveis: nome, tipo, obrigatória/opcional, restrições
3. Escolha o tier de sintaxe: `{{variable}}` (tier-1) ou [VARIABLE] (tier-2)
4. Defina o injection_point: system ou user
5. Escreva o corpo do template com todos os slots de variável como placeholders vazios
6. Forneça ao menos um exemplo completo de invocação com todos os slots preenchidos
7. Declare o formato de saída (o que o template renderizado produz)
8. Valide: todas as variáveis do corpo declaradas, 8 gates HARD + 10 SOFT, corpo <= 4096 bytes
## Referências
- prompt-template-builder SCHEMA.md v1.0.0
- LangChain PromptTemplate / ChatPromptTemplate
- Especificação do Mustache (templates sem lógica)
- Documentação do motor de templates Jinja2

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_prompt_template]] | downstream | 0.57 |
| [[prompt-template-builder]] | downstream | 0.57 |
| [[bld_orchestration_prompt_template]] | downstream | 0.50 |
