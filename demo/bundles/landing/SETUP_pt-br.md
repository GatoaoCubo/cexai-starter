# SETUP -- landing (bundle CEXAI) -- guia combinado PT-BR

Guia geral do bundle `landing`: um agente Landing Page Builder portável,
baseado no contrato de 12 pillars da CEXAI (kind `landing_page`, pillar
P05, nucleus N03). Para o setup detalhado por plataforma, veja os
arquivos específicos:

- **ChatGPT (Projects ou Custom GPT)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

## O que este bundle é

Um agente que recebe uma descrição de produto/oferta em texto livre e
devolve uma **landing page completa e pronta para publicar** -- código
funcional (HTML+Tailwind por padrão, ou React/Next.js/Astro se você
pedir), responsiva (mobile-first), com dark mode, SEO on-page e
acessibilidade WCAG AA. Não é um wireframe nem uma maquete: é a página
pronta, com assets placeholder que você substitui antes do deploy.

## Arquivos do bundle (overview)

```
landing/
  P01_knowledge.md ... P12_orchestration.md  <- SUBA os 12 como Knowledge
  customgpt_instructions.json                <- config pronta para Custom GPT (ChatGPT)
  system_instruction.md                      <- COLE como Instructions/system prompt (Claude, Gemini, qualquer IA)
  README.md                                  <- overview + passo a passo rápido
  SETUP_*.md                                 <- guias de setup (este + 3 específicos)
```

Diferente de bundles maiores da família CEXAI (que separam uma variante
"enxuta" para plano free de uma variante "full" com Actions pagas), o
bundle `landing` já é enxuto por natureza: um único agente 100%
generativo, sem chamadas a APIs externas, sem chaves, sem Actions. Os
mesmos 15 arquivos do núcleo funcionam identicamente em qualquer uma das
3 plataformas.

## Opção A -- ChatGPT (Projects ou Custom GPT)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo:
1. **Projects** (recomendado, plano free): crie um Project, cole
   `system_instruction.md` nas Instructions, suba os 12 arquivos de pillar
   como Files.
2. **Custom GPT** (ChatGPT Plus, publicável): use
   `customgpt_instructions.json` diretamente -- os campos `name`,
   `description`, `instructions` e `conversation_starters` mapeiam 1:1
   para os campos do Configure.
3. Nenhuma Action é necessária; Web Browsing é opcional (só para
   inspiração visual em concorrentes).

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Claude Project.
2. Cole `system_instruction.md` nas Project Instructions.
3. Suba os 12 arquivos de pillar como Project Knowledge.
4. Bônus: peça para o Claude abrir a página gerada como **Artifact** --
   você vê a landing page renderizada, sem sair do chat.

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem em gemini.google.com.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos de pillar como Knowledge.
4. Aproveite a janela de contexto grande do Gemini para iterar várias
   vezes na mesma página, na mesma conversa.

## Comparativo rápido entre plataformas

| Aspecto | ChatGPT Projects | Custom GPT | Claude Projects | Gemini Gems |
|---------|------------------|------------|-------------------|-------------|
| Plano mínimo | Free | Plus | Free | Free (conta Google) |
| Publicável na loja | Não | Sim | Não | Sim (Gems públicos) |
| Pré-visualização renderizada | Não | Não | Sim (Artifact) | Não |
| Limite de arquivos de Knowledge | Por tamanho | 20 arquivos | Por tamanho | Por tamanho |
| Chaves de API necessárias | Nenhuma | Nenhuma | Nenhuma | Nenhuma |

## Como o agente funciona (visão geral)

O agente segue o pipeline documentado nos 12 arquivos de pillar deste
bundle (detalhe completo em `P03_prompt.md` e `P08_architecture.md`):

1. **BRIEF**: coleta produto, público, objetivo, tom de voz e stack
   preferido (do seu input ou de um `brand_config`, se houver).
2. **STRUCTURE**: escolhe a ordem das 12 seções conforme o objetivo
   (SaaS, serviço/agência, curso/infoproduto ou portfólio -- ver
   `P03_prompt.md`).
3. **DESIGN TOKENS + BUILD + ASSEMBLE**: gera cada seção, monta a página
   em um único arquivo (ou componente, se você pediu React/Next.js/Astro).
4. **OPTIMIZE**: adiciona SEO (meta tags, Open Graph, JSON-LD),
   acessibilidade e performance (lazy loading, CSS crítico).
5. **VALIDATE**: confere as 12 seções, responsividade, CTAs, alt text e
   contraste de cor antes de entregar (gates completos em `P07_evals.md`).

## Como usar (fluxo típico)

1. Diga o que você quer: `Crie uma landing page para <produto/oferta>`.
2. O agente confirma marca, público, tom de voz e stack (ou assume com
   `[fornecer: ...]` se você não tiver dado ainda).
3. Ele entrega a página completa em um bloco de código, pronta para
   copiar e colar.
4. Você substitui os placeholders (`[fornecer: ...]`, imagens, links de
   deploy) pelos dados reais da sua marca.
5. Você salva como `index.html` (ou o arquivo do stack escolhido) e faz o
   deploy: Vercel, Netlify, GitHub Pages, ou qualquer hospedagem estática.

## Solução de problemas

- **"Ele inventou o nome da marca / preço"** -> P11 (Feedback) proíbe
  isso explicitamente. Reforce: "todo campo sem input real deve ficar como
  `[fornecer: ...]`, nunca inventado".
- **A página saiu só em inglês** -> as instructions já fixam
  `Idioma: pt-BR`; peça explicitamente para a copy sair em PT-BR.
- **Faltaram seções** -> peça "inclua as 12 seções completas"; o agente
  pode omitir seções menos relevantes ao objetivo se você não pedir todas
  (ver `P07_evals.md` -> gate S01 e H03).
- **Quero outro stack (React/Next.js/Astro)** -> peça explicitamente no
  prompt; o padrão é HTML + Tailwind CDN (zero build, deploy instantâneo).
- **Quero pré-visualizar antes de exportar** -> use Claude Projects (ver
  `SETUP_claude_projects.md`) para renderizar a página em um Artifact, ou
  copie o HTML para um arquivo local e abra no navegador.

## Compatibilidade

Este bundle é o mesmo, byte a byte funcional, nas 3 plataformas: os 12
arquivos de pillar e o `system_instruction.md` não mudam. O que muda é
apenas ONDE você cola a instrução e sobe os arquivos -- ver os 3 guias
específicos acima para os detalhes de cada interface.
