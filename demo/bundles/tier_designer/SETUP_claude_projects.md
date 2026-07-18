# SETUP -- Claude Projects

Setup do bundle `tier_designer` (agente Projetista de Planos de Assinatura)
em Claude Projects. Sem MCP, sem Actions, sem chave de API -- os 12 arquivos
+ o texto de instruções são tudo que o agente precisa. ~5 minutos.

## Pré-requisitos

- Conta Claude com Projects habilitado (confira o que está disponível no
  seu plano -- Projects costuma ter uso mais generoso em planos pagos).
- ZERO chaves de API ou integrações necessárias.

## Passo a passo

### 1. Crie o Project

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Dê um nome, por exemplo: `Planos de Assinatura [sua marca]`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project knowledge** / instruções personalizadas
   (ícone de engrenagem do projeto).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle (inclui um
   comentário HTML no topo com metadados de geração -- pode deixar, o
   Claude trata como contexto e não como instrução ativa).
3. Cole no campo de instruções personalizadas do projeto.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca, se já tiver -- senão, o agente vai pedir essa informação antes de
   produzir qualquer coisa em vez de inventar.

### 3. Suba os 12 arquivos de Knowledge

Em **Project knowledge**, suba os 12 arquivos `P0X` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não limita a quantidade de arquivos como algumas rotas do
ChatGPT -- o limite é por tamanho total do projeto, então os 12 arquivos
deste bundle cabem com folga.

### 4. Teste

Em uma conversa dentro do projeto:

> `Crie os tiers de assinatura para uma plataforma de cursos online, cobranca em BRL, quero 3 planos`

O agente deve:
1. Escolher a unidade de monetização (flat/per_seat/per_usage/hybrid) e
   justificar a escolha.
2. Entregar tiers com nomes orientados a resultado, preço em centavos,
   feature_matrix tabular (nunca lista em prosa).
3. Marcar com `[fornecer: ...]` ou `[A CONFIRMAR]` qualquer dado que você
   não informou -- nunca inventar.

## Por que Claude Projects funciona bem para este bundle

| Aspecto | Detalhe |
|---------|---------|
| Ferramentas externas necessárias | nenhuma -- o agente é puramente raciocínio + conhecimento de domínio |
| Tamanho dos 12 arquivos | cabem com folga no limite de Project knowledge |
| Persistência | a config de tiers gerada em uma conversa pode ser colada de volta em outra, dentro do mesmo projeto |

## Fidelidade declarada: FULL

Este agente não depende de Actions, MCP ou browsing -- é um agente de
raciocínio + conhecimento de domínio (precificação SaaS, feature matrix,
grandfathering, expansão de MRR). Os 12 arquivos cobrem 100% do contrato
original; nada foi cortado ou resumido para caber em Claude Projects.

## Solução de problemas

- **"Quero que ele lembre a config entre conversas diferentes"** -> dentro
  do mesmo Project, o Project knowledge persiste; para retomar uma config
  já gerada em uma conversa nova, cole o YAML de volta no chat.
- **"Ele não seguiu a voz da marca"** -> confira se você preencheu os
  campos VOZ DA MARCA (Tom, Valores) nas Instructions -- sem isso, o
  placeholder `[fornecer: ...]` fica ativo de propósito.
- **"Ele misturou subscription_tier com content_monetization (cursos,
  afiliados)"** -> reforce: "produza apenas subscription_tier -- não combine
  com estratégias de content monetization" (ver `P02_model.md`, seção
  Escopo).
- **"Ele inventou um dado"** -> reforce: "todo número ou fato sem origem
  real precisa vir marcado como placeholder, nunca inventado" (ver
  `P11_feedback.md`, seção Antipadrões).
- **"Prefiro ChatGPT ou Gemini"** -> veja `SETUP_chatgpt_projects.md` ou
  `SETUP_gemini_gems.md`; os mesmos 12 arquivos + o mesmo texto de
  instruções servem para os três.
