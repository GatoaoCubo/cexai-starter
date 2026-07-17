# SETUP -- Gemini Gems

Setup do bundle codexa-v2 pesquisa em Gemini Gems. Variante TIER 1 default
com TIER 3 best-effort via Gemini extensions. ~5 minutos.

## Pre-requisitos

- Conta Google + acesso a gemini.google.com.
- (Opcional) Extensions de Search habilitadas para TIER 2 browsing.
- TIER 3 actions: Gemini Gems tem suporte limitado a tools; firecrawl
  pode ser possivel via `url_context` extension (best-effort).

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Va em **Gems** -> **+ Create new Gem**.
3. Nome: `Pesquisa codexa-v2 (Gemini variant)`.
4. Description: `Pesquisa de mercado e-commerce BR (codexa-v2)`.

### 2. Cole as Instructions

1. Abra `gemini/Gem_instructions.md` deste bundle.
2. Copie TODO o conteudo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos de `gemini/knowledge/`:

- `P01_knowledge.md` ... `P12_orchestration.md`

Gemini Gems aceita knowledge files; tamanho total limite varia.

### 4. (Opcional) Configure extensions

Em **Extensions** do Gem:
- **Google Search** -- habilita TIER 2 browsing
- **url_context** -- se disponivel, habilita best-effort TIER 3a firecrawl
  via Gemini deep linking

### 5. Teste

Em uma conversa do Gem:

> `Pesquisa completa: garrafa termica 500ml inox`

O Gem deve:
1. Confirmar categoria + marketplaces.
2. Declarar TIER 1 paste como default (sem TIER 3 actions diretos).
3. Gerar queries sem acento.
4. Entregar URLs de busca + template de paste.
5. Esperar o paste do usuario.
6. Entregar relatorio + handoff.

## Fidelidade declarada: PARTIAL

| Razao | Detalhe |
|-------|---------|
| Gemini Gems tem suporte limitado a tools/actions | TIER 3 nao reachable diretamente |
| TIER 3a firecrawl: best-effort via url_context | Se url_context permite, pode raspar; senao, TIER 1 |
| TIER 3b brave_search: NAO disponivel | Sem extension Brave |
| TIER 3c tavily: NAO disponivel | Sem extension Tavily |
| Search extension cobre parte de TIER 2 browsing | BR-localizado via google search |

## Vantagens vs Claude/Custom GPT

- **Gemini context window grande** (>1M tokens em modelos recentes).
- **Google Search nativo** funciona razoavelmente bem para SERP em sites menores.
- **Multi-modal nativo**: se a sua pesquisa precisa olhar imagens (e.g.
  qualidade visual de listings), Gemini pode ajudar diretamente.

## Limitacoes

- **Sem Actions nativas**: voce nao pode subir os OpenAPI YAMLs como o Custom GPT.
- **MCP nao suportado** (a partir de 2026-05; pode mudar).
- **Modelo de capabilities mais restrito** que Custom GPT.

## Como usar (fluxo tipico no Gem)

1. `Pesquisa completa: tapete de yoga antiderrapante`
2. O Gem confirma categoria + marketplaces.
3. Declara TIER 1 paste default (TIER 3 nao disponivel).
4. Gera queries sem acento.
5. Entrega URLs + template de paste.
6. Voce abre 3-5 anuncios no navegador logado, cola um bloco por concorrente.
7. O Gem extrai os campos, monta tabela, deriva gaps.
8. Entrega relatorio Markdown + JSON handoff.

## Upgrade path

Se voce precisa de TIER 3 actions (firecrawl + brave + tavily) com tier router
+ fallback chain + CRAG-lite:

- **Custom GPT FULL** (ChatGPT Plus) -- ver `SETUP_chatgpt_custom_gpt.md`.
- **Claude Projects com MCP** -- ver `SETUP_claude_projects.md`.

Gemini Gems variant e o setup mais minimal -- ideal para pesquisas
rapidas com TIER 1 paste OU quando voce ja esta no ecosystem Google e
nao quer mudar de plataforma.

## Solucao de problemas

- **Search nao retorna nada para o produto** -> tente queries mais especificas
  (longtails) em vez de heads.
- **url_context nao raspa marketplace** -> esperado (anti-bot); use TIER 1 paste.
- **Quero TIER 3 actions** -> upgrade para Custom GPT FULL ou Claude Projects.
- **Multi-modal**: se quer analisar imagens de concorrentes, anexe a imagem
  no chat e peca para o Gem descreve-la. O Gem multi-modal e bom nisso.
