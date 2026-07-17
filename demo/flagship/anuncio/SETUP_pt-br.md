# SETUP -- Anuncio no Custom GPT (ChatGPT Plus/Team/Enterprise)

Guia humano para montar o agente "anuncio" como **Custom GPT**. Leva ~5 minutos. Este arquivo NAO sobe no GPT.

## O que voce vai precisar
- Os arquivos desta pasta:
  - `00_instructions.md` (vai no campo de instrucoes)
  - `knowledge/P01_knowledge.md` ... `knowledge/P12_orchestration.md` (12 arquivos de conhecimento -- 13 itens total com 00_instructions)
- ChatGPT **Plus/Team/Enterprise**.

## Passo a passo

1. **Crie o GPT**
   - Acesse `chatgpt.com` -> menu lateral -> **Explorar GPTs** -> **+ Criar** (ou `chatgpt.com/gpts/editor`).
   - Va para a aba **Configure** (Configurar).

2. **Nome e descricao**
   - Nome: `Anuncio (Codexa v2) -- Gerador de Anuncios de Marketplace`
   - Descricao: `Gera titulos, descricao mobile-first, keywords e bullets otimizados para Mercado Livre, Shopee, Amazon BR e Magalu. Powered by CEXAI architecture.`

3. **Cole as instrucoes**
   - Abra `00_instructions.md`, copie TODO o conteudo (~6.6k chars).
   - Cole no campo **Instructions** (Instrucoes). Cabe no limite de 8000 caracteres.

4. **Suba o conhecimento**
   - Na secao **Knowledge** (Conhecimento), clique em **Upload files**.
   - Suba os **12 arquivos** de `knowledge/`:
     `P01_knowledge.md, P02_model.md, P03_prompt.md, P04_tools.md, P05_output.md, P06_schema.md, P07_evaluation.md, P08_architecture.md, P09_config.md, P10_memory.md, P11_feedback.md, P12_orchestration.md`
   - **NAO suba** `00_instructions.md` (vai no campo Instructions), nem `manifest.yaml`, nem nada de `cexai/`, `projects_free/`, `claude/`, `gemini/`, `SETUP_*.md`, `README.md`, `CONVENTION*.md`.

5. **Ative as capabilities**
   - Marque **Code Interpreter & Data Analysis** (ESSENCIAL -- para contar caracteres e keywords).
   - Marque **Web Browsing** (opcional -- para benchmark de concorrentes, best-effort).
   - **DALL-E**: deixe DESLIGADO (este agente gera texto, nao imagem).

6. **Conversation starters (sugestoes)**
   - `Gerar anuncio de Mercado Livre para [produto], categoria [x], preco R$ [y]`
   - `Criar titulo Shopee 100-120 chars para [produto] com emoji no inicio`
   - `Anuncio Amazon BR (marca primeiro) para [produto]`
   - `2 blocos de keywords (115-120) para [produto]`

7. **Salve** (Create/Update) -> escolha visibilidade (apenas eu / link / publico).

8. **Teste**: peca um anuncio de ML e confira se o titulo sai com 58-60 chars, descricao sem rotulos de framework, bullets 250-299 chars, e o bloco "Suposicoes e dados a confirmar" presente.

## O que esta camada CEXAI adiciona

Voce NAO precisa subir a pasta `cexai/` no Custom GPT -- ela e a SOURCE OF TRUTH dos contratos tipados que ALIMENTARAM o conteudo dos 12 P uploaded. Os pillars `Pxx_*.md` que voce upload-ou ja contem as referencias `[[cexai/<name>]]` para audit-trail; o Custom GPT le-os como narrativa rica.

A subpasta `cexai/` so e diretamente usada em Claude Projects (com .mcp.json) e Gemini Gems quando voce quer dispatchar o crew composable via `cex_crew.py`.

## Verificacao rapida (smoke test)
Peca: *"Gere um anuncio de Mercado Livre para garrafa termica inox 1L, categoria Casa > Cozinha > Garrafas, preco R$ 89,90, diferenciais: 12h gelado, a prova de vazamento."*

Confira na resposta:
- [ ] 3 titulos, cada um com 58-60 chars, sem conectores (de/para/com/e).
- [ ] Descricao mobile-first sem rotulos e sem R$.
- [ ] 10 bullets etiquetados por origem (FEATURE/PAIN_POINT/GAP/SPEC), cada 250-299 chars.
- [ ] 2 blocos de keywords com contagem (115-120 termos cada).
- [ ] Tabela de qualidade 5D + status APROVADO/REVISAR.
- [ ] Bloco "## Suposicoes e dados a confirmar" presente.

## Powered by
CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei) -- github.com/GatoaoCubo/cex
