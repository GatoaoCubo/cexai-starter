# SETUP -- Gemini Gems (bundle Landing Page)

Setup do bundle `landing` (CEXAI, kind `landing_page`) em Gemini Gems.
~5 minutos. Nenhuma chave de API, nenhuma extension é obrigatória -- este
é um agente 100% generativo (texto entra, código de página sai).

## Pré-requisitos

- Conta Google + acesso a **gemini.google.com**.
- ZERO chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Landing Page Builder (CEXAI)`.
4. Description: `Gera landing pages completas (HTML/React/Next.js/Astro) a partir de uma descrição de produto ou oferta.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos de pillar:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. (Opcional) Extensions

Este bundle não exige nenhuma extension para funcionar. Se quiser, você
pode habilitar:
- **Google Search** -- útil apenas se você pedir para o agente olhar
  páginas de concorrentes antes de desenhar a sua (ver `P04_tools.md` ->
  Reference Tools). Não é necessário para gerar a página.

### 5. Teste

Em uma conversa do Gem:

> `Crie uma landing page para <produto/oferta>`

O Gem deve:
1. Confirmar (ou assumir com placeholders `[fornecer: ...]`) marca,
   público e tom de voz, se ainda não souber.
2. Gerar a página completa: as 12 seções, responsiva, dark mode, em um
   único bloco de código HTML (ou React/Next.js/Astro, se você pedir).
3. Entregar as instruções de deploy.

## Vantagens do Gemini para este bundle

- **Janela de contexto grande** (bem acima de 1M tokens nos modelos mais
  recentes) -- útil quando você pede várias rodadas de ajuste na mesma
  página, na mesma conversa.
- **Multi-modal nativo**: se você quer que o Gem analise uma imagem de
  referência (um print de uma landing page concorrente, um moodboard),
  anexe a imagem no chat e peça para ele se inspirar no estilo visual.

## Limitações

- Gemini Gems tem suporte mais restrito a Actions/tools do que Custom GPT
  (ChatGPT) -- mas este bundle não precisa de nenhuma, então isso não afeta
  o uso principal.
- Sem pré-visualização renderizada nativa da página (diferente do Artifact
  do Claude) -- copie o HTML gerado e abra localmente para visualizar.

## O que este bundle NÃO faz (honestidade de escopo)

- NÃO faz deploy da página por você -- entrega o código, você publica.
- NÃO navega a web ao vivo por padrão.
- NÃO gera imagens reais -- usa URLs de placeholder que você substitui.
- Todo campo `[fornecer: ...]` precisa da SUA marca real antes de publicar;
  o agente nunca inventa nome de marca, preço ou dado que você não deu.

## Solução de problemas

- **"Ele inventou o nome da marca / preço"** -> reforce: "todo campo sem
  input real deve ficar como `[fornecer: ...]`, nunca inventado".
- **A página saiu só em inglês** -> as Instructions já fixam
  `Idioma: pt-BR`; reforce pedindo explicitamente copy em PT-BR.
- **Quero React/Next.js/Astro em vez de HTML puro** -> peça explicitamente;
  o stack padrão é HTML + Tailwind CDN (zero build, deploy instantâneo).
- **Quero pré-visualizar a página renderizada** -> copie o bloco de código
  HTML gerado para um arquivo `index.html` local e abra no navegador, ou
  use `SETUP_claude_projects.md` (Claude tem Artifact nativo para isso).
