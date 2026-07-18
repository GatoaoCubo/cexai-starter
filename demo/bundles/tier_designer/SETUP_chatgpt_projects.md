# SETUP -- ChatGPT Projects e Custom GPT

Setup do bundle `tier_designer` (agente Projetista de Planos de Assinatura) no
ChatGPT. Duas rotas possíveis: **Projects** (mais rápida) ou **Custom GPT**
(GPT persistente e compartilhável). Nenhuma das duas exige chave de API --
este agente não chama nenhuma ferramenta externa, ele só raciocina sobre o
que você descreve mais o conhecimento de domínio dos 12 arquivos. ~5 minutos.

## Pré-requisitos

- Conta ChatGPT com Projects ou Custom GPTs habilitados (normalmente planos
  pagos -- confira o que está disponível na sua conta).
- ZERO chaves de API necessárias.

## Opção A -- ChatGPT Projects (recomendado, mais rápido)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Dê um nome, por exemplo: `Planos de Assinatura [sua marca]`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole no campo Instructions do projeto.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca (nome, tom de voz, valores) -- ou deixe como estão: o agente vai
   pedir essa informação antes de produzir qualquer coisa em vez de
   inventar.

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os 12 arquivos `P0X` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Esses 12 arquivos SÃO o contrato completo de como o agente projeta um
`subscription_tier`: schema de campos, gates de qualidade (H01-H11), rubrica
de pontuação (D1-D10), exemplos golden e antiexemplos. Não existe versão
reduzida -- suba os 12.

### 4. Teste

Inicie uma conversa dentro do project:

> `Projete a matriz de planos para um SaaS de gestão financeira B2B, cobranca em BRL, 3 tiers`

O agente deve:
1. Usar (ou perguntar) os dados de negócio: produto, moeda, unidade de
   monetização (flat/per_seat/per_usage/hybrid).
2. Entregar de 3 a 4 tiers com nomes orientados a resultado (Starter,
   Growth, Business, Enterprise) -- nunca Bronze/Silver/Gold.
3. Entregar preços em centavos (nunca em ponto flutuante), feature_matrix
   tabular, e política de grandfathering quando aplicável.
4. Nunca inventar um número sem marcar `[fornecer: ...]` ou `[A CONFIRMAR]`.

## Opção B -- Custom GPT (GPT persistente e compartilhável)

Use esta rota se você quer um GPT com link próprio -- por exemplo, para o
time todo usar, ou para publicar no catálogo interno da sua organização.

### 1. Crie o GPT

1. Acesse **chatgpt.com** -> **Explore GPTs** -> **+ Create** -> aba
   **Configure**.
2. **Name**: copie o campo `name` de `customgpt_instructions.json` (troque
   o placeholder de marca pelo nome real).
3. **Description**: copie o campo `description` do mesmo arquivo.

### 2. Cole as Instructions

1. Abra `customgpt_instructions.json` neste bundle.
2. Copie o valor do campo `instructions` (a string completa) para o campo
   **Instructions** do GPT.

### 3. Suba os 12 arquivos de Knowledge

Mesmos 12 arquivos `P0X` da Opção A, agora em **Knowledge**.

### 4. Conversation starter

Adicione o texto de `conversation_starters[0]` do JSON como sugestão de
prompt inicial.

### 5. Capabilities

Deixe **Web Browsing**, **Code Interpreter** e **DALL-E** desligados --
nenhum é necessário (o JSON já declara os três como `false` em
`capabilities`). Este agente não precisa de nenhuma ferramenta externa para
funcionar com fidelidade completa.

## Fidelidade declarada: FULL

| Motivo | Detalhe |
|-------|---------|
| Sem dependência de ferramentas externas | O agente só precisa de raciocínio + os 12 arquivos de conhecimento -- não há Actions, MCP nem browsing envolvidos |
| Os 12 pillares cabem inteiros em Files/Knowledge | Nenhum pillar precisa ser resumido ou cortado |
| Mesmo contrato em qualquer rota | Projects (mais rápido) e Custom GPT (persistente) usam o MESMO texto de instruções e os mesmos 12 arquivos |

## Como usar (fluxo típico)

1. Descreva o produto e o modelo de negócio: `Crie os tiers de assinatura
   para uma ferramenta de automação de marketing, modelo per_seat, BR`.
2. O agente escolhe a unidade de monetização (flat/per_seat/per_usage/hybrid),
   desenha de 3 a 4 tiers com nomes orientados a resultado, e entrega o
   objeto de preço no formato canônico do Stripe (unit_amount em centavos,
   currency ISO 4217, interval).
3. Todo número sem fonte real vem marcado com `[fornecer: ...]` -- preencha
   e peça a versão final.

## Solução de problemas

- **"O placeholder `[fornecer: ...]` não some"** -> normal, ele só some
  quando você fornece o dado real (nome da marca, tom de voz) nas
  Instructions. Edite o campo com os seus dados.
- **"Ele usou nome de medalha (Bronze/Silver/Gold)"** -> reforce: "use nomes
  de tier orientados a resultado (Starter/Growth/Business/Enterprise), nunca
  metáforas de medalha" (ver `P02_model.md`, seção Regras).
- **"Ele inventou um preço em ponto flutuante (9.99)"** -> reforce: "todo
  preço deve ser um inteiro na menor unidade de moeda (centavos), nunca
  ponto flutuante" (ver `P06_schema.md`, Restrições).
- **"Quero usar em outra IA"** -> veja `SETUP_claude_projects.md` ou
  `SETUP_gemini_gems.md`; os mesmos 12 arquivos servem para as três.
- **"Prefiro não criar um Custom GPT"** -> a Opção A (Projects) é
  equivalente em conteúdo e não exige acesso ao catálogo de GPTs.
