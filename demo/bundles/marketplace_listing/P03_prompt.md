---
id: bld_prompt_marketplace_listing
kind: instruction
pillar: P03
llm_function: REASON
8f: F4_reason
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Processo: construir um marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, prompt, process, P03]
tldr: "Processo pesquisar > compor > validar para produzir um marketplace_listing que espelha exatamente o mapeamento de campos, o formato de seções e o gate de prontidão de _tools/capability_generators/marketplace_listing.py."
density_score: 0.9
related:
  - bld_schema_marketplace_listing
  - bld_output_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_knowledge_marketplace_listing
  - bld_config_marketplace_listing
---

# Processo: construir um marketplace_listing
## Entradas
Uma linha de catálogo G1 (titulo_ml, descricao, categoria_ml, marca, condicao, preco,
estoque, fotos, atributos, sku) + marketplace opcional (padrão `mercado_livre`) + o
contrato [[bld_schema_marketplace_listing]].

## Passo 1 -- PESQUISAR (F3 INJECT)
- Carregue [[bld_schema_marketplace_listing]] (fonte da verdade) + [[bld_knowledge_marketplace_listing]].
- Confirme que marketplace assume `mercado_livre` por padrão (o único canal que
  `CHANNEL_ADAPTERS` conecta hoje).
- Leia a linha G1; note quais campos estão presentes vs. ausentes -- a ausência conduz o
  gate, nunca um valor fabricado.

## Passo 2 -- COMPOR (F6 PRODUCE)
- Mapeie G1 -> G2 exatamente: titulo_ml->title, descricao->description.plain_text,
  categoria_ml->category_id, condicao->condition (novo->new, usado->used,
  recondicionado->refurbished, desconhecido->new), preco->price, estoque->available_quantity,
  fotos->pictures[].url (string separada por vírgula OU array JSON; SEM filtro https no
  generator em produção), atributos->attributes[]{id,value_name} (objeto JSON),
  sku->seller_custom_field.
- Injete BRAND a partir de marca quando ausente de atributos (verificação de id sem
  diferenciar maiúsculas/minúsculas); injete SELLER_SKU a partir de sku quando ausente.
  BRAND é prependido, SELLER_SKU é anexado ao final -- nunca sobrescreva um atributo que a
  linha já declara.
- listing_type_id assume `gold_special` por padrão; currency_id é sempre `BRL`.
- Componha as 6 seções na ordem CONGELADA (veja [[bld_schema_marketplace_listing]]); use
  os placeholders exatos e honestos quando um campo estiver ausente:
  "(sem titulo_ml -- obrigatorio)", "(sem categoria_ml -- obrigatorio)",
  "(sem preco -- obrigatorio)", "(sem sku)", "(sem marca -- obrigatorio pelo ML)",
  "(sem descricao -- recomendado)", e para Fotos
  "(sem fotos -- adicione URLs em fotos ou envie via upload no slot abaixo)" --
  strings literais do generator, reproduza-as exatamente, sem acentuar.
- Seção Payload ML: serialize o dicionário ml_listing em JSON (ASCII-safe), truncando a
  prévia em 900 caracteres com "..." exatamente como a própria convenção de prévia do
  generator.

## Passo 3 -- VALIDAR (F7 GOVERN)
- Compute o gate de prontidão: score começa em 1.0; -0,20 titulo_ml ausente; -0,05 titulo_ml
  >60 caracteres; -0,15 categoria_ml ausente; -0,15 preco<=0; -0,05 descricao ausente; -0,10
  sem fotos; -0,05 marca ausente; piso em 0,0. passed = zero itens em missing_required
  (somente titulo_ml/categoria_ml/preco) E score >= 0.70.
- Confirme que o corpo é <= 6144 bytes; confirme que os títulos/ordem das seções batem
  exatamente com [[bld_schema_marketplace_listing]].
- Autoverificação clean-room: nenhuma URL de foto, preço ou valor de atributo fabricado.
- Defina `quality: null`; compile.

## Disciplina de saída
Emita somente o artefato (frontmatter + corpo) conforme [[bld_output_marketplace_listing]].
Sem preâmbulo, sem conversa paralela.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.55 |
| [[bld_output_marketplace_listing]] | downstream | 0.5 |
| [[bld_eval_marketplace_listing]] | downstream | 0.48 |
| [[bld_knowledge_marketplace_listing]] | related | 0.42 |
| [[bld_config_marketplace_listing]] | related | 0.38 |
