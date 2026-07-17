# SETUP -- Custom GPT FULL (ChatGPT Plus)

Setup completo para distribuicao pesquisa-v2 no Custom GPT. ~10 minutos
totais (5 min de upload + 5 min para configurar as 3 chaves de API).

## Pre-requisitos

- Conta ChatGPT Plus (necessario para criar Custom GPTs com Actions).
- (Opcional) 3 chaves de API para TIER 3: firecrawl + brave_search + tavily.
  Sem chaves, o agente funciona em TIER 1 paste apenas (default sempre-free).

## Passo a passo

### 1. Crie o Custom GPT

1. Acesse **chatgpt.com** -> menu lateral -> **Explore GPTs** -> **+ Create**.
2. Va na aba **Configure**.
3. **Name**: `Pesquisa de Mercado E-commerce BR (codexa-v2)`
4. **Description**: `Pesquisa de mercado e-commerce BR: keywords, concorrentes, precos e SEO. 3 actions opcionais (firecrawl + brave_search + tavily) com tier router e fallback chain.`

### 2. Cole as Instructions

1. Abra `00_instructions.md` deste bundle.
2. Copie TODO o conteudo (6042 caracteres -- cabe no limite 8000 com folga).
3. Cole no campo **Instructions**.

### 3. Suba os 12 arquivos de Knowledge

1. Clique em **Upload files**.
2. Suba os **12 arquivos** de `knowledge/`:
   - `P01_knowledge.md`
   - `P02_model.md`
   - `P03_prompt.md`
   - `P04_tools.md`
   - `P05_output.md`
   - `P06_schema.md`
   - `P07_evaluation.md`
   - `P08_architecture.md`
   - `P09_config.md`
   - `P10_memory.md`
   - `P11_feedback.md`
   - `P12_orchestration.md`
3. Confirme que aparecem todos os 12.

> Custom GPT tem limite de 20 arquivos por GPT. 12 + 0 = 12, dentro do limite.

### 4. Configure capabilities

Marque:
- **Web Browsing** -- essencial para TIER 2 (best-effort fallback).
- **Code Interpreter & Data Analysis** -- opcional, util para consolidar
  benchmark e calcular sweet spot.
- **DALL-E Image Generation** -- NAO usado por este agente.

### 5. (Opcional mas RECOMENDADO) Configure as 3 Actions

#### TIER 3a -- firecrawl

1. Crie uma conta em **firecrawl.dev** e gere uma **API key** (`fc-...`).
   Free tier: 500 credits/mo.
2. No Custom GPT, va em **Configure -> Actions -> Create new action**.
3. Em **Schema**, cole TODO o conteudo de `actions/firecrawl_action.yaml`.
4. Em **Authentication**:
   - Type: **API Key**
   - Auth Type: **Bearer**
   - API Key: cole sua chave `fc-...`
5. Salve.

#### TIER 3b -- brave_search (NOVO em v2)

1. Crie uma conta em **api.search.brave.com** -> **Get Started**.
   Plano grátis: 2000 queries/mo.
2. Gere uma chave (formato `BSA...`).
3. No Custom GPT, va em **Configure -> Actions -> Create new action**.
4. Em **Schema**, cole o conteudo de `actions/brave_search_action.yaml`.
5. Em **Authentication**:
   - Type: **API Key**
   - Auth Type: **Custom**
   - Custom Header Name: `X-Subscription-Token`
   - API Key: cole sua chave Brave
6. Salve.

#### TIER 3c -- tavily (NOVO em v2)

1. Crie uma conta em **tavily.com** -> **Get Free API Key**.
   Plano grátis: 1000 queries/mo.
2. Gere uma chave (formato `tvly-...`).
3. No Custom GPT, va em **Configure -> Actions -> Create new action**.
4. Em **Schema**, cole o conteudo de `actions/tavily_search_action.yaml`.
5. Em **Authentication**:
   - Type: **API Key**
   - QUIRK: Tavily prefere a chave NO BODY da requisicao como campo `api_key`.
     O schema usa um Custom Header como compromise. Configure assim:
     - Auth Type: **Custom**
     - Custom Header Name: `X-Tavily-Key`
     - API Key: cole sua chave `tvly-...`
   - Alternativamente, voce pode adicionar o campo `api_key` manualmente
     no body de cada chamada (veja a documentacao oficial Tavily).
6. Salve.

### 6. Conversation starters

Adicione algumas sugestoes:

- `Pesquisa completa: garrafa termica 500ml inox`
- `Analise os concorrentes de creme hidratante facial no Mercado Livre`
- `Gere queries de busca para fone bluetooth esportivo`
- `Pesquisa enxuta (so TIER 1 paste): tapete de yoga`

### 7. Salvar + publicar

1. Clique em **Create/Update**.
2. Escolha visibilidade:
   - **Only me** (privado, recomendado para testes)
   - **Anyone with a link** (compartilhavel)
   - **Public** (listado em Explore GPTs)

### 8. Teste

Envie no GPT:

> `Pesquisa completa: garrafa termica 500ml inox`

O agente deve:
1. Confirmar a categoria + marketplaces (ou aceitar defaults).
2. Perguntar qual TIER usar (default TIER 1 se voce nao tiver as chaves
   configuradas; oferece TIER 3 se houver).
3. Gerar queries sem acento, com modificadores de compra.
4. Coletar dados (via TIER 1 paste OU via Actions se configuradas).
5. Entregar relatorio Markdown + JSON handoff + Confidence X.X/10.

## Verificacao da configuracao

Apos setup, voce pode pedir ao agente:

> `Qual a sua configuracao de TIER atual?`

Ele deve listar:
- TIER 1 paste: SEMPRE disponivel
- TIER 2 browsing: ATIVO (Web Browsing capability)
- TIER 3a firecrawl: ATIVO/INATIVO (depende de Actions)
- TIER 3b brave_search: ATIVO/INATIVO
- TIER 3c tavily: ATIVO/INATIVO

## Limites e quotas

Cada Action consome a sua quota de provider. Average per pesquisa:
- firecrawl: 3-5 scrapes (de 500 free/mo) = ~100 pesquisas/mo
- brave_search: 5 SERP queries (de 2000 free/mo) = ~400 pesquisas/mo
- tavily: 2-3 queries (de 1000 free/mo) = ~333 pesquisas/mo

Bottleneck (free tier combined): ~100 pesquisas/mo, limitado por firecrawl.
Cache (P10) estende para ~200-300 com re-references.

## Solucao de problemas

- **Action 401** -> chave invalida ou ausente. Verifique no painel do provider.
- **Action 402 (firecrawl)** -> creditos esgotados. Fallback automatico para tavily extract -> TIER 1 paste.
- **Action 429** -> rate limit. Espera 60s e retry (automatico).
- **"Pagina vazia"** -> anti-bot. Tente com waitFor=12000 ou use TIER 1 paste.
- **Confianca < 8.0 consistente** -> falta de dados; colete mais via TIER 1 paste.
- **GPT pergunta a mesma coisa varias vezes** -> reforce: "lembre o que ja confirmamos
  (produto, categoria) e nao repergunte (P10 memory)".
