# SETUP -- Anuncio no Claude Projects (com MCP opcional + crew dispatch)

Guia para montar o agente "anuncio" como **Claude Project** em claude.ai. Leva ~7 min com MCP opcional, ~3 min sem.

## O que voce vai precisar
- Pasta `claude/` deste bundle (Project_instructions.md + knowledge/ tree + cexai_crew_setup.md + opcional .mcp.json).
- Conta Claude.ai (Pro/Team) -- Projects e free em Pro+.
- (Opcional) Chaves API para upgrade lanes: `FIRECRAWL_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc.

## Passo a passo (3 minutos, sem MCP)

1. **Crie um Project** em claude.ai -> menu lateral -> **Projects** -> **+ New project**. Nome: **"Anuncio (Codexa v2)"**.

2. **Cole as instrucoes.** Abra `claude/Project_instructions.md`, copie TODO o conteudo e cole no campo **Instructions** do project (Claude aceita texto longo aqui).

3. **Suba o conhecimento.** Em "Files" do project, faca upload da pasta `claude/knowledge/` -- 12 arquivos P01..P12.

4. **Pronto.** Inicie uma conversa dentro do project. Forneca os 4 obrigatorios (product_name, marketplace, category, price_brl).

## Passo a passo upgrade -- com MCP (mais 4 min)

5. **Configure MCP servers (opcional).**
   - Em Claude Desktop, edite `~/.config/Claude/claude_desktop_config.json` (Mac/Linux) ou `%APPDATA%\Claude\claude_desktop_config.json` (Windows).
   - Adicione o snippet de `claude/.mcp.json` -- principal: firecrawl-mcp + brave-search-mcp.
   - Defina env vars: `FIRECRAWL_API_KEY=<sua_chave>`, `BRAVE_API_KEY=<sua_chave>` (no shell ou no proprio claude_desktop_config.json).
   - Reinicie o Claude Desktop.

6. **Verifique MCP ativo.** Em uma conversa do project, escreva "que MCP tools voce tem disponivel?" -- deve listar `firecrawl_scrape`, `brave_search` ou similar.

## Crew composable (dispatch via cex_crew.py)

Para anuncios em volume ou para usar os 3 papeis (writer/critic/compliance) como dispatches separados, voce pode rodar o crew via repo CEXAI:

```bash
# Pre-req: ter o repo cex clonado + Python 3.11+ + cex_crew.py
git clone https://github.com/GatoaoCubo/cex.git
cd cex

# Mostra o plano do crew (dry-run)
python _tools/cex_crew.py show anuncio_v5

# Executa o crew para 1 anuncio (charter aponta o produto)
python _tools/cex_crew.py run anuncio_v5 \
    --charter _bundles/codexa-v2/anuncio/cexai/team_charter_anuncio_default.md \
    --execute
```

Cada papel:
- **writer** -- gera cadeia titles -> keywords -> bullets -> description -> faqs.
- **critic** -- aplica rubrica 5D + emite ISSUE_TO_FIX.
- **compliance** -- valida TOS + ANVISA + fabrication patterns.

Detalhes em `claude/cexai_crew_setup.md`.

## Upgrade lanes ativas em Claude Projects

| Capability | Trigger | O que muda vs Custom GPT |
|------------|---------|---------------------------|
| MCP firecrawl | `FIRECRAWL_API_KEY` set | scraping confiavel substitui paste-intake |
| MCP search (brave/tavily) | `BRAVE_API_KEY` set | busca real para benchmark/longtails |
| LLM Judge Council (cross-provider) | `ANTHROPIC_API_KEY` + `GEMINI_API_KEY` set | dim FACTUAL avaliada por 3 judges |
| Crew dispatch (3 papeis paralelos) | repo cex + cex_crew.py | volume + auditabilidade |

Sem nenhuma chave -> degrade silencioso para paste-intake + self-judge (mesmo comportamento do Custom GPT).

## Dicas de uso
- Claude Projects aceita o `Project_instructions.md` em escala MUITO maior que o limite Custom GPT (8000 chars). Pode usar o `00_instructions.md` raiz expandido ou o `Project_instructions.md` ainda mais denso.
- Cada conversa dentro do project carrega TODOS os 12 arquivos como contexto -- alta densidade.
- Para anuncios em portugues com diacritico, Claude Sonnet/Opus respeita encoding UTF-8 nativo.

## Verificacao rapida (smoke test)
Peca: *"Gere um anuncio de Mercado Livre para garrafa termica inox 1L, categoria Casa > Cozinha > Garrafas, preco R$ 89,90, diferenciais: 12h gelado, a prova de vazamento."*

Mesma checklist (titulos 58-60, bullets 250-299, bloco "Suposicoes").

## Powered by
CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei) -- github.com/GatoaoCubo/cex
