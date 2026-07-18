# SETUP -- Gemini Gems

Setup do bundle `marketplace_listing` em Gemini Gems. Esta capability não
usa nenhuma extensão (Search, code execution, etc.) -- é uma tarefa pura de
mapeamento + validação de texto. ~5 minutos.

## Pré-requisitos

- Conta Google + acesso a **gemini.google.com**.
- ZERO extensions ou chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome sugerido: `Marketplace Listing (Channel Projection)`.
4. Description sugerida: `Mapeia um produto para um anúncio de marketplace (Mercado Livre) com relatório de prontidão`.

### 2. Cole as instruções

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca (nome, tom de voz, valores) antes de usar em produção.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos `P0X_*.md` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Extensions

Não é necessário ativar nenhuma extension (nem Google Search, nem
url_context) -- esta capability não navega a web nem raspa páginas; ela
mapeia os dados que você fornece na conversa para o formato de anúncio ML.

### 5. Teste

Em uma conversa do Gem:

> `Mapeie uma cafeteira elétrica 110V para um anúncio no Mercado Livre -- título, preço, categoria, prontidão`

O Gem deve:
1. Pedir os campos da linha de catálogo que faltarem (titulo_ml, descricao,
   categoria_ml, marca, condicao, preco, estoque, fotos, atributos, sku).
2. Mapear cada campo para o payload ML conforme `P01_knowledge.md` e
   `P06_schema.md`.
3. Emitir as 6 seções congeladas na ordem exata (Listagem ML, Preco e
   Estoque, Fotos, Atributos, Descricao, Payload ML) -- ver
   `P05_output.md`.
4. Usar os placeholders honestos do gerador (ex.: "(sem sku)") para
   qualquer campo opcional ausente, nunca inventar um valor.
5. Calcular o gate de prontidão (score/passed/missing_required/notes)
   conforme `P07_evals.md`.

## Fidelidade declarada: FULL

Diferente de bundles de pesquisa (que dependem de Search/url_context para
coletar dados externos), o `marketplace_listing` só processa os dados que
você já tem sobre o produto. Sem nenhuma extension, o Gem já entrega o
contrato completo dos 12 pilares.

## Vantagens do Gemini para este caso de uso

- **Janela de contexto grande** (>1M tokens em modelos recentes) -- cabem
  os 12 arquivos deste bundle várias vezes.
- **Multi-modal nativo**: se você tem fotos do produto, pode anexá-las na
  conversa e pedir para o Gem descrevê-las -- útil para preencher o campo
  `fotos` e a seção `Atributos` com mais precisão.

## Solução de problemas

- **"Ele inventou preço, foto ou atributo"** -> reforce: "clean-room
  sempre -- nenhuma URL de foto, preço ou atributo fabricado" (ver
  `P11_feedback.md`, sinal `fabricated_photo_url`).
- **"O título veio cortado"** -> o contrato só avisa acima de 60
  caracteres, nunca trunca (ver `P01_knowledge.md`, seção "Regra de
  título do ML").
- **"As seções vieram fora de ordem"** -> cole `P06_schema.md` de novo e
  peça para o Gem reler antes de responder -- ordem e títulos das 6 seções
  são congelados (gate H05 em `P07_evals.md`).
- **Quero publicar de verdade no Mercado Livre** -> este bundle cobre
  mapear + validar; a publicação HTTP real sempre fica sob controle do
  operador, fora do escopo deste agente.
