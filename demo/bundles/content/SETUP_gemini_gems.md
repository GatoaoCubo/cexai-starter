# SETUP -- Gemini Gems

Setup do bundle `content` (agent de knowledge_card, arquitetura CEXAI) em
Gemini Gems. ~5 minutos.

## Pre-requisitos

- Conta Google + acesso a gemini.google.com.
- Preencha os campos `[fornecer: ...]` de `system_instruction.md` com o
  nome, o tom de voz e os valores da sua marca antes de subir.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Va em **Gems** -> **+ Create new Gem**.
3. Nome: o nome da sua marca seguido de "Content".
4. Description: `Agent de captura de conhecimento e documentacao (knowledge card), arquitetura CEXAI.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteudo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Teste

Em uma conversa do Gem:

> `Documentar o processo de integracao de novos funcionarios como um knowledge card`

O Gem deve:
1. Confirmar o processo/topico.
2. Produzir o knowledge_card completo (frontmatter + corpo estruturado).
3. Usar `[fornecer: ...]` para qualquer dado que voce nao informou -- nunca
   inventar.

## Vantagens do Gemini

- **Context window grande** (mais de 1M tokens nos modelos recentes) -- cabe
  tranquilamente os 12 arquivos deste bundle mais o conhecimento real da sua
  empresa.
- **Multi-modal nativo**: se voce quer documentar um processo a partir de um
  print de tela, planilha ou diagrama, pode anexar o arquivo direto na
  conversa.

## Limitacoes

- Gemini Gems tem suporte mais limitado a tools/Actions que o Custom GPT --
  irrelevante aqui, ja que este bundle nao usa nenhuma Action.
- A Knowledge do Gem tem um limite de tamanho total (confira o limite atual
  da sua conta); os 12 arquivos deste bundle somam poucos KB, entao cabem
  com folga.

## Fidelidade declarada: completa

Este bundle nao depende de nenhuma capability externa (sem Actions, sem MCP,
sem chave de API) -- os 12 arquivos de pilar + as Instructions sao o agent
inteiro em qualquer runtime, incluindo o Gemini.

## Solucao de problemas

- **O Gem parece ignorar um dos 12 arquivos** -> confirme que todos os 12
  foram de fato indexados em Knowledge (a interface do Gemini as vezes
  atrasa a indexacao de arquivos recem-subidos).
- **Resposta generica demais** -> confirme que voce preencheu os
  `[fornecer: ...]` antes de colar as Instructions.
- **Quero um card mais denso** -> peca: "aumente a densidade de informacao
  seguindo P01_knowledge.md e P09_config.md (tabelas e bullets antes de
  prosa)".
- **Quero migrar para Custom GPT ou Claude depois** -> os mesmos 12 arquivos
  servem para os tres runtimes; so troque onde a instrucao e colada.
