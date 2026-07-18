# SETUP -- ChatGPT (Custom GPT e ChatGPT Projects)

Setup do bundle CEXAI "Conhecimento e Documentacao" (capacidade `docs`, kind
`knowledge_card`) no ChatGPT. Duas formas de subir este bundle -- escolha a
que combina com seu plano. ~5-10 minutos.

## Pre-requisitos

- Conta ChatGPT. Custom GPT exige ChatGPT Plus/Team/Enterprise. ChatGPT Free
  nao cria Custom GPTs, mas roda ChatGPT Projects normalmente (Opcao B).
- ZERO chaves de API necessarias -- este agente nao usa Actions, Web
  Browsing, Code Interpreter nem DALL-E (veja `customgpt_instructions.json`
  -> campo `capabilities`, todas `false`). Ele funciona 100% via Knowledge +
  Instructions.

## Opcao A -- Custom GPT (recomendado se voce tem ChatGPT Plus)

### 1. Crie o Custom GPT

1. Acesse **chatgpt.com** -> menu lateral -> **Explore GPTs** -> **+ Create**.
2. Va na aba **Configure**.
3. **Name**: copie o campo `name` de `customgpt_instructions.json` (contem
   um placeholder `[fornecer: nome da marca]` -- troque pelo nome real da
   sua marca antes de publicar).
4. **Description**: copie o campo `description` de `customgpt_instructions.json`.

### 2. Cole as Instructions

1. Abra `customgpt_instructions.json`.
2. Copie o valor do campo `instructions` (o texto entre aspas, com as
   quebras de linha `\n`).
3. Cole no campo **Instructions** do Custom GPT.

Alternativa mais simples: cole o conteudo INTEIRO de `system_instruction.md`
-- e o mesmo texto, ja formatado como arquivo de texto puro (sem o JSON em
volta).

### 3. Suba os 12 arquivos de Knowledge

Clique em **Upload files** e suba os 12 arquivos P0X deste bundle:

- `P01_knowledge.md`
- `P02_model.md`
- `P03_prompt.md`
- `P04_tools.md`
- `P05_output.md`
- `P06_schema.md`
- `P07_evals.md`
- `P08_architecture.md`
- `P09_config.md`
- `P10_memory.md`
- `P11_feedback.md`
- `P12_orchestration.md`

> Custom GPT tem limite de 20 arquivos por GPT -- 12 arquivos fica bem
> dentro do limite, com folga para voce adicionar seus proprios documentos
> de marca ao lado.

### 4. Conversation starters

Copie o array `conversation_starters` de `customgpt_instructions.json`
(hoje traz 1 sugestao: "Capturar \<assunto\> como documentacao pronta para
RAG"). Adicione variacoes proprias, por exemplo:

- "Documentar o fluxo de onboarding de clientes como knowledge_card"
- "Estruturar a nossa politica de reembolso para busca RAG"

### 5. Capabilities

Nenhuma capability precisa ser marcada -- Web Browsing, Code Interpreter e
DALL-E ficam desligados (este agente so precisa da Knowledge). Deixe todas
desmarcadas, a nao ser que seu uso particular exija outra coisa.

### 6. Salve e publique

1. Clique em **Create/Update**.
2. Escolha a visibilidade: **Only me** (privado, recomendado para testes),
   **Anyone with a link**, ou **Public** (listado em Explore GPTs).

### 7. Teste

Envie no GPT:

> `Capturar politica de trocas e devolucoes como documentacao pronta para RAG`

O agente deve:
1. Confirmar o assunto e pedir os detalhes que faltarem.
2. Produzir um artefato `knowledge_card` completo (frontmatter YAML + corpo),
   inteiramente em pt-BR, seguindo a estrutura ensinada pelos 12 arquivos P0X.
3. Nunca inventar fatos -- qualquer campo sem informacao real vira um
   placeholder explicito `[fornecer: ...]`.

## Opcao B -- ChatGPT Projects (funciona em planos sem Custom GPT)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Conhecimento e Documentacao ([sua marca])`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (icone de engrenagem).
2. Cole o conteudo INTEIRO de `system_instruction.md`.

### 3. Suba os 12 arquivos em Files

Em **Files** do projeto, suba os mesmos 12 arquivos P0X listados na Opcao A.

### 4. Teste

Dentro de uma conversa do projeto, envie o mesmo teste do passo 7 da Opcao A.

## Antes de publicar -- preencha os placeholders

Este bundle e generico, sem dado de nenhum tenant especifico. Antes de usar,
edite `system_instruction.md` e `customgpt_instructions.json` e troque cada
`[fornecer: ...]` pelo dado real da sua marca:

- `[fornecer: nome da marca (brand_config.identity.BRAND_NAME)]` -> o nome
  da sua empresa/produto.
- `[fornecer: tom de voz da marca (nao configurado)]` -> ex.: "direto,
  tecnico, sem jargao de vendas".
- `[fornecer: valores da marca]` -> ex.: "transparencia, precisao, respeito
  ao tempo do cliente".

## Solucao de problemas

- **"O GPT nao usou os 12 arquivos"** -> confirme que os 12 foram marcados
  como Knowledge (nao apenas anexados numa mensagem avulsa) e que aparecem
  processados, sem erro, na tela de upload.
- **"A saida veio em ingles"** -> reforce a linha "Idioma: pt-BR" no fim das
  Instructions; se voce editou o texto, confirme que ela sobreviveu.
- **"Ele inventou um dado que eu nao dei"** -> viola a secao REGRAS DE
  PROTECAO de `system_instruction.md`; cole o texto de novo, sem cortar essa
  secao.
- **"Quero trocar o kind ou o pipeline"** -> os 12 arquivos P0X sao o
  contrato completo (12 pillars = 12 ISOs) do kind `knowledge_card`; para
  outro kind, use outro bundle CEXAI.
