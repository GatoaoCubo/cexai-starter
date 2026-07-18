# SETUP -- Gemini Gems

Setup do bundle CEXAI `ads` (Ads and Copy) em Gemini Gems. Este bundle não
precisa de extensions nem de tools externas -- é um agente de geração de
texto puro. ~5 minutos.

## Pré-requisitos

- Conta Google + acesso a gemini.google.com.
- ZERO chaves de API ou extensions necessárias.
- Os 15 arquivos do núcleo deste bundle baixados em uma pasta local.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Ads and Copy`.
4. Description: copie o campo `description` de `customgpt_instructions.json`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo **Instructions** do Gem.
4. Substitua os marcadores `[fornecer: ...]` (nome da marca, tom de voz,
   valores) pelos dados reais da sua marca.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos de pilar:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Extensions

Nenhuma extension é necessária. Deixe **Google Search** e as demais
extensions desligadas -- este agente só precisa gerar texto a partir do
conhecimento carregado, não buscar nada ao vivo.

### 5. Teste

Em uma conversa do Gem:

> Escreva a copy de anúncio para tênis de corrida visando corredores
> iniciantes de 25-40 anos

O Gem deve responder com um artefato `prompt_template` (hooks, CTAs e
variantes por tamanho de plataforma) na voz de marca configurada.

## Vantagens do Gemini Gems para este bundle

- **Context window grande** (>1M tokens em modelos recentes) -- folga
  enorme para os 12 arquivos de pilar, mesmo com conversas longas.
- **Setup rápido**: sem extensions, sem chaves, sem MCP.

## Solução de problemas

- **O Gem inventa nome de marca, tom ou valores** -> reforce nas
  Instructions: "NUNCA fabrique fatos; use [fornecer: ...] quando faltar dado".
- **A saída não parece um `prompt_template`** -> confirme que os 12 arquivos
  P0X foram carregados como Knowledge (o Gem usa `P03_prompt.md` +
  `P05_output.md` + `P06_schema.md` para saber o formato esperado).
- **Quero mudar o idioma de saída** -> edite o campo `Language` em
  `system_instruction.md` (default: `pt-BR`).
