# SETUP -- Claude Projects

Setup do bundle `leadgen` (Captação de Leads) em Claude Projects. Variante
completa com os 12 arquivos de pillar como Project Knowledge, mais a opção
de conectar MCP bridges de busca/web para o agente localizar leads reais.
~10 minutos (5 min de setup + 5 min de wiring MCP, se quiser).

## Pré-requisitos

- Conta Claude (Pro ou Team) com Projects habilitado.
- (Opcional) Um MCP server de busca web (ex.: `brave-search`, `fetch`) se
  você quiser que o agente tente localizar leads ao vivo em vez de apenas
  estruturar dados que você cola na conversa.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome sugerido: `Captação de Leads (leadgen)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie todo o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.
4. Substitua os marcadores `[fornecer: ...]` pelo nome, tom de voz e
   valores reais da sua marca.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos de pillar deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho
total, ~30MB), então os 12 arquivos cabem com folga.

### 4. (Opcional) Configure um MCP bridge de busca

Se você quer que o agente tente localizar leads reais na web em vez de
apenas depender do que você cola na conversa:

#### 4a. Escolha um MCP server de busca/web

| Provider | MCP server | Como rodar |
|----------|-----------|------------|
| brave_search | https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search | `npx @modelcontextprotocol/server-brave-search` |
| fetch | https://github.com/modelcontextprotocol/servers/tree/main/src/fetch | `uvx mcp-server-fetch` |

#### 4b. Configure o `.mcp.json` do Claude Desktop

Edite `claude_desktop_config.json` (MacOS: `~/Library/Application
Support/Claude/`; Windows: caminho equivalente) e adicione o server
escolhido:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA..."
      }
    }
  }
}
```

#### 4c. Restart e verifique

Restart o Claude Desktop. Em uma conversa do Project, pergunte:

> "Quais MCP servers estão disponíveis para este Project?"

Claude deve listar o `brave-search` (ou o server que você configurou).

### 5. Teste

Em uma conversa do Project:

> `Encontre leads para dentistas em Curitiba a partir de "clínica odontológica" -- marketplace, CNPJ, social`

O agente deve:
1. Detectar se há um MCP de busca disponível (se você configurou o passo 4).
2. Confirmar o perfil e a seed.
3. Percorrer os canais disponíveis, coletando dados reais via MCP quando
   possível, ou pedindo que você cole os dados quando não houver acesso.
4. Entregar a lista tipada de leads + status honesto por fonte + veredito
   go/no-go.

## Fidelidade declarada

- Sem MCP: `parcial` -- o agente estrutura e verifica os dados que você cola
  na conversa, mas não busca sozinho.
- Com MCP de busca configurado: `full` -- o agente também tenta localizar
  leads ao vivo antes de pedir que você complete manualmente.

## Vantagens do Claude vs Custom GPT / Projects do ChatGPT

| Aspecto | Custom GPT / ChatGPT Projects | Claude Projects |
|---------|-----------|----------------|
| Chamadas de ferramenta paralelas | Sequencial (a OpenAI roda em série) | Nativamente paralela via tool_use |
| Janela de contexto | 128K | 200K |
| Project Knowledge | Custom GPT: limite de 20 arquivos; Projects: sem limite de arquivos | Sem limite por arquivo (limite total ~30MB) |
| Ecossistema de ferramentas | Actions (OpenAPI) -- não usadas neste bundle | MCP servers (mais flexível, opcional) |

## Solução de problemas

- **MCP server não aparece** -> verifique a sintaxe do
  `claude_desktop_config.json` e reinicie o Claude Desktop.
- **Chave inválida** -> teste a chave direto na API, fora do MCP.
- **Sem MCP** -> o agente ainda funciona bem: cole os dados que você já
  levantou (planilha, print, lista de contatos) e ele estrutura no formato
  tipado com status honesto por fonte.
- **"Ele inventou um contato"** -> reforce: "todo lead precisa de origem
  real (MCP/paste/CNPJ oficial); o que não tiver confirmação, marque como
  bloqueado ou pulado".
