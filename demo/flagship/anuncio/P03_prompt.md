---
agent: anuncio
pillar: P03
pillar_name: prompt
lang: pt-BR
source: api/core/anuncio_synthesizer.py (prompts reais: titles/keywords/bullets/description/faqs, SYSTEM_INSTRUCTION); api/v1/anuncios.py (ISSUE_TO_FIX); records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md (teaching StoryBrand)
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: prompt_template
cexai_typed_artifacts:
  - cexai/prompt_template_intake.md
  - cexai/prompt_template_titles.md
  - cexai/prompt_template_keywords.md
  - cexai/prompt_template_bullets.md
  - cexai/prompt_template_description.md
  - cexai/prompt_template_faqs.md
  - cexai/few_shot_example_gatilhos_x10.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P03 -- Receitas de Prompt (templates de geração por estágio)

As receitas textuais que o agente usa para gerar cada bloco. São o "como gerar".

> **Camada CEXAI:** cada estágio de geração vive como `prompt_template` tipado em `cexai/` -- [[cexai/prompt_template_intake]] (Estagio 0), [[cexai/prompt_template_titles]] (3a), [[cexai/prompt_template_keywords]] (3b), [[cexai/prompt_template_bullets]] (3c), [[cexai/prompt_template_description]] (3d), [[cexai/prompt_template_faqs]] (3e). Os exemplos canônicos de gatilho mental em [[cexai/few_shot_example_gatilhos_x10]].

## Estágio 0 -- INTAKE (coleta por paste -- SEMPRE primeiro)
> **URLs de marketplace NÃO são acessíveis.** Você não abre links de mercadolivre.com.br, shopee, amazon ou magalu -- eles bloqueiam bot / exigem JS/login. Logo, todo input que seria uma URL (`product_url`, `competitor_url`) vira **coleta por paste**: o usuário abre o link no navegador dele e COLA o conteúdo aqui.
>
> Antes de qualquer geração, peça os inputs com este template de copiar-e-colar (adapte ao que já foi fornecido -- não repita o que o usuário já deu):
>
> ```
> Para gerar seu anúncio, cole aqui:
> - Nome do produto:
> - Descrição atual (cole, se houver):
> - Ficha técnica / especificações (dimensões, material, peso, voltagem, composição, conteúdo da embalagem, etc.):
> - Preço (BRL):
> - Diferenciais / USPs:
> - Marketplace alvo (mercadolivre | shopee | amazon | magalu):
> - (opcional) Texto de 1-3 anúncios concorrentes (COLE o texto, não o link):
> ```
>
> Inclua sempre esta linha quando o usuário oferecer apenas um link:
> **"Se você só tem o link (ex: mercadolivre.com.br/...), eu não consigo abrir com confiabilidade -- abra no seu navegador e cole aqui a descrição e a ficha técnica."**
>
> Gere **só a partir do que foi colado**. Spec ausente -> `[PREENCHER: <campo>]` (nunca invente). Em seguida vá para o Estágio 1.

## Estágio 1 -- Pesquisa do produto
> A partir de {product_name}, {category}, {price_brl}, {differentials}, {target_audience}, extraia:
> - **primary_keyword**: o principal termo de busca do produto.
> - **secondary_keywords**: 10-20 termos relacionados (variações, long-tail, sinônimos).
> - **category_path**: caminho na árvore (ex.: "Casa > Cozinha > Garrafas").
> - **price_tier**: budget | mid | premium (a partir do preço e categoria).
> - **selling_points**: top 5 USPs (diferenciais traduzidos em benefício).
> - **competitor_gaps**: o que os concorrentes deixam de oferecer.
> - **audience_intent**: a intenção de busca (ex.: "comprar garrafa térmica boa").

## Estágio 2 -- Títulos (3 variações)
> Gere **3 títulos** seguindo as regras EXATAS do {marketplace} (P01/P09). Conte os caracteres.
> Fórmulas-base:
> - Variação 1: `[KW_PRIMARIA] + [MATERIAL] + [TAMANHO] + [USP_1]`
> - Variação 2: `[KW_PRIMARIA] + [USP_1] + [USP_2] + [MATERIAL]`
> - Variação 3: `[KW_PRIMARIA] + [BENEFICIO_1] + [TAMANHO] + [MARCA]`
> Regras: keyword primária nas 3 primeiras palavras; ML sem conectores; Shopee 1-2 emojis no início; Amazon marca primeiro; máx. 2 repetições de keyword.

## Bullets (10x -- geração V5, antes da descrição)
> Gere **10 bullets** (Amazon: 5). Cada bullet em ML tem **250-299 caracteres** (texto corrido, **sem emoji**, sem prefixo em CAPS). Cada bullet nasce de uma origem real, nesta prioridade: 1 feature -> 1 bullet (feature convertida em benefício); se faltam, 1 pain_point -> 1 bullet; depois 1 gap -> 1 bullet. Integre 1-2 keywords por bullet naturalmente. Comece com letra maiúscula. **Nunca** invente specs nem use placeholders. Conte os caracteres antes de responder.

## Estágio 3 -- Descrição (6 folds mobile-first, V5)
> Escreva a descrição em PT-BR. 92% dos compradores brasileiros leem no celular -- estruture em 6 folds (sem imprimir rótulos):
> - **Fold 1** (95% leem): proposta de valor + bullets como lista.
> - **Fold 2** (65%): specs técnicas DO INPUT (omita as ausentes -- nunca invente).
> - **Fold 3** (35%): casos de uso + diferenciais.
> - **Fold 4** (20%): objeções (de reclamações reais) ou omita se não há dados.
> - **Fold 5** (SEO): FAQ inline + keywords longtail em cenários de uso reais.
> - **Fold 6**: CTA natural (2-3 linhas).
> Comprimento ML: **5000-7000 caracteres**. Integre as top keywords. ML usa `<b>/<br>/<ul>` na html_description; Shopee usa texto puro. Frases de até 20 palavras. Não cite preço (R$). Sem rótulos de framework. Sem tags [VERIFICAR]/[COMPLETAR]/[TODO]/[CHECK].
>
> *Nota didática (FAT legado):* a lógica StoryBrand de 7 seções (P01) ainda serve de bússola narrativa (herói/problema/guia/plano/CTA), mas a produção V5 entrega em 6 folds mobile-first, não em 7 rótulos.

## FAQs (5-7)
> Gere 5-7 perguntas (tamanho, durabilidade, preço, entrega, garantia). 1 reclamação real do input -> 1 FAQ com resposta assertiva (2-3 frases, sem hedge tipo "depende"/"pode variar"). Sem placeholders.

## Estágio 4 -- SEO (2 blocos de keywords)
> **Bloco 1 -- Comercial (alta intenção de compra), 115-120 keywords**, separadas por vírgula:
> head terms; variantes long-tail; combinações marca+produto; variantes de tamanho/cor/material; "comprar {produto}"; "melhor {produto}".
>
> **Bloco 2 -- Informacional, 115-120 keywords**, separadas por vírgula:
> "como usar {produto}"; "para que serve {produto}"; "qual melhor {categoria}"; buscas baseadas em problema; buscas de comparação.
>
> Sem duplicatas entre os blocos. Densidade-alvo 1-3%.

## Estágio 5 -- Formatação por marketplace
> Reformate todo o conteúdo para o {marketplace} alvo (ver P05/P09 para o shape exato). Garanta limites de caractere, campos obrigatórios preenchidos e compliance de TOS.

## Injeção de feedback (autocorreção em retry)
Quando uma dimensão falha no gate, injete a instrução de correção correspondente e regere só a seção afetada (mapa completo em [[cexai/revision_loop_policy_anuncio]]):
- `TITLE_SHORT` -> "O título DEVE ter 58-60 caracteres. Some keywords de diferenciação."
- `TITLE_LONG` -> "Máx. 60 caracteres. Remova a palavra menos importante."
- `TITLE_CONNECTORS` -> "Remova conectores (e, com, de, para); use separadores."
- `SECTION_LABELS` -> "REMOVA todos os rótulos (HERÓI, GUIA, PLANO, CTA...) do texto."
- `PRICE_IN_DESC` -> "Remova toda referência a preço (R$) da descrição."
- `LONG_SENTENCES` -> "Quebre frases para máx. 20 palavras. Use pontos."
- `FEW_TRIGGERS` -> "Inclua >= 5 gatilhos: social_proof, scarcity, authority, urgency, guarantee."
- `LOW_DENSITY` -> "Repita a keyword principal a cada 2 parágrafos. Alvo 3%."
- `NO_CTA` -> "Adicione uma chamada para ação clara no parágrafo final."
- `NO_BULLETS` -> "Gere EXATAMENTE a quantidade de bullets; cada um 250-299 chars."
- `BULLET_SHORT` -> "Cada bullet DEVE ter 250-299 chars. Expanda com detalhes de benefício."
- `BULLET_LONG` -> "Cada bullet DEVE ter 250-299 chars. Reduza o texto."

## Related CEXAI artifacts

- [[prompt-template-builder]] -- parameterized prompt contract
