# SETUP -- ads (Ads and Copy) -- guia combinado PT-BR

Guia geral do bundle `ads`. Para o passo a passo detalhado por runtime, veja
os arquivos específicos:

- **ChatGPT (Custom GPT ou Projects)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

## O que este bundle é

Um bundle portátil de agente para **gerar copy de anúncio e prompt
templates de campanha na voz da sua marca** -- hooks, CTAs e variantes por
tamanho de plataforma. É o formato CEXAI "12 ISO": um arquivo de
especificação por pilar (P01-P12), o mesmo contrato de builder usado
internamente pela CEXAI para o kind `prompt_template`.

Diferente de bundles com coleta de dados ao vivo (pesquisa de mercado, por
exemplo), este agente **não precisa de nenhuma ferramenta externa, Action,
MCP server ou chave de API**. É puramente geração de texto a partir do
conhecimento carregado (os 12 arquivos de pilar) e da instrução (persona +
regras). Isso torna o setup idêntico e simples em qualquer runtime.

## Arquivos do bundle (overview)

```
ads/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge
  customgpt_instructions.json                 <- config pronta pro Custom GPT (name/description/instructions)
  system_instruction.md                       <- a mesma instrução em formato system prompt
  README.md                                   <- índice do bundle + passo a passo resumido
  SETUP_chatgpt_projects.md                   <- guia deste runtime
  SETUP_claude_projects.md                    <- guia deste runtime
  SETUP_gemini_gems.md                        <- guia deste runtime
  SETUP_pt-br.md                              <- este arquivo
```

## Passo a passo universal (qualquer IA com upload de arquivo + system prompt)

1. Crie um assistente/agente/projeto novo na plataforma escolhida.
2. Cole o conteúdo de `system_instruction.md` (ou o campo `instructions` de
   `customgpt_instructions.json`) como a instrução/persona do assistente.
3. Anexe os 12 arquivos `P0X_*.md` como Knowledge/arquivos de contexto.
4. Preencha os marcadores `[fornecer: ...]` com os dados reais da sua marca
   (nome, tom de voz, valores).
5. Teste com: "Escreva a copy de anúncio para \<produto/oferta\> visando \<público\>".

## Comparativo rápido por runtime

| Aspecto | Custom GPT | ChatGPT Projects | Claude Projects | Gemini Gems |
|---------|-----------|-------------------|------------------|-------------|
| Plano exigido | Plus | Qualquer | Free/Pro/Team | Conta Google |
| Cole as Instructions em | Configure -> Instructions | Instructions do projeto | Custom instructions | Instructions do Gem |
| Suba a Knowledge em | Knowledge | Files | Project knowledge | Knowledge |
| Limite de arquivos | 20 | por tamanho total | por tamanho total | varia |
| Actions/tools/MCP | não usa neste bundle | não usa neste bundle | não usa neste bundle | não usa neste bundle |
| Conversation starters | campo dedicado | cole na 1a mensagem | cole na 1a mensagem | cole na 1a mensagem |

## Por que este bundle não tem tier de coleta nem Actions

Bundles CEXAI que pesquisam mercado ao vivo (marketplaces, concorrentes)
precisam de tiers de coleta de dados e de Actions/MCP para navegar a web. O
bundle `ads` fica na ponta OPOSTA da esteira: ele recebe um `intent` em
texto (o que você quer anunciar, para quem) e devolve copy -- não precisa
buscar nada ao vivo. Por isso o setup é uniformemente simples nos 4
runtimes, sem variantes ENXUTO/FULL nem chaves de API.

## Procedência / honestidade

Nunca fabricar: todo marcador `[fornecer: ...]` é um campo sem dado real de
entrada -- preencha com a sua própria marca antes de usar. Os 12 ISOs de
pilar são o contrato de builder genérico e público do kind `prompt_template`
-- sem dado de nenhum tenant. Se você pedir algo fora do escopo "ads" (por
exemplo, pesquisa de mercado ou pricing), o agente deve redirecionar --
essa é uma guardrail explícita em `system_instruction.md`.

## Solução de problemas (todos os runtimes)

- **O agente inventa nome de marca, tom ou valores** -> reforce: "NUNCA
  fabrique fatos; use [fornecer: ...] quando faltar dado real".
- **A saída não parece um `prompt_template`** -> confirme que os 12 arquivos
  P0X foram carregados como Knowledge (o agente usa `P03_prompt.md` +
  `P05_output.md` + `P06_schema.md` para saber o formato esperado).
- **Quero mudar o idioma de saída** -> edite o campo `Language` em
  `system_instruction.md` (default: `pt-BR`).
- **Quero adaptar para outro núcleo/domínio** -> troque os 12 arquivos de
  pilar pelo bundle correspondente (cada capability CEXAI publica seu
  próprio conjunto de 12 ISOs).
