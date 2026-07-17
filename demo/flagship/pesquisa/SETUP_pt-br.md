# SETUP -- pesquisa (codexa-v2) -- guia combinado PT-BR

Guia geral do bundle. Para setup detalhado por runtime, veja os arquivos
especificos:

- **Custom GPT (Plus)** -> `SETUP_chatgpt_custom_gpt.md`
- **ChatGPT Projects (free)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade do v2**: `full` (era `partial ~70%` no v1). A versao codexa-v2
> recupera ~95% da capacidade do retriever de producao usando 3 actions
> opcionais (firecrawl + brave_search + tavily) + tier router + fallback
> chain + CRAG-lite + CRITIC verify.

## Arquivos do bundle (overview)

```
pesquisa/
  00_instructions.md            <- COLE no campo "Instructions" do Custom GPT
  knowledge/                    <- SUBA os 12 como "Knowledge"
    P01_knowledge.md ... P12_orchestration.md
  actions/                      <- 3 OpenAPI specs (so Custom GPT FULL)
    firecrawl_action.yaml
    brave_search_action.yaml
    tavily_search_action.yaml
  projects_free/                <- 5 arquivos para ChatGPT Projects (free plan)
  claude/                       <- variant Claude Projects
  gemini/                       <- variant Gemini Gems
  cexai/                        <- artifacts typed CEXAI (source of truth)
  manifest.yaml                 <- metadados (NAO sobe)
  CONVENTION.md                 <- constitution (NAO sobe)
  CONVENTION_CEXAI_DELTA.md     <- annex v2 (NAO sobe)
  README.md                     <- frame competitivo + setup overview
  SETUP_*.md                    <- guias de setup (este + 4 especificos)
```

## Opcao A -- Custom GPT (ChatGPT Plus) -- recomendado

Veja `SETUP_chatgpt_custom_gpt.md` para o passo-a-passo completo.

Resumo:
1. Crie um Custom GPT em chatgpt.com.
2. Cole `00_instructions.md` no campo Instructions (6042 chars, cabe no limite 8000).
3. Suba os 12 arquivos de `knowledge/` como Knowledge.
4. (Opcional) Configure as 3 Actions usando os YAMLs de `actions/` com suas chaves de API:
   - `${FIRECRAWL_API_KEY}` (firecrawl.dev, free 500/mo)
   - `${BRAVE_API_KEY}` (api.search.brave.com, free 2000/mo)
   - `${TAVILY_API_KEY}` (tavily.com, free 1000/mo)
5. Marque capabilities: Web Browsing (TIER 2) + Code Interpreter (consolidacao).
6. Teste com: `Pesquisa completa: garrafa termica 500ml inox`.

## Opcao B -- ChatGPT Projects (free) -- ENXUTO

Veja `SETUP_chatgpt_projects.md` para o passo-a-passo completo.

Resumo:
1. Crie um Project em chatgpt.com.
2. Cole `projects_free/00_instructions.md` nas Instructions do projeto.
3. Suba os 5 arquivos de `projects_free/` como Files.
4. Modelo com web habilitado para TIER 2.
5. Sem Actions (Projects nao tem o campo). Voce so usa TIER 1 paste.
6. Fidelidade declarada: `partial` (TIER 3 nao reachable; documente como
   upgrade path para Custom GPT).

## Opcao C -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo-a-passo completo.

Resumo:
1. Crie um Claude Project.
2. Cole `claude/Project_instructions.md` nas Instructions.
3. Suba `claude/knowledge/Pxx_*.md` como Knowledge.
4. (Opcional) Wire `claude/.mcp.json` apontando para MCP bridges seus para
   firecrawl + brave_search + tavily.
5. Fidelidade: `full` se MCP wiring; `partial` so com TIER 1.

## Opcao D -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo-a-passo completo.

Resumo:
1. Crie um Gem em gemini.google.com.
2. Cole `gemini/Gem_instructions.md` nas Instructions.
3. Suba `gemini/knowledge/Pxx_*.md` como retrieval knowledge.
4. Capabilities: Search + Code execution (se disponiveis).
5. TIER 3 best-effort via Gemini extensions (firecrawl maybe via url_context).
6. Fidelidade: `partial` (TIER 1 default, TIER 3 incomplete).

## Capabilities recomendadas por runtime

| Capability | Custom GPT | Projects | Claude | Gemini |
|------------|-----------|----------|--------|--------|
| Web Browsing (TIER 2) | YES | YES (modelo com web) | tool_use native | search extension |
| Code Interpreter | OPCIONAL | OPCIONAL | YES | partial |
| Action firecrawl | YES | NO | via MCP | url_context (best-effort) |
| Action brave_search | YES | NO | via MCP | NO |
| Action tavily | YES | NO | via MCP | NO |
| DALL-E | NO | NO | NO | NO |

## Como o agente coleta dados (3 tiers + 3 actions)

A coleta de preco/vendas/reviews dos concorrentes tem 3 niveis (detalhe em
`knowledge/P04_tools.md`):

- **TIER 1 PASTE (default, gratis, todos runtimes)**: o agente diz quais
  anuncios abrir e da um template; voce abre no seu navegador logado
  (anti-bot contornado por sessao humana) e cola os campos. Caminho recomendado.
- **TIER 2 Web browsing nativo**: o agente tenta abrir paginas. Funciona em
  paginas sem anti-bot, mas e **parcial e nao confiavel** em ML/Shopee/Amazon.
- **TIER 3a/b/c -- 3 Actions** (so Custom GPT FULL, opcional): restauram o
  scraping real + SERP enumeration + research context. Exigem 3 chaves.

## Como usar (fluxo tipico)

1. Diga o produto: `Pesquisa completa: tapete de yoga antiderrapante`.
2. O agente confirma a categoria, os marketplaces e qual TIER de coleta usar.
3. Ele gera as queries (sem acento) e te entrega as URLs de busca + template.
4. **TIER 1**: voce abre 3-5 anuncios no seu navegador logado e cola os campos.
   (Ou, com TIER 3, ele raspa via Actions; com TIER 2, ele tenta navegar.)
5. No fim, recebe o **relatorio Markdown** + o **bloco JSON de handoff** +
   `Confidence X.X/10` + o bloco "Suposicoes e dados a confirmar".
6. O handoff e o que voce entrega ao agente de **anuncio**.

## Solucao de problemas

- **"Ele inventou precos"** -> P06/P07/P11 proibem. Reforce: "todo numero
  precisa de origem (paste/browsing/firecrawl/brave/tavily/user); o que
  faltar, marque [A CONFIRMAR]".
- **Web browsing parcial em ML/Shopee** -> e esperado (anti-bot). Use TIER 1
  ou configure as 3 Actions (TIER 3) para scraping real.
- **Action 402 (creditos)** -> firecrawl quota esgotada. O fallback chain
  automatico tenta tavily extract, depois TIER 1 paste.
- **Quero apenas brave + tavily, nao firecrawl** -> setar
  `enable_firecrawl: false` nas Instructions (ver P09 feature flags).
- **Queries com acento** -> queries sem acento (padrao marketplace);
  so o relatorio usa acento.
- **Categoria nao perguntada** -> diga explicitamente no primeiro prompt.

## Compatibilidade com pesquisa-v1

Voce ja usava o codexa-v1 pesquisa bundle? codexa-v2 e compativel:
- Mesma estrutura de 12 pilares + 00_instructions.
- Mesmo schema de input (PesquisaRequest) + output (MercadoResponse + ConcorrentesResponse + TendenciasResponse).
- Os campos JSON nao mudaram (head_terms, longtails, synonyms, marketplace_data, etc.).

O que mudou:
- Nome canonico do agente: era satellite-named, agora e simplesmente `pesquisa` (D2 -- drop satellite naming).
- `data_sources` enum: adiciona `firecrawl`, `brave`, `tavily` ao lado dos legados.
- 2 novas Actions (brave_search, tavily) + firecrawl hardened.
- Tier router + fallback chain + CRAG-lite + CRITIC verify.
- 4 runtime variants (era so Custom GPT + Projects).

Se voce ja tem um Custom GPT v1 rodando, basta:
1. Substituir o `00_instructions.md` no campo Instructions.
2. Substituir os 12 arquivos de Knowledge.
3. Adicionar as 2 novas Actions (brave_search + tavily) + atualizar firecrawl.
4. Configurar as chaves brave + tavily (ja tinha firecrawl).
