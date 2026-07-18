# SETUP -- Gemini Gems

Setup do bundle `roi_calc` (Calculadora de ROI) em Gemini Gems. Este bundle
não usa extensions nem ferramentas externas -- e só conhecimento +
instrução. ~5 minutos.

## Pre-requisitos

- Conta Google + acesso a gemini.google.com.
- ZERO extensions ou chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Calculadora de ROI -- [fornecer: nome da marca]`.
4. Description: `Quantifica o valor que um comprador obtém -- horas e
   dinheiro economizados, prazo de retorno e retorno anual.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.
4. Antes de usar, substitua os placeholders `[fornecer: ...]` (nome da
   marca, tom de voz, valores) pelos dados reais da sua marca.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os **12 arquivos** deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Capabilities

Nenhuma extension é necessária. Este agente não navega na web e não
executa código -- ele raciocina inteiramente sobre os dados que você
fornece na conversa. Deixe as extensions do Gem desligadas.

### 5. Teste

Em uma conversa do Gem:

> `Monte um caso de ROI para uma equipe de 8 pessoas, valor da hora de R$ 80, gastando 6 horas/semana no processo atual`

O Gem deve:
1. Confirmar (ou perguntar) os parâmetros que faltarem.
2. Calcular ROI %, prazo de retorno (payback), NPV e redução de TCO.
3. Entregar o modelo de saída com premissas explícitas, sem inventar dados.

## Vantagens do Gemini para este bundle

- **Janela de contexto grande** (mais de 1M tokens em modelos recentes) --
  folga enorme para os 12 arquivos de Knowledge deste bundle (pequenos).
- **Setup mais rápido**: sem Actions, sem MCP, sem extensions -- só paste +
  upload.

## Fidelidade declarada: FULL

Sem Actions, sem MCP, sem tiers de coleta externa -- os 12 arquivos de
Knowledge + a instrução cobrem 100% da capacidade do agente em qualquer
runtime, incluindo Gemini.

## Solução de problemas

- **"Ele inventou um preço ou uma economia"** -> reforce: "todo número
  precisa vir da minha entrada; sem dado real, use `[fornecer: ...]`".
- **Faltam arquivos de Knowledge** -> confirme que os 12 `P0X_*.md` foram
  todos anexados ao Gem.
- **Quero ChatGPT ou Claude** -> veja `SETUP_chatgpt_projects.md` ou
  `SETUP_claude_projects.md`.
