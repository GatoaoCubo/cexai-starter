---
quality: null
id: p11_fb_multimodal_prompt
kind: builder_default
pillar: P11
title: "Feedback: Multimodal Prompt"
domain: multimodal_prompt
version: 1.1.0
tags: [feedback, anti-patterns, P11, multimodal_prompt]
8f: "F7_govern"
keywords: [multimodal prompt, regras nunca, modos de falha, correção de etapa, feedback, anti-padrões, multimodal_prompt, modos de falha comuns, modo de falha, protocolo de correção]
tldr: "Anti-padrões e protocolo de correção para builders de multimodal prompt. 6 regras NUNCA + 4 modos de falha + correção em 3 etapas."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - p11_fb__builder
  - p11_fb_quality_gate
  - p11_fb_prompt_template
  - p11_fb_validation_schema
  - p11_fb_input_schema
  - p11_fb_context_file
  - p11_fb_system_prompt
  - p11_fb_pipeline_template
  - p11_fb_skill
  - p11_fb_event_schema
---
# Feedback: Multimodal Prompt

## Anti-Padrões (NUNCA fazer)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribuir pontuação de qualidade à própria saída | H01 |
| Sem alucinação | Citar fontes; sem fatos, métricas ou referências inventadas | H03 |
| Código somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com frontmatter YAML válido | H01 |
| Sem qualidade abaixo de 8.0 | Refazer o rascunho antes de publicar se a autoavaliação < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas ou restrições concretas | Adicionar especificidades dos builder ISOs |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality não nulo | Adicionar todos os campos obrigatórios conforme o schema |
| Corpo só com prosa | densidade < 0.85, sem tabelas | Converter listas em tabelas |
| Divergência do schema de saída | Saída não corresponde ao output template | Reler o ISO bld_output |

## Protocolo de Correção

| Etapa | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Retornar ao F6 PRODUCE com instrução de correção explícita | F6 |
| 3 | Rodar novamente o F7 GOVERN | F7 |
| 4 | Máx. 2 retentativas antes de escalar para N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar os 12 ISOs (1:1 com os pilares) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py após salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a pontuação de qualidade para o orquestrador N07
- O builder NÃO DEVE se autoavaliar: o campo quality é sempre nulo na própria saída
## Limiares de Qualidade

| Dimensão | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica | 30% | >= 8.0 | L2 |
| Coerência semântica | 40% | >= 8.5 | L3 |
| Pontuação de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 1 | S05 |

## Checagem de Gate

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```

```yaml
# Estrutura de saída esperada
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 7/7
density: 0.85+
```


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb__builder]] | sibling | 0.34 |
| [[p11_fb_quality_gate]] | sibling | 0.34 |
| [[p11_fb_prompt_template]] | sibling | 0.34 |
| [[p11_fb_validation_schema]] | sibling | 0.33 |
| [[p11_fb_input_schema]] | sibling | 0.33 |
| [[p11_fb_context_file]] | sibling | 0.33 |
| [[p11_fb_system_prompt]] | sibling | 0.33 |
| [[p11_fb_pipeline_template]] | sibling | 0.33 |
| [[p11_fb_skill]] | sibling | 0.33 |
| [[p11_fb_event_schema]] | sibling | 0.33 |
