---
quality: null
id: p11_fb_product_match
kind: builder_default
pillar: P11
title: "Feedback -- Product Match"
domain: product_match
version: 1.1.0
tags: [feedback, anti-patterns, P11, product_match]
8f: "F7_govern"
keywords: [product match, regras nunca, modos de falha, correção de passo, feedback, antipadrões, product_match, modos de falha comuns, modo de falha, protocolo de correção]
tldr: "Antipadrões e protocolo de correção para builders de product_match. 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-02"
updated: "2026-07-02"
related:
  - p11_fb_quality_gate
---
# Feedback: Product Match

## Antipadrões (NUNCA faça)

| Regra | Violação | Gate |
|------|-----------|------|
| Sem autoavaliação | Nunca atribua uma pontuação de qualidade à sua própria saída | H01 |
| Sem alucinação | Nunca afirme que `reverse_image`/`embedding`/`manual` produzem um match real hoje -- product_match.py não tem implementação para nenhum dos três | H03 |
| Código só-ASCII | Sem emoji, sem caracteres acentuados em .py/.ps1/.sh | H04 |
| Sem saída parcial | Artefato completo; sem truncamento, sem "..." | H05 |
| Sem omissão de frontmatter | Todo artefato começa com frontmatter YAML válido | H01 |
| Sem EAN/GTIN/código de barras como chave de join | Estruturalmente excluídos por design (todo revendedor os recodifica) | H10 |

## Modos de Falha Comuns

| Modo de Falha | Sinal | Correção |
|-------------|--------|-----|
| Confiança de match fabricada | Uma linha SIM/PARCIAL com confiança > 0 enquanto `match_engine=none` ou sem credencial | Reler a Matriz de Status do Motor de Match em `bld_knowledge_product_match.md`; offline é SEMPRE NAO em 0.0 |
| Seções de saída reordenadas ou renomeadas | Títulos/ordem das seções divergem de Resultado do match -> Auditoria de catalogo -> Proveniencia -> Veredito | Reler `bld_output_product_match.md`; a forma é congelada em `MOLD_PRODUCT_MATCH` |
| Gate `match_confiavel` ausente | Seção Veredito presente mas sem gate booleano nomeado + bloqueadores | Adicionar a linha `match_confiavel` conforme `bld_schema_product_match.md` |
| Chave de join inclui um campo excluído | `match_join_keys` lista `ean`/`gtin`/`barcode` sem reconhecer a exclusão | Checar `_DEFAULT_EXCLUDE_KEYS` em `product_match.py`; documentar a exclusão explicitamente |

## Protocolo de Correção

| Passo | Ação | Gate |
|------|--------|------|
| 1 | Identificar qual gate H01-H10 falhou | F7 |
| 2 | Retornar a F6 PRODUCE com instrução explícita de correção | F6 |
| 3 | Rerodar F7 GOVERN | F7 |
| 4 | Máximo 2 tentativas antes de escalar para N07 | F8 |

## Comportamentos-Chave

- O builder DEVE carregar todos os 12 ISOs (1:1 com os pillars) antes de produzir qualquer artefato
- O builder DEVE rodar o gate de qualidade F7 GOVERN antes de salvar a saída
- O builder DEVE compilar a saída via cex_compile.py após salvar (F8 COLLABORATE)
- O builder DEVE sinalizar a conclusão com a pontuação de qualidade para o orquestrador N07
- O builder NÃO DEVE se autoavaliar: o campo quality é sempre null na própria saída
- O builder DEVE fundamentar toda afirmação sobre match_engine no comportamento real de `build()`
  em `product_match.py`, nunca no vocabulário aspiracional do enum

## Limiares de Qualidade

| Dimensão | Peso | Meta | Gate |
|-----------|--------|------|------|
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
gates_passed: 7/7
density: 0.85+
```

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| p11_fb_quality_gate | sibling | 0.76 |
