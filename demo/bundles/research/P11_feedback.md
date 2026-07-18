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
keywords: [knowledge card, never rules, failure modes, step correction, feedback, anti-patterns, knowledge_card, common failure modes, failure mode, correction protocol]
tldr: "Anti-patterns and correction protocol for knowledge card builders. 6 NEVER rules + 4 failure modes + 3-step correction."
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

## Anti-Padrões (NUNCA faça)

| Regra | Violação | Gate |
|------|-----------|------|
| Não se autopontue | Nunca atribua uma nota de qualidade à própria saída | H01 |
| Sem alucinação | Cite as fontes; nenhum fato, métrica ou referência inventados | H03 |
| Código somente ASCII | Sem emoji, sem caractere acentuado em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com frontmatter YAML válido | H01 |
| Sem quality abaixo de 8.0 | Reescreva antes de publicar se a autoavaliação for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas ou restrições concretas | Adicione especificidades a partir dos ISOs do builder |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality não nulo | Adicione todos os campos obrigatórios conforme o schema |
| Corpo só com prosa | densidade < 0.85, sem tabelas | Converta listas em tabelas |
| Incompatibilidade com o schema de saída | A saída não corresponde ao output template | Releia o ISO bld_output |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identifique qual gate H01-H07 falhou | F7 |
| 2 | Volte ao F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rode o F7 GOVERN de novo | F7 |
| 4 | Máximo de 2 retentativas antes de escalar ao N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar todos os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py depois de salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a nota de qualidade ao orquestrador N07
- O builder NÃO DEVE se autopontuar: o campo quality é sempre null na própria saída
## Limiares de Qualidade

| Dimensão | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica | 30% | >= 8.0 | L2 |
| Coerência semântica | 40% | >= 8.5 | L3 |
| Score de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 1 | S05 |

## Checagem de Gate

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
| [[p11_fb__builder]] | sibling | 0.38 |
| [[p11_fb_quality_gate]] | sibling | 0.38 |
| [[p11_fb_model_card]] | sibling | 0.37 |
| [[p11_fb_agent_card]] | sibling | 0.37 |
| [[p11_fb_prompt_template]] | sibling | 0.37 |
| [[p11_fb_kind]] | sibling | 0.37 |
| [[p11_fb_context_map]] | sibling | 0.37 |
| [[p11_fb_validation_schema]] | sibling | 0.37 |
| [[p11_fb_input_schema]] | sibling | 0.37 |
| [[p11_fb_path_config]] | sibling | 0.37 |
