# SETUP -- codexa-imagens em ChatGPT Projects (perfil ENXUTO)

Guia para colocar o codexa-imagens no ar como **ChatGPT Project** (plano free
ou pago). Versao ENXUTO = 5 arquivos. Este arquivo e para humanos -- NAO suba
no Project.

> Powered by CEXAI 12P (300+ kinds, 12 pillars, 8 nuclei).

---

## Por que Projects ENXUTO

- Funciona no **plano FREE** (Custom GPT exige pago).
- Project memory persiste contexto entre conversas.
- Teto de 5 arquivos por Project -- o ENXUTO ja dobra P06-P12 nos 5.

---

## Passo a passo (ENXUTO)

Ver `projects_free/LEIA_setup.md` para o guia detalhado. Resumo:

1. **chatgpt.com** -> Projects -> New project: `codexa-imagens -- Foto de Produto`.
2. **Instructions**: cole `projects_free/00_instructions.md` (~6300 chars).
3. **Files** (5 arquivos da pasta `projects_free/`):
   - `P01_knowledge.md` (com marketplace specs dobrado)
   - `P02_model.md`
   - `P03_prompt.md` (com 13 templates dobrado)
   - `P04_tools.md`
   - `P05_output.md` (com TOS compliance dobrado)
4. Confirme que **Image generation / DALL-E** esta disponivel no seu plano.
5. Teste com 1 produto real.

---

## Lanes opcionais L1-L5 (NAO se aplicam ao ChatGPT Projects)

Mesma limitacao do Custom GPT: sem MCP, sem env vars, sem lanes externas. Use
o **primary lane (DALL-E nativo)** + texto + paste-intake. Para as lanes
completas, use Claude Projects (`claude/`) ou Gemini Gems (`gemini/`).

---

## Quando preferir o Custom GPT FULL

- Voce ja paga ChatGPT Plus -> Custom GPT FULL aceita 12 arquivos sem dobrar
  conteudo. Mais limpo e auditavel.
- Voce quer compartilhar o GPT publicamente / com um time.

## Quando preferir o ENXUTO

- Plano free.
- So precisa do agente para uso pessoal.

---

## Checklist
- [ ] Instructions colado (de `projects_free/00_instructions.md`)
- [ ] 5 arquivos P01-P05 ENXUTO subidos
- [ ] DALL-E / image gen disponivel no seu plano (ou ciente que usa prompts por fora)
- [ ] Testado com 1 produto real
- [ ] Bloco C2PA disclosure no output funcionando
