# SETUP -- codexa-imagens em Custom GPT (Custom GPT FULL)

Guia para colocar o codexa-imagens (engenharia de prompt para foto de produto)
no ar como **Custom GPT** (precisa ChatGPT Plus/Team/Enterprise). Este arquivo
e para humanos -- NAO suba no GPT.

> Powered by CEXAI 12P (300+ kinds, 12 pillars, 8 nuclei).

---

## Por que Custom GPT FULL (e nao Projects)

- Tem **DALL-E nativo** (gera imagem de verdade)
- Persiste como GPT reutilizavel e compartilhavel
- Aceita **20 arquivos de conhecimento** (versao FULL = 12 + folga)
- Tem **Web Browsing** + **Code Interpreter** + **Image Gen**

---

## Passo a passo (Custom GPT FULL)

1. Acesse **chatgpt.com** -> menu lateral -> **GPTs** -> **Create** (ou
   chatgpt.com/gpts/editor).
2. Va na aba **Configure**.
3. **Name**: `codexa-imagens -- Foto de Produto` (ou o nome que preferir).
4. **Description**: `Engenharia de prompt para fotografia de produto
   (Midjourney/DALL-E/SD) + direcao de arte e compliance de marketplace BR.
   Powered by CEXAI 12P.`
5. **Instructions**: abra `00_instructions.md`, copie TODO o conteudo e cole
   neste campo. (Tem ~7800 caracteres; o limite e 8000 -- cabe.)
6. **Knowledge**: clique em **Upload files** e suba os **12 arquivos** da
   pasta `knowledge/`:
   - `P01_knowledge.md` ate `P12_orchestration.md` (12 arquivos)
   (NAO suba `00_instructions.md`, `SETUP_*.md`, `manifest.yaml`, ou
   `cexai/` typed artifacts.)
7. **Capabilities** (marque):
   - [x] **DALL-E Image Generation** -- ESSENCIAL (e o primary lane).
   - [x] **Web Browsing** -- para calibrar com concorrentes / checar specs.
   - [x] **Code Interpreter & Data Analysis** -- L6 lane (checar dimensao/ratio).
8. (Opcional) **Conversation starters**, sugestoes:
   - "Crie prompts de foto para um serum de vidro 30ml, fundo branco, Mercado Livre"
   - "Direcao de arte para uma capinha de celular colorida no Instagram"
   - "Gera a imagem do produto que descrevi"
9. Clique em **Create / Update**. Pronto.

---

## Lanes opcionais L1-L5 (NAO se aplicam ao Custom GPT)

As lanes L1 (Gemini Vision), L2 (Gemini grid), L3 (ComfyUI), L4 (Qwen3-VL),
L5 (Firecrawl) requerem env vars + integracao MCP. **No Custom GPT**, voce nao
tem acesso a essas lanes -- o agente cai no **primary lane (DALL-E nativo)**
por default + extracao do texto + paste-intake para concorrentes.

Se quiser as lanes: suba o bundle para **Claude Projects** (ver `claude/`) ou
**Gemini Gems** (ver `gemini/`).

---

## Sobre a capacidade DALL-E (primary lane)

- O agente usa o **DALL-E nativo** da OpenAI para gerar imagens reais --
  porem **uma imagem por vez** (nao o grid de 9 cenas do backend original).
- Para 9 cenas, peca uma de cada vez; o agente mantem os atributos do produto
  fixos para consistencia.
- DALL-E **nao** le parametros de Midjourney (`--ar`, `--v`) nem de Stable
  Diffusion (Steps/CFG) -- esses servem para quando voce levar o prompt a
  essas ferramentas externas.
- Para **main image de marketplace** (fundo branco RGB 255,255,255 exato),
  pode ser necessario remover o fundo na pos-producao -- o agente avisa.
- Sempre que gerar via DALL-E, o agente emite um **bloco C2PA disclosure**
  para voce copiar na sua listing (compliance AI-content 2026+).

---

## Limitacao importante (seja realista)

Sem L1/L4 ativas (nao disponiveis no Custom GPT), o bundle **nao** tem analise
de visao precisa. **Descreva o produto** (cor, material, formato, tamanho) ou
cole o texto do anuncio -- e assim que o agente extrai os atributos. Para
visao precisa, use Claude Projects ou Gemini Gems.

---

## Checklist rapido
- [ ] Instructions colado (de `00_instructions.md`, 7800 chars)
- [ ] 12 arquivos `knowledge/P01..P12` subidos
- [ ] DALL-E ativado (Custom GPT capability)
- [ ] Web browsing ativado
- [ ] Code interpreter ativado (L6 dimension check)
- [ ] Testado com 1 produto real
- [ ] Bloco C2PA disclosure no output funcionando
