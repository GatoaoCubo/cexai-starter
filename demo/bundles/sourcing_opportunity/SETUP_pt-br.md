# SETUP -- sourcing_opportunity (Sourcing Opportunity Matrix) -- guia combinado PT-BR

Guia geral do bundle. Para o passo a passo detalhado por plataforma, veja os arquivos
específicos:

- **ChatGPT (Custom GPT e Projects)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `full` em qualquer plataforma. Diferente de bundles que dependem de Actions,
> MCP, ou busca ao vivo, `sourcing_opportunity` é 100% Knowledge + instrução -- nenhuma
> capacidade se perde ao trocar de assistente. O próprio gerador real
> (`_tools/capability_generators/sourcing_opportunity.py`) já é offline-determinístico por
> design: sem uma credencial + `demand_sources`, toda célula de mercado/demanda renderiza
> honestamente `"nao pesquisado"` e o gate `sourcing_confiavel` fica BLOQUEADO, nunca um valor
> inventado. Isso significa que qualquer plataforma reproduz o mesmo comportamento correto, sem
> degradação.

## Arquivos do bundle (visão geral)

```
sourcing_opportunity/
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

- **O que ele cruza**: o custo do seu catálogo de fornecedor (lado da oferta, `catalog_sources`)
  contra preço e demanda de mercado por tipo de produto normalizado -- nunca por EAN/GTIN/código
  de barras, porque todo revendedor recodifica esses valores.
- **O que ele ranqueia**: cada produto recebe um `opp_score` ponderado (margem + demanda +
  estoque + confiança) e uma margem bruta (ou líquida, com `show_net_margin=true`) calculada a
  partir do custo, da taxa de canal e do frete.
- **O que ele nunca faz**: fabricar um preço de venda ou nível de demanda quando não há
  credencial + `demand_sources` -- nesse caso, toda célula correspondente é honestamente
  `"nao pesquisado"`. Isso é intencional (honest-null / degrade-never), não uma limitação a
  esconder.
- **As 8 seções de saída, sempre nesta ordem**: Resumo executivo (campos) -> Matriz de
  oportunidade (tabela, 9 colunas) -> Leitura por categoria (tabela, 5 colunas) -> Cobertura
  (campos) -> Verificacao (top-N) (tabela, 5 colunas) -> Match / auditoria (tabela, 4 colunas) ->
  Proveniencia (campos) -> Veredito + proximos passos (campos, com o gate nomeado
  `sourcing_confiavel`).

## Solução de problemas (comum a todas as plataformas)

- **"Ele inventou um preço de mercado ou nível de demanda"** -> reforce: "sem credencial de
  demanda ao vivo, toda célula de mercado/demanda é honest-null (`nao pesquisado`) -- nunca
  invente um valor" (ver `P01_knowledge.md`, Armadilhas).
- **"Ele reordenou ou renomeou as seções de saída"** -> reforce: "a ordem Resumo executivo ->
  Matriz de oportunidade -> Leitura por categoria -> Cobertura -> Verificacao (top-N) -> Match /
  auditoria -> Proveniencia -> Veredito + proximos passos é congelada; não reordene, não
  renomeie, não troque o layout" (ver `P06_schema.md` e `P09_config.md`).
- **"Ele tratou EAN/GTIN/código de barras como chave de join válida"** -> reforce a exclusão
  estrutural: todo revendedor recodifica esses valores (ver `P02_model.md` e `P09_config.md`).
- **"Ele declarou sourcing_confiavel sem as condições"** -> reforce que as 4 condições
  (margem_bruta_top >= 25%, top-N verificado, nenhum item crítico sem preço, frescor != RED)
  precisam vir explicitadas junto com o valor true/false (ver `P05_output.md`).
- **"Os placeholders [fornecer: ...] continuam na resposta"** -> esperado até você preencher a
  marca real -- é o comportamento honest-null por design.
- **Quero conectar uma fonte de demanda de mercado real (preço/reviews/ranking de vendas ao
  vivo)** -> isso exige uma credencial + `demand_sources` no lado do gerador real
  (`_tools/capability_generators/sourcing_opportunity.py`); os 12 pillars documentam o contrato
  honestamente para quando essa fonte existir, sem fingir que ela já está conectada.

## Compatibilidade

Este bundle segue a mesma estrutura de 12 pillars (P01-P12) usada por todos os bundles de
capability do CEXAI -- se você já subiu outro bundle CEXAI antes (por exemplo `product_match`
ou `roi_calc`), o fluxo de upload é idêntico; só o conteúdo dos 12 arquivos e da instrução muda
por capability.
