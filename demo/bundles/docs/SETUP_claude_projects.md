# SETUP -- Claude Projects

Setup do bundle CEXAI "Conhecimento e Documentacao" (capacidade `docs`, kind
`knowledge_card`) em Claude Projects. ~5 minutos, sem chaves de API.

## Pre-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO chaves de API ou MCP necessarias -- este agente funciona 100% via
  Project Knowledge + Custom Instructions (sem Actions, sem tools externas).

## Passo a passo

### 1. Crie o Project

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Conhecimento e Documentacao ([sua marca])`.

### 2. Cole as Custom Instructions

1. Abra o projeto -> **Project instructions** / Custom instructions (painel
   lateral).
2. Copie TODO o conteudo de `system_instruction.md` deste bundle (o
   comentario HTML da primeira linha e so proveniencia -- pode incluir ou
   remover, e inerte para o comportamento do agente).
3. Cole nas Custom Instructions do projeto.

### 3. Suba os 12 arquivos de Knowledge

Em **Project knowledge**, suba os 12 arquivos P0X deste bundle:

`P01_knowledge.md` ... `P12_orchestration.md` (a lista completa esta no
`README.md` deste bundle).

Claude Projects nao impoe um numero fixo de arquivos -- o limite e por
tamanho total do projeto. Os 12 arquivos deste bundle juntos somam poucos
KB, entao voce tem folga enorme para adicionar seus proprios documentos de
marca ao lado deles.

### 4. Preencha os placeholders

Antes de usar, edite a copia de `system_instruction.md` que voce colou e
troque cada `[fornecer: ...]` pelo dado real da sua marca -- nome, tom de
voz, valores. Lista completa em `SETUP_pt-br.md`.

### 5. Teste

Em uma conversa do Project:

> `Documentar o processo de onboarding de clientes como knowledge_card`

O agente deve:
1. Confirmar o assunto e pedir o que faltar.
2. Produzir um artefato `knowledge_card` (frontmatter YAML + corpo, em
   pt-BR) seguindo a estrutura ensinada pelos 12 arquivos P0X.
3. Emitir `[fornecer: ...]` em vez de inventar qualquer fato sem fonte.

## Vantagens do Claude Projects para este bundle

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|----------------|
| Limite de arquivos | 20 por GPT | sem limite fixo por arquivo (limite e por tamanho total) |
| Context window | 128K | 200K |
| Chaves de API / Actions | Nenhuma exigida por este bundle | Nenhuma exigida por este bundle |
| Custo | Plus ($20/mes) para Custom GPT | Pro ($20/mes) ou Free com limites |
| Tool calls paralelas | Sequenciais | Nativas via tool_use (nao usado por este bundle) |

## Solucao de problemas

- **"Claude nao usou os arquivos de Knowledge"** -> confirme que os 12
  arquivos aparecem na lista de Project knowledge (nao apenas anexados numa
  mensagem avulsa da conversa).
- **"A saida veio em ingles"** -> confirme que a linha "Idioma: pt-BR"
  sobreviveu na copia colada nas Custom Instructions.
- **"Quero rodar isso via API/Console em vez do site"** -> cole o mesmo
  `system_instruction.md` como system prompt e injete os 12 arquivos como
  contexto (RAG ou colados diretamente); o comportamento e identico.
- **"Quero adicionar meus proprios documentos de marca"** -> suba-os junto
  com os 12 P0X em Project knowledge; o agente passa a citar as duas fontes.
