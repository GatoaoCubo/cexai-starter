# SETUP -- Claude Projects

Setup do bundle **Construtor de Email** (`email_builder`) em Claude Projects.
Sem Actions, sem MCP, sem chave de API -- é só colar a instrução e subir a
base de conhecimento. ~5 minutos.

## Pré-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO integrações externas necessárias (este agente não chama ferramenta
  nenhuma fora do próprio modelo).

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Construtor de Email (email_builder)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral, ícone de engrenagem).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle (o
   comentário HTML da primeira linha pode ficar -- é só uma marca de
   proveniência, não afeta o comportamento do agente).
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge

Em **Project Knowledge**, suba os 12 arquivos de pillar:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de contagem de arquivos (o limite é por
tamanho total do projeto, bem folgado para 12 arquivos de texto).

### 4. Nenhuma integração adicional é necessária

Diferente de agentes de pesquisa que dependem de MCP bridges para buscar
dado externo, o Construtor de Email é 100% autocontido: ele produz um
prompt template a partir do que está na sua base de conhecimento (os 12
pillars) e da sua brand voice. Não há passo de "conectar MCP" aqui.

### 5. Preencha a sua marca

Antes do primeiro teste, edite as Project Instructions e substitua os
marcadores `[fornecer: ...]`:
- `[fornecer: nome da marca]` -> o nome do seu negócio.
- `[fornecer: tom de voz da marca]` -> ex.: "consultivo, direto, sem jargão técnico".
- `[fornecer: valores da marca]` -> ex.: "transparência, agilidade, foco no resultado do cliente".

### 6. Teste

Em uma conversa do Project:

> `Escreva um email de marketing para o lançamento do produto X -- assunto, preheader, corpo`

O agente deve:
1. Entender a campanha/público a partir do seu pedido.
2. Entregar um **prompt template** de email (com slots de variável como
   `{{campaign}}`, `{{audience}}`, `{{cta}}`), não um email já finalizado.
3. Cobrir linhas de assunto (com variações), preheader e blocos de corpo.
4. Marcar com `[fornecer: ...]` qualquer dado que ele não tenha (preço,
   prazo, nome exato do produto) em vez de inventar.

## Fidelidade declarada: FULL

Este bundle não tem tiers de coleta nem Actions -- a mesma base de 12
pillars que roda no Custom GPT roda aqui, com o mesmo comportamento.

## Vantagens do Claude Projects para este bundle

| Aspecto | Custom GPT / ChatGPT Projects | Claude Projects |
|---------|-----------------|----------------|
| Limite de arquivos de Knowledge | 20 (Custom GPT) | Sem limite de contagem (limite por tamanho total) |
| Context window | 128K | 200K |
| Necessário plano pago | Só para Custom GPT (Projects é free) | Free já funciona |
| Setup de Actions/MCP | Não aplicável (agente não usa) | Não aplicável (agente não usa) |

Para este bundle específico a diferença prática entre runtimes é pequena --
os três (ChatGPT, Claude, Gemini) entregam fidelidade completa, já que não
há Action nem tier de coleta em jogo. Escolha o runtime que você já usa no
dia a dia.

## Como usar (fluxo típico)

1. Diga a campanha: `Preciso de um email para recuperação de carrinho abandonado`.
2. Claude gera o prompt template: variações de assunto, preheader, estrutura
   de corpo (saudação, corpo principal, CTA, rodapé), com os campos
   variáveis explícitos.
3. Você preenche os `{{slots}}` com os dados reais (ou pede para o próprio
   Claude renderizar um exemplo preenchido, colando valores concretos).
4. Você leva o resultado renderizado para a sua ferramenta de envio de email.

## Solução de problemas

- **"Ele inventou um dado (preço, prazo, nome de produto)"** -> reforce:
  "nunca fabrique fatos; sem dado real, emita `[fornecer: ...]`" (já está
  nas Guardrails do system_instruction, mas reforçar ajuda em sessões longas).
- **Resposta veio em inglês** -> peça explicitamente "responda em português
  do Brasil"; confirme que colou o `system_instruction.md` (que já fixa
  `Idioma: pt-BR`) nas Project Instructions, não só nos Knowledge files.
- **Quer só um email pronto, não um template** -> peça: "renderize um
  exemplo completo do template acima, preenchido para <produto/campanha
  específica>" -- o comportamento default é entregar o molde reutilizável.
- **Quer saber onde colocar sua brand_config.yaml real** -> anexe o arquivo de
  configuração de marca da sua empresa como mais um arquivo de Knowledge do
  projeto; o agente vai priorizá-lo sobre os placeholders `[fornecer: ...]`.
