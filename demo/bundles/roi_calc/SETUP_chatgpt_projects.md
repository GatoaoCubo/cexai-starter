# SETUP -- ChatGPT Projects

Setup do bundle `roi_calc` (Calculadora de ROI) em ChatGPT Projects. Este
bundle não usa Actions nem chaves de API -- e só conhecimento + instrução.
~5 minutos.

## Pre-requisitos

- Conta ChatGPT (o recurso Projects está disponível em contas pagas e,
  progressivamente, em contas gratuitas -- verifique no seu menu lateral).
- ZERO chaves de API necessárias: este agente não chama nenhuma ferramenta
  externa (`web_browsing`, `code_interpreter` e `dalle` são todos `false`
  em `customgpt_instructions.json`).

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Calculadora de ROI -- [fornecer: nome da marca]`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole no campo Instructions do projeto.
4. Antes de usar, substitua os placeholders `[fornecer: ...]` (nome da
   marca, tom de voz, valores) pelos dados reais da sua marca.

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

### 4. Capabilities

Nenhuma capability é necessária. Este agente é puramente input -> raciocínio
-> output (não navega na web, não executa código, não gera imagens). Deixe
o modelo padrão do Project como está.

### 5. Teste

Inicie uma conversa dentro do project:

> `Monte um caso de ROI para uma equipe de 8 pessoas, valor da hora de R$ 80, gastando 6 horas/semana no processo atual`

O agente deve:
1. Confirmar (ou perguntar) os parâmetros de entrada que faltarem
   (investimento inicial, economia anual, custo de implementação, horizonte
   de tempo, taxa de desconto, manutenção anual -- ver `P05_output.md`).
2. Calcular ROI %, prazo de retorno (payback), NPV e redução de TCO usando
   as fórmulas de `P05_output.md`.
3. Entregar o modelo de saída com premissas explícitas -- nunca inventar
   números; qualquer dado que faltar vira `[fornecer: ...]`.

## Fidelidade declarada: FULL

Diferente de bundles com coleta de dados externos (pesquisa de mercado,
scraping), a Calculadora de ROI é 100% raciocínio + fórmula sobre os dados
que você fornece. Sem Actions, sem MCP, sem tiers de coleta -- os 12
arquivos de Knowledge + a instrução cobrem 100% da capacidade do agente em
qualquer runtime.

## Solução de problemas

- **"Ele inventou um preço ou uma economia"** -> reforce: "todo número
  precisa vir da minha entrada; sem dado real, use `[fornecer: ...]`".
- **Faltam arquivos de Knowledge** -> confirme que os 12 `P0X_*.md` foram
  todos anexados (Projects não avisa se faltar um).
- **Quero usar no Custom GPT em vez de Projects** -> veja `README.md` ->
  seção "Upload" -> ChatGPT (Custom GPT), usando `customgpt_instructions.json`.
- **Quero Claude ou Gemini** -> veja `SETUP_claude_projects.md` ou
  `SETUP_gemini_gems.md`.
