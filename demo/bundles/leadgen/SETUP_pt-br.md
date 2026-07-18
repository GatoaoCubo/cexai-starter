# SETUP -- leadgen (Captação de Leads) -- guia combinado PT-BR

Guia geral do bundle `leadgen`. Para o setup detalhado por plataforma, veja
os arquivos específicos:

- **ChatGPT (Custom GPT)** -> resumo na Opção A abaixo (ver também `README.md`)
- **ChatGPT Projects** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: este bundle não usa nenhuma Action/API externa -- é um
> agente de conhecimento + instruções puro (research_pipeline). Por isso,
> a fidelidade é praticamente a mesma em qualquer uma das 4 plataformas: o
> que muda entre elas é a janela de contexto, o limite de arquivos e se a
> busca web nativa está ligada ou não.

## Arquivos do bundle (overview)

```
leadgen/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge/Files
  customgpt_instructions.json                  <- config pronta para Custom GPT
  system_instruction.md                        <- COLE como Instructions/system prompt
  README.md                                    <- visão geral + passo a passo de upload
  SETUP_chatgpt_projects.md                    <- guia ChatGPT Projects
  SETUP_claude_projects.md                     <- guia Claude Projects
  SETUP_gemini_gems.md                         <- guia Gemini Gems
  SETUP_pt-br.md                               <- este arquivo
```

## Opção A -- ChatGPT (Custom GPT)

Resumo (passo a passo completo também no `README.md`):

1. Vá em **Explore GPTs -> Create -> Configure**.
2. Suba os 12 arquivos `P0X_*.md` como Knowledge.
3. Cole o campo `instructions` de `customgpt_instructions.json` na caixa
   de Instructions (ou cole `system_instruction.md` direto).
4. Preencha os marcadores `[fornecer: ...]` com o nome, tom de voz e
   valores reais da sua marca.
5. Capabilities: **Web Browsing** ligado se você quer que o agente tente
   localizar leads ao vivo; **Code Interpreter** é opcional.
6. Teste com: `Encontre leads para <perfil> a partir de <seed> --
   marketplace, CNPJ, social`.

## Opção B -- ChatGPT Projects

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo: crie um Project, cole `system_instruction.md` nas Instructions,
suba os 12 arquivos de pillar como Files, escolha um modelo com web search
se quiser busca ao vivo. Fidelidade: `full` (nada é perdido -- este bundle
não tem Actions para comparar).

## Opção C -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo: crie um Project, cole `system_instruction.md` nas Project
Instructions, suba os 12 arquivos de pillar como Knowledge. Opcionalmente,
conecte um MCP server de busca (`brave-search`, `fetch`) para o agente
tentar localizar leads ao vivo. Fidelidade: `parcial` sem MCP, `full` com
MCP de busca configurado.

## Opção D -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo: crie um Gem, cole `system_instruction.md` nas Instructions, suba os
12 arquivos de pillar como Knowledge, habilite a extension **Google
Search** se quiser busca ao vivo. Fidelidade: `parcial` sem Search, `boa`
com Search habilitada.

## Capabilities recomendadas por plataforma

| Capability | Custom GPT | ChatGPT Projects | Claude | Gemini |
|------------|-----------|----------|--------|--------|
| Web Browsing / Search (busca ao vivo) | opcional | opcional (modelo com web) | via MCP (opcional) | extension Google Search (opcional) |
| Code Interpreter | opcional | opcional | nativo (análise de arquivo) | parcial |
| Actions/MCP externos | não usados neste bundle | não disponível | MCP (opcional) | não suportado |
| DALL-E | não | não | não | não |

## Como o agente coleta os leads (honestidade por fonte)

Este bundle não empacota nenhuma ferramenta de scraping ao vivo -- o que
ele empacota é a **metodologia** (os 12 pillars: quais canais existem,
como pontuar e verificar, como decidir o veredito go/no-go) mais o
**guardrail de honestidade**. Na prática, isso significa:

- **Com busca web/MCP ligado (qualquer plataforma)**: o agente tenta
  localizar leads públicos nos canais disponíveis (marketplace B2C, CNPJ
  B2B, social UGC) e cita a origem de cada um.
- **Sem busca ligada, ou para canais que exigem login/API paga** (ex.:
  consulta oficial de CNPJ, redes sociais autenticadas): o agente marca o
  canal como `bloqueado` ou `pulado` -- **nunca inventa um contato** para
  preencher a lacuna.
- **Você sempre pode colar dados**: se já tem uma planilha, export de CRM
  ou print de uma listagem, cole na conversa; o agente estrutura os dados
  no formato tipado de lead, com a mesma disciplina de honestidade.

## Como usar (fluxo típico)

1. Diga o perfil e a seed: `Encontre leads para <perfil> a partir de
   <seed> -- marketplace, CNPJ, social`.
2. O agente confirma o perfil, a seed e quais canais vai percorrer.
3. Ele coleta o que conseguir ao vivo (se a plataforma tiver busca/MCP
   ligado) e pede que você cole o que faltar.
4. No fim, você recebe a **lista tipada de leads** com status honesto por
   fonte (`ok` / `bloqueado` / `pulado`) e o **veredito go/no-go**.
5. Essa lista é o que você importa no seu CRM (a entidade `leads`).

## Solução de problemas

- **"Ele inventou um contato"** -> os 12 pillars proibem isso
  explicitamente. Reforce: "todo lead precisa de origem real (busca/MCP/
  paste/CNPJ oficial); o que não tiver confirmação, marque como bloqueado
  ou pulado".
- **Busca não alcança um canal (CNPJ, social autenticado)** -> esperado;
  nenhuma das 4 plataformas contorna login/API paga automaticamente. Cole
  os dados que você já tem.
- **Os placeholders `[fornecer: ...]` aparecem na resposta** -> volte nas
  Instructions/system prompt e preencha nome da marca, tom de voz e
  valores antes de usar com clientes reais.
- **Quero mais capacidade de busca ao vivo** -> Claude Projects com MCP de
  busca configurado (`SETUP_claude_projects.md`) é a opção mais flexível
  hoje entre as 4.
