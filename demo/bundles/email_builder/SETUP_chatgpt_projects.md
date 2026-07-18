# SETUP -- ChatGPT Projects (plano free)

Setup do bundle **Construtor de Email** (`email_builder`) em ChatGPT Projects.
Este agente não usa Actions, não chama API externa e não precisa de nenhuma
chave -- por isso o plano **free** entrega fidelidade **completa**, igual ao
Custom GPT. ~5 minutos.

## Pré-requisitos

- Conta ChatGPT (plano free é suficiente).
- ZERO chaves de API necessárias.
- Os 15 arquivos deste bundle (12 pillars + `customgpt_instructions.json` +
  `system_instruction.md` + `README.md`) já baixados na sua máquina.

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Construtor de Email (email_builder)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o campo `instructions` de `customgpt_instructions.json` (ou, se
   preferir, todo o conteúdo de `system_instruction.md` -- os dois têm o
   mesmo texto, só em formatos diferentes).
3. Cole nas Instructions do projeto.

### 3. Suba os 12 arquivos de Knowledge

Em **Files** do projeto, suba os **12 arquivos de pillar**:

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

> ChatGPT Projects tem limite de 20 arquivos por projeto. 12 arquivos fica
> bem dentro do limite -- sobra espaço para você anexar sua própria
> brand_config (guia de marca, exemplos de email anteriores, etc.) se quiser.

### 4. Capabilities

Nenhuma capability especial é necessária. Este agente não navega na web, não
chama Actions e não gera imagem -- ele só lê a base de conhecimento (os 12
arquivos) e produz texto (o prompt template de email). Deixe o modelo padrão
do projeto como está.

### 5. Preencha a sua marca

Antes do primeiro teste, edite as Instructions e substitua os marcadores
`[fornecer: ...]` pelos dados reais da sua marca:
- `[fornecer: nome da marca]` -> o nome do seu negócio.
- `[fornecer: tom de voz da marca]` -> ex.: "direto, caloroso, sem jargão".
- `[fornecer: valores da marca]` -> ex.: "transparência, agilidade, cuidado com o cliente".

### 6. Teste

Inicie uma conversa dentro do project:

> `Escreva um email de marketing para o lançamento do produto X -- assunto, preheader, corpo`

O agente deve:
1. Confirmar (ou assumir, se você já deu contexto suficiente) a campanha e o público-alvo.
2. Gerar um **prompt template** de email -- ou seja, um molde reutilizável com
   slots de variável (`{{campaign}}`, `{{audience}}`, `{{tone}}` etc.), não um
   único email já finalizado.
3. Estruturar a saída em blocos: linhas de assunto (algumas variações),
   preheader, e os blocos de corpo do email.
4. Emitir `[fornecer: ...]` explícito em qualquer campo sem dado real (nunca
   inventar preço, nome de produto ou prazo de campanha).

## Fidelidade declarada: FULL

| Motivo | Detalhe |
|-------|---------|
| Sem Actions | Este agente é um gerador de texto puro -- não existe API externa a perder |
| Sem tiers de coleta | Diferente de agentes de pesquisa, aqui não há dado "ao vivo" para buscar |
| 12 arquivos de Knowledge completos | Os mesmos 12 pillars do Custom GPT, sem versão reduzida |

Ou seja: **ChatGPT Projects entrega exatamente a mesma capacidade que um
Custom GPT** para este bundle, porque não há Actions nem chave de API em jogo.

## Upgrade path para Custom GPT (opcional)

Você só precisa de um Custom GPT se quiser:
- Um link público/compartilhável com nome e ícone próprios (Explore GPTs).
- Distribuir o agente para outras pessoas sem que elas precisem copiar
  Instructions e Knowledge manualmente.

Nesse caso: crie um Custom GPT em **chatgpt.com -> Explore GPTs -> Create**,
cole o mesmo `instructions` e suba os mesmos 12 arquivos de `P0X_*.md` como
Knowledge. A fidelidade é idêntica à do Project -- a única diferença é a
forma de distribuição.

## Como usar (fluxo típico)

1. Diga a campanha ou o objetivo: `Preciso de um email para recuperação de carrinho abandonado`.
2. O agente gera o prompt template: variações de assunto, preheader e a
   estrutura de corpo (saudação, corpo principal, CTA, rodapé), com os campos
   variáveis explícitos (produto, nome do cliente, desconto, prazo).
3. Você preenche os `{{slots}}` do template com os dados reais da campanha
   (ou pede ao próprio agente para renderizar um exemplo preenchido).
4. Você usa o template renderizado na sua ferramenta de envio de email
   (ESP, plataforma de automação, etc.).

## Solução de problemas

- **"Ele inventou um nome de produto ou preço"** -> reforce nas Instructions:
  "nunca fabrique fatos, preços, nomes ou dados; sem dado real, emita
  `[fornecer: ...]`".
- **"A saída veio em inglês"** -> confirme que colou as Instructions em
  PT-BR (o campo `Idioma: pt-BR` já está na instrução) e peça explicitamente:
  "responda em português do Brasil".
- **"Ele entregou um email pronto em vez de um template"** -> peça
  explicitamente: "entregue como prompt template, com os campos variáveis
  marcados, não como um email já preenchido" (o comportamento correto é
  produzir o molde; renderizar um exemplo preenchido é um passo opcional
  seguinte).
- **Quero compartilhar com o time** -> use o upgrade path para Custom GPT
  acima, ou compartilhe este bundle (a pasta `email_builder/`) diretamente.
