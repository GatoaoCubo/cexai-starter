# SETUP -- Claude Projects

Setup do bundle `marketplace_listing` em Claude Projects. Nenhuma ferramenta
externa (MCP, navegação web) é necessária -- esta capability mapeia e
valida um produto para um anúncio de marketplace usando só os 12 arquivos
de conhecimento + as instruções. ~5 minutos.

## Pré-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO chaves de API ou MCP bridges necessários.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome sugerido: `Marketplace Listing (Channel Projection)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca (nome, tom de voz, valores) antes de usar em produção.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos `P0X_*.md` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho
total) -- os 12 arquivos deste bundle cabem com folga.

### 4. Teste

Em uma conversa do Project:

> `Mapeie uma cafeteira elétrica 110V para um anúncio no Mercado Livre -- título, preço, categoria, prontidão`

O agente deve:
1. Pedir os campos da linha de catálogo que faltarem (titulo_ml, descricao,
   categoria_ml, marca, condicao, preco, estoque, fotos, atributos, sku).
2. Mapear cada campo para o payload ML (`title`, `category_id`, `price`,
   `currency_id`, `available_quantity`, `condition`, `listing_type_id`,
   `description.plain_text`, `pictures[].url`, `attributes[]`,
   `seller_custom_field`) conforme `P01_knowledge.md` e `P06_schema.md`.
3. Emitir as 6 seções congeladas na ordem exata: Listagem ML, Preco e
   Estoque, Fotos, Atributos, Descricao, Payload ML (pronto para
   publicar) -- ver `P05_output.md`.
4. Injetar BRAND (a partir de marca) e SELLER_SKU (a partir de sku) quando
   ausentes dos atributos, sem sobrescrever o que já existir.
5. Calcular o gate de prontidão (score/passed/missing_required/notes) e
   devolver o veredito (`PUBLISH`, `REVISE` ou `REJECT`) conforme
   `P07_evals.md`.

## Por que este bundle não precisa de MCP

Bundles de pesquisa (ex.: `pesquisa_produto`) usam MCP para conectar
ferramentas externas de busca/raspagem. O `marketplace_listing` é diferente:
ele só mapeia e valida dados que **você já tem** (a linha de catálogo do
produto) -- não há navegação web, scraping ou API externa no escopo deste
agente. Publicar de verdade no Mercado Livre fica sempre sob controle do
operador, fora deste bundle.

## Fidelidade declarada: FULL

Sem nenhuma ferramenta externa, o Claude Project já entrega o contrato
completo dos 12 pilares -- não existe um modo "parcial" para esta
capability.

## Solução de problemas

- **"Ele inventou um preço, foto ou atributo"** -> reforce: "clean-room
  sempre -- nenhuma URL de foto, preço ou atributo fabricado" (ver
  `P11_feedback.md`, sinal `fabricated_photo_url`, e `P02_model.md`, regra
  6).
- **"As 6 seções vieram fora de ordem"** -> peça para o agente reler
  `P06_schema.md` antes de responder de novo -- título, ordem e layout das
  6 seções são congelados (gate H05 em `P07_evals.md`).
- **"Ele confundiu quality com o score de prontidão"** -> são dois campos
  distintos: `quality` é sempre `null` (meta do CEX); `score` é o float
  0.0-1.0 do gate de prontidão (ver `P10_memory.md`).
- **Contexto do projeto ficou grande** -> os 12 arquivos deste bundle
  cabem folgadamente no limite de 200K tokens de contexto do Claude; não é
  necessário remover nenhum.
