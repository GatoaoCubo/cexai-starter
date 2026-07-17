# SETUP -- ChatGPT Projects ENXUTO (plano free)

Setup do bundle codexa-v2 pesquisa no ChatGPT Projects (plano free). Variante
ENXUTO -- 5 arquivos em vez de 12, sem Actions. TIER 1 paste e o unico tier
disponivel (TIER 3 actions nao funcionam em Projects). ~5 minutos.

## Pre-requisitos

- Conta ChatGPT (plano free e suficiente).
- ZERO chaves de API necessarias (TIER 3 nao reachable).

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Pesquisa codexa-v2 (ENXUTO)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (icone de engrenagem).
2. Copie o conteudo de `projects_free/00_instructions.md`.
3. Cole nas Instructions do projeto.

### 3. Suba os 5 arquivos de Files

Em **Files** do projeto, suba **5 arquivos** de `projects_free/`:

- `P01_knowledge.md`
- `P02_model.md`
- `P03_prompt.md`
- `P04_tools.md` -- contem so a parte TIER 1 paste (sem TIER 3 actions)
- `P05_output.md` -- inclui essenciais de P06 (schema) + P07 (gate) + P11 (anti-hallucination)

Tambem suba:
- `LEIA_setup.md` -- guia rapido para usuario final

### 4. Capabilities

Em vez de capabilities por Custom GPT, use o modelo padrao com web habilitado:
- Selecione um modelo que tenha **web search / browsing** ativado (GPT-4o, etc.).
- **Code interpreter** opcional para consolidacao de benchmark.

### 5. Teste

Inicie uma conversa dentro do project:

> `Pesquisa completa: garrafa termica 500ml inox`

O agente deve:
1. Confirmar categoria + marketplaces.
2. Avisar que esta no perfil ENXUTO (TIER 1 paste only).
3. Gerar queries, entregar URLs + template de paste.
4. Esperar voce colar os dados dos 3-5 concorrentes.
5. Entregar relatorio + JSON handoff.

## Fidelidade declarada: PARTIAL

| Razao | Detalhe |
|-------|---------|
| Projects nao tem Actions | TIER 3 (firecrawl + brave + tavily) nao reachable |
| TIER 1 paste e o unico tier disponivel | Voce coleta no seu navegador logado |
| Pillares P06-P12 foldados nos 5 arquivos | Cobertura essencial via P05 enxuto |

## Como o ENXUTO ainda entrega valor

Mesmo sem TIER 3 actions, o ENXUTO mantem:
- Framework completo de geracao de queries (head + longtail + sinonimos)
- Analise de concorrentes (criterios + ranking + gaps)
- Taxonomia de SEO (inbound + outbound + negativas)
- Schema de handoff identico ao Custom GPT FULL
- Anti-hallucination 7-point (preservado)
- Code-block discipline (preservado)

O que voce perde:
- Parallel SERP enumeration (TIER 3b brave)
- Auto page extraction (TIER 3a firecrawl)
- Review/trend context (TIER 3c tavily)
- CRAG-lite per-retrieval scoring (sem retrievals para scorear)

## Upgrade path para Custom GPT FULL

Quando voce upgrade para ChatGPT Plus:
1. Crie um Custom GPT seguindo `SETUP_chatgpt_custom_gpt.md`.
2. Use os 12 arquivos de `knowledge/` em vez dos 5 de `projects_free/`.
3. Configure as 3 Actions (firecrawl + brave + tavily).
4. Fidelidade salta para `full`.

O Project ENXUTO continua funcionando em paralelo.

## Como usar (fluxo tipico no ENXUTO)

1. `Pesquisa completa: garrafa termica 500ml`
2. Agente confirma categoria, marketplaces.
3. Agente gera queries sem acento + entrega URLs de busca + template de paste:
   ```
   === CONCORRENTE 1 - Mercado Livre ===
   URL:
   Titulo:
   Preco atual: R$
   ...
   ```
4. Voce abre 3-5 anuncios no seu navegador logado e cola um bloco por concorrente.
5. Agente extrai os campos, monta a tabela de benchmark, deriva gaps.
6. Entrega relatorio Markdown + JSON handoff.

## Solucao de problemas

- **"Ele inventou precos"** -> reforce: "todo numero precisa de origem
  (paste/browsing/user); sem dado coletado -> [A CONFIRMAR]".
- **Web browsing falha em ML/Shopee** -> esperado (anti-bot). Use TIER 1 paste.
- **Quero TIER 3 actions** -> upgrade para Custom GPT FULL (ChatGPT Plus).
- **Volume de dados grande** -> ative Code Interpreter para consolidacao.
