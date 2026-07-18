# SETUP -- Gemini Gems

Setup do bundle `pricing` (agente de Precificacao) em Gemini Gems. Sem
extensions, sem chave de API -- os 12 arquivos + o texto de instrucoes
bastam. ~5 minutos.

## Pre-requisitos

- Conta Google com acesso a **gemini.google.com** e a funcionalidade Gems
  habilitada (a disponibilidade varia por plano e regiao -- confira o que
  esta liberado na sua conta).
- ZERO chaves de API ou extensions necessarias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Va em **Gems** -> **+ Create new Gem** (ou "Novo Gem").
3. Nome: `Precificacao [sua marca]`.
4. Descricao: `Agente de precificacao e monetizacao de conteudo (CEXAI)`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteudo.
3. Cole no campo Instructions do Gem.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca, se ja tiver.

### 3. Suba a Knowledge

Em **Knowledge** (arquivos) do Gem, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Extensions

Nenhuma extension e necessaria. Deixe Google Search e demais extensions
desligadas se quiser testar exatamente o que os 12 arquivos + as
instrucoes entregam sozinhos. Este agente nao pesquisa na web: ele projeta
a config de precificacao a partir do que voce descreve mais o
conhecimento de dominio ja embutido nos 12 arquivos.

### 5. Teste

Em uma conversa do Gem:

> `Crie os niveis de precificacao para um app de treino que vende assinatura mensal, BR, quero 3 tiers`

O Gem deve:
1. Seguir o pipeline de 9 estagios, usando so os estagios relevantes ao seu caso.
2. Entregar os 3 tiers com precos em centavos e margem minima explicita.
3. Marcar dados que faltam com `[fornecer: ...]` em vez de inventar.

## Fidelidade declarada: FULL

Como este agente e puramente de raciocinio + conhecimento de dominio
(nenhuma Action, MCP ou browsing envolvida), o Gemini Gems entrega a MESMA
capacidade que ChatGPT ou Claude para este bundle especifico -- a diferenca
pratica entre plataformas fica por conta da janela de contexto e do limite
de tamanho da Knowledge, nao da capacidade do agente em si.

## Vantagens do Gemini para este bundle

- Janela de contexto tipicamente grande -- folga para colar configs longas
  de volta para o Gem revisar.
- Multi-modal nativo -- se voce quiser colar um print de uma tela de
  precos de um concorrente, o Gem pode descreve-la como insumo (mas os
  precos ainda precisam ser confirmados por voce; a imagem nao vira fonte
  automatica de verdade).

## Solucao de problemas

- **"O Gem ignorou parte das instructions"** -> confira se colou o
  `system_instruction.md` inteiro, incluindo os placeholders
  `[fornecer: ...]`.
- **"Quero versionar a config gerada"** -> salve o YAML de saida em um
  arquivo seu; o Gem nao persiste artefatos fora da conversa.
- **"Ele inventou um dado"** -> reforce: "todo numero ou fato sem origem
  real precisa vir marcado como placeholder, nunca inventado".
- **"Prefiro ChatGPT ou Claude"** -> veja `SETUP_chatgpt_projects.md` ou
  `SETUP_claude_projects.md`; os mesmos 12 arquivos + instrucoes servem
  para os tres.
