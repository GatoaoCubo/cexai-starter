---
id: p11_fb_content_monetization
kind: builder_default
pillar: P11
title: "Feedback: Content Monetization"
domain: content_monetization
version: 1.1.0
quality: null
tags: [feedback, anti-patterns, P11, content_monetization]
8f: "F7_govern"
keywords: [monetizacao de conteudo, regras nunca, modos de falha, correcao de passo, feedback, antipadroes, content_monetization, modos de falha comuns, modo de falha, protocolo de correcao]
tldr: "Antipadroes e protocolo de correcao para builders de monetizacao de conteudo. 6 regras NUNCA + 4 modos de falha + correcao em 3 passos."
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
  - p11_fb_output_validator
  - p11_fb_context_file
  - p11_fb_pattern
---
# Feedback: Content Monetization

## Antipadroes (NUNCA faca)

| Regra | Violacao | Gate |
|------|-----------|------|
| Sem autoavaliacao | Nunca atribua uma nota de qualidade ao proprio output | H01 |
| Sem alucinacao | Cite as fontes; nenhum fato, metrica ou referencia inventada | H03 |
| Codigo apenas ASCII | Sem emoji, sem caractere acentuado em .py/.ps1/.sh | H04 |
| Sem output parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissao de frontmatter | Todo artefato comeca com frontmatter YAML valido | H01 |
| Sem qualidade abaixo de 8.0 | Reescreva antes de publicar se a autoavaliacao for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correcao |
|-------------|--------|-----|
| Secao de identidade vaga | Sem capacidades, ferramentas ou restricoes concretas | Adicionar especificos vindos das ISOs do builder |
| Campos de frontmatter faltando | id, kind, pillar ausentes ou quality diferente de null | Adicionar todos os campos obrigatorios do schema |
| Corpo so com prosa | densidade < 0.85, sem tabelas | Converter listas em tabelas |
| Output nao bate com o schema | O output nao corresponde ao output template | Reler a ISO bld_output |

## Protocolo de Correcao

| Passo | Acao | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Voltar ao F6 PRODUCE com instrucao de correcao explicita | F6 |
| 3 | Rodar F7 GOVERN novamente | F7 |
| 4 | Maximo de 2 tentativas antes de escalar para N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar as 12 ISOs (1:1 com os pillares) antes de produzir qualquer artefato
- O builder DEVE rodar o quality gate do F7 GOVERN antes de salvar o output
- O builder DEVE compilar o output via cex_compile.py apos salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusao com a nota de qualidade para o orquestrador N07
- O builder NAO PODE se autoavaliar: o campo quality e sempre null no proprio output
## Limiares de Qualidade

| Dimensao | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica | 30% | >= 8.0 | L2 |
| Coerencia semantica | 40% | >= 8.5 | L3 |
| Pontuacao de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 1 | S05 |

## Checagem de Gate

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```

```yaml
# Estrutura de output esperada
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 7/7
density: 0.85+
```


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb_quality_gate]] | sibling | 0.42 |
| [[p11_fb__builder]] | sibling | 0.41 |
| [[p11_fb_audit_log]] | sibling | 0.41 |
| [[p11_fb_workflow]] | sibling | 0.41 |
| [[p11_fb_validation_schema]] | sibling | 0.41 |
| [[p11_fb_data_contract]] | sibling | 0.41 |
| [[p11_fb_input_schema]] | sibling | 0.41 |
| [[p11_fb_output_validator]] | sibling | 0.40 |
| [[p11_fb_context_file]] | sibling | 0.40 |
| [[p11_fb_pattern]] | sibling | 0.40 |
