---
kind: architecture
id: bld_architecture_product_match
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes do product_match -- inventário, dependências, e posição arquitetural
quality: null
title: "Arquitetura -- Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [mapa de componentes do product_match, e posição arquitetural, construção de product_match, arquitetura product match, product_match, builder, examples, inventário de componentes, grafo de dependências, tabela de fronteiras]
density_score: 0.90
related:
  - product-match-builder
  - bld_architecture_vision_tool
  - opportunity-matrix-builder
---
## Inventário de Componentes
| Nome | Papel | Dono | Status |
|------|------|-------|--------|
| items | Lista de itens do fornecedor a casar/auditar (code, photo_uri, dimension, desc) | product_match | obrigatório |
| match_join_keys | Campos de join por não-chave composta | product_match | obrigatório |
| match_exclude_keys | Campos que NUNCA entram no join (ean, gtin, barcode) | product_match | interno (ausente do mold do dashboard) |
| match_engine | Motor de casamento (reverse_image/embedding/manual/none) | product_match | obrigatório |
| match_confidence_floor | Piso que um match precisa ultrapassar para contar SIM | product_match | obrigatório |
| audit_enabled | Ativa/desativa o efeito colateral de auditoria de catálogo | product_match | recomendado |
| audit_min_photo_px | Limiar de baixa resolução para a auditoria de foto | product_match | recomendado |
| match_confiavel | Gate de veredito nomeado (F7) | product_match | obrigatório |
| gerador | `_tools/capability_generators/product_match.py` `@register("product_match")` | N03 | implementação |
| mold | `MOLD_PRODUCT_MATCH` (apps/dashboard_web/lib/molds.ts) | N03 | espelho do contrato |
| consumidor (auxiliares compartilhados) | `sourcing_opportunity.py` (N06) importa `_normalize_join_key` + `_audit_text_vs_photo` | N06 | consumidor |
## Grafo de Dependências
```
items               --alimenta-->       match_join_keys
match_join_keys     --compõe-->         _normalize_join_key (chave composta)
match_exclude_keys  --remove-->         match_join_keys (defensivo, registrado como nota)
match_engine        --seleciona-->      linhas de Resultado do match
match_confidence_floor --limita-->      match_confiavel
audit_enabled       --ativa/desativa--> Auditoria de catalogo
audit_min_photo_px  --limiariza-->      _audit_text_vs_photo (sinalização de baixa resolução)
Resultado do match  --alimenta-->       Veredito (Cobertura)
Auditoria de catalogo --alimenta-->     Veredito (Bloqueadores, itens sem foto/baixa resolução)
sourcing_opportunity.py --importa--> _normalize_join_key + _audit_text_vs_photo (reuso pelo N06)
```
| De | Para | Tipo | Dados |
|------|----|------|------|
| items | match_join_keys | alimenta | dicts brutos de item |
| match_join_keys | Resultado do match | compõe | string da chave composta de match |
| match_engine | Resultado do match | seleciona | texto do motivo da linha ("nao executado" vs "pendente") |
| match_confidence_floor | Veredito | limita | proporção de Cobertura + match_confiavel |
| audit_min_photo_px | Auditoria de catalogo | limiariza | emissão da sinalização de baixa resolução |
| Resultado do match + Auditoria de catalogo | Veredito | alimenta | Cobertura + Bloqueadores |
| product_match.py | sourcing_opportunity.py | auxiliar compartilhado | `_normalize_join_key`, `_audit_text_vs_photo` (soft-import, product_match.py:314-330) |
## Tabela de Fronteiras
| product_match É | product_match NÃO É |
|-------------------|------------------------|
| Um join por NÃO-chave composta (foto+dimensão+código do fornecedor) entre um item de fornecedor e um anúncio de marketplace | Um primitivo bruto de análise visual que retorna rótulos de imagem arbitrários (vision_tool) |
| Um auditor de catálogo que roda offline sobre dados LOCAIS do item (texto-vs-foto, baixa resolução, contagem de peças) | Um ranking de custo x demanda no buy-side (opportunity_matrix, capability irmã #15, P11/N06) |
| Degrade-never: offline (match_engine=none ou sem credencial) sempre retorna NAO honesto, nunca um match fabricado | Um relatório de prontidão de publicação por projeção de canal (marketplace_listing, P05/N06) |
| Só spec: nenhum código de implementação de reverse-image/embedding no artefato .md | Um battle card de comparação de concorrentes (competitive_matrix) |
| Fonte de auxiliares compartilhados para a própria etapa de auditoria visual do `sourcing_opportunity.py` | Uma busca reversa de imagem ao vivo -- como implementado, `reverse_image`/`embedding`/`manual` são valores de enum SEM nenhum caminho de código funcional (product_match.py:396-406 emite o mesmo placeholder honesto que `none`) |
## Mapa de Camadas
| Camada | Componentes | Propósito |
|-------|-----------|---------|
| entrada | items, match_join_keys, match_exclude_keys | Define o que é casado e por qual chave composta |
| processamento | match_engine, match_confidence_floor, audit_enabled, audit_min_photo_px | Seleciona o motor, limita a confiança, roda a auditoria |
| saída | Resultado do match, Auditoria de catalogo, Proveniencia, Veredito | 4 seções congeladas (ordem de MOLD_PRODUCT_MATCH) |
| governança | Gate match_confiavel, fórmula de pontuação (product_match.py:511-522) | Veredito F7 GOVERN + pontuação |
| chamadores | execução no dashboard (N03, verbo=analyze), sourcing_opportunity.py (N06, auxiliares compartilhados) | Consumidores em runtime |
## Zonas de Confusão
| Cenário | Parece Ser | Na Verdade É | Regra |
|---|---|---|---|
| "Analisar esta foto de produto" (sem alvo de join) | product_match | vision_tool | vision_tool=analisa uma imagem; product_match=une DOIS registros por chave composta |
| "Ranquear fornecedores por custo vs demanda" | product_match | opportunity_matrix | opportunity_matrix=economia buy-side (P11/N06); product_match=casamento de registros (P04/N03) |
| "Este anúncio está pronto para publicar no Mercado Livre" | product_match | marketplace_listing | marketplace_listing=prontidão por projeção de canal (P05/N06); product_match=só casamento+auditoria |
| "Casar por código de barras EAN/GTIN" | product_match | (não suportado por design) | EAN/GTIN/código de barras são ESTRUTURALMENTE EXCLUÍDOS -- todo revendedor os recodifica |
## Árvore de Decisão
- Unir um item de fornecedor a um anúncio de marketplace por foto/dimensão/código, com EAN excluído? -> product_match
- Analisar uma imagem sem alvo de join? -> vision_tool
- Ranquear oportunidades de buy-side por custo vs demanda? -> opportunity_matrix
- Avaliar a prontidão de publicação por canal de um anúncio já casado? -> marketplace_listing
## Comparação com Vizinhos
| Dimensão | product_match | opportunity_matrix | Diferença |
|---|---|---|---|
| Pillar | P04 (tools) | P11 (feedback/gate) | Pillar diferente apesar de ambos serem "sourcing" (catálogo #15/#16) |
| llm_function | CALL | GOVERN | product_match executa um join; opportunity_matrix renderiza um veredito |
| Nucleus | N03 | N06 | RACI: N03 engenharia constrói ferramentas; N06 comercial é dono da economia de preço/sourcing |
| Formato de saída | table+list+fields+fields (4) | fields+table+table+fields+table+table+fields+fields (8, conforme capability_contracts_v1.0.md #15) | product_match é o primitivo de auditoria visual compartilhado, mais estreito |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[product-match-builder]] | upstream | 0.50 |
| [[bld_architecture_vision_tool]] | sibling | 0.40 |
| [[opportunity-matrix-builder]] | sibling | 0.36 |
| n01_sourcing_rigor | related | 0.34 |
