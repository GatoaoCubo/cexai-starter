---
kind: knowledge_card
id: bld_knowledge_card_product_match
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para a produção de product_match -- especificação de casamento visual de registros (record-linkage) e auditoria de catálogo
sources: _tools/capability_generators/product_match.py, apps/dashboard_web/lib/molds.ts (MOLD_PRODUCT_MATCH), apps/dashboard_web/lib/capability_contracts_v1.0.md (section 16), _tools/cex_run_capability.py (_BASE_CAPABILITIES), N06_commercial/P08_architecture/p08_adr_opportunity_matrix_kind.md, _docs/specs/contract/n01_sourcing_rigor.md
quality: null
title: "Ficha de Conhecimento -- Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F3_inject"
keywords: [construção de product_match, ficha de conhecimento product match, product_match, builder, examples, [record_linkage, catalog_audit], conhecimento de domínio, resumo executivo product match, tabela de especificação, matriz de status do motor de match]
density_score: 0.90
related:
  - bld_schema_product_match
---

# Conhecimento de Domínio: product_match
## Resumo Executivo
`product_match` é resolução de entidades / casamento de registros (record-linkage): ele une um
item de fornecedor a um anúncio de marketplace por uma NÃO-chave composta (foto + dimensão +
código do fornecedor), com EAN/GTIN/código de barras EXCLUÍDOS de propósito, porque todo
revendedor recodifica esses valores (regra aprendida na prática, numa rodada real de sourcing que
motivou este kind -- `p08_adr_opportunity_matrix_kind.md`). Também funciona como auditor de
catálogo: mesmo totalmente offline, sinaliza divergência cadastral texto-vs-foto e fotos
ausentes/de baixa resolução em dados LOCAIS do item. Preenche uma lacuna real da taxonomia -- o
CEX não tinha nenhum kind de resolução de entidades antes deste ADR (driver c). É o motor de
match compartilhado por trás TANTO da etapa de auditoria buy-side do `sourcing_opportunity` (N06)
QUANTO, conforme o ADR, do merge de golden-record de saída do TUDAO.
## Tabela de Especificação
| Propriedade | Valor |
|----------|-------|
| Pillar | P04 (tools) |
| Nucleus | N03 (`_tools/cex_run_capability.py` `_BASE_CAPABILITIES["product_match"]`) |
| Verbo | analyze |
| llm_function | CALL (kinds_meta.json) |
| primary_8f | F4_reason (kinds_meta.json -- NÃO F5, apesar de llm_function=CALL) |
| RUN_MODE | offline-deterministic (constante `RUN_MODE` de product_match.py) |
| contract_version | "1.0.0" (constante do módulo) / "1.0" (MOLD_PRODUCT_MATCH.contract_version) |
| Seções de saída | 4, ordem congelada: table, list, fields, fields |
| Gate nomeado | `match_confiavel` (seção Veredito) |
| Bytes máximos de corpo | 5120 |
## Matriz de Status do Motor de Match (fundamentada em product_match.py:340-406 -- ler antes de citar "reverse_image" como funcional)
| Motor | No enum fechado? | Realmente implementado em build()? | Linha emitida |
|--------|:---:|:---:|-------------|
| none | SIM (padrão) | N/A -- força `offline=True` | "NAO", "nao executado -- sem motor de match", 0.0 |
| reverse_image | SIM | NÃO | "NAO", "pendente -- run live com motor 'reverse_image'", 0.0 |
| embedding | SIM | NÃO | "NAO", "pendente -- run live com motor 'embedding'", 0.0 |
| manual | SIM | NÃO | "NAO", "pendente -- run live com motor 'manual'", 0.0 |
Todo branch -- offline ou não, qualquer motor, com ou sem credencial -- hoje retorna um NAO
honesto com confiança 0.0. `matched_count` é sempre 0 por construção, então `match_confiavel` não
pode passar hoje (fórmula do gate: `(not offline) and (total>0) and (matched_count>=total)`). O
lado de AUDITORIA de catálogo (`_audit_text_vs_photo`) é a única análise hoje funcional, e roda
sobre dados locais sem nenhuma chamada de rede.
## Padrões
- **Chave composta, nunca um único campo**: `_normalize_join_key` monta `key=value|key=value|...`
  a partir de quaisquer campos de `match_join_keys` que o item de fato carregue; um campo ausente
  é silenciosamente ignorado (nunca preenchido com um placeholder)
- **A exclusão é estrutural, não acidental**: `match_exclude_keys` (padrão ean/gtin/barcode) é
  removida do join mesmo que o `match_join_keys` de um chamador deixe uma delas vazar -- é
  defensivo, registrado como nota, nunca um descarte silencioso
- **A auditoria roda independentemente do match_engine**: `audit_enabled` é independente de
  `match_engine`; mesmo `match_engine=none` ainda produz sinalizações de divergência cadastral
- **Auxiliares compartilhados, não um serviço compartilhado**: `_normalize_join_key` +
  `_audit_text_vs_photo` são funções PURAS (sem I/O) importáveis pelo nome -- `sourcing_opportunity.py`
  faz soft-import de ambas (product_match.py:314-330) em vez de chamar um microsserviço compartilhado
| Padrão | Quando usar |
|---------|-------------|
| match_engine=none (padrão) | Toda execução hoje -- ainda não existe motor ao vivo |
| audit_enabled=true (padrão) | Sempre, a menos que o chamador queira só as linhas brutas de match |
| audit_min_photo_px ajustado para cima (>200) | Catálogos com exigência mais rígida de qualidade de foto (ex.: marketplaces premium) |
## Antipadrões
| Antipadrão | Por que falha |
|-------------|-------------|
| Descrever `reverse_image`/`embedding`/`manual` como funcionais hoje | product_match.py NÃO tem implementação para nenhum dos três (verificado lendo build(), linhas 396-406) -- são placeholders de um enum fechado |
| Tratar EAN/GTIN/código de barras como chave de join válida | Estruturalmente excluídos -- todo revendedor os recodifica (driver do ADR, evidência real de sourcing) |
| Reordenar as 4 seções de saída | `capability_contracts_v1.0.md` congela ordem+layout; StructuredResultView é fixo em fields\|table\|list |
| Fabricar um match SIM/PARCIAL quando offline | Degrade-never: offline SEMPRE retorna NAO em 0.0, nunca inventado (product_match.py:386-393) |
| Confundir com vision_tool | product_match é um JOIN de dois registros + auditoria; vision_tool analisa UMA imagem sem alvo de join |
| Confundir com opportunity_matrix | opportunity_matrix (P11/N06) ranqueia custo x demanda no buy-side; product_match (P04/N03) é casamento de registros |
## Aplicação
1. Identifique a tarefa de join item-de-fornecedor x anúncio-de-marketplace e confirme que EAN/GTIN/código de barras estão excluídos
2. Enumere `match_join_keys` (padrão foto/dimensão/código do fornecedor) e qualquer `match_exclude_keys` extra
3. Selecione `match_engine` a partir do enum fechado, documentando com honestidade a não-implementação atual
4. Defina `match_confidence_floor` (padrão 0.7) e `audit_min_photo_px` (padrão 200)
5. Declare as 4 seções de saída na ordem congelada e o gate `match_confiavel` + seus bloqueadores

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_schema_product_match]] | downstream | 0.48 |
| [[bld_knowledge_vision_tool]] | sibling | 0.44 |
| p08_adr_opportunity_matrix_kind | upstream | 0.43 |
| n01_sourcing_rigor | upstream | 0.40 |
| n03_schema | upstream | 0.36 |
