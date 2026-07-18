---
kind: tools
id: bld_tools_research_pipeline
pillar: P04
llm_function: CALL
purpose: Ferramentas, APIs e fontes de dados disponíveis para o research pipeline
quality: null
title: "Ferramentas: Pipeline de Pesquisa"
version: "1.0.0"
author: n03_builder
tags: [research_pipeline, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos para a construção de pipelines de pesquisa, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de pipeline de pesquisa"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [research pipeline construction, tools research pipeline, research_pipeline, builder, examples, https://google.serper.dev/search, https://api.exa.ai/search, https://api.search.brave.com, https://api.tavily.com/search, npx -y firecrawl-mcp]
density_score: 0.90
related:
  - p01_kc_source_catalog
  - ex_research_pipeline_ecommerce_br
  - p04_tool_mcp_config
  - bld_knowledge_card_search_tool
  - bld_tools_model_provider
  - p04_ss_tier_router
  - mcp_server_firecrawl_anúncio
  - n06_api_access_pricing
  - p04_browser_scraping_config_n01
  - kc_api_reference
---
# Ferramentas: research-pipeline-builder

## Catálogo de Fontes de Dados (30+ fontes)

### Inbound -- Fontes de Marketplace / Produto
| Fonte | API/Método | Autenticação | Custo | Dados |
|--------|-----------|------|------|------|
| MercadoLivre | REST API v3 | APP_ID+SECRET | Grátis (com rate limit) | title, price, sold_qty, seller, reviews |
| Shopee | Affiliate API + Firecrawl | API key | créditos Firecrawl | title, price, shop_rating, flash_sale |
| Amazon BR | Keepa API + Firecrawl | KEEPA_KEY | €19/mês | title, price, BSR, reviews, price_history |
| Magalu | Firecrawl deep scrape | FIRECRAWL_KEY | créditos | title, price, rating, seller |
| Americanas | Firecrawl deep scrape | FIRECRAWL_KEY | créditos | title, price, rating |
| Casas Bahia | Firecrawl deep scrape | FIRECRAWL_KEY | créditos | title, price, rating |
| Shein | Firecrawl deep scrape | FIRECRAWL_KEY | créditos | title, price, reviews |
| Temu | Firecrawl deep scrape | FIRECRAWL_KEY | créditos | title, price, sold_qty |

### Search -- Motores de Busca Web
| Fonte | API | Autenticação | Custo | Especialidade |
|--------|-----|------|------|-----------|
| Serper | `https://google.serper.dev/search` | SERPER_API_KEY | $0.30/1K | SERP do Google |
| Exa | `https://api.exa.ai/search` | EXA_API_KEY | $0.10/query | Neural (artigos, docs) |
| Gemini Search | Grounding da API Gemini | GOOGLE_API_KEY | incluso | grounding do Google |
| OpenAI Search | Responses API web_search | OPENAI_API_KEY | por token | busca web do GPT |
| Brave | `https://api.search.brave.com` | BRAVE_API_KEY | Tier gratuito 2K/mês | Focado em privacidade |
| Tavily | `https://api.tavily.com/search` | TAVILY_API_KEY | Tier gratuito 1K/mês | Qualidade de pesquisa |

### Outbound -- Social / Reviews / Comunidade
| Fonte | API/Método | Autenticação | Dados |
|--------|-----------|------|------|
| YouTube | Data API v3 + transcrições | YOUTUBE_API_KEY | vídeos, transcrições, comentários |
| Reddit | OAuth REST API | REDDIT_CLIENT_ID | posts, comentários, sentimento |
| ReclameAqui | Scrape via Firecrawl | FIRECRAWL_KEY | reclamações, avaliações, respostas |
| Twitter/X | Firecrawl + Serper | varia | posts, engajamento, sentimento |

### Trends -- Rastreamento de Preço / Tendência
| Fonte | API | Autenticação | Dados |
|--------|-----|------|------|
| Google Trends | pytrends (não oficial) | nenhuma | volume de busca, queries relacionadas |
| Keepa | REST API | KEEPA_KEY | histórico de preço da Amazon, BSR |

### RAG -- Conhecimento Interno
| Fonte | Método | Dados |
|--------|--------|------|
| Docs locais | Embedding + busca vetorial | Documentos da empresa |
| Supabase | pgvector | Base de conhecimento com embeddings |

## Ferramentas MCP (para o N01 Claude CLI)
| MCP | Comando | Finalidade |
|-----|---------|---------|
| firecrawl | `npx -y firecrawl-mcp` | Scraping profundo de marketplaces |
| fetch | `uvx mcp-server-fetch` | URL → markdown |
| brave-search | `npx @anthropic/mcp-server-brave-search` | Busca web |
| markitdown | `npx -y markitdown-mcp` | PDF/DOCX → markdown |

## Roteamento Multi-Modelo
| Tarefa | Modelo | Por que |
|------|-------|-----|
| Extração | gemini-2.5-flash | Dados estruturados, 40x mais barato |
| Raciocínio | gpt-5-mini / claude-sonnet | Análise complexa |
| Volume social | gemini-2.5-flash | Alto volume, baixo custo |
| Verificação CRITIC | o4-mini | Modelo de raciocínio captura erros |

## Permissões de Ferramentas

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDO | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| NEGADO | Write, Edit | Explicitamente bloqueado |
| EFETIVO | Bash, Glob, Grep, Read | PERMITIDO exceto NEGADO |


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_source_catalog]] | upstream | 0.58 |
| [[ex_research_pipeline_ecommerce_br]] | related | 0.44 |
| [[p04_tool_mcp_config]] | related | 0.29 |
| [[bld_knowledge_card_search_tool]] | upstream | 0.27 |
| [[bld_tools_model_provider]] | sibling | 0.26 |
| [[p04_ss_tier_router]] | related | 0.26 |
| [[mcp_server_firecrawl_anúncio]] | related | 0.26 |
| [[n06_api_access_pricing]] | downstream | 0.26 |
| [[p04_browser_scraping_config_n01]] | related | 0.25 |
| [[kc_api_reference]] | upstream | 0.24 |
