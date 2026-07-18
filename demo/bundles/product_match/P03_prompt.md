---
kind: instruction
id: bld_instruction_product_match
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para product_match
pattern: pipeline de 3 fases (pesquisa -> compor -> validar)
quality: null
title: "Instruções -- Product Match"
version: "1.0.0"
author: n03_builder
tags:
  - "product_match"
  - "builder"
  - "examples"
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F6_produce"
keywords:
  - "construção de product_match"
  - "instruções product match"
  - "product_match"
  - "builder"
  - "examples"
  - "{{vars}}"
  - "^p04_pm_[a-z][a-z0-9_]+$"
  - "p04_pm_"
  - "reverse image match"
  - "catalog audit"
density_score: 0.90
related:
  - bld_schema_product_match
---
# Instruções: Como Produzir um product_match
## Fase 1: PESQUISA
1. Identifique a tarefa de casamento de registros: qual catálogo de fornecedor se une a qual
   conjunto de anúncios de marketplace
2. Leia `_tools/capability_generators/product_match.py` `build()` de ponta a ponta -- o gerador É
   a fonte da verdade; uma spec que o contradiz está errada por definição
3. Confirme os 6 campos de entrada expostos no dashboard contra `MOLD_PRODUCT_MATCH.input_contract`
   (apps/dashboard_web/lib/molds.ts): items, match_join_keys, match_engine,
   match_confidence_floor, audit_enabled, audit_min_photo_px
4. Anote o override interno `match_exclude_keys` (lido pelo gerador, ausente do mold do
   dashboard) -- padrão `[ean, gtin, barcode]`
5. Confirme as 4 seções de saída + ordem/layout congelados contra `MOLD_PRODUCT_MATCH.output_sections`
6. Verifique o status de implementação do match_engine (bld_knowledge_product_match.md) -- NÃO
   descreva um valor do enum como funcional a menos que o código prove isso
7. Verifique se já existem artefatos product_match para evitar duplicatas (`p04_pm_*.md`)
8. Confirme o slug da capability para o id: snake_case, minúsculas, sem hifens
## Fase 2: COMPOSIÇÃO
1. Leia `bld_schema_product_match.md` -- fonte da verdade para todos os campos
2. Leia `bld_output_product_match.md` -- preencha `{{vars}}` seguindo as restrições do SCHEMA
3. Preencha o frontmatter: todos os campos obrigatórios (quality: null -- nunca se autoavalie)
4. Escreva a seção Overview: o que é casado/auditado, quem consome a saída (execução no
   dashboard, `sourcing_opportunity.py`), enquadramento offline-first
5. Escreva a seção Input Contract: os 6 campos do dashboard + o override interno
   `match_exclude_keys`, cada um com tipo/obrigatoriedade/padrão exatamente como em
   `MOLD_PRODUCT_MATCH`
6. Escreva as Output Sections: Resultado do match (table), Auditoria de catalogo (list),
   Proveniencia (fields), Veredito (fields) -- nesta ordem exata, com as colunas/chaves
   exatamente declaradas
7. Escreva a seção Gate: o gate nomeado `match_confiavel` + seu vocabulário de bloqueadores (URL
   pública de foto ausente, foto de baixa resolução, match_engine ainda `none`)
8. Verifique se o corpo é <= 5120 bytes
9. Verifique se o id casa com `^p04_pm_[a-z][a-z0-9_]+$`
## Fase 3: VALIDAÇÃO
1. Verifique `p11_qg_product_match.md` -- confirme manualmente cada gate HARD
2. Confirme que o frontmatter YAML parseia sem erros
3. Confirme que o id casa com o prefixo `p04_pm_`
4. Confirme que kind == product_match
5. Confirme que as 4 seções de saída casam exatamente com a ordem, o layout e as colunas de
   `MOLD_PRODUCT_MATCH`
6. Confirme que match_engine é um dos 4 valores do enum fechado (reverse_image, embedding,
   manual, none)
7. Confirme que EAN/GTIN/código de barras estão documentados como EXCLUÍDOS, nunca como chave de
   join ativa
8. Confirme que a regra honest-null offline está declarada: match_engine=none ou sem credencial
   -> toda linha de match é NAO em 0.0, nunca fabricada
9. Cheque cruzado de fronteira: apenas casamento de registros + auditoria de catálogo (não
   vision_tool, não opportunity_matrix, não marketplace_listing)?
10. Revise se a pontuação < 8.0 antes de entregar

## Carregamento de ISO

```yaml
loader: cex_skill_loader
injection_point: F3_compose
priority: high
```

```bash
python _tools/cex_skill_loader.py --verify product_match
```

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `instruction` |
| Pillar | P03 |
| Domain | construção de product_match |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_vision_tool]] | sibling | 0.49 |
| [[bld_prompt_output_validator]] | sibling | 0.47 |
| [[bld_prompt_data_contract]] | sibling | 0.45 |
| [[bld_schema_product_match]] | upstream | 0.40 |
