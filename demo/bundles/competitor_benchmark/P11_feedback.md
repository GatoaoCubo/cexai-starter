---
id: p11_fb_competitive_matrix
kind: builder_default
pillar: P11
title: "Feedback: Competitive Matrix"
domain: competitive_matrix
version: 1.1.0
quality: null
tags: [feedback, anti-patterns, P11, competitive_matrix]
8f: "F7_govern"
keywords: [competitive matrix, never rules, failure modes, step correction, feedback, anti-patterns, competitive_matrix, common failure modes, failure mode, correction protocol]
tldr: "Antipadrões e protocolo de correção para builders de competitive_matrix. 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - p11_fb_quality_gate
  - p11_fb__builder
  - p11_fb_audit_log
  - p11_fb_workflow
  - p11_fb_validation_schema
  - p11_fb_data_contract
  - p11_fb_input_schema
  - p11_fb_context_file
  - p11_fb_pattern
  - p11_fb_compliance_framework
---
# Feedback: Competitive Matrix

## Antipadrões (NUNCA fazer)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribuir pontuação de qualidade a própria saída | H01 |
| Sem alucinação | Citar fontes; nenhum fato, métrica ou referência inventados | H03 |
| Código somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com frontmatter YAML válido | H01 |
| Sem qualidade abaixo de 8.0 | Redigir novamente antes de publicar se a autoavaliação for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas ou restrições concretas | Adicionar específicos dos ISOs do builder |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality não nulo | Adicionar todos os campos obrigatórios conforme o schema |
| Corpo somente com prosa | densidade < 0.85, sem tabelas | Converter listas em tabelas |
| Incompatibilidade do schema de saída | A saída não corresponde ao template de saída | Reler o ISO bld_output |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Voltar para F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rodar novamente F7 GOVERN | F7 |
| 4 | Máximo de 2 tentativas antes de escalar para N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar todos os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py depois de salvar (F8 COLLABORATE)
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

## Verificação do Gate

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

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[p11_fb_quality_gate]] | sibling | 0.36 |
| [[p11_fb__builder]] | sibling | 0.36 |
| [[p11_fb_audit_log]] | sibling | 0.35 |
| [[p11_fb_workflow]] | sibling | 0.35 |
| [[p11_fb_validation_schema]] | sibling | 0.35 |
| [[p11_fb_data_contract]] | sibling | 0.35 |
| [[p11_fb_input_schema]] | sibling | 0.35 |
| [[p11_fb_context_file]] | sibling | 0.35 |
| [[p11_fb_pattern]] | sibling | 0.35 |
| [[p11_fb_compliance_framework]] | sibling | 0.35 |
