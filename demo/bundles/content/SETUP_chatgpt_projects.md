# SETUP -- ChatGPT (Custom GPT ou Projects)

Setup do bundle `content` (agent de knowledge_card, arquitetura CEXAI) no
ChatGPT. Duas formas de rodar, dependendo do seu plano: Custom GPT (ChatGPT
Plus, ~5 min) ou ChatGPT Projects (qualquer plano, ~5 min). As duas usam os
MESMOS 12 arquivos de pilar -- este bundle nao tem tiers de coleta, Actions,
nem chaves de API.

## Pre-requisitos

- Conta ChatGPT (free ou Plus).
- Preencha os campos `[fornecer: ...]` de `system_instruction.md` (ou de
  `customgpt_instructions.json`) com o nome, o tom de voz e os valores da SUA
  marca antes de subir -- isso e o que faz o agent falar como voce, e nao de
  forma generica.

## Opcao A -- Custom GPT (ChatGPT Plus)

### 1. Crie o Custom GPT

1. Acesse **chatgpt.com** -> menu lateral -> **Explore GPTs** -> **+ Create**.
2. Va na aba **Configure**.
3. **Name**: cole o campo `name` de `customgpt_instructions.json` (ou digite
   o nome da sua marca seguido de " -- Content").
4. **Description**: cole o campo `description` de `customgpt_instructions.json`.

### 2. Cole as Instructions

1. Abra `customgpt_instructions.json` deste bundle.
2. Copie o conteudo do campo `instructions` (e o mesmo texto de
   `system_instruction.md`, so que em formato JSON).
3. Cole no campo **Instructions** do Custom GPT.

### 3. Suba os 12 arquivos de Knowledge

1. Clique em **Upload files**.
2. Suba os 12 arquivos, de `P01_knowledge.md` ate `P12_orchestration.md`.
3. Confirme que os 12 aparecem na lista.

> Custom GPT aceita ate 20 arquivos por GPT. Os 12 deste bundle ficam bem
> dentro do limite -- sobra espaco para voce anexar conhecimento real da sua
> empresa depois.

### 4. Capabilities

- **Web Browsing**: opcional (este agent nao depende de busca na web).
- **Code Interpreter**: opcional (util se voce quiser consolidar varios
  cards de uma vez).
- **DALL-E**: NAO usado por este agent.

### 5. Conversation starters

Adicione algumas sugestoes na configuracao do GPT:

- `Documentar o processo de integracao de novos funcionarios como um knowledge card`
- `Documentar nossa politica de reembolso como um knowledge card`
- `Destilar o que sabemos sobre o nosso concorrente principal em um knowledge card`

### 6. Salvar + publicar

1. Clique em **Create/Update**.
2. Escolha a visibilidade: **Only me** (recomendado para testar primeiro),
   **Anyone with a link**, ou **Public**.

## Opcao B -- ChatGPT Projects (qualquer plano)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: o nome da sua marca seguido de "Content".

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (icone de engrenagem).
2. Copie o conteudo de `system_instruction.md`.
3. Cole nas Instructions do projeto.

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os 12 arquivos, de `P01_knowledge.md` ate
`P12_orchestration.md`.

### 4. Teste

Inicie uma conversa dentro do project:

> `Documentar o processo de integracao de novos funcionarios como um knowledge card`

O agent deve:
1. Confirmar (ou perguntar) o processo/topico exato a documentar.
2. Produzir um knowledge_card completo: frontmatter + corpo estruturado
   (Referencia Rapida, Conceitos-Chave, Fases da Estrategia, Regras de Ouro,
   Fluxo, Comparativo, Referencias).
3. Nunca inventar um dado que voce nao forneceu -- em vez disso, emitir um
   placeholder `[fornecer: ...]`.

## Fidelidade declarada: completa nas duas opcoes

Diferente de bundles com Actions (pesquisa de mercado, etc.), este bundle nao
tem tiers de coleta nem chaves de API -- os 12 arquivos de pilar SAO o agent
completo, em qualquer runtime. A unica diferenca entre Custom GPT e Projects
e o mecanismo de configuracao (Actions e conversation starters ficam
disponiveis so no Custom GPT).

## Solucao de problemas

- **"O agent inventou o processo"** -> reforce: "nunca fabrique fatos; onde
  faltar dado, use `[fornecer: ...]`" (ja esta nas Instructions, mas
  reforcar na conversa ajuda).
- **Faltam secoes no card gerado** -> peca explicitamente: "siga a estrutura
  completa de P06_schema.md (domain_kc ou meta_kc)".
- **Quero trocar o tom de voz** -> edite os campos `[fornecer: ...]` em
  `system_instruction.md` / `customgpt_instructions.json` ANTES de subir, ou
  peca ao agent para ajustar o tom durante a conversa.
- **Quero fazer upgrade de Projects para Custom GPT** -> os mesmos 12
  arquivos servem para as duas opcoes; so troque onde a instrucao e colada.
