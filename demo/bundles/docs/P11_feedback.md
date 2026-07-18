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
  - p11_fb_prompt_template
  - p11_fb_kind
  - p11_fb_context_map
  - p11_fb_validation_schema
  - p11_fb_input_schema
  - p11_fb_path_config
  - p11_fb_context_file
  - p11_fb_pipeline_template
---
# Feedback: knowledge_card

## Antipadroes (NUNCA faca)

| Regra | Violacao | Gate |
|------|-----------|------|
| Sem autopontuacao | Nunca atribua pontuacao de qualidade ao proprio output | H01 |
| Sem alucinacao | Cite fontes; nenhum fato, metrica ou referencia inventados | H03 |
| Codigo somente ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem output parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissao de frontmatter | Todo artefato comeca com frontmatter YAML valido | H01 |
| Sem qualidade abaixo de 8.0 | Reescreva antes de publicar se a autoavaliacao for < 8.0 | H07 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correcao |
|-------------|--------|-----|
| Secao de identidade vaga | Sem capacidades, ferramentas ou restricoes concretas | Adicione especificidades dos ISOs do builder |
| Campos de frontmatter ausentes | id, kind, pillar ausentes ou quality diferente de null | Adicione todos os campos obrigatorios conforme o schema |
| Corpo somente em prosa | densidade < 0.85, sem tabelas | Converta listas em tabelas |
| Output nao corresponde ao schema | O output nao corresponde ao template de saida | Releia o ISO bld_output |

## Protocolo de Correcao

| Passo | Acao | Gate |
|------|------|------|
| 1 | Identifique qual gate H01-H07 falhou | F7 |
| 2 | Volte para F6 PRODUCE com instrucao explicita de correcao | F6 |
| 3 | Execute F7 GOVERN novamente | F7 |
| 4 | Maximo 2 tentativas antes de escalar para o N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE executar o gate de qualidade F7 GOVERN antes de salvar o output
- O builder DEVE compilar o output via cex_compile.py apos salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusao com a pontuacao de qualidade para o orquestrador N07
- O builder NAO DEVE se autopontuar: o campo quality e sempre null no proprio output
## Limiares de Qualidade

| Dimensao | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica | 30% | >= 8.0 | L2 |
| Coerencia semantica | 40% | >= 8.5 | L3 |
| Pontuacao de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 1 | S05 |

## Verificacao de Gate

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
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[p11_fb__builder]] | irmao | 0.39 |
| [[p11_fb_quality_gate]] | irmao | 0.39 |
| [[p11_fb_prompt_template]] | irmao | 0.39 |
| [[p11_fb_kind]] | irmao | 0.38 |
| [[p11_fb_context_map]] | irmao | 0.38 |
| [[p11_fb_validation_schema]] | irmao | 0.38 |
| [[p11_fb_input_schema]] | irmao | 0.38 |
| [[p11_fb_path_config]] | irmao | 0.38 |
| [[p11_fb_context_file]] | irmao | 0.38 |
| [[p11_fb_pipeline_template]] | irmao | 0.38 |
