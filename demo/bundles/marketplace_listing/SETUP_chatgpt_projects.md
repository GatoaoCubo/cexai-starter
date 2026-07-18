# SETUP -- ChatGPT (Projects ou Custom GPT)

Setup do bundle `marketplace_listing` no ChatGPT. Esta capability é uma
projeção de texto pura (mapear uma linha de catálogo em um anúncio ML +
relatório de prontidão) -- não precisa de navegação web, code interpreter
nem DALL-E, então funciona com **fidelidade total** em qualquer plano.
~5 minutos.

## Pré-requisitos

- Conta ChatGPT (o plano free já é suficiente via **Projects**).
- ZERO chaves de API necessárias -- este agente não usa Actions.

## Opção A -- ChatGPT Projects (recomendado, funciona no plano free)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome sugerido: `Marketplace Listing (Channel Projection)`.

### 2. Cole as instruções

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o conteúdo de `system_instruction.md` deste bundle.
3. Cole no campo Instructions do projeto.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua marca
   (nome, tom de voz, valores) antes de usar em produção.

### 3. Suba os 12 arquivos de Knowledge

Em **Files** do projeto, suba os 12 arquivos `P0X_*.md` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Capabilities

Deixe **Web Browsing**, **Code Interpreter** e **DALL-E** desligados -- esta
capability não usa nenhum dos três (veja `customgpt_instructions.json` ->
`capabilities`, todos `false`). Ligar não ajuda e pode distrair o modelo.

### 5. Teste

Inicie uma conversa dentro do project:

> `Mapeie uma cafeteira elétrica 110V para um anúncio no Mercado Livre -- título, preço, categoria, prontidão`

O agente deve:
1. Pedir (ou usar) os campos da linha de catálogo (titulo_ml, descricao,
   categoria_ml, marca, condicao, preco, estoque, fotos, atributos, sku).
2. Mapear cada campo para o payload ML conforme `P01_knowledge.md` e
   `P06_schema.md`.
3. Emitir as 6 seções congeladas (Listagem ML, Preco e Estoque, Fotos,
   Atributos, Descricao, Payload ML) exatamente como descrito em
   `P05_output.md`.
4. Para qualquer dado que faltar, usar o placeholder honesto (ex.: "(sem
   sku)"), nunca inventar.
5. Calcular o gate de prontidão (score/passed/missing_required/notes)
   conforme `P07_evals.md`.

## Opção B -- Custom GPT (plano ChatGPT Plus)

Se preferir um GPT publicável/compartilhável em vez de um Project:

1. **Explore GPTs** -> **Create** -> aba **Configure**.
2. Cole o campo `instructions` de `customgpt_instructions.json` na caixa de
   Instructions do GPT (é o mesmo texto de `system_instruction.md`).
3. Em **Name**, use o campo `name` do mesmo JSON (troque o placeholder da
   marca).
4. Em **Conversation starters**, use o item de `conversation_starters`.
5. Suba os 12 arquivos `P0X_*.md` como Knowledge.
6. Capabilities: mantenha Web Browsing, Code Interpreter e DALL-E
   desligados (mesma razão da Opção A).

## Fidelidade declarada: FULL

Diferente de bundles de pesquisa que dependem de Actions/navegação web
(fidelidade parcial em planos sem Actions), o `marketplace_listing` é uma
tarefa de mapeamento + validação puramente textual. Tanto Projects (free)
quanto Custom GPT (Plus) entregam o **contrato completo** -- nenhuma
funcionalidade fica de fora no plano gratuito.

## Solução de problemas

- **"Ele inventou um preço ou categoria"** -> reforce nas Instructions: "todo
  campo sem dado real vira um placeholder `[fornecer: ...]` ou o texto
  honesto do gerador (ex.: `(sem preco -- obrigatorio)`), nunca um valor
  inventado" (ver `P11_feedback.md`, sinal `fabricated_photo_url`).
- **"Ele truncou o título"** -> o contrato só avisa acima de 60 caracteres,
  nunca trunca (ver `P01_knowledge.md`, seção "Regra de título do ML").
- **"As seções vieram fora de ordem ou renomeadas"** -> cole `P06_schema.md`
  de novo e peça para o agente reler antes de reproduzir -- a ordem e os
  títulos das 6 seções são congelados (gate H05 em `P07_evals.md`).
- **Quer publicar de verdade no Mercado Livre** -> este bundle cobre
  mapear + validar; a publicação HTTP real fica sempre sob controle do
  operador (fora do escopo deste agente).
