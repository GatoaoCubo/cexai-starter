---
id: p10_lr_product_match_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-07-02
updated: 2026-07-02
author: builder_agent
observation: "A leitura estática de _tools/capability_generators/product_match.py (build(), linhas 323-544) mostra que TODOS os quatro valores do enum match_engine (reverse_image, embedding, manual, none) hoje resolvem para a MESMA linha honest-NAO-em-0.0; só o texto do motivo muda ('nao executado' vs 'pendente -- run live com motor X'). Nenhum casador ao vivo existe ainda. O lado de auditoria de catálogo (_audit_text_vs_photo) é o único caminho de análise funcional e roda inteiramente offline sobre campos locais do item."
pattern: "Fundamente toda spec product_match no comportamento REAL de branch do gerador, não no vocabulário aspiracional do enum. Documente match_engine como um enum fechado com uma coluna honesta de 'implementado: não' por valor até que um motor ao vivo seja lançado. Espelhe as 4 seções de saída IDÊNTICAS, byte a byte, à ordem+layout de MOLD_PRODUCT_MATCH. Mantenha o corpo abaixo de 5120 bytes."
evidence: "Leitura direta do código-fonte (nesta sessão de build, 2026-07-02): product_match.py linhas 386-406 (branches offline e não-offline emitem ambos NAO), linhas 476-524 (fórmula do gate match_confiavel + deduções de pontuação), apps/dashboard_web/lib/molds.ts linhas 3289-3391 (mock de MOLD_PRODUCT_MATCH, contract_version 1.0)."
confidence: 0.9
outcome: OBSERVATION
domain: product_match
tags: [product-match, record-linkage, catalog-audit, match-engine-status, offline-honest-null, join-key]
tldr: "match_engine é um enum fechado onde só 'none' é comportamentalmente distinto hoje (força offline); reverse_image/embedding/manual são placeholders não implementados. O lado de auditoria é a única análise hoje real. Manter abaixo de 5120 bytes."
impact_score: 7.5
decay_rate: 0.05
agent_group: n03_engineering
keywords: [product match, status do motor de match, exclusão de chave de join, honest null offline, auditoria de catálogo, casamento de registros, gate match_confiavel]
memory_scope: project
observation_types: [reference, project]
quality: null
title: "Memória -- Product Match"
8f: "F7_govern"
density_score: 0.90
llm_function: INJECT
related:
  - product-match-builder
  - bld_schema_product_match
---
## Resumo
`product_match` é consumido por dois chamadores hoje: o caminho de execução no dashboard (N03,
verbo=analyze) e `sourcing_opportunity.py` (N06), que faz soft-import dos dois auxiliares PUROS
`_normalize_join_key` e `_audit_text_vs_photo` para sua própria etapa de auditoria visual. Como o
lado de match é um esqueleto (nenhum motor ao vivo de reverse-image/embedding/manual existe), uma
spec que sugira capacidade de casamento ao vivo enganaria ambos os chamadores. A diferença entre
uma spec product_match honesta e uma enganosa se resume a uma decisão tomada no momento da spec:
a spec afirma que o vocabulário do enum está implementado, ou documenta o enum como
fechado-mas-em-grande-parte-não-implementado?
## Padrão
**Documente match_engine como um enum fechado com uma coluna explícita de status de
implementação.** Status do motor de match (fundamentado em product_match.py, não aspiracional):
1. `none` (padrão): o ÚNICO valor com comportamento de código distinto -- força `offline=True`
   incondicionalmente, independente de uma credencial fornecida.
2. `reverse_image` / `embedding` / `manual`: membros válidos do enum, implementação zero -- o
   gerador emite a mesma linha honest-NAO com uma string de motivo "pendente -- run live com
   motor '{engine}'" (product_match.py:396-406).
3. Uma string não reconhecida cai de volta para `none` com uma nota, nunca um crash.
Regras de chave de join:
1. `match_join_keys` padrão: `[photo, dimension, supplier_code]` -- composta, nunca um único campo.
2. `match_exclude_keys` (padrão `[ean, gtin, barcode]`) é um override INTERNO -- presente nas
   chamadas `inputs.get(...)` de `product_match.py` mas AUSENTE de
   `MOLD_PRODUCT_MATCH.input_contract` (os 6 campos expostos no dashboard). Uma spec o documenta
   como um controle avançado/interno, não como um campo do dashboard.
3. Uma chave de join que também aparece no conjunto de exclusão é removida defensivamente e
   registrada (product_match.py:372-377) -- nunca honrada silenciosamente.
Orçamento de bytes das seções de saída (máximo 5120): Overview (300) + Input Contract (1200) +
Output Sections (2400) + Gate (600) = ~4500, deixando folga para prosa adjacente ao frontmatter.
## Antipadrão
1. Descrever `reverse_image` como "chama o Google Lens" ou similar -- nenhuma chamada assim existe
   na base de código até esta leitura; é um placeholder de enum.
2. Tratar `match_confiavel` como alcançável hoje -- `matched_count` é 0 por construção enquanto
   offline, e não existe branch ao vivo que o preencha também (product_match.py:396-406), então o
   gate não pode passar hoje independente da entrada.
3. Omitir o override interno `match_exclude_keys` por estar ausente do mold do dashboard (uma
   spec completa documenta tanto a superfície exposta no dashboard QUANTO a de override interno).
4. Reordenar as 4 seções de saída ou mudar um conjunto de colunas (a forma é congelada em
   `MOLD_PRODUCT_MATCH`; ver `capability_contracts_v1.0.md` "How to build to this contract").
5. Usar EAN/GTIN/código de barras como chave de join (estruturalmente excluídos -- todo revendedor
   os recodifica).
6. Definir quality com um valor não-null (autoavaliação corrompe as métricas de qualidade do pool).
## Contexto
Limite de corpo 5120B. Orçamento: Overview (300) + Input Contract (1200) + Output Sections (2400)
+ Gate (600). Link para `_tools/capability_generators/product_match.py` para a implementação
real; não duplique o código dele na spec (só spec, conforme as restrições do SCHEMA).

## Metadados

```yaml
id: p10_lr_product_match_builder
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply p10-lr-product-match-builder.md
```

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `learning_record` |
| Pillar | P10 |
| Domain | product_match |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_product_match]] | upstream | 0.43 |
| [[product-match-builder]] | upstream | 0.34 |
| [[bld_schema_product_match]] | upstream | 0.34 |
