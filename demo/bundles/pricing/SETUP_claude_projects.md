# SETUP -- Claude Projects

Setup do bundle `pricing` (agente de Precificacao) em Claude Projects. Sem
MCP, sem Actions, sem chave de API -- os 12 arquivos + o texto de
instrucoes sao tudo que o agente precisa. ~5 minutos.

## Pre-requisitos

- Conta Claude com Projects habilitado (confira o que esta disponivel no
  seu plano -- Projects costuma ter uso mais generoso em planos pagos).
- ZERO chaves de API ou integracoes necessarias.

## Passo a passo

### 1. Crie o Project

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. De um nome, por exemplo: `Precificacao [sua marca]`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project knowledge** / instrucoes personalizadas
   (icone de engrenagem do projeto).
2. Copie TODO o conteudo de `system_instruction.md` deste bundle (inclui um
   comentario HTML no topo com metadados de geracao -- pode deixar, o
   Claude trata como contexto e nao como instrucao ativa).
3. Cole no campo de instrucoes personalizadas do projeto.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca, se ja tiver -- senao, o agente vai pedir essa informacao antes de
   produzir qualquer coisa em vez de inventar.

### 3. Suba os 12 arquivos de Knowledge

Em **Project knowledge**, suba os 12 arquivos `P0X` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects nao limita a quantidade de arquivos como algumas rotas do
ChatGPT -- o limite e por tamanho total do projeto, entao os 12 arquivos
deste bundle cabem com folga.

### 4. Teste

Em uma conversa dentro do projeto:

> `Crie os niveis de precificacao para uma agencia que vende relatorios de SEO por assinatura, BR`

O agente deve:
1. Seguir o pipeline de 9 estagios (PARSE->PRICING->CREDITS->CHECKOUT->
   COURSES->ADS->EMAILS->VALIDATE->DEPLOY), usando so os estagios
   relevantes ao seu caso.
2. Entregar tiers com precos em centavos, margem minima explicita
   (>= 30%), politica de saldo negativo (overdraft) definida.
3. Marcar com `[fornecer: ...]` ou `[A CONFIRMAR]` qualquer dado que voce
   nao informou -- nunca inventar.

## Por que Claude Projects funciona bem para este bundle

| Aspecto | Detalhe |
|---------|---------|
| Ferramentas externas necessarias | nenhuma -- o agente e puramente raciocinio + conhecimento de dominio |
| Tamanho dos 12 arquivos | cabem com folga no limite de Project knowledge |
| Persistencia | a config gerada em uma conversa pode ser colada de volta em outra, dentro do mesmo projeto |

## Fidelidade declarada: FULL

Este agente nao depende de Actions, MCP ou browsing -- e um agente de
raciocinio + conhecimento de dominio (precificacao, creditos, checkout,
cursos, anuncios, e-mail). Os 12 arquivos cobrem 100% do contrato original;
nada foi cortado ou resumido para caber em Claude Projects.

## Solucao de problemas

- **"Quero que ele lembre a config entre conversas diferentes"** -> dentro
  do mesmo Project, o Project knowledge persiste; para retomar uma config
  ja gerada em uma conversa nova, cole o YAML de volta no chat.
- **"Ele nao seguiu a voz da marca"** -> confira se voce preencheu os
  campos VOZ DA MARCA (Tom, Valores) nas Instructions -- sem isso, o
  placeholder `[fornecer: ...]` fica ativo de proposito.
- **"Ele inventou um dado"** -> reforce: "todo numero ou fato sem origem
  real precisa vir marcado como placeholder, nunca inventado" (ver
  `P11_feedback.md`, secao Antipadroes).
- **"Prefiro ChatGPT ou Gemini"** -> veja `SETUP_chatgpt_projects.md` ou
  `SETUP_gemini_gems.md`; os mesmos 12 arquivos + o mesmo texto de
  instrucoes servem para os tres.
