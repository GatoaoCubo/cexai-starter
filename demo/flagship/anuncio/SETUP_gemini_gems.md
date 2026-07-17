# SETUP -- Anuncio no Gemini Gems (Google AI Studio + Workspace)

Guia para montar o agente "anuncio" como **Gemini Gem** em gemini.google.com. Leva ~5 min.

## O que voce vai precisar
- Pasta `gemini/` deste bundle (Gem_instructions.md + retrieval/ tree).
- Conta Google com acesso a Gems (Gemini Advanced ou Workspace).

## Passo a passo

1. **Crie um Gem.**
   - Acesse `gemini.google.com` -> menu lateral -> **Gem manager** -> **+ New Gem**.
   - Nome: **"Anuncio (Codexa v2)"**.
   - Descricao curta: "Gera anuncios de marketplace BR otimizados (ML/Shopee/Amazon/Magalu)."

2. **Cole as instrucoes.**
   - Abra `gemini/Gem_instructions.md`, copie TODO o conteudo.
   - Cole no campo **Instructions** do Gem (Gemini aceita texto longo).

3. **Suba o conhecimento (retrieval).**
   - Em **Knowledge** do Gem, suba os 12 arquivos de `gemini/retrieval/`:
     `P01_knowledge.md, P02_model.md, ..., P12_orchestration.md`.
   - Gemini usa retrieval-grounded responses -- os files viram contexto pesquisavel pelo modelo.

4. **Verifique configuracao.**
   - Saida: PT-BR.
   - Style: respeita as instrucoes do Gem (anuncio profissional + caloroso + persuasivo sobre fato).

5. **Pronto.** Inicie uma conversa no Gem. Forneca os 4 obrigatorios (product_name, marketplace, category, price_brl).

## Diferencas vs Custom GPT

| Capability | Custom GPT | Gemini Gems |
|------------|-------------|--------------|
| Knowledge upload | aceita .md direto | aceita .md (retrieval-grounded) |
| Char limit das instrucoes | 8000 chars | substancialmente maior |
| Code interpreter (contar chars) | nativo (toggle) | menos confiavel -- peca explicitamente |
| Web browsing | nativo (toggle) | nativo (toggle) |
| MCP support | nao | parcial via Google AI Studio (experimental) |
| Cross-provider judge | self-judge | self-judge (sem council nativo) |

## Crew composable (via cex_crew.py)

Para usar os 3 papeis (writer/critic/compliance) como dispatches separados em volume:

```bash
# Pre-req: ter o repo cex clonado + Python 3.11+
git clone https://github.com/GatoaoCubo/cex.git
cd cex

# Mostra o plano
python _tools/cex_crew.py show anuncio_v5

# Executa para 1 anuncio
python _tools/cex_crew.py run anuncio_v5 \
    --charter _bundles/codexa-v2/anuncio/cexai/team_charter_anuncio_default.md \
    --execute
```

Cada role pode ser despachado para Gemini explicitamente via `nucleus_models.yaml` (especificar `gemini-2.5-flash` ou `pro` como provider).

## Dicas de uso
- Gemini respeita PT-BR com acentos nativo.
- Para contagem precisa de caracteres (essencial em bullets 250-299 ML), peca: "use code/calculator para contar os chars de cada bullet".
- Retrieval-grounded: o Gemini pesquisa nos 12 P files conforme a pergunta -- mais natural que upload de bloco unico, menos previsivel que Custom GPT.

## Verificacao rapida (smoke test)
Peca: *"Gere um anuncio de Mercado Livre para garrafa termica inox 1L, categoria Casa > Cozinha > Garrafas, preco R$ 89,90, diferenciais: 12h gelado, a prova de vazamento."*

Mesma checklist (titulos 58-60, bullets 250-299, bloco "Suposicoes").

## Powered by
CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei) -- github.com/GatoaoCubo/cex
