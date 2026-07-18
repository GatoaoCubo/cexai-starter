---
quality: null
id: p11_fb_oauth_app_config
kind: builder_default
pillar: P11
title: "Feedback: Oauth App Config"
domain: oauth_app_config
version: 1.1.0
tags: [feedback, anti-patterns, P11, oauth_app_config]
8f: "F7_govern"
keywords: [oauth app config, never rules, failure modes, step correction, feedback, anti-patterns, oauth_app_config, common failure modes, failure mode, correction protocol]
tldr: "Anti-padrões e protocolo de correção para builders de config de app OAuth. 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - p11_fb__builder
  - p11_fb_quality_gate
  - p11_fb_validation_schema
  - p11_fb_input_schema
  - p11_fb_context_file
  - p11_fb_path_config
  - p11_fb_pipeline_template
  - p11_fb_context_window_config
  - p11_fb_skill
  - p11_fb_event_schema
---
# Feedback: Oauth App Config

## Anti-Padrões (NUNCA fazer)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribuir score de qualidade à própria saída | H01 |
| Sem alucinação | Citar fontes; nenhum fato, métrica ou referência inventada | H03 |
| Código somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com frontmatter YAML válido | H01 |
| Sem qualidade abaixo de 8.0 | Reescrever antes de publicar se a autoavaliação for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas ou restrições concretas | Adicionar específicos dos ISOs do builder |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality não nulo | Adicionar todos os campos obrigatórios conforme o schema |
| Corpo só com prosa | densidade < 0.85, sem tabelas | Converter listas em tabelas |
| Incompatibilidade do schema de saída | A saída não corresponde ao template de saída | Reler o ISO bld_output |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Retornar a F6 PRODUCE com instrução de correção explícita | F6 |
| 3 | Rerodar F7 GOVERN | F7 |
| 4 | Máximo de 2 retentativas antes de escalar para N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar todos os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o quality gate F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py após salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com o score de qualidade para o orquestrador N07
- O builder NÃO DEVE se autoavaliar: o campo quality é sempre null na própria saída
## Limites de Qualidade

| Dimensão | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica | 30% | >= 8.0 | L2 |
| Coerência semântica | 40% | >= 8.5 | L3 |
| Score de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 1 | S05 |

## Checagem do Gate

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
| [[p11_fb__builder]] | sibling | 0.36 |
| [[p11_fb_quality_gate]] | sibling | 0.36 |
| [[p11_fb_validation_schema]] | sibling | 0.35 |
| [[p11_fb_input_schema]] | sibling | 0.35 |
| [[p11_fb_context_file]] | sibling | 0.35 |
| [[p11_fb_path_config]] | sibling | 0.35 |
| [[p11_fb_pipeline_template]] | sibling | 0.35 |
| [[p11_fb_context_window_config]] | sibling | 0.35 |
| [[p11_fb_skill]] | sibling | 0.35 |
| [[p11_fb_event_schema]] | sibling | 0.35 |
