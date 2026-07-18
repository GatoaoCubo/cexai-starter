# SETUP -- product_match (Product Match + Catalog Audit) -- guia combinado PT-BR

Guia geral do bundle. Para o passo a passo detalhado por plataforma, veja os arquivos
específicos:

- **ChatGPT (Custom GPT e Projects)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `full` em qualquer plataforma. Diferente de bundles que dependem de Actions,
> MCP, ou busca ao vivo, `product_match` é 100% Knowledge + instrução -- nenhuma capacidade se
> perde ao trocar de assistente. O próprio motor de match real (`_tools/capability_generators/
> product_match.py`) já é offline-honest-null por design: com `match_engine=none` (o padrão),
> toda linha de resultado é um NAO honesto em confiança 0.0, nunca um match inventado. Isso
> significa que qualquer plataforma reproduz o mesmo comportamento correto, sem degradação.

## Arquivos do bundle (visão geral)

```
product_match/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge em qualquer assistente
  customgpt_instructions.json                 <- config pronta para o Custom GPT do ChatGPT
  system_instruction.md                       <- mesma instrução em formato system prompt (Claude, Gemini, qualquer IA)
  README.md                                   <- visão geral do bundle + passo a passo rápido
  SETUP_chatgpt_projects.md                   <- guia detalhado: ChatGPT (Custom GPT + Projects)
  SETUP_claude_projects.md                    <- guia detalhado: Claude Projects
  SETUP_gemini_gems.md                        <- guia detalhado: Gemini Gems
  SETUP_pt-br.md                              <- este arquivo (visão combinada)
```

## Opção A -- ChatGPT (Custom GPT ou Projects)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo das duas variantes.

Resumo:
1. Custom GPT: crie em **Explore GPTs -> Create**, cole `name`/`description`/`instructions` de
   `customgpt_instructions.json`, suba os 12 arquivos de Knowledge.
2. Projects: crie um **Project**, cole `system_instruction.md` nas Instructions, suba os 12
   arquivos em Files.
3. Nenhuma Action, nenhuma chave de API -- nenhuma das duas variantes perde capacidade.

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Project em **claude.ai**.
2. Cole `system_instruction.md` nas Project Instructions.
3. Suba os 12 arquivos `P01_knowledge.md` ... `P12_orchestration.md` como Knowledge (sem limite
   de contagem de arquivos).

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem em **gemini.google.com**.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos como Knowledge do Gem. Nenhuma extension é necessária.

## Opção D -- Qualquer outra IA

Qualquer assistente com (a) um campo de system prompt/instruções e (b) upload de arquivos como
contexto/retrieval funciona:

1. Cole `system_instruction.md` como system prompt.
2. Suba os 12 arquivos `P0X_*.md` como contexto/Knowledge/RAG source (o nome varia por
   plataforma).
3. Se a plataforma não aceitar upload de arquivo, cole o conteúdo dos 12 pillars diretamente no
   próprio system prompt, na ordem P01 -> P12 -- o contrato continua o mesmo.

## Preencha a marca antes de usar (em qualquer plataforma)

Todo marcador `[fornecer: ...]` em `system_instruction.md` ou em `customgpt_instructions.json`
(nome da marca, tom de voz, valores) é um campo honesto sem dado real ainda -- é o comportamento
correto do bundle, não um erro. Substitua cada um pela informação real da sua marca antes de usar
em produção. Nunca peça para o modelo "adivinhar" o valor -- ele foi instruído explicitamente a
nunca fazer isso (ver a seção LIMITES DE SEGURANÇA em `system_instruction.md`).

## Como o agente funciona (contrato em uma página)

O contrato completo está nos 12 pillars, mas o resumo essencial:

- **O que ele casa**: um item de fornecedor a um anúncio de marketplace, por uma chave composta
  não-exclusiva (foto + dimensão + código do fornecedor) -- nunca por EAN/GTIN/código de barras,
  porque todo revendedor recodifica esses valores.
- **O que ele audita**: divergência cadastral texto-vs-foto e fotos ausentes/de baixa resolução,
  no catálogo local, mesmo totalmente offline e sem nenhum motor de match ativo.
- **O que ele nunca faz**: fabricar um match SIM/PARCIAL quando `match_engine=none` (o padrão) --
  toda linha nesse caso é um NAO honesto em confiança 0.0. Isso é intencional (degrade-never),
  não uma limitação a esconder.
- **As 4 seções de saída, sempre nesta ordem**: Resultado do match (tabela) -> Auditoria de
  catálogo (lista) -> Proveniência (campos) -> Veredito (campos, com o gate nomeado
  `match_confiavel`).

## Solução de problemas (comum a todas as plataformas)

- **"Ele inventou um resultado de match com confiança alta"** -> reforce: "enquanto
  match_engine=none, toda linha é NAO em confiança 0.0 -- nunca invente um SIM/PARCIAL" (ver
  `P01_knowledge.md`, Matriz de Status do Motor de Match).
- **"Ele reordenou ou renomeou as seções de saída"** -> reforce: "a ordem Resultado do match ->
  Auditoria de catálogo -> Proveniência -> Veredito é congelada; não reordene, não renomeie, não
  troque o layout" (ver `P06_schema.md` e `P09_config.md`).
- **"Ele tratou EAN/GTIN/código de barras como chave de join válida"** -> reforce a exclusão
  estrutural: todo revendedor recodifica esses valores (ver `P09_config.md`).
- **"Os placeholders [fornecer: ...] continuam na resposta"** -> esperado até você preencher a
  marca real -- é o comportamento honest-null por design.
- **Quero ativar um motor de match real (reverse-image, embedding, manual)** -> nenhum dos três
  tem implementação hoje (ver `P01_knowledge.md`); os 12 pillars documentam o contrato
  honestamente para quando um motor ao vivo existir, sem fingir que ele já existe.

## Compatibilidade

Este bundle segue a mesma estrutura de 12 pillars (P01-P12) usada por todos os bundles de
capability do CEXAI -- se você já subiu outro bundle CEXAI antes (por exemplo `pesquisa_produto`
ou `marketplace_listing`), o fluxo de upload é idêntico; só o conteúdo dos 12 arquivos e da
instrução muda por capability.
