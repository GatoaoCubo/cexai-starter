# SETUP -- ChatGPT Projects e Custom GPT

Setup do bundle `pricing` (agente de Precificacao) no ChatGPT. Duas rotas
possiveis: **Projects** (mais rapida) ou **Custom GPT** (GPT persistente e
compartilhavel). Nenhuma das duas exige chave de API -- este agente nao
chama nenhuma ferramenta externa, ele so raciocina sobre o que voce descreve
mais o conhecimento de dominio dos 12 arquivos. ~5 minutos.

## Pre-requisitos

- Conta ChatGPT com Projects ou Custom GPTs habilitados (normalmente planos
  pagos -- confira o que esta disponivel na sua conta).
- ZERO chaves de API necessarias.

## Opcao A -- ChatGPT Projects (recomendado, mais rapido)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. De um nome, por exemplo: `Precificacao [sua marca]`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (icone de engrenagem).
2. Copie TODO o conteudo de `system_instruction.md` deste bundle.
3. Cole no campo Instructions do projeto.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca (nome, tom de voz, valores) -- ou deixe como estao: o agente vai
   pedir essa informacao antes de produzir qualquer coisa em vez de
   inventar.

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os 12 arquivos `P0X` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Esses 12 arquivos SAO o contrato completo de como o agente projeta um
`content_monetization`: schema de campos, exemplos golden, gates de
qualidade, arquitetura do pipeline de 9 estagios. Nao existe versao
reduzida -- suba os 12.

### 4. Teste

Inicie uma conversa dentro do project:

> `Crie os niveis de precificacao para um SaaS de gestao financeira, publico BR, cobranca em BRL`

O agente deve:
1. Usar (ou perguntar) os dados de negocio: nicho, moeda, mercado.
2. Seguir o pipeline de 9 estagios (PARSE->PRICING->CREDITS->CHECKOUT->
   COURSES->ADS->EMAILS->VALIDATE->DEPLOY), aplicando so os estagios
   relevantes ao seu caso.
3. Entregar tiers com precos em centavos, margem minima >= 30% explicita, e
   nunca inventar numero sem marcar `[fornecer: ...]` ou `[A CONFIRMAR]`.

## Opcao B -- Custom GPT (GPT persistente e compartilhavel)

Use esta rota se voce quer um GPT com link proprio -- por exemplo, para o
time todo usar, ou para publicar no catalogo interno da sua organizacao.

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

Mesmos 12 arquivos `P0X` da Opcao A, agora em **Knowledge**.

### 4. Conversation starter

Adicione o texto de `conversation_starters[0]` do JSON como sugestao de
prompt inicial.

### 5. Capabilities

Deixe **Web Browsing**, **Code Interpreter** e **DALL-E** desligados --
nenhum e necessario (o JSON ja declara os tres como `false` em
`capabilities`). Este agente nao precisa de nenhuma ferramenta externa para
funcionar com fidelidade completa.

## Fidelidade declarada: FULL

| Motivo | Detalhe |
|-------|---------|
| Sem dependencia de ferramentas externas | O agente so precisa de raciocinio + os 12 arquivos de conhecimento -- nao ha Actions, MCP nem browsing envolvidos |
| Os 12 pillares cabem inteiros em Files/Knowledge | Nenhum pillar precisa ser resumido ou cortado |
| Mesmo contrato em qualquer rota | Projects (mais rapido) e Custom GPT (persistente) usam o MESMO texto de instrucoes e os mesmos 12 arquivos |

## Como usar (fluxo tipico)

1. Descreva o produto/servico e o mercado: `Crie a precificacao para um curso de marcenaria, Hotmart, BR`.
2. O agente aplica o pipeline de 9 estagios e devolve os tiers, o sistema de
   creditos (se fizer sentido para o seu caso) e a integracao de checkout
   recomendada.
3. Todo numero sem fonte real vem marcado com `[fornecer: ...]` -- preencha
   e peca a versao final.

## Solucao de problemas

- **"O placeholder `[fornecer: ...]` nao some"** -> normal, ele so some
  quando voce fornece o dado real (nome da marca, tom de voz) nas
  Instructions. Edite o campo com os seus dados.
- **"Ele inventou um preco"** -> reforce: "todo preco ou numero sem origem
  real precisa vir marcado como placeholder, nunca inventado".
- **"Quero usar em outra IA"** -> veja `SETUP_claude_projects.md` ou
  `SETUP_gemini_gems.md`; os mesmos 12 arquivos servem para as tres.
- **"Prefiro nao criar um Custom GPT"** -> a Opcao A (Projects) e
  equivalente em conteudo e nao exige acesso ao catalogo de GPTs.
