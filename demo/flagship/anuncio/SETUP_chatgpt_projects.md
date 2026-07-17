# SETUP -- Anuncio no ChatGPT Projects (perfil ENXUTO, plano free)

Guia para montar o agente "anuncio" no **ChatGPT Projects**, plano free (max 5 arquivos por projeto + campo de instrucoes separado). Leva ~3 minutos.

> O perfil **FULL** (12 arquivos P01..P12) vive na pasta raiz do bundle (`knowledge/` + `00_instructions.md`) e e para **Custom GPT (ChatGPT Plus)**. Use **este perfil ENXUTO** no plano free.

## O que voce vai precisar
- Os 6 arquivos desta pasta `projects_free/`:
  - `00_instructions.md` (vai no campo de instrucoes do projeto)
  - `P01_knowledge.md`
  - `P02_model.md`
  - `P03_prompt.md`
  - `P04_tools.md`
  - `P05_output.md`
- Qualquer conta ChatGPT (free, Plus, Team).

## Passo a passo

1. **Crie um Projeto** no ChatGPT (menu lateral -> "Projetos" / "Projects" -> "Novo projeto"). De o nome **"Anuncio (Codexa v2)"**.

2. **Cole as instrucoes.** Abra `projects_free/00_instructions.md`, copie TODO o conteudo e cole no campo **Instrucoes do projeto** (em "Instrucoes" / "Instructions" do projeto). Cabem no limite do campo (~7k chars).

3. **Suba os 5 arquivos de conhecimento.** Em "Arquivos" / "Files" do projeto, faca upload destes 5 (e somente estes):
   - `P01_knowledge.md`
   - `P02_model.md`
   - `P03_prompt.md`
   - `P04_tools.md`
   - `P05_output.md`

4. **Pronto.** Inicie uma conversa dentro do projeto. Forneca: **nome do produto, marketplace (ML/Shopee/Amazon/Magalu), categoria e preco (R$)** -- esses sao obrigatorios. Quanto mais diferenciais, publico-alvo e specs reais voce der, melhor o anuncio.

## Dicas de uso
- **Conte sempre os caracteres.** No free, o code interpreter pode nao estar disponivel; peca ao agente para conferir os limites manualmente (ML: titulo 58-60, bullets 250-299).
- **Nao invente specs.** Se o agente pedir um dado (peso, material, certificacao), e proposital: o agente nunca fabrica especificacao tecnica. Forneca ou aceite o `[PREENCHER]`.
- **Bloco final.** Toda entrega termina com "## Suposicoes e dados a confirmar" -- leia essa lista antes de publicar.
- **Web browsing** (se ativo no seu plano): peca para conferir 3-5 concorrentes reais antes de gerar.

## O que muda do FULL para o ENXUTO
Nada de essencial. Os 5 arquivos foram adaptados para serem autossuficientes:
- limites/config (eram P09) -> embutidos em **P05** (e regras de geracao em P03).
- rubrica de qualidade + self-check (eram P07) -> embutidos em **P05** e nas instrucoes.
- inputs obrigatorios (eram P06) -> embutidos em **P03**.
- compliance/anti-alucinacao/autocorrecao (eram P11) -> embutidos em **P03**, **P05** e nas instrucoes.
- loop operacional (era P12) -> embutido nas instrucoes.

Voce tem o mesmo agente, com menos arquivos.

## Verificacao rapida (smoke test)
Peca: *"Gere um anuncio de Mercado Livre para garrafa termica inox 1L, categoria Casa > Cozinha > Garrafas, preco R$ 89,90, diferenciais: 12h gelado, a prova de vazamento."*

Mesma checklist do Custom GPT FULL (titulos 58-60, descricao sem rotulos, bullets 250-299, bloco "Suposicoes" presente).

## Powered by
CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei) -- github.com/GatoaoCubo/cex
