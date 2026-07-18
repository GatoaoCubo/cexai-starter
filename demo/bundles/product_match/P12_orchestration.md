---
kind: collaboration
id: bld_collaboration_product_match
pillar: P12
llm_function: COLLABORATE
purpose: Como o product-match-builder trabalha em equipes (crews) com outros builders
pattern: cada builder precisa saber seu PAPEL numa equipe, o que RECEBE e o que PRODUZ
quality: null
title: "Colaboração -- Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F8_collaborate"
keywords: [construção de product_match, colaboração product match, product_match, builder, examples, "### crew: auditoria de sourcing", "### crew: merge de golden-record", meu papel, composições de equipe, auditoria de catálogo]
density_score: 0.90
related:
  - product-match-builder
  - opportunity-matrix-builder
---
# Colaboração: product-match-builder
## Meu Papel em Equipes (Crews)
Eu sou um ESPECIALISTA. Eu respondo a UMA pergunta: "qual chave composta une um item de
fornecedor a um anúncio de marketplace, e qual divergência cadastral a auditoria revela ao longo
do caminho?"
Eu não implemento busca reversa de imagem nem embeddings. Eu não ranqueio oportunidades de
buy-side. Eu não avalio prontidão de publicação por canal. Eu especifico um contrato de
casamento de registros + auditoria de catálogo para que uma execução no dashboard (N03) e outros
geradores (ex.: a auditoria de sourcing do N06) possam compor contra ele.
NOTA: em TEMPO DE EXECUÇÃO, a geração da capability `product_match` é inteiramente de
propriedade do gerador Python determinístico (`@register("product_match")` em
`_tools/capability_generators/product_match.py`) -- o passo F2 BECOME é deliberadamente pulado na
execução ao vivo da capability ("o seam do gerador estruturado É O DONO da saída",
`_tools/cex_run_capability.py:129,141`). Eu autoro/evoluo o artefato .md de spec do KIND (a
documentação do CONTRATO) ao qual o gerador está sujeito; eu não o substituo nem rodo no lugar dele.
## Composições de Equipe
### Crew: "Auditoria de Sourcing"
```
  1. product-match-builder      -> "spec de casamento fornecedor x anúncio + auditoria de catálogo"
  2. opportunity-matrix-builder -> "join de custo x demanda no buy-side que consome as sinalizações da auditoria"
  3. data-contract-builder      -> "schema produtor-consumidor para a lista de entrada `items`"
```
### Crew: "Merge de Golden-Record" (TUDAO / marketplace_listing)
```
  1. product-match-builder -> "spec de chave composta de join (foto+dimensão+código do fornecedor)"
  2. output-validator-builder -> "valida as 4 seções de saída congeladas pós-LLM"
  3. vision-tool-builder    -> "o primitivo de reverse-image/embedding que product_match encapsularia"
```
### Crew: "Gate de Qualidade de Catálogo"
```
  1. product-match-builder -> "spec de auditoria de divergência texto-vs-foto + foto de baixa resolução"
  2. quality-gate-builder  -> "definição do gate match_confiavel + vocabulário de bloqueadores"
  3. scoring-rubric-builder -> "fórmula de pontuação (penalidade offline, penalidade sem-foto)"
```
## Protocolo de Handoff
### Eu Recebo
- seeds: a forma do item de fornecedor sendo casado (code, photo_uri, dimension, desc), o
  marketplace alvo, qualquer preferência de match_engine, requisitos de piso de confiança
### Eu Produzo
- artefato product_match (.md + frontmatter .yaml)
- commitado em: `N03_engineering/P04_tools/examples/p04_pm_{name}.md`
### Eu Sinalizo
- sinal: complete (com a pontuação de qualidade vinda de QUALITY_GATES)
- se quality < 8.0: sinal de retry com as falhas de gate específicas
## Builders dos Quais Dependo
`vision_tool` (P04, o primitivo visual bruto que `match_engine=reverse_image` eventualmente
encapsularia -- AINDA NÃO implementado; `data_contract` (P06, o schema produtor-consumidor de
`items`); `output_validator` (P05, valida as 4 seções congeladas) -- os três são dependências
DECLARADAS de taxonomia (`.cex/kinds_meta.json` `depends_on`), não imports Python (verificado:
product_match.py não importa nenhum deles).
## Builders Que Dependem de Mim
| Builder | Por quê |
|---------|-------|
| opportunity-matrix-builder | A seção 6 "Match / auditoria" de `opportunity_matrix` mostra o resultado do MEU motor (conforme `bld_model_opportunity_matrix.md` Crew Role: "NÃO realiza casamento visual de produtos... isso é product_match") |
| marketplace-listing-builder | O merge de golden-record do TUDAO compartilha meus auxiliares `_normalize_join_key` + `_audit_text_vs_photo` (conforme a intenção declarada do ADR; ainda não conectado até esta leitura) |
| agent-builder | Agentes que rodam um workflow de sourcing/auditoria de catálogo invocam `product_match` como um passo |
## Aplicação de Fronteiras
| Pedido | Minha resposta |
|---------|-------------|
| "Analisar esta foto de um produto para rótulos/objetos" | Redirecionar para vision-tool-builder (sem alvo de join = vision_tool, não product_match) |
| "Ranquear meus fornecedores por custo vs demanda de mercado" | Redirecionar para opportunity-matrix-builder (economia buy-side, P11/N06) |
| "Este anúncio está pronto para publicar no Mercado Livre" | Redirecionar para marketplace-listing-builder (prontidão de canal, P05/N06) |
| "Casar estes dois produtos por EAN/código de barras" | Explicar a exclusão estrutural (todo revendedor recodifica EAN/GTIN/código de barras); oferecer a chave composta foto+dimensão+código do fornecedor no lugar |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[product-match-builder]] | upstream | 0.41 |
| [[bld_orchestration_vision_tool]] | sibling | 0.35 |
| [[bld_prompt_product_match]] | upstream | 0.32 |
| [[opportunity-matrix-builder]] | sibling | 0.30 |
