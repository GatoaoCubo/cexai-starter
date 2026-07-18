# SETUP -- Construtor de Email (`email_builder`) -- guia combinado PT-BR

Guia geral do bundle. Para o passo a passo detalhado por runtime, veja os
arquivos específicos:

- **ChatGPT Projects (free) ou Custom GPT** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `full` em qualquer um dos três runtimes. Este bundle é um
> gerador de prompt template (texto) -- não depende de Actions, MCP, chave de
> API ou tiers de coleta de dado externo. Diferente de bundles de pesquisa
> (que perdem capacidade em runtimes sem suporte a Actions), o Construtor de
> Email entrega a mesma capacidade em ChatGPT, Claude e Gemini.

## O que este bundle faz

O **Construtor de Email** é o agente que gera **prompt templates de email
HTML responsivo**: linhas de assunto (com variações), preheader e blocos de
corpo alinhados à sua marca, para uma campanha ou um envio de ciclo de vida
(lifecycle: boas-vindas, carrinho abandonado, reengajamento, etc.).

Importante: a saída é um **template reutilizável** -- um molde com campos
variáveis (`{{campaign}}`, `{{audience}}`, `{{tone}}`, `{{cta}}` etc.) --, não
um único email já pronto. Você preenche os campos variáveis (ou pede para o
próprio agente renderizar um exemplo preenchido) e reaproveita o mesmo
template em campanhas futuras trocando apenas os valores.

## Arquivos do bundle (visão geral)

```
email_builder/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge
  customgpt_instructions.json                 <- config pronta para Custom GPT (schema + instructions)
  system_instruction.md                       <- a mesma instrução em formato de system prompt
  README.md                                   <- visão geral + upload rápido em 3 formas
  SETUP_chatgpt_projects.md                   <- passo a passo ChatGPT (Projects + Custom GPT)
  SETUP_claude_projects.md                    <- passo a passo Claude Projects
  SETUP_gemini_gems.md                        <- passo a passo Gemini Gems
  SETUP_pt-br.md                              <- este arquivo
```

## Opção A -- ChatGPT (Projects ou Custom GPT)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Project em chatgpt.com (plano free já serve).
2. Cole o campo `instructions` de `customgpt_instructions.json` (ou o
   conteúdo de `system_instruction.md`) nas Instructions do projeto.
3. Suba os 12 arquivos `P0X_*.md` como Files/Knowledge.
4. Nenhuma capability especial é necessária (sem web browsing, sem code
   interpreter, sem Actions).
5. Teste com: `Escreva um email de marketing para o lançamento do produto X -- assunto, preheader, corpo`.
6. (Opcional) Se quiser um link público com nome/ícone próprios, migre para
   um Custom GPT -- mesmo conteúdo, mesma fidelidade.

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Claude Project.
2. Cole `system_instruction.md` nas Project Instructions.
3. Suba os 12 arquivos `P0X_*.md` como Project Knowledge.
4. Nenhuma configuração de MCP é necessária (o agente não chama ferramenta externa).
5. Teste com o mesmo prompt de exemplo acima.

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem em gemini.google.com.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge.
4. Nenhuma extension é necessária.
5. Teste com o mesmo prompt de exemplo acima.

## Comparação rápida entre runtimes

| Aspecto | ChatGPT Projects | Custom GPT | Claude Projects | Gemini Gems |
|------------|-----------|----------|--------|--------|
| Plano necessário | Free | Plus | Free/Pro | Contas Google |
| Limite de arquivos de Knowledge | 20 | 20 | Sem limite de contagem | Múltiplos arquivos |
| Actions/MCP necessários | Não | Não | Não | Não |
| Fidelidade | full | full | full | full |
| Link público compartilhável | Não | Sim | Sim (via Project) | Sim (via Gem) |

## Como usar (fluxo típico, qualquer runtime)

1. Antes do primeiro teste, preencha os marcadores `[fornecer: ...]` nas
   Instructions com os dados reais da sua marca (nome, tom de voz, valores).
2. Diga a campanha ou o objetivo do email:
   `Preciso de um email para recuperação de carrinho abandonado`.
3. O agente entrega o **prompt template**: variações de linha de assunto,
   preheader, e a estrutura de corpo (saudação, corpo principal, CTA,
   rodapé), com os campos variáveis explícitos.
4. Você preenche os `{{slots}}` com os dados reais da campanha -- ou pede ao
   próprio agente para renderizar um exemplo completo e preenchido.
5. Você leva o resultado (o template ou o exemplo renderizado) para a sua
   ferramenta de envio de email (ESP, plataforma de automação, etc.).

## Exemplos de pedidos (conversation starters)

- `Escreva um email de marketing para o lançamento do produto X -- assunto, preheader, corpo`
- `Preciso de um email de boas-vindas para novos assinantes da newsletter`
- `Gere 3 variações de linha de assunto para uma campanha de Black Friday`
- `Monte o template de email de recuperação de carrinho abandonado, com desconto`

## Solução de problemas

- **"Ele inventou um dado (preço, prazo, nome de produto)"** -> as
  Guardrails do `system_instruction.md` proíbem isso -- reforce: "nunca
  fabrique fatos, preços, nomes ou dados; sem dado real, emita
  `[fornecer: ...]`".
- **A saída veio em inglês** -> confirme que colou as Instructions
  completas (elas já fixam `Idioma: pt-BR`) e peça explicitamente "responda
  em português do Brasil".
- **Ele entregou um email pronto em vez de um template** -> peça
  explicitamente "entregue como prompt template, com os campos variáveis
  marcados" -- o comportamento default é o molde reutilizável; um exemplo
  preenchido é um passo opcional seguinte, não o produto principal.
- **Quero usar a brand_config.yaml real da minha empresa** -> anexe o
  arquivo de configuração de marca como mais um item de Knowledge/Files; o
  agente prioriza dado real sobre os placeholders `[fornecer: ...]`.
- **Marcadores `[fornecer: ...]` não configurados** -> normal em um bundle
  público/genérico. Edite as Instructions (ou o `system_instruction.md`
  antes de colar) substituindo cada marcador pelo dado real da sua marca.

## Compatibilidade entre runtimes

Os três runtimes (ChatGPT, Claude, Gemini) consomem exatamente o mesmo par
de arquivos-fonte -- `system_instruction.md` (ou o campo `instructions` de
`customgpt_instructions.json`, que carrega o mesmo texto) + os 12 arquivos
`P0X_*.md`. Não há variante "enxuta" nem versão reduzida neste bundle: como
o Construtor de Email não depende de Actions, tier de coleta externa nem
chave de API, qualquer um dos três runtimes recebe a capacidade completa.
