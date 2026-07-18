# SETUP -- ChatGPT (bundle Landing Page)

Setup do bundle `landing` (CEXAI, kind `landing_page`) no ChatGPT. Duas
rotas possíveis a partir dos MESMOS 15 arquivos deste bundle: **Projects**
(mais simples, funciona no plano free) ou **Custom GPT** (publicável,
usa o `customgpt_instructions.json` diretamente). ~5 minutos em qualquer
uma das duas.

## Pré-requisitos

- Conta ChatGPT (free já é suficiente para a rota Projects).
- ZERO chaves de API necessárias -- este bundle não usa Actions nem
  ferramentas externas. É um agente 100% generativo: você descreve o
  produto/oferta, ele devolve o código da página.

## Opção A -- ChatGPT Projects (recomendado)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Landing Page Builder (CEXAI)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie todo o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Instructions do projeto.

### 3. Suba os 12 arquivos de Knowledge

Em **Files** do projeto, suba os **12 arquivos de pillar**:

- `P01_knowledge.md` ... `P12_orchestration.md`

Esses 12 arquivos SÃO o contrato completo do builder (identidade, regras,
schema de saída, quality gates, memória, colaboração) -- não há uma versão
"enxuta" separada para este bundle, ele já é enxuto por natureza.

### 4. Capabilities

Este agente não precisa de nenhuma capability especial:
- **Web Browsing**: opcional. Ligue se você quiser que o agente espie
  páginas de concorrentes antes de desenhar a sua (ver `P04_tools.md` ->
  Reference Tools). Não é necessário para gerar a página.
- **Code Interpreter**: não necessário (o agente produz código como texto,
  não executa nada).
- **DALL-E**: não necessário (o agente usa URLs de imagem placeholder --
  picsum.photos, ui-avatars.com -- que você substitui depois).

### 5. Teste

Inicie uma conversa dentro do project:

> `Crie uma landing page para <produto/oferta>`

O agente deve:
1. Perguntar (ou assumir com placeholders `[fornecer: ...]`) o nome da
   marca, o público e o tom de voz, se ainda não souber.
2. Gerar a página completa: as 12 seções (HERO, PROBLEM, SOLUTION,
   FEATURES, SOCIAL-PROOF, HOW-IT-WORKS, PRICING, TESTIMONIALS, FAQ, CTA,
   FOOTER, META), responsiva, com dark mode, em um único bloco de código.
3. Entregar as instruções de deploy (salvar como `index.html`, substituir
   placeholders, publicar em Vercel/Netlify/GitHub Pages).

## Opção B -- Custom GPT (ChatGPT Plus, publicável na loja de GPTs)

Se você quer um GPT publicável (com nome, ícone e descrição próprios) em
vez de um Project privado, use `customgpt_instructions.json`:

### 1. Crie o GPT

1. Acesse **chatgpt.com** -> **Explore GPTs** -> **Create**.
2. Vá para a aba **Configure**.

### 2. Preencha os campos com o JSON

Abra `customgpt_instructions.json` e copie cada campo para o campo
correspondente do Configure:

| Campo do Configure | Campo do JSON |
|---------------------|---------------|
| Name | `name` |
| Description | `description` |
| Instructions | `instructions` |
| Conversation starters | `conversation_starters` (1 item) |

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge**, suba os mesmos 12 arquivos `P01_knowledge.md` ...
`P12_orchestration.md`.

### 4. Capabilities

O bloco `capabilities` do JSON já declara o padrão recomendado --
`web_browsing: false`, `code_interpreter: false`, `dalle: false`. Marque
as caixas de acordo (todas desligadas por padrão; Web Browsing é opcional,
ver Opção A acima).

### 5. Teste

Use o mesmo conversation starter: `Crie uma landing page para <produto/oferta>`.

## O que este bundle NÃO faz (honestidade de escopo)

- NÃO faz deploy da página por você -- entrega o código, você publica.
- NÃO navega a web ao vivo por padrão -- Web Browsing é opcional e só
  serve para inspiração visual de concorrentes.
- NÃO gera imagens reais -- usa URLs de placeholder que você substitui.
- Antes de publicar, todo campo `[fornecer: ...]` precisa da SUA marca real;
  o agente nunca inventa nome de marca, preço ou dado que você não deu.

## Solução de problemas

- **"Ele inventou o nome da marca / preço"** -> reforce: "todo campo sem
  input real deve ficar como `[fornecer: ...]`, nunca inventado".
- **A página saiu só em inglês** -> as Instructions já fixam
  `Idioma: pt-BR`; se persistir, peça explicitamente "responda e escreva a
  copy em PT-BR".
- **Quero React/Next.js/Astro em vez de HTML puro** -> peça explicitamente
  no prompt; o stack padrão é HTML + Tailwind CDN (zero build).
- **Faltou alguma das 12 seções** -> peça "inclua as 12 seções completas"
  (o agente pode omitir seções menos relevantes se você não pedir todas).
