---
quality: null
version: 1.1.0
id: p11_fb_research_pipeline
kind: builder_default
pillar: P11
title: "Feedback: Pipeline de Pesquisa"
domain: research_pipeline
tags: [feedback, anti-patterns, P11, research_pipeline]
tldr: "Feedback do Research Pipeline: antipadrões, sinais de regressão e gatilhos de melhoria de qualidade"
8f: "F7_govern"
keywords: [research pipeline, research pipeline feedback, regression signals, and quality improvement triggers, feedback, anti-patterns, research_pipeline, common failure modes, correction protocol, key behaviors]
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - p11_fb_prompt_version
  - p11_fb__builder
  - p11_fb_golden_test
  - p11_fb_retriever
  - p11_fb_pipeline_template
  - p11_fb_retriever_config
  - p11_fb_quality_gate
  - p11_fb_knowledge_graph
  - p11_fb_response_format
  - p11_fb_output_validator
---
# Feedback: Pipeline de Pesquisa

## Antipadrões (NUNCA faça)

- **Sem auto-pontuação**: nunca atribua uma nota de qualidade ao seu próprio output
- **Sem alucinação**: cite fontes; não invente fatos, métricas ou referências
- **Código somente ASCII**: sem emoji, sem caracteres acentuados em output .py/.ps1/.sh
- **Sem output parcial**: produza o artefato completo; sem truncamento, sem placeholders "..."
- **Sem omissão de frontmatter**: todo artefato deve começar com um frontmatter YAML válido
- **Sem qualidade abaixo de 8.0**: reescreva antes de publicar se a autoavaliação for < 8.0

## Modos de Falha Comuns do Research Pipeline

- Seção de identidade vaga (sem capacidades, ferramentas ou restrições concretas)
- Campos obrigatórios do frontmatter ausentes (id, kind, pillar, quality: null)
- Corpo apenas com prosa -- sem tabelas, sem dados estruturados (densidade < 0.85)
- Output não corresponde ao schema do output template

## Protocolo de Correção

1. Identifique qual gate H01-H07 falhou
2. Volte ao F6 PRODUCE com instrução explícita de correção
3. Rode o F7 GOVERN novamente
4. Máximo de 2 tentativas antes de escalar para o N07

## Comportamentos-Chave

- O builder DEVE carregar os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar o output
- O builder DEVE compilar o output via cex_compile.py depois de salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a nota de qualidade para o orquestrador N07
- O builder NÃO DEVE se autopontuar: o campo quality é sempre null no próprio output
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
| [[p11_fb_prompt_version]] | sibling | 0.35 |
| [[p11_fb__builder]] | sibling | 0.35 |
| [[p11_fb_golden_test]] | sibling | 0.35 |
| [[p11_fb_retriever]] | sibling | 0.35 |
| [[p11_fb_pipeline_template]] | sibling | 0.35 |
| [[p11_fb_retriever_config]] | sibling | 0.35 |
| [[p11_fb_quality_gate]] | sibling | 0.35 |
| [[p11_fb_knowledge_graph]] | sibling | 0.35 |
| [[p11_fb_response_format]] | sibling | 0.35 |
| [[p11_fb_output_validator]] | sibling | 0.35 |
