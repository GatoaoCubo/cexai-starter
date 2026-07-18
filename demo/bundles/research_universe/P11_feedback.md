---
id: p11_fb_research_universe
kind: builder_default
pillar: P11
title: "Feedback: Research Universe"
domain: research_universe
version: 1.0.0
quality: null
tags: [feedback, anti-patterns, P11, research_universe]
8f: "F7_govern"
keywords: [research universe, never rules, failure modes, step correction, feedback, anti-patterns, research_universe, common failure modes, failure mode, correction protocol]
tldr: "Antipadrões e protocolo de correção para builders de research_universe. 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-17"
updated: "2026-07-17"
related:
  - p11_fb_quality_gate
  - p11_fb_competitive_matrix
  - p11_fb_knowledge_card
---
# Feedback: Research Universe

## Antipadrões (NUNCA fazer)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribuir pontuação de qualidade a própria saída | H01 |
| Sem fabricação de dado | Nunca inventar CNPJ, índice de reputação, volume de busca ou razão social sem fonte | H06 |
| Sem confusão ok/blocked/skipped | Nunca apresentar uma trilha bloqueada ou pulada como se tivesse dado real | H05, H07 |
| Sem saída parcial silenciosa | Sempre reportar as 6 trilhas na tabela final, mesmo quando a maioria falhou | H04 |
| Sem omissão de frontmatter | Todo artefato começa com frontmatter YAML válido | H01 |
| Sem qualidade abaixo de 8.0 | Redigir novamente antes de publicar se a autoavaliação for < 8.0 | -- |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Sentimento sem trecho-fonte | Trilha "Sentimento em PT" preenchida sem citar de qual trilha o texto veio | Marcar `skipped` até haver texto real das trilhas Sinal Social/Reputação |
| Perguntas multi-perspectiva genéricas | Perguntas que serviriam para qualquer semente ("o que os clientes acham?") | Reescrever amarrando cada pergunta a um dado específico já coletado sobre esta semente |
| `blocked` e `skipped` trocados | Motivo descreve falha de acesso mas o rótulo diz `skipped` (ou vice-versa) | Reler a definição em P06 e corrigir o rótulo -- eles tem causas diferentes |
| `coverage_score` incoerente com a tabela | Número de cobertura não bate com a contagem real de trilhas `ok` | Recalcular: trilhas `ok` / 6, sempre |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Voltar para F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rodar novamente F7 GOVERN | F7 |
| 4 | Máximo de 2 tentativas antes de escalar para o usuário/N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar todos os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE tentar as 6 trilhas para toda semente, mesmo esperando `skipped` em algumas
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py depois de salvar (F8 COLLABORATE)
- O builder NÃO DEVE se autoavaliar: o campo quality é sempre null na própria saída
- O builder NÃO DEVE preencher uma trilha `blocked`/`skipped` com dado inventado sob nenhuma circunstância

## Limiares de Qualidade

| Dimensão | Peso | Meta | Gate |
|-----------|--------|--------|------|
| Completude estrutural (6 trilhas presentes) | 30% | >= 8.0 | L1 |
| Conformidade com a rubrica (P07) | 30% | >= 8.0 | L2 |
| Honestidade ok/blocked/skipped | 40% | >= 9.0 | L3 |
| Pontuação de densidade | -- | >= 0.85 | S09 |
| Tabelas presentes | -- | >= 6 (uma por trilha + status) | S05 |

## Verificação do Gate

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```

```yaml
# Expected output structure
structural: 8.5+
rubric: 8.0+
average: 8.0+
gates_passed: 7/7
density: 0.85+
```

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[p11_fb_quality_gate]] | sibling | 0.36 |
| [[p11_fb_competitive_matrix]] | sibling | 0.32 |
| [[p11_fb_knowledge_card]] | sibling | 0.30 |
| [[p01_qg_research_universe]] | upstream | 0.28 |
