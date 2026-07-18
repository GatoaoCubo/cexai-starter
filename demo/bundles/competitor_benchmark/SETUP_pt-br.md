# SETUP -- Matriz de Benchmark de Concorrentes -- guia geral combinado

Guia geral do pacote. Para o passo a passo detalhado por runtime, veja os
arquivos específicos:

- **ChatGPT Projects (free)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`
- **ChatGPT (Custom GPT)** -> resumo abaixo (Opção A); usa
  `customgpt_instructions.json` diretamente, sem arquivo dedicado.

> Este pacote não usa Actions externas, chaves de API ou tiers de coleta de
> dados -- os mesmos 12 arquivos + a mesma instrução funcionam de forma
> idêntica nos 4 runtimes. A única diferença entre eles é ONDE você cola a
> instrução e sobe os arquivos, não O QUE o agente sabe fazer.

## Arquivos do bundle (visão geral)

```
competitor_benchmark/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge/Files
  customgpt_instructions.json                 <- config pronta para Custom GPT (name, description,
                                                  instructions, conversation_starters)
  system_instruction.md                       <- a mesma instrução, pronta para colar em
                                                  Claude Projects, Gemini Gems ou qualquer IA
  README.md                                   <- visão geral + upload rápido (3+1 caminhos)
  SETUP_chatgpt_projects.md                   <- passo a passo ChatGPT Projects (free)
  SETUP_claude_projects.md                    <- passo a passo Claude Projects
  SETUP_gemini_gems.md                        <- passo a passo Gemini Gems
  SETUP_pt-br.md                              <- este arquivo (visão combinada)
```

## Opção A -- ChatGPT (Custom GPT) -- recomendado se você tem ChatGPT Plus

1. Acesse **chatgpt.com** -> **Explore GPTs** -> **+ Create** -> aba **Configure**.
2. **Name**: use o campo `name` de `customgpt_instructions.json` (troque o
   marcador `[fornecer: nome da marca ...]` pelo nome real da sua marca).
3. **Description**: use o campo `description` do mesmo arquivo.
4. **Instructions**: copie o campo `instructions` (JSON) e cole na caixa de
   Instructions -- é o mesmo texto de `system_instruction.md`, só que
   escapado como string JSON.
5. **Knowledge**: suba os 12 arquivos `P01_knowledge.md` ... `P12_orchestration.md`.
6. **Conversation starters**: use o array `conversation_starters` do JSON
   (hoje contém: "Comparar `<produto>` com `<concorrentes>` em preço,
   funcionalidades e posicionamento").
7. **Capabilities**: Web Browsing opcional (pesquisa pública de
   concorrentes); Code Interpreter opcional (consolidação de tabelas);
   DALL-E não usado por este agente.
8. Salve e escolha a visibilidade (Only me / Anyone with a link / Public).
9. Teste com o conversation starter acima.

Nenhuma Action, MCP ou chave de API é necessária -- este pacote é
100% Knowledge + Instructions.

## Opção B -- ChatGPT Projects (free)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo: crie um Project -> cole `system_instruction.md` (ou o campo
`instructions` do JSON) nas Instructions -> suba os 12 arquivos como Files
-> teste. ~5 minutos, plano free é suficiente.

## Opção C -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo: crie um Project -> cole `system_instruction.md` nas Project
Instructions -> suba os 12 arquivos como Knowledge -> teste. ~10 minutos.

## Opção D -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo: crie um Gem -> cole `system_instruction.md` nas Instructions ->
suba os 12 arquivos como Knowledge -> (opcional) habilite Google Search ->
teste. ~5 minutos.

## Comparação rápida entre runtimes

| Aspecto | Custom GPT | ChatGPT Projects | Claude Projects | Gemini Gems |
|---------|-----------|-------------------|------------------|-------------|
| Plano mínimo | Plus | Free | Free/Pro | Free (conta Google) |
| Arquivos de Knowledge | 12 | 12 | 12 | 12 |
| Actions/API keys | Nenhuma | Nenhuma | Nenhuma | Nenhuma |
| Web/Search nativo | Web Browsing (opcional) | Web Browsing (opcional) | não tem equivalente nativo | Google Search (extension opcional) |
| Publicável/compartilhável | Sim (Explore GPTs) | Não (privado ao Project) | Não (privado ao Project) | Sim (compartilhar Gem) |
| Context window | 128K | 128K | até 200K | 1M+ (modelos recentes) |

## Como o agente coleta os dados de concorrentes

Este pacote não tem Actions nem tiers de scraping -- a coleta é sempre uma
destas duas formas, e o agente é transparente sobre qual está usando:

1. **Você fornece os dados diretamente na conversa** (copiar e colar da
   página do concorrente, uma planilha, um print, etc.). Caminho padrão,
   funciona em qualquer runtime, sempre disponível.
2. **O agente pesquisa a web** -- se a capability de Web Browsing/Search
   estiver habilitada (ChatGPT ou Gemini). Best-effort; páginas com
   proteção anti-bot podem falhar, e aí o agente pede para você colar
   os dados manualmente.

Em ambos os casos, o guardrail é o mesmo: **nenhum dado sem fonte** entra
na matriz final sem o marcador `[fornecer: ...]` ou uma citação explícita.

## Como usar (fluxo típico, qualquer runtime)

1. Diga o que quer comparar: `Comparar [meu produto] com [concorrente A] e [concorrente B] em preço, funcionalidades e posicionamento`.
2. O agente confirma os concorrentes e as dimensões (preço, funcionalidades,
   suporte, integrações, etc.) -- ou aceita os que você já deu.
3. Ele pede (ou busca, se Web Browsing/Search estiver ligado) os dados que
   faltam.
4. Ele entrega a matriz estruturada: feature parity grid (Sim/Não/Parcial/
   Roadmap Q# AAAA), posicionamento estilo Gartner MQ, battle card
   (nos vs concorrente primário, com par objeção-contra-argumento) e
   comparação de preços.
5. Qualquer dado sem fonte vem marcado `[fornecer: ...]` em vez de
   inventado.

## Solução de problemas (comum aos 4 runtimes)

- **"Ele inventou preço, nome ou funcionalidade de concorrente"** -> P06/P07/P11
  proibem isso explicitamente. Reforce: "toda alegação competitiva precisa
  de fonte primária com data de acesso; sem dado real, use [fornecer: ...]".
- **"Ele usou superlativo sem citar analista"** ("líder de mercado",
  "melhor da categoria") -> peça a fonte (Gartner, Forrester, G2) ou peça
  para reescrever sem o superlativo.
- **"Faltou o battle card ou o contra-argumento de objeção"** -> peça
  explicitamente: "monte o battle card com um par objeção-contra-argumento
  para o concorrente primário" (isso é um gate HARD -- H06 -- em `P07_evals.md`).
- **"A tabela ficou vaga (rápido/lento, caro/barato)"** -> peça um valor
  mensurável; a regra do schema (`P06_schema.md`) é Sim/Não/Parcial/Roadmap
  ou número, nunca adjetivo solto.
- **Marcadores `[fornecer: ...]` nunca desaparecem** -> normal até você
  preencher a Instruction com os dados reais da sua marca (nome, tom de
  voz, valores) -- o agente nunca inventa esses campos por você.

## Compatibilidade entre runtimes

Os 4 caminhos usam exatamente os mesmos 12 arquivos de pilar e a mesma
instrução -- não há "versão reduzida" nem "versão completa" deste pacote.
A diferença entre eles é puramente onde você cola/sobe cada peça e quais
capabilities nativas (Web Browsing / Google Search) estão disponíveis.
