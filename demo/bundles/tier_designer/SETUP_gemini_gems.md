# SETUP -- Gemini Gems

Setup do bundle `tier_designer` (agente Projetista de Planos de Assinatura)
em Gemini Gems. Sem extensions, sem chave de API -- os 12 arquivos + o
texto de instruções bastam. ~5 minutos.

## Pré-requisitos

- Conta Google com acesso a **gemini.google.com** e a funcionalidade Gems
  habilitada (a disponibilidade varia por plano e região -- confira o que
  está liberado na sua conta).
- ZERO chaves de API ou extensions necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem** (ou "Novo Gem").
3. Nome: `Planos de Assinatura [sua marca]`.
4. Descrição: `Agente projetista de planos e tiers de assinatura SaaS (CEXAI)`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca, se já tiver.

### 3. Suba a Knowledge

Em **Knowledge** (arquivos) do Gem, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Extensions

Nenhuma extension é necessária. Deixe Google Search e demais extensions
desligadas se quiser testar exatamente o que os 12 arquivos + as
instruções entregam sozinhos. Este agente não pesquisa na web: ele projeta
a matriz de planos a partir do que você descreve mais o conhecimento de
domínio já embutido nos 12 arquivos.

### 5. Teste

Em uma conversa do Gem:

> `Projete os planos de assinatura para um app de treino com assinatura mensal, BR, quero 3 tiers`

O Gem deve:
1. Escolher a unidade de monetização e desenhar de 3 a 4 tiers com nomes
   orientados a resultado.
2. Entregar os tiers com preços em centavos e feature_matrix tabular.
3. Marcar dados que faltam com `[fornecer: ...]` em vez de inventar.

## Fidelidade declarada: FULL

Como este agente é puramente de raciocínio + conhecimento de domínio
(nenhuma Action, MCP ou browsing envolvida), o Gemini Gems entrega a MESMA
capacidade que ChatGPT ou Claude para este bundle específico -- a diferença
prática entre plataformas fica por conta da janela de contexto e do limite
de tamanho da Knowledge, não da capacidade do agente em si.

## Vantagens do Gemini para este bundle

- Janela de contexto tipicamente grande -- folga para colar matrizes de
  planos longas de volta para o Gem revisar.
- Multi-modal nativo -- se você quiser colar um print da página de preços de
  um concorrente, o Gem pode descrevê-la como insumo (mas os preços ainda
  precisam ser confirmados por você; a imagem não vira fonte automática de
  verdade).

## Solução de problemas

- **"O Gem ignorou parte das instructions"** -> confira se colou o
  `system_instruction.md` inteiro, incluindo os placeholders
  `[fornecer: ...]`.
- **"Quero versionar a matriz de planos gerada"** -> salve o YAML de saída
  em um arquivo seu; o Gem não persiste artefatos fora da conversa.
- **"Ele inventou um dado"** -> reforce: "todo número ou fato sem origem
  real precisa vir marcado como placeholder, nunca inventado".
- **"Prefiro ChatGPT ou Claude"** -> veja `SETUP_chatgpt_projects.md` ou
  `SETUP_claude_projects.md`; os mesmos 12 arquivos + instruções servem
  para os três.
