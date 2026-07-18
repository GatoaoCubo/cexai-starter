# SETUP -- Gemini Gems

Setup do pacote **Universo de Pesquisa (Cérebro Multi-Fonte)** (CEXAI) em
Gemini Gems. 12 arquivos de Knowledge + instrução colada. ~5 minutos.

## Pre-requisitos

- Conta Google + acesso a gemini.google.com.
- (Opcional) Extension de Google Search habilitada, se você quiser que o
  Gem pesquise dados públicos da semente.
- Nenhuma chave de API necessária.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome sugerido: `Universo de Pesquisa (Cérebro Multi-Fonte)`.
4. Description: `Pesquisa multi-fonte a partir de uma semente -- firmografia, sinal social, reputação, sentimento, SEO e perguntas multi-perspectiva, com status honesto por trilha.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.
4. Substitua os marcadores `[fornecer: ...]` pelos dados reais da sua marca
   antes de usar (nome, tom de voz, valores).

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Gemini Gems aceita arquivos de knowledge; o tamanho total dos 12 arquivos
deste pacote é pequeno (bem abaixo de qualquer limite prático).

### 4. (Opcional) Configure extensions

Em **Extensions** do Gem:
- **Google Search** -- habilita o Gem a buscar dados públicos da semente
  (CNPJ, página de loja de app, Reclame Aqui, SEO) durante a conversa. Sem
  essa extension, o Gem trabalha apenas com o que você fornecer no chat --
  e cada trilha sem dado real fica honestamente `blocked`.

### 5. Teste

Em uma conversa do Gem:

> `Pesquise [nome da empresa ou produto] -- firmografia, social, reputação, SEO e perguntas`

O Gem deve:
1. Confirmar a semente e classificar o tipo (produto, marca, CNPJ, empresa,
   palavra-chave ou `store:id`).
2. Pedir os dados que faltam, ou usar Google Search (se habilitado) para
   contexto público.
3. Estruturar as 6 trilhas em tabelas, com a Tabela de Status por Trilha
   (`ok`/`blocked`/`skipped`) ao final.
4. Marcar qualquer dado sem fonte como `blocked` -- nunca inventar.

## Vantagens do Gemini para este pacote

- **Context window grande** (mais de 1M tokens nos modelos recentes) --
  folga enorme para os 12 pilares + conversas longas cobrindo as 6 trilhas.
- **Google Search nativo** (via extension) é uma boa fonte de contexto
  público para firmografia, sinal social e SEO.
- **Multi-modal nativo**: se você quer analisar visualmente um print de
  loja de app ou de uma página do Reclame Aqui, pode anexar a imagem e
  pedir para o Gem extrair os campos e incorporar isso na trilha correta.

## Limitações

- Sem Actions/tools customizadas neste pacote (não são necessárias -- toda
  a lógica está nos 12 arquivos + na instrução).
- Google Search (quando habilitado) é best-effort para fontes com
  proteção anti-bot ou exigência de login (ex.: algumas páginas de CNPJ) --
  para esses casos, cole os dados diretamente na conversa.

## Como o agente evita fabricar dados

Ver `P02_model.md`, `P06_schema.md`, `P07_evals.md` e `P11_feedback.md`.
Resumo:
- Toda trilha `ok` exige fonte primária + data de acesso.
- `blocked` (fonte existe, acesso falhou) e `skipped` (não se aplica a esta
  semente) nunca são confundidos.
- Sem dado real, o Gem marca a trilha como `blocked` ou `skipped` -- nunca
  adivinha um CNPJ, índice de reputação ou volume de busca.

## Solução de problemas

- **"Ele inventou um dado"** -> reforce: "toda trilha ok precisa de fonte
  com data de acesso; sem dado real, marque blocked".
- **Search não retorna nada útil** -> tente uma busca mais específica (nome
  exato da empresa/CNPJ em vez do nome genérico do setor).
- **Quero usar sem Search** -> normal; cole os dados diretamente na
  conversa (print de app store, texto do Reclame Aqui, resultado de
  consulta de CNPJ).
- **Quero mais precisão/controle** -> considere Claude Projects
  (`SETUP_claude_projects.md`) ou ChatGPT (`SETUP_chatgpt_projects.md`
  ou Custom GPT via `README.md`).
