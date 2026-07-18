---
id: p11_fb_knowledge_card
kind: builder_default
pillar: P11
title: "Feedback: Knowledge Card"
domain: knowledge_card
version: 1.1.0
quality: null
tags: [feedback, anti-patterns, P11, knowledge_card]
8f: "F7_govern"
keywords: [knowledge card, regras never, modos de falha, correção passo a passo, feedback, antipadrões, knowledge_card, modos de falha comuns, modo de falha, protocolo de correção]
tldr: "Antipadrões e protocolo de correção para builders de knowledge card. 6 regras NEVER + 4 modos de falha + correção em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - p11_fb__builder
  - p11_fb_quality_gate
  - p11_fb_model_card
  - p11_fb_agent_card
  - p11_fb_prompt_template
  - p11_fb_kind
  - p11_fb_context_map
  - p11_fb_validation_schema
  - p11_fb_input_schema
  - p11_fb_path_config
---
# Feedback: Knowledge Card

## Antipadrões (NUNCA faça)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribua nota de qualidade à própria saída | H01 |
| Sem alucinação | Cite fontes; sem fatos, métricas, ou referências inventadas | H03 |
| Código somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artifact completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artifact começa com frontmatter YAML válido | H01 |
| Sem quality abaixo de 8.0 | Reescreva antes de publicar se a autoavaliação for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas, ou restrições concretas | Adicione especificidades dos ISOs do builder |
| Campos de frontmatter faltando | id, kind, pillar ausentes ou quality não nulo | Adicione todos os campos obrigatórios conforme o schema |
| Corpo só em prosa | densidade < 0.85, sem tabelas | Converta listas em tabelas |
| Saída não bate com o schema | A saída não corresponde ao template de saída | Releia o ISO bld_output |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identifique qual gate H01-H07 falhou | F7 |
| 2 | Volte para F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rode F7 GOVERN de novo | F7 |
| 4 | Máximo 2 retentativas antes de escalar para o N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artifact
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py depois de salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a nota de qualidade para o orchestrator N07
- O builder NÃO DEVE se autoavaliar: o campo quality é sempre null na própria saída
## Limiares de Qualidade

| Dimensão | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica | 30% | >= 8.0 | L2 |
| Coerência semântica | 40% | >= 8.5 | L3 |
| Nota de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 1 | S05 |

## Verificação de Gate

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```

```yaml
# Expected output structure
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 7/7
density: 0.85+
```


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb__builder]] | sibling | 0.36 |
| [[p11_fb_quality_gate]] | sibling | 0.36 |
| [[p11_fb_model_card]] | sibling | 0.36 |
| [[p11_fb_agent_card]] | sibling | 0.36 |
| [[p11_fb_prompt_template]] | sibling | 0.36 |
| [[p11_fb_kind]] | sibling | 0.36 |
| [[p11_fb_context_map]] | sibling | 0.36 |
| [[p11_fb_validation_schema]] | sibling | 0.36 |
| [[p11_fb_input_schema]] | sibling | 0.35 |
| [[p11_fb_path_config]] | sibling | 0.35 |
