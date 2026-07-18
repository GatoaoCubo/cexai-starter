# SETUP -- marketplace_listing -- guia combinado PT-BR

Guia geral do bundle `marketplace_listing` (Marketplace Listing / Channel
Projection). Para o passo a passo detalhado por plataforma, veja os guias
específicos:

- **ChatGPT (Projects ou Custom GPT)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `FULL` em qualquer plataforma. Esta capability mapeia um
> produto do seu catálogo para um anúncio de marketplace + relatório de
> prontidão usando só texto -- não depende de Actions, MCP, navegação web
> nem chaves de API. O que você sobe (12 arquivos + instruções) é o
> contrato inteiro; não existe uma versão "enxuta" degradada.

## O que este bundle faz

Recebe os dados de um produto (o equivalente a uma linha de catálogo:
titulo_ml, descricao, categoria_ml, marca, condicao, preco, estoque, fotos,
atributos, sku) e devolve:
1. Um payload de anúncio no formato da API de Items do Mercado Livre
   (`title`, `category_id`, `price`, `currency_id`, `available_quantity`,
   `condition`, `listing_type_id`, `description.plain_text`,
   `pictures[].url`, `attributes[]`, `seller_custom_field`).
2. Um relatório de prontidão honesto -- `PUBLISH` (pronto), `REVISE`
   (precisa de ajuste) ou `REJECT` (dados insuficientes), com a lista exata
   de campos faltantes.

Mapear e validar são operações puras (só o modelo pensando em texto);
publicar de fato no marketplace sempre fica sob controle do operador, fora
do escopo deste agente.

## Arquivos do bundle (visão geral)

```
marketplace_listing/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge/Files
  customgpt_instructions.json                 <- config pronta para Custom GPT (name/description/instructions)
  system_instruction.md                       <- as mesmas instruções em formato paste-ready
  README.md                                   <- visão geral + passo a passo resumido
  SETUP_chatgpt_projects.md                   <- guia ChatGPT (Projects + Custom GPT)
  SETUP_claude_projects.md                    <- guia Claude Projects
  SETUP_gemini_gems.md                        <- guia Gemini Gems
  SETUP_pt-br.md                              <- este arquivo (guia combinado)
```

## Opção A -- ChatGPT (Projects, plano free, ou Custom GPT, plano Plus)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Project (ou um Custom GPT) em chatgpt.com.
2. Cole o conteúdo de `system_instruction.md` (ou o campo `instructions` de
   `customgpt_instructions.json`) nas Instructions.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge/Files.
4. Deixe Web Browsing, Code Interpreter e DALL-E desligados -- não são
   usados por esta capability.
5. Teste com: `Mapeie uma cafeteira elétrica 110V para um anúncio no Mercado Livre -- título, preço, categoria, prontidão`.

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Claude Project.
2. Cole `system_instruction.md` nas Project Instructions.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge.
4. Nenhum MCP bridge é necessário -- a capability não chama ferramentas
   externas.

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem em gemini.google.com.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge.
4. Nenhuma extension é necessária.

## Opção D -- qualquer IA com prompt de sistema

Qualquer assistente que aceite um system prompt + arquivos de contexto
funciona:
1. Cole `system_instruction.md` como system prompt.
2. Anexe (ou cole) o conteúdo dos 12 arquivos `P0X_*.md` como contexto/
   conhecimento.
3. Use o mesmo prompt de teste das opções acima.

## Antes de usar em produção

Todo campo `[fornecer: ...]` em `system_instruction.md` e
`customgpt_instructions.json` é um placeholder honesto -- preencha com o
nome, tom de voz e valores reais da sua marca (veja
`.cex/brand/brand_config.yaml` se você já tem um CEXAI configurado, ou
simplesmente edite o texto à mão).

## Como usar (fluxo típico, em qualquer plataforma)

1. Diga o produto e o marketplace: `Mapeie <produto> para um anúncio no <marketplace>`.
2. O agente pergunta os campos que faltarem da linha de catálogo (título,
   descrição, categoria, marca, condição, preço, estoque, fotos,
   atributos, SKU).
3. Ele mapeia cada campo para o payload ML e monta as 6 seções congeladas:
   Listagem ML, Preco e Estoque, Fotos, Atributos, Descricao, Payload ML
   (pronto para publicar).
4. BRAND (a partir da marca) e SELLER_SKU (a partir do SKU) são injetados
   automaticamente nos atributos quando ausentes, sem sobrescrever o que
   você já informou.
5. Você recebe o veredito de prontidão (`score`, `passed`,
   `missing_required`, `notes`) e o payload JSON pronto para publicar.
6. A publicação real no marketplace continua manual/sob controle do
   operador -- este agente nunca publica sozinho.

## Solução de problemas

- **"Ele inventou preço, foto, categoria ou atributo"** -> P02/P07/P11
  proíbem isso. Reforce: "nunca fabrique -- todo campo sem dado real vira
  um placeholder honesto, nunca um valor inventado" (mesma disciplina
  clean-room descrita em `P04_tools.md` e `P11_feedback.md`).
- **"O título saiu truncado"** -> o contrato só avisa acima de 60
  caracteres (`ML_TITLE_MAX`), nunca trunca -- ver `P01_knowledge.md`.
- **"As 6 seções vieram fora de ordem ou renomeadas"** -> peça para o
  agente reler `P06_schema.md` -- título, ordem e layout das 6 seções são
  congelados (gate H05 em `P07_evals.md`).
- **"BRAND ou SELLER_SKU não apareceram nos atributos"** -> confirme que
  `marca`/`sku` foram informados na linha de catálogo; a injeção só
  acontece quando o dado de origem existe (nunca inventada) -- ver
  `P09_config.md`.
- **"Confundiu quality com o score de prontidão"** -> são dois campos
  distintos: `quality` é sempre `null` (meta do CEX, nunca autoavaliada);
  `score` é o float 0.0-1.0 do gate de prontidão -- ver `P10_memory.md`.
- **Quer trocar o canal de marketplace** -> hoje só `mercado_livre` está
  conectado (`CHANNEL_ADAPTERS`); o formato de saída permanece
  específico do ML mesmo se outro nome de canal for informado -- ver
  `P09_config.md`.

## Compatibilidade

Este bundle segue a mesma arquitetura CEXAI dos demais bundles da
plataforma: 12 pilares (P01 conhecimento até P12 orquestração), frontmatter
tipado, `quality: null` sempre (nunca autoavaliação), e placeholders
`[fornecer: ...]` em vez de dados fabricados. Se você já usa outro bundle
CEXAI, o fluxo de setup é idêntico -- só troca o nome dos 12 arquivos e o
texto das instruções.
