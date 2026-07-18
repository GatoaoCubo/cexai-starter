---
quality: null
id: p11_fb_subscription_tier
kind: builder_default
pillar: P11
title: "Feedback: Subscription Tier"
domain: subscription_tier
version: 1.1.0
tags: [feedback, anti-patterns, P11, subscription_tier]
8f: "F7_govern"
keywords: [subscription tier, regras nunca, modos de falha, correção de passo, feedback, antipadrões, subscription_tier, modos de falha comuns, modo de falha, protocolo de correção]
tldr: "Antipadrões e protocolo de correção para builders de subscription tier. 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
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
# Feedback: Subscription Tier

## Antipadrões (NUNCA faça)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribuir pontuação de qualidade à própria saída | H01 |
| Sem alucinação | Cite fontes; nada de fatos, métricas ou referências inventadas | H03 |
| Código somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com um frontmatter YAML válido | H01 |
| Sem qualidade abaixo de 8.0 | Reescrever antes de publicar se a autoavaliação for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas ou restrições concretas | Adicionar detalhes específicos das ISOs do builder |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality diferente de null | Adicionar todos os campos obrigatórios conforme o schema |
| Corpo somente em prosa | densidade < 0.85, sem tabelas | Converter listas em tabelas |
| Saída fora do schema | A saída não corresponde ao output template | Reler a ISO bld_output |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Retornar a F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Reexecutar F7 GOVERN | F7 |
| 4 | Máximo de 2 tentativas antes de escalar para N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar as 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE executar o gate de qualidade F7 GOVERN antes de salvar a saída
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

| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[p11_fb_quality_gate]] | sibling | 0.37 |
| [[p11_fb__builder]] | sibling | 0.37 |
| [[p11_fb_audit_log]] | sibling | 0.36 |
| [[p11_fb_workflow]] | sibling | 0.36 |
| [[p11_fb_validation_schema]] | sibling | 0.36 |
| [[p11_fb_data_contract]] | sibling | 0.36 |
| [[p11_fb_input_schema]] | sibling | 0.36 |
| [[p11_fb_context_file]] | sibling | 0.36 |
| [[p11_fb_pattern]] | sibling | 0.36 |
| [[p11_fb_compliance_framework]] | sibling | 0.36 |
