# SETUP -- Claude Projects

Setup do bundle codexa-v2 pesquisa em Claude Projects. Variante completa
com knowledge tree + MCP bridges para as 3 actions (TIER 3 via MCP).
~15 minutos (10 min setup + 5 min wiring MCP se quiser TIER 3).

## Pre-requisitos

- Conta Claude (Pro ou Team) com Projects habilitado.
- (Opcional) MCP bridges configurados para firecrawl + brave_search + tavily.
  Voce pode rodar os 3 como MCP servers locais OU usar bridges hospedados.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Pesquisa codexa-v2 (Claude variant)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie TODO o conteudo de `claude/Project_instructions.md`.
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos de `claude/knowledge/`:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects nao tem limite de 20 arquivos (limite e por tamanho total).

### 4. (Opcional) Configure MCP bridges para TIER 3

Se voce quer TIER 3 (firecrawl + brave_search + tavily) via Claude:

#### 4a. Setup MCP bridges localmente

Voce precisa de 3 MCP servers que exponham as APIs como tools. Opcoes:

| Provider | MCP server | Como rodar |
|----------|-----------|------------|
| firecrawl | https://github.com/mendableai/firecrawl-mcp-server | `npm install -g firecrawl-mcp-server` |
| brave_search | https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search | `npx @modelcontextprotocol/server-brave-search` |
| tavily | https://github.com/tavily-ai/tavily-mcp | `npm install -g tavily-mcp` |

#### 4b. Configure `claude/.mcp.json`

O bundle ja inclui um `claude/.mcp.json` skeleton. Edite-o com suas chaves:

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "firecrawl-mcp-server",
      "env": {
        "FIRECRAWL_API_KEY": "fc-..."
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA..."
      }
    },
    "tavily": {
      "command": "tavily-mcp",
      "env": {
        "TAVILY_API_KEY": "tvly-..."
      }
    }
  }
}
```

#### 4c. Configure Claude para usar o MCP

Em Claude Desktop, edite `~/Library/Application Support/Claude/claude_desktop_config.json`
(MacOS) ou equivalent Windows path, e mescle o conteudo do `.mcp.json` acima.

Restart Claude Desktop.

#### 4d. Verifique

Em uma conversa do Project, pergunte:

> "Quais MCP servers estao disponiveis para este Project?"

Claude deve listar firecrawl + brave-search + tavily.

### 5. Teste

Em uma conversa do Project:

> `Pesquisa completa: garrafa termica 500ml inox`

O agente deve:
1. Detectar quais MCP servers estao reachable (se voce wirou).
2. Confirmar categoria + marketplaces + tier preference.
3. Gerar queries.
4. Coletar dados via TIER 3 (se MCP disponivel) ou TIER 1 paste.
5. Entregar relatorio + handoff.

## Fidelidade declarada

- Sem MCP wiring: `partial` (TIER 1 + TIER 2 only)
- Com MCP wiring para 3 providers: `full`

## Vantagens do Claude vs Custom GPT

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|----------------|
| Parallel tool calls | Sequential (OpenAI runs them in series) | Native parallel via tool_use |
| Context window | 128K | 200K |
| Project Knowledge | 20-file limit | sem limite por arquivo (limite total ~30MB) |
| MCP ecosystem | Actions (OpenAPI) | MCP servers (mais flexivel) |
| Cost | Plus ($20/mo) + Action API costs | Pro ($20/mo) + MCP provider costs |

## Solucao de problemas

- **MCP server nao aparece** -> verifique `claude_desktop_config.json` syntax + restart Claude Desktop.
- **Chave invalida** -> teste a chave fora do MCP (curl direto na API).
- **Sem MCP, sem TIER 3** -> use TIER 1 paste, ja funciona bem.
- **Parallel calls falham** -> Claude tool_use natively supports parallel; se falhar,
  use sequential fallback (o tier router cobre).
