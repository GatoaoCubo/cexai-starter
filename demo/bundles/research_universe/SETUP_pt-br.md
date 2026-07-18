# SETUP -- Universo de Pesquisa (Cérebro Multi-Fonte) -- guia geral combinado

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
research_universe/
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
   (hoje contém: "Pesquise `<produto/marca/CNPJ>` -- firmografia, social,
   reputação, SEO e perguntas").
7. **Capabilities**: Web Browsing opcional (pesquisa pública da semente);
   Code Interpreter opcional (consolidação de trilhas); DALL-E não usado
   por este agente.
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

## O mecanismo central: status honesto por trilha

Este pacote roda UMA semente através de 6 trilhas independentes, e cada uma
reporta seu próprio status -- este é o comportamento mais importante do
agente (detalhe em `P06_schema.md` e `P07_evals.md`):

| Trilha | O que cobre |
|--------|--------------|
| Firmografia (CNPJ/IBGE) | Razão social, CNAE, porte, situação cadastral |
| Sinal Social (App Store / Reddit / YouTube) | Avaliações, menções, tom geral |
| Reputação (Reclame Aqui) | Índice de reputação, % respondidas/resolvidas |
| Sentimento em PT | Positivo/neutro/negativo sobre texto já coletado |
| Palavras-chave de SEO | Termos + intenção de busca relacionados a semente |
| Perguntas Multi-Perspectiva | Perguntas por papel: cliente, concorrente, investidor/regulador, parceiro |

Cada trilha fecha com um de 3 status (o rótulo técnico fica em inglês, já
que é o valor de contrato original desta capacidade):
- **`ok`** -- dado real coletado, com fonte + data de acesso.
- **`blocked`** -- a fonte existe, mas não foi acessada nesta sessão/ambiente.
- **`skipped`** -- a trilha não se aplica a este tipo de semente.

## Como o agente coleta os dados da semente

Este pacote não tem Actions nem chaves de API -- a coleta é sempre uma
destas duas formas, e o agente é transparente sobre qual está usando:

1. **Você fornece os dados diretamente na conversa** (print de app store,
   texto da página do Reclame Aqui, resultado de consulta de CNPJ, etc.).
   Caminho padrão, funciona em qualquer runtime, sempre disponível.
2. **O agente pesquisa a web** -- se a capability de Web Browsing/Search
   estiver habilitada (ChatGPT ou Gemini). Best-effort; fontes com proteção
   anti-bot ou login podem falhar, e aí a trilha correspondente fica
   `blocked` e o agente pede para você colar os dados manualmente.

Em ambos os casos, o guardrail é o mesmo: **nenhum dado sem fonte** entra
no relatório final como `ok` -- sem fonte, a trilha é `blocked`, nunca
inventada.

## Como usar (fluxo típico, qualquer runtime)

1. Diga a semente: `Pesquise [empresa/produto/CNPJ] -- firmografia, social, reputação, SEO e perguntas`.
2. O agente confirma a semente e classifica o tipo (produto, marca, CNPJ,
   empresa, palavra-chave ou `store:id`) -- e decide quais das 6 trilhas se
   aplicam.
3. Ele pede (ou busca, se Web Browsing/Search estiver ligado) os dados que
   faltam.
4. Ele entrega o relatório unificado: as 6 trilhas + a Tabela de Status por
   Trilha (`ok`/`blocked`/`skipped`, cada uma com motivo quando não for
   `ok`) + a Procedência Consolidada.
5. Qualquer dado sem fonte vem marcado `blocked` em vez de inventado.

## Solução de problemas (comum aos 4 runtimes)

- **"Ele inventou um CNPJ, um índice de reputação ou um volume de busca"**
  -> P06/P07/P11 proibem isso explicitamente. Reforce: "toda trilha ok
  precisa de fonte primária com data de acesso; sem dado real, marque a
  trilha como blocked".
- **"Ele confundiu blocked com skipped"** -> peça a reclassificação:
  `skipped` = não se aplica a esta semente; `blocked` = a fonte existe mas
  não foi acessada agora (isso é um gate HARD -- H07 -- em `P07_evals.md`).
- **"Faltou uma das 6 trilhas na tabela final"** -> peça explicitamente:
  "reporte as 6 trilhas na Tabela de Status, mesmo as que ficaram blocked
  ou skipped" (gate HARD H04).
- **"Sentimento em PT sem fonte"** -> peça a fonte: sentimento só pode
  vir do texto já coletado nas trilhas Sinal Social ou Reputação; sem
  texto, a trilha é `skipped`.
- **Marcadores `[fornecer: ...]` nunca desaparecem** -> normal até você
  preencher a Instruction com os dados reais da sua marca (nome, tom de
  voz, valores) -- o agente nunca inventa esses campos por você.

## Compatibilidade entre runtimes

Os 4 caminhos usam exatamente os mesmos 12 arquivos de pilar e a mesma
instrução -- não há "versão reduzida" nem "versão completa" deste pacote.
A diferença entre eles é puramente onde você cola/sobe cada peça e quais
capabilities nativas (Web Browsing / Google Search) estão disponíveis.
