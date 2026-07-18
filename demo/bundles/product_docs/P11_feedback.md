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
tldr: "Antipadrões e protocolo de correção para builders de knowledge_card. 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
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
  - p11_fb_kind
  - p11_fb_scoring_rubric
  - p11_fb_context_map
  - p11_fb_validation_schema
  - p11_fb_input_schema
  - p11_fb_path_config
---
# Feedback: Knowledge Card

## Antipadrões (NUNCA faça)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autopontuação | Nunca atribua pontuação de qualidade a própria saída | H01 |
| Sem alucinação | Cite fontes; sem fatos, métricas ou referências inventadas | H03 |
| Código somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com frontmatter YAML válido | H01 |
| Sem qualidade abaixo de 8.0 | Reescreva antes de publicar se a autoavaliação for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Seção de identidade vaga | Sem capacidades, ferramentas ou restrições concretas | Adicione específicos vindos dos ISOs do builder |
| Campos de frontmatter faltando | id, kind, pillar ausentes ou quality diferente de null | Adicione todos os campos obrigatórios conforme o schema |
| Corpo somente em prosa | densidade < 0.85, sem tabelas | Converta listas em tabelas |
| Descompasso no schema de saída | A saída não bate com o output_template | Releia o ISO bld_output |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|------|------|
| 1 | Identifique qual gate H01-H07 falhou | F7 |
| 2 | Volte ao F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rode o F7 GOVERN de novo | F7 |
| 4 | Max 2 retries antes de escalar para o N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar todos os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py após salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a pontuação de qualidade para o orchestrator N07
- O builder NÃO DEVE se autopontuar: o campo quality é sempre null na própria saída
## Limiares de Qualidade

| Dimensão | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com o rubric | 30% | >= 8.0 | L2 |
| Coerência semântica | 40% | >= 8.5 | L3 |
| Pontuação de densidade | -- | >= 0.85 | S09 |
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

## Artefatos Relacionados

| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[p11_fb__builder]] | irmão | 0.36 |
| [[p11_fb_quality_gate]] | irmão | 0.36 |
| [[p11_fb_model_card]] | irmão | 0.35 |
| [[p11_fb_agent_card]] | irmão | 0.35 |
| [[p11_fb_kind]] | irmão | 0.35 |
| [[p11_fb_scoring_rubric]] | irmão | 0.35 |
| [[p11_fb_context_map]] | irmão | 0.35 |
| [[p11_fb_validation_schema]] | irmão | 0.35 |
| [[p11_fb_input_schema]] | irmão | 0.35 |
| [[p11_fb_path_config]] | irmão | 0.35 |
