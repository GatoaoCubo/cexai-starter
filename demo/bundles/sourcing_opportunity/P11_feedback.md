---
quality: null
id: p11_fb_opportunity_matrix
kind: builder_default
pillar: P11
title: "Feedback -- Opportunity Matrix"
domain: opportunity_matrix
version: 1.1.0
tags: [feedback, anti-patterns, P11, opportunity_matrix]
8f: "F7_govern"
keywords: [opportunity matrix, regras nunca, modos de falha, protocolo de correção, feedback, antipadrões, opportunity_matrix, modos de falha comuns, sourcing_confiavel, honest-null]
tldr: "Antipadrões e protocolo de correção para builders de opportunity matrix. 6 regras NUNCA + 4 modos de falha + correção em 4 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-02"
updated: "2026-07-02"
related:
  - opportunity-matrix-builder
---
# Feedback: Opportunity Matrix

## Antipadrões (NUNCA faça)
| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribua uma pontuação de qualidade à sua própria saída | H01 |
| Sem alucinação | Cite fontes; sem fatos, métricas ou referências inventadas | H03 |
| Código só-ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem dado de mercado fabricado | Nunca mostre um preço de venda/nível de demanda como real quando offline/bloqueado -- só honest-null | H07 |
| Sem chave de join EAN/GTIN | Nunca use ean/gtin/barcode como chave de join entre marketplaces | H08 |

## Modos de Falha Comuns
| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Drift de seção | Contagem de seções != 8, ou títulos/ordem diferem de MOLD_SOURCING_OPPORTUNITY | Reler o ISO bld_output; restaurar a forma congelada |
| Divergência de célula de tabela | Uma linha de tabela tem mais/menos células que seu array de colunas | Recontar contra a lista de colunas congelada de cada seção |
| Descarte silencioso de linhas não cobertas | Contagens de cauda-longa / bucket-manual ausentes de Cobertura | Expor toda linha parseada em algum lugar (priced, manual, ou cauda-longa) |
| Gate declarado sem condições | "sourcing_confiavel: true" sem nenhuma condição booleana mostrada | Adicionar a string das 4 condições + uma linha de avaliação (S4) |

## Protocolo de Correção
| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H08 falhou | F7 |
| 2 | Retornar a F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rerodar F7 GOVERN | F7 |
| 4 | Máximo 2 tentativas antes de escalar para N07 | F8 |

## Comportamentos-Chave
- O builder DEVE carregar todos os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py após salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a pontuação de qualidade para o orquestrador N07
- O builder NÃO DEVE se autoavaliar: o campo quality é sempre null na própria saída

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
# Estrutura de saída esperada
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 8/8
density: 0.85+
```

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_opportunity_matrix]] | sibling | 0.75 |
| [[opportunity-matrix-builder]] | sibling | 0.70 |
| p08_adr_opportunity_matrix_kind | upstream | 0.40 |
