# SETUP -- Gemini Gems

Setup do pacote **Matriz de Benchmark de Concorrentes** (CEXAI) em Gemini
Gems. 12 arquivos de Knowledge + instrução colada. ~5 minutos.

## Pré-requisitos

- Conta Google + acesso a gemini.google.com.
- (Opcional) Extension de Google Search habilitada, se você quiser que o
  Gem pesquise dados públicos de concorrentes.
- Nenhuma chave de API necessária.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome sugerido: `Matriz de Benchmark de Concorrentes`.
4. Description: `Matriz de benchmark competitivo -- concorrentes avaliados em preço, funcionalidades e posicionamento, com fonte citada.`

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
- **Google Search** -- habilita o Gem a buscar dados públicos de
  concorrentes (site, página de preços) durante a conversa. Sem essa
  extension, o Gem trabalha apenas com o que você fornecer no chat.

### 5. Teste

Em uma conversa do Gem:

> `Comparar [meu produto] com [concorrente A] e [concorrente B] em preço, funcionalidades e posicionamento`

O Gem deve:
1. Confirmar os concorrentes e as dimensões de comparação.
2. Pedir os dados que faltam, ou usar Google Search (se habilitado) para
   contexto público.
3. Estruturar a feature parity grid, o posicionamento Gartner MQ, o
   battle card e a comparação de preços em tabelas.
4. Marcar qualquer dado sem fonte como `[fornecer: ...]`.

## Vantagens do Gemini para este pacote

- **Context window grande** (mais de 1M tokens nos modelos recentes) --
  folga enorme para os 12 pilares + conversas longas com muitos concorrentes.
- **Google Search nativo** (via extension) é uma boa fonte de contexto
  público para SERP de páginas de concorrentes.
- **Multi-modal nativo**: se você quer comparar visualmente a interface ou
  o material de marketing de um concorrente, pode anexar uma imagem e
  pedir para o Gem descrevê-la e incorporar isso na análise.

## Limitações

- Sem Actions/tools customizadas neste pacote (não são necessárias -- toda
  a lógica está nos 12 arquivos + na instrução).
- Google Search (quando habilitado) é best-effort para sites com
  proteção anti-bot -- para esses casos, cole os dados diretamente na
  conversa.

## Como o agente evita fabricar dados

Ver `P02_model.md`, `P06_schema.md`, `P07_evals.md` e `P11_feedback.md`.
Resumo:
- Toda alegação competitiva exige fonte primária + data de acesso.
- Superlativos sem citação de analista são proibidos.
- Itens de roadmap sempre rotulados com trimestre e ano.
- Sem dado real, o Gem emite `[fornecer: ...]` -- nunca adivinha.

## Solução de problemas

- **"Ele inventou um dado"** -> reforce: "toda alegação precisa de fonte
  com data de acesso; sem dado real, use [fornecer: ...]".
- **Search não retorna nada útil** -> tente uma busca mais específica
  (nome exato do produto do concorrente em vez do nome da categoria).
- **Quero usar sem Search** -> normal; cole os dados do concorrente
  diretamente na conversa (copiados da página dele, por exemplo).
- **Quero mais precisão/controle** -> considere Claude Projects
  (`SETUP_claude_projects.md`) ou ChatGPT (`SETUP_chatgpt_projects.md`
  ou Custom GPT via `README.md`).
