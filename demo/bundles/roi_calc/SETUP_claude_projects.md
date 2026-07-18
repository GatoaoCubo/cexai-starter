# SETUP -- Claude Projects

Setup do bundle `roi_calc` (Calculadora de ROI) em Claude Projects. Este
bundle não precisa de MCP nem de nenhuma ferramenta externa -- e só
conhecimento + instrução. ~5 minutos.

## Pre-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO chaves de API ou MCP servers necessários.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Calculadora de ROI -- [fornecer: nome da marca]`.

### 2. Cole as Custom Instructions

1. Abra o projeto -> **Custom instructions** / **Project instructions** (no
   painel lateral).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Custom Instructions do projeto.
4. Antes de usar, substitua os placeholders `[fornecer: ...]` (nome da
   marca, tom de voz, valores) pelos dados reais da sua marca.

### 3. Suba os 12 arquivos de Knowledge

Em **Project knowledge**, anexe os **12 arquivos** deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho
total acumulado do projeto) -- os 12 arquivos deste bundle cabem
folgadamente.

### 4. Capabilities

Nenhuma configuração adicional é necessária. Este agente não usa tools,
não navega na web e não precisa de MCP -- é um raciocinador puro sobre os
dados que você fornece na conversa.

### 5. Teste

Em uma conversa do Project:

> `Monte um caso de ROI para uma equipe de 8 pessoas, valor da hora de R$ 80, gastando 6 horas/semana no processo atual`

O agente deve:
1. Confirmar (ou perguntar) os parâmetros que faltarem.
2. Calcular ROI %, prazo de retorno (payback), NPV e redução de TCO.
3. Entregar o modelo de saída com premissas explícitas, sem inventar dados.

## Vantagens do Claude Projects para este bundle

| Aspecto | ChatGPT (Custom GPT / Projects) | Claude Projects |
|---------|-----------------------|----------------|
| Limite de arquivos de conhecimento | 20 arquivos (Custom GPT) | Sem limite por arquivo (limite por tamanho total) |
| Contexto | 128K (varia por modelo) | 200K |
| Custo | Plus ($20/mês) para Custom GPT; Projects também em planos gratuitos | Pro ($20/mês) ou Free, conforme o plano |
| Setup deste bundle | Igual -- só paste + upload | Igual -- só paste + upload |

## Fidelidade declarada: FULL

Sem Actions, sem MCP, sem tiers de coleta externa -- os 12 arquivos de
Knowledge + a instrução cobrem 100% da capacidade do agente em qualquer
runtime, incluindo Claude.

## Solução de problemas

- **"Ele inventou um preço ou uma economia"** -> reforce na conversa: "todo
  número precisa vir da minha entrada; sem dado real, use `[fornecer: ...]`".
- **Faltam arquivos de Knowledge** -> confirme que os 12 `P0X_*.md` foram
  todos anexados ao Project.
- **Quero ChatGPT ou Gemini** -> veja `SETUP_chatgpt_projects.md` ou
  `SETUP_gemini_gems.md`.
