---
id: p11_fb_knowledge_card
kind: builder_default
pillar: P11
title: "Feedback: knowledge_card"
domain: knowledge_card
version: 1.1.0
quality: null
tags: [feedback, anti-patterns, P11, knowledge_card]
8f: "F7_govern"
keywords: [knowledge card, never rules, failure modes, step correction, feedback, anti-patterns, knowledge_card, common failure modes, failure mode, correction protocol]
tldr: "Anti-padroes e protocolo de correcao para builders de knowledge_card. 6 regras NUNCA + 4 modos de falha + correcao em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - p11_fb__builder
  - p11_fb_prompt_template
  - p11_fb_kind
  - p11_fb_context_map
  - p11_fb_validation_schema
  - p11_fb_context_file
  - p11_fb_input_schema
  - p11_fb_path_config
  - p11_fb_agent_card
  - p11_fb_model_card
---
# Feedback: knowledge_card

## Anti-Padroes (NUNCA faca)

| Regra | Violacao | Portao |
|------|-----------|------|
| Sem auto-pontuacao | Nunca atribua nota de qualidade a propria saida | H01 |
| Sem alucinacao | Cite fontes; nada de fato, metrica ou referencia inventada | H03 |
| Codigo somente ASCII | Sem emoji, sem caractere acentuado em .py/.ps1/.sh | H04 |
| Sem saida parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissao de frontmatter | Todo artefato comeca com frontmatter YAML valido | H01 |
| Sem qualidade abaixo de 8.0 | Reescreva antes de publicar se a autoavaliacao for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correcao |
|-------------|--------|-----|
| Secao de identidade vaga | Sem capacidade, ferramenta ou restricao concreta | Adicione especificidades dos ISOs do builder |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality diferente de null | Adicione todos os campos obrigatorios do schema |
| Corpo so em prosa | densidade < 0.85, sem tabela | Converta listas em tabelas |
| Saida nao bate com o schema | A saida nao bate com o output template | Releia o ISO bld_output |

## Protocolo de Correcao

| Passo | Acao | Portao |
|------|--------|------|
| 1 | Identifique qual portao H01-H07 falhou | F7 |
| 2 | Volte ao F6 PRODUCE com instrucao explicita de correcao | F6 |
| 3 | Rode o F7 GOVERN de novo | F7 |
| 4 | No maximo 2 retentativas antes de escalar para o N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar os 12 ISOs (1:1 com os pilares) antes de produzir qualquer artefato
- O builder DEVE rodar o portao de qualidade F7 GOVERN antes de salvar a saida
- O builder DEVE compilar a saida via cex_compile.py depois de salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusao com a nota de qualidade para o orchestrator N07
- O builder NAO DEVE se auto-pontuar: o campo quality e sempre null na propria saida
## Limiares de Qualidade

| Dimensao | Peso | Meta | Portao |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica | 30% | >= 8.0 | L2 |
| Coerencia semantica | 40% | >= 8.5 | L3 |
| Nota de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 1 | S05 |

## Checagem de Portao

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

| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[p11_fb__builder]] | sibling | 0.34 |
| [[p11_fb_prompt_template]] | sibling | 0.33 |
| [[p11_fb_kind]] | sibling | 0.33 |
| [[p11_fb_context_map]] | sibling | 0.33 |
| [[p11_fb_validation_schema]] | sibling | 0.33 |
| [[p11_fb_context_file]] | sibling | 0.33 |
| [[p11_fb_input_schema]] | sibling | 0.33 |
| [[p11_fb_path_config]] | sibling | 0.33 |
| [[p11_fb_agent_card]] | sibling | 0.33 |
| [[p11_fb_model_card]] | sibling | 0.33 |
