# SETUP -- codexa-imagens em Gemini Gems (L1 + L2 nativos)

Guia para colocar o codexa-imagens no ar como **Gemini Gem**. Este arquivo e
para humanos -- NAO suba no Gem.

> Powered by CEXAI 12P (300+ kinds, 12 pillars, 8 nuclei).

---

## Por que Gemini Gems

Gemini Gems tem **L1 (vision) + L2 (image grid) + Imagen 3 primary lane** todos
**nativos**, sem precisar de env vars nem MCP. E o runtime mais simples para
fidelidade completa do bundle original.

- **Imagen 3 nativo** -- equivalente ao DALL-E primary lane.
- **Gemini Vision nativo** -- L1 lane, visao de upload por default.
- **Gemini 2.5 Flash Image grid** -- L2 lane, 3x3 9-em-1 nativo.
- **Code execution nativo** -- L6 lane, dimension check.
- **Google Search nativo** -- parte da L5 (calibracao de estilo).

Lanes que NAO se aplicam em Gemini Gems:
- L3 ComfyUI (precisa MCP, so Claude)
- L4 Qwen3-VL Ollama (precisa MCP, so Claude)
- L5 Firecrawl avanzado (precisa integration externa, so Claude)

Para L3/L4 use `claude/` em vez disso.

---

## Passo a passo

1. **gemini.google.com** -> Gems -> Create a new gem: `codexa-imagens -- Foto de Produto`.
2. **Instructions**: cole `gemini/Gem_instructions.md`.
3. **Knowledge**: suba os **12 arquivos** de `gemini/knowledge/` (ou da pasta
   `knowledge/` original -- conteudo identico).
4. **Native capabilities** (sao ativadas automaticamente):
   - Imagen 3 (image gen)
   - Vision (L1)
   - Image grid generation (L2 -- precisa "gera o grid completo de 9 cenas em uma chamada")
   - Code execution (L6)
   - Google Search (parcial L5)
5. Teste com 1 produto real.

---

## Sobre o `.mcp.json` (NAO se aplica aqui)

O arquivo `claude/.mcp.json` e exclusivo do runtime Claude Projects. Em Gemini
Gems voce NAO precisa dele -- as capabilities equivalentes (Vision, Imagen,
grid, code) sao todas nativas.

---

## Quando preferir Gemini Gems

- Voce quer L1+L2 nativos sem configurar env/MCP.
- Voce ja usa Google ecosystem (search nativo ajuda em L5).
- Voce quer custo zero de API (Imagen 3 + Gemini Vision incluidos no Gemini Advanced).

## Quando NAO usar Gemini Gems

- Voce precisa de L3 ComfyUI ou L4 Qwen3-VL local -> use Claude Projects.
- Voce ja paga ChatGPT Plus e quer DALL-E (qualidade diferente do Imagen 3).

---

## Diferenca de qualidade visual (Imagen 3 vs DALL-E vs MJ)

- **Imagen 3** (Gemini nativo): forte em fotorrealismo, fundo branco confiavel,
  precision em pequenos detalhes. Bom para main image marketplace.
- **DALL-E** (Custom GPT nativo): forte em narrative, lighting expressivo, menos
  preciso em compliance branco RGB exato.
- **MJ v6.1** (externo): pico de qualidade artistica/estilo; precisa rodar fora.

O bundle entrega prompts otimizados para os 3 motores. Voce escolhe o motor
de geracao conforme runtime + necessidade.

---

## Checklist
- [ ] Gem instructions colado
- [ ] 12 arquivos knowledge subidos
- [ ] Capabilities nativas ativas (verificar)
- [ ] Testado com 1 produto real
- [ ] L1 vision marcando inferencias "(confirme)"
- [ ] L2 grid 3x3 funciona em "gera o grid completo de 9 cenas"
- [ ] Bloco C2PA disclosure no output funcionando
