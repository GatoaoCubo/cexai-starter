# SETUP -- ChatGPT Projects

Setup do pacote **Matriz de Benchmark de Concorrentes** (CEXAI) no ChatGPT
Projects. Funciona no plano free (não precisa de ChatGPT Plus). 12 arquivos
de Knowledge, zero Actions, zero chaves de API. ~5 minutos.

## Pré-requisitos

- Conta ChatGPT (plano free é suficiente -- Projects não exige Plus).
- ZERO chaves de API necessárias (este pacote não usa Actions externas).

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome sugerido: `Matriz de Benchmark de Concorrentes`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o campo `instructions` de `customgpt_instructions.json` -- ou,
   alternativamente, todo o conteúdo de `system_instruction.md` (os dois
   são o mesmo texto; use o que for mais conveniente de copiar).
3. Cole nas Instructions do projeto.
4. Antes de usar, substitua os marcadores `[fornecer: ...]` pelos dados
   reais da sua marca (nome, tom de voz, valores). Um marcador deixado
   sem preencher aparece no output como `[fornecer: ...]` -- isso é
   intencional (o agente nunca fabrica o que você não informou).

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os **12 arquivos** deste bundle:

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

Confirme que os 12 aparecem na lista de Files do projeto.

### 4. Capabilities

Não há Actions para configurar neste pacote. Recomendado:
- **Web Browsing** -- opcional. Útil se você quiser que o agente pesquise
  dados públicos de concorrentes (site, página de preços) durante a
  conversa. Sem Web Browsing, o agente depende inteiramente dos dados que
  você fornecer no chat -- o que é perfeitamente válido, só mais manual.
- **Code Interpreter** -- opcional, útil para consolidar tabelas grandes ou
  calcular médias/faixas de preço a partir de vários pontos de dado.

### 5. Teste

Inicie uma conversa dentro do project:

> `Comparar [meu produto] com [concorrente A] e [concorrente B] em preço, funcionalidades e posicionamento`

O agente deve:
1. Confirmar quais concorrentes e quais dimensões comparar (preço,
   funcionalidades, suporte, integrações etc.).
2. Pedir os dados que faltam -- ou usar Web Browsing (se habilitado) para
   buscar informações públicas.
3. Estruturar a saída em tabelas: feature parity grid, posicionamento
   estilo Gartner MQ, battle card (nos vs concorrente primário) e
   comparação de preços.
4. Marcar qualquer dado sem fonte verificada como `[fornecer: ...]` em vez
   de adivinhar.

## Como o agente evita fabricar dados

Este é o comportamento mais importante do pacote (ver P06/P07/P11):
- Toda alegação competitiva precisa de uma fonte primária com data de acesso.
- Superlativos ("melhor", "líder de mercado", "#1") são proibidos sem uma
  citação de analista (Gartner, Forrester, G2).
- Itens de roadmap (funcionalidades ainda não lançadas) sempre vem
  rotulados com trimestre e ano -- nunca apresentados como já disponíveis.
- Se um dado não foi fornecido nem verificado, o agente emite
  `[fornecer: ...]` em vez de inventar um número.

## Solução de problemas

- **"Ele inventou um preço ou uma funcionalidade"** -> reforce na conversa:
  "toda alegação competitiva precisa citar uma fonte com data de acesso;
  sem dado real, use [fornecer: ...]". Isso é um NUNCA explícito do
  builder (ver `P02_model.md` e `P11_feedback.md`).
- **"Ele usou um adjetivo vago (rápido, caro, fácil)"** -> peça um valor
  mensurável ("quantos ms de latência?", "qual o preço exato?").
- **Quero que ele pesquise a web sozinho** -> habilite a capability Web
  Browsing no passo 4.
- **Arquivo não aparece na lista de Files** -> reenvie; Projects as vezes
  demora alguns segundos para indexar arquivos grandes.
- **Quero um Custom GPT publicável em vez de um Project privado** -> use
  `customgpt_instructions.json` direto em Explore GPTs -> Create (ver
  `README.md`, seção Upload).
