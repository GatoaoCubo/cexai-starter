# SETUP -- Claude Projects (bundle Landing Page)

Setup do bundle `landing` (CEXAI, kind `landing_page`) em Claude Projects.
~5 minutos. Nenhuma chave de API, nenhuma Action, nenhum MCP é necessário --
este é um agente 100% generativo (texto entra, código de página sai).

## Pré-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO chaves de API necessárias.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Landing Page Builder (CEXAI)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral, ícone de
   engrenagem ou "Set custom instructions").
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge

Em **Project Knowledge**, suba os 12 arquivos de pillar:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos como o Custom GPT da OpenAI
(o limite é por tamanho total do projeto, não por contagem de arquivos) --
os 12 arquivos deste bundle cabem com folga.

### 4. Teste

Em uma conversa dentro do Project:

> `Crie uma landing page para <produto/oferta>`

O agente deve:
1. Confirmar (ou assumir com placeholders `[fornecer: ...]`) marca, público
   e tom de voz, se ainda não souber.
2. Gerar a página completa: as 12 seções, responsiva, dark mode, em um
   único bloco de código HTML (ou React/Next.js/Astro, se você pedir).
3. Entregar as instruções de deploy.

### 5. (Bônus específico do Claude) Pré-visualize a página em um Artifact

Claude.ai renderiza blocos de código HTML como **Artifact** -- um painel
lateral que mostra a página JÁ RODANDO, sem você precisar salvar o arquivo
e abrir no navegador. Para aproveitar isso, peça explicitamente:

> `Crie a landing page e mostre o resultado renderizado`

Se o Claude não abrir o Artifact automaticamente, peça: "abra isso como um
Artifact para eu ver a página renderizada". Isso é útil para iterar no
design (cores, copy, seções) antes de exportar o HTML final para deploy.

## Vantagens do Claude Projects para este bundle

| Aspecto | Custom GPT (ChatGPT) | Claude Projects |
|---------|-----------------------|------------------|
| Pré-visualização da página | Nenhuma nativa (você copia o HTML e abre localmente) | Artifact renderiza a página inline, sem sair do chat |
| Limite de arquivos de knowledge | 20 arquivos | Sem limite por contagem (limite por tamanho total) |
| Janela de contexto | Menor | Maior -- útil quando você pede várias iterações da mesma página na mesma conversa |
| Custo | Precisa de Plus para Custom GPT | Funciona no plano Free |

## O que este bundle NÃO faz (honestidade de escopo)

- NÃO faz deploy da página por você -- entrega o código, você publica.
- NÃO navega a web ao vivo por padrão (ver `P04_tools.md` -> Reference
  Tools para os casos em que isso seria útil, ex.: inspiração visual de
  concorrentes).
- NÃO gera imagens reais -- usa URLs de placeholder que você substitui.
- Todo campo `[fornecer: ...]` precisa da SUA marca real antes de publicar;
  o agente nunca inventa nome de marca, preço ou dado que você não deu.

## Solução de problemas

- **"Ele inventou o nome da marca / preço"** -> reforce: "todo campo sem
  input real deve ficar como `[fornecer: ...]`, nunca inventado".
- **Não abriu o Artifact sozinho** -> peça explicitamente "abra como
  Artifact" ou "renderize a página".
- **A página saiu só em inglês** -> as Project Instructions já fixam
  `Idioma: pt-BR`; reforce pedindo explicitamente copy em PT-BR.
- **Quero React/Next.js/Astro em vez de HTML puro** -> peça explicitamente;
  o stack padrão é HTML + Tailwind CDN (zero build, deploy instantâneo).
