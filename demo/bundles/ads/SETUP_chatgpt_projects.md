# SETUP -- ChatGPT (Custom GPT ou Projects)

Setup do bundle CEXAI `ads` (Ads and Copy) no ChatGPT. Este bundle não usa
Actions, tools externas nem chaves de API -- é um agente 100% de geração de
texto (copy de anúncio), então QUALQUER plano ChatGPT funciona. ~5 minutos.

## Pré-requisitos

- Conta ChatGPT (plano free serve para Projects; Custom GPT próprio exige Plus).
- ZERO chaves de API necessárias.
- Os 15 arquivos do núcleo deste bundle (12 pilares P0X + `customgpt_instructions.json`
  + `system_instruction.md` + `README.md`) baixados em uma pasta local.

## Opção A -- Custom GPT (ChatGPT Plus)

### 1. Crie o GPT

1. Acesse **chatgpt.com** -> **Explore GPTs** -> **Create** (ou **+ Create a GPT**).
2. Vá para a aba **Configure**.

### 2. Preencha nome e descrição

1. **Name**: copie o campo `name` de `customgpt_instructions.json`.
2. **Description**: copie o campo `description` de `customgpt_instructions.json`.

### 3. Cole as Instructions

1. Abra `customgpt_instructions.json`.
2. Copie o valor do campo `instructions` (a string inteira).
3. Cole na caixa **Instructions** do Configure.

### 4. Suba os 12 arquivos de Knowledge

Em **Knowledge**, faça upload dos 12 arquivos de pilar:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 5. Conversation starters

Em **Conversation starters**, adicione a entrada de `conversation_starters`
do JSON:

> Escreva a copy de anúncio para \<produto/oferta\> visando \<público\>

### 6. Capabilities

Nenhuma capability é necessária -- deixe **Web Browsing**, **Code
Interpreter** e **DALL-E** desligados (o JSON já declara os 3 como `false`).

### 7. Antes de publicar

Substitua TODO marcador `[fornecer: ...]` (nome da marca, tom de voz,
valores) pelos dados reais da sua marca -- direto no texto que você colou
em Instructions.

### 8. Teste

> Escreva a copy de anúncio para tênis de corrida visando corredores
> iniciantes de 25-40 anos

O agente deve produzir um artefato `prompt_template` com hooks, CTAs e
variantes por tamanho de plataforma, na voz de marca configurada.

## Opção B -- ChatGPT Projects (qualquer plano)

Se você não tem ChatGPT Plus (ou prefere um Project em vez de um GPT público):

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Ads and Copy`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o conteúdo de `system_instruction.md`.
3. Cole nas Instructions do projeto (substitua os `[fornecer: ...]` pelos
   dados da sua marca antes ou depois de colar).

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os 12 arquivos `P0X_*.md`.

### 4. Teste

Use a mesma mensagem de teste da Opção A, dentro de uma conversa do projeto.

## Diferença entre as duas opções

| Aspecto | Custom GPT | Projects |
|---------|-----------|----------|
| Plano exigido | ChatGPT Plus | Qualquer plano |
| Visibilidade | Pode ser publicado/compartilhado | Privado, dentro da sua conta |
| Conversation starters | Sim (campo dedicado) | Não (cole na primeira mensagem) |
| Limite de arquivos de Knowledge | 20 | Por tamanho total, não por contagem |

## Solução de problemas

- **O agente inventa nome de marca, tom ou valores** -> reforce nas
  Instructions: "NUNCA fabrique fatos; use [fornecer: ...] quando faltar dado".
- **A saída não parece um `prompt_template`** -> confirme que os 12 arquivos
  P0X foram carregados como Knowledge (o agente usa `P03_prompt.md` +
  `P05_output.md` + `P06_schema.md` para saber o formato esperado).
- **Quero trocar o idioma de saída** -> edite o campo `Language` em
  `system_instruction.md` (default: `pt-BR`).
