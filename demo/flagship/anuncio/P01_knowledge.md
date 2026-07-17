---
agent: anuncio
pillar: P01
pillar_name: knowledge
lang: pt-BR
source: records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md; api/v1/anuncios.py
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: knowledge_card
cexai_typed_artifacts:
  - cexai/env_config_marketplace_specs.md
  - cexai/content_filter_anvisa_fabrication.md
  - cexai/enum_def_marketplace.md
  - cexai/few_shot_example_gatilhos_x10.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P01 -- Base de Conhecimento (regras de marketplace BR)

Tudo que o agente `anuncio` precisa saber **de cor** sobre anúncios em marketplaces brasileiros.

> **Camada CEXAI:** os parâmetros estruturados deste pilar vivem como kinds tipados em [[cexai/env_config_marketplace_specs]] (limites por marketplace), [[cexai/enum_def_marketplace]] (4 marketplaces), [[cexai/content_filter_anvisa_fabrication]] (regex de ANVISA + fabrication patterns) e [[cexai/few_shot_example_gatilhos_x10]] (catálogo de gatilhos sobre fato real). Este arquivo é a versão narrativa para o agente memorizar; o contrato canônico está em `cexai/`.

## Regras por marketplace (LEI -- verifique caractere a caractere)

### Mercado Livre (mercadolivre)
- **Título: 58-60 caracteres (ESTRITO).** Mire 58-60; nunca menos de 58, nunca mais de 60.
- **Formato:** `[TERMO_CABECA] [ATRIBUTO_1] [ATRIBUTO_2] [DIFERENCIAL] [ATRIBUTO_3]`.
- **PROIBIDO conectores** no título: "de", "para", "com", "e", "a", "o". Use separadores/espaços.
- **Capitalize** a primeira letra de cada palavra (Title Case).
- Inclua **pelo menos 1 diferenciador**. Keyword primária nas **3 primeiras palavras**.
- Descrição aceita HTML simples: `<b>`, `<br>`, `<ul>`. Ficha técnica como pares atributo/valor.
- **Descrição ML longa: mínimo 5000 caracteres** (regra de produção V5), estruturada em 6 folds mobile-first (ver P03). Tipo de anúncio: `gold_special` ou `gold_pro`. Até 10 keywords/tags.

### Shopee (shopee)
- **Título/name: 100-120 caracteres** (permite mais que ML).
- **Formato:** `[TERMO_CABECA] [ATRIBUTO_1] [ATRIBUTO_2] [ATRIBUTO_3] [MARCA]`.
- **Emojis: 1-2 no máximo**, posicionados no início para chamar atenção.
- **Front-load**: coloque as keywords primárias logo no começo do título.
- Descrição em **texto puro** (sem HTML), emojis permitidos com moderação.
- Atributos específicos da categoria. Defina estoque, preço, categoria, imagens mínimas.

### Amazon BR (amazon)
- **Título: 150-200 caracteres.**
- **Formato:** `[MARCA] - [TERMO_CABECA] [ATRIBUTO_1] [ATRIBUTO_2] - [TAMANHO/COR]`.
- **MARCA obrigatoriamente PRIMEIRO** (regra dura da Amazon).
- **Sem emojis.** Estilo profissional.
- **Bullet points: exatamente 5** (não 10) no formato Amazon.
- Descrição pronta para A+ Content. `search_terms` no backend: máx. 250 bytes.

### Magalu (magalu)
- Suportado no contrato de I/O. Sem regra de título dedicada na fonte -- use o padrão ML como base segura (título conciso, sem conectores, keywords no início) e ajuste para o nicho.

## StoryBrand -- 7 seções da descrição (referência)
1. **HERÓI (cliente)** -- identifica a necessidade do cliente (2-3 linhas).
2. **PROBLEMA** -- a dor que ele sente (2-3 linhas).
3. **GUIA (produto)** -- como o produto resolve (3-5 linhas).
4. **PLANO** -- como usar/comprar (2-3 itens).
5. **CHAMADA PARA AÇÃO** -- por que comprar AGORA (1-2 linhas).
6. **SUCESSO** -- como a vida fica depois da compra (2-3 linhas).
7. **FRACASSO** -- o que acontece sem o produto (1-2 linhas).
> Os rótulos acima orientam a escrita, mas **NUNCA aparecem no texto entregue** (ver P11). A produção V5 entrega em 6 folds mobile-first; StoryBrand é bússola narrativa.

## Bullets -- comprimento e origem (V5, regra de produção)
- **10 bullets** (Amazon: 5). Cada bullet em ML tem **250-299 caracteres** (texto corrido, sem emoji). Shopee 100-250; Amazon/Magalu 100-500. Conte caractere a caractere (o validador rejeita fora da faixa).
- Cada bullet nasce de uma **origem real** do input, nesta prioridade: `feature` (diferencial -> benefício) > `pain_point` (dor que o produto resolve) > `gap` (diferencial vs concorrência) > `spec` (dado técnico fornecido). Se faltam dados, destaque benefícios gerais do produto -- **nunca** placeholders nem specs inventadas.
- Integre 1-2 keywords por bullet naturalmente. Comece cada bullet com letra maiúscula.

## Gatilhos mentais (apoio à escrita dos bullets)
prova_social, escassez, autoridade, urgência, garantia, reciprocidade, novidade, ancoragem, pertencimento, especificidade. São lentes de persuasão para tornar o benefício atraente -- mas o **fato** do bullet vem sempre da origem real (acima), nunca de claim inventado.

> **CEXAI:** 10 exemplos canônicos (1 por gatilho) em [[cexai/few_shot_example_gatilhos_x10]] -- catálogo que o writer puxa em F3 INJECT.

## Tiers de preço
- **budget** -- entrada, foco em custo-benefício.
- **mid** -- equilíbrio preço/qualidade.
- **premium** -- sofisticação, materiais, exclusividade.

## Taxonomia de categoria
Caminho hierárquico: `Casa > Cozinha > Garrafas`. Sempre mapeie o produto à árvore de categoria do marketplace alvo para herdar atributos esperados.

## Palavras/práticas proibidas (compliance)
- Superlativos sem prova: "o melhor", "número 1", "líder", "imbatível", "perfeito".
- CAIXA ALTA em frases inteiras; pontuação spam ("!!!", "★★★").
- Keyword stuffing: repetir o mesmo termo > 2x.
- Claims de saúde/cura sem respaldo; promessas de resultado garantido sem base.
- Preço (R$) dentro da descrição.

## Densidade de keyword
Ideal **1-3%** do texto. Repita a keyword principal de forma natural a cada ~2 parágrafos, sem forçar.

## Termos ANVISA proibidos (claims terapêuticos) -- substituição automática
O validador de produção troca automaticamente termos médicos por linguagem permitida. Nunca afirme que o produto trata/cura doenças:

| Proibido | Use |
|----------|-----|
| trata | auxilia |
| cura | contribui para o bem-estar |
| previne | auxilia na rotina |
| combate | auxilia no cuidado |
| medicamento / remédio | produto |
| cicatriza | auxilia no cuidado da pele |
| anti-inflamatório | calmante |
| antibacteriano | com propriedades higienizantes |
| antifúngico | com propriedades de limpeza |

> **CEXAI:** regex tipado + estratégia de substituição em [[cexai/content_filter_anvisa_fabrication]].

## Padrões de fabricação BLOQUEADOS (penalidade crítica no gate)
O validador detecta e penaliza (-1.5 cada) qualquer claim inventado destes tipos:
- **Vendas/social falsos:** "+500 vendidos", "mais de 1000 clientes", "milhares de famílias".
- **Avaliação falsa:** "4,8/5 estrelas".
- **Certificação falsa:** "certificado INMETRO/ANVISA", "homologado", "aprovado" -- só se o usuário forneceu a prova.
- **Estoque falso:** "apenas 3 unidades", "últimas restantes".
- **Garantia falsa:** "garantia de 12 meses" -- só se fornecida.
- **Brinde falso:** "brinde", "bônus", "kit incluso" -- só se fornecido.
- **Testimonial inventado:** "Maria S., São Paulo".
> Estes só são permitidos quando o dado vem do input do usuário. Na dúvida, omita ou marque como a confirmar (ver P11).

## Related CEXAI artifacts

- [[knowledge-card-builder]] -- typed knowledge unit (KC)
