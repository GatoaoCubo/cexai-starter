# SETUP -- codexa-imagens em Claude Projects (strongest runtime para upgrade lanes)

Guia para colocar o codexa-imagens no ar como **Claude Project** com MCP
servers opcionais (lanes L1-L5). Este arquivo e para humanos -- NAO suba.

> Powered by CEXAI 12P (300+ kinds, 12 pillars, 8 nuclei).

---

## Por que Claude Projects

Claude Projects e o runtime **mais completo deste bundle** porque suporta MCP
nativamente. Voce pode ativar **TODAS as 5 lanes opcionais**:
- L1 Gemini Vision (vision-analyze)
- L2 Gemini Flash Image grid 3x3
- L3 ComfyUI local (CEXAI factory parity)
- L4 Qwen3-VL Ollama (free local vision)
- L5 Firecrawl (scrape product URL for style calibration)

Limitacao: Claude nao tem image-gen primary nativo. Use:
- L3 ComfyUI via MCP (se setup local), OU
- L2 Gemini Image via MCP (precisa GEMINI_API_KEY), OU
- Entregue os prompts para o usuario rodar DALL-E externamente (default).

---

## Passo a passo

1. **claude.ai** -> Projects -> New project: `codexa-imagens -- Foto de Produto`.
2. **Project instructions**: cole `claude/Project_instructions.md`.
3. **Knowledge**: suba os **12 arquivos** de `claude/knowledge/` (ou da
   pasta `knowledge/` original -- conteudo identico).
4. **MCP setup** (opcional, ativa lanes L1-L5):
   - Copie `claude/.mcp.json` para a configuracao do seu Claude (Claude
     Desktop / Claude Code).
   - Defina as env vars das lanes que quer ativar:
     - L1/L2: `GEMINI_API_KEY=<sua_key>`
     - L3: `COMFYUI_HOST=http://localhost:8188` (precisa ComfyUI local)
     - L4: `OLLAMA_HOST=http://localhost:11434` + `ollama pull qwen2.5vl`
     - L5: `FIRECRAWL_API_KEY=<sua_key>`
   - Lanes sem env = silenciosamente desativadas (degrade-never).
5. Teste com 1 produto real. O agente deve listar as lanes ativas no inicio
   da primeira resposta.

---

## Sobre o .mcp.json

O arquivo `claude/.mcp.json` declara 5 MCP server bindings, cada um marcado
`_optional: true` + `_fallback_to: <fallback_path>`. Voce instala SOMENTE os
que quer; os demais ficam dormentes.

Cada lane corresponde a um typed CEXAI kind:
- L1, L4 -> `vision_tool` kind
- L2, L3 -> `multi_modal_config` kind
- L5 -> `browser_tool` kind
- L6 (code exec) -> `code_executor` kind (sandboxed nativo do Claude)

---

## Quando preferir Claude Projects

- Voce quer maxima capacidade (todas as lanes via MCP).
- Voce ja roda ComfyUI local e quer o L3 lane.
- Voce tem GEMINI_API_KEY e quer L1+L2 sem ir para Gemini Gems.
- Voce valoriza vision nativo do Claude (descricao de upload boa por default).

## Quando NAO usar Claude Projects para este bundle

- Voce so quer image-gen nativo simples (Custom GPT ou Gemini Gems sao melhores).
- Voce nao quer configurar nada -- Gemini Gems tem L1+L2 nativos sem env.

---

## Checklist
- [ ] Project instructions colado
- [ ] 12 arquivos knowledge subidos
- [ ] .mcp.json configurado (opcional)
- [ ] Env vars das lanes desejadas setadas
- [ ] Testado com 1 produto real
- [ ] Lanes ativas listadas no inicio da resposta (transparencia)
- [ ] Bloco C2PA disclosure no output funcionando
