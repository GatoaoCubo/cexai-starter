---
quality: null
id: p11_fb_prompt_template
kind: builder_default
pillar: P11
title: "Feedback: Prompt Template"
domain: prompt_template
version: 1.1.0
tags: [feedback, anti-patterns, P11, prompt_template]
8f: "F7_govern"
keywords: [prompt template, never rules, failure modes, step correction, feedback, anti-patterns, prompt_template, common failure modes, failure mode, correction protocol]
tldr: "Antipadrões e protocolo de correção para builders de prompt template. 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - p11_fb__builder
  - p11_fb_quality_gate
  - p11_fb_pipeline_template
  - p11_fb_context_map
  - p11_fb_validation_schema
  - p11_fb_input_schema
  - p11_fb_path_config
  - p11_fb_context_file
  - p11_fb_system_prompt
  - p11_fb_model_card
---
# Feedback: Prompt Template

## Antipadrões (NUNCA fazer)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribuir pontuação de qualidade à própria saída | H01 |
| Sem alucinação | Citar fontes; sem fatos, métricas ou referências inventadas | H03 |
| Código somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com um frontmatter YAML válido | H01 |
| Sem quality abaixo de 8.0 | Refazer o rascunho antes de publicar se a autoavaliação for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas ou constraints concretas | Adicionar especificidades a partir dos ISOs do builder |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality não nulo | Adicionar todos os campos obrigatórios conforme o schema |
| Corpo só com prosa | densidade < 0.85, sem tabelas | Converter listas em tabelas |
| Descompasso com o schema de saída | A saída não corresponde ao output template | Reler o ISO bld_output |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Retornar a F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rodar F7 GOVERN novamente | F7 |
| 4 | Máximo de 2 tentativas antes de escalar para o N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py após salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a pontuação de qualidade para o orquestrador N07
- O builder NÃO DEVE se autoavaliar: o campo quality é sempre null na própria saída

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
| [[p11_fb__builder]] | sibling | 0.37 |
| [[p11_fb_quality_gate]] | sibling | 0.37 |
| [[p11_fb_pipeline_template]] | sibling | 0.36 |
| [[p11_fb_context_map]] | sibling | 0.36 |
| [[p11_fb_validation_schema]] | sibling | 0.36 |
| [[p11_fb_input_schema]] | sibling | 0.36 |
| [[p11_fb_path_config]] | sibling | 0.36 |
| [[p11_fb_context_file]] | sibling | 0.36 |
| [[p11_fb_system_prompt]] | sibling | 0.36 |
| [[p11_fb_model_card]] | sibling | 0.36 |
