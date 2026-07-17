---
agent: anuncio
pillar: P05
pillar_name: output
lang: pt-BR
source: api/v1/anuncios.py (export_anuncio_md, result.content, baselinker_export); api/core/anuncio_synthesizer.py (AnuncioGenerationResult); records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md (Output Schema)
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: response_format
cexai_typed_artifacts:
  - cexai/response_format_anuncio_md.md
  - cexai/validation_schema_anuncio_output.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P05 -- Contratos de Saída (formato exato da entrega)

O formato final que o agente entrega. Espelha o `export/md` e o objeto `result.content` reais do pipeline de produção V5.

> **Camada CEXAI:** o formato canônico vive em [[cexai/response_format_anuncio_md]] (4 code blocks + meta) e o shape de saída validado em [[cexai/validation_schema_anuncio_output]] (12 campos + universal validators).

## REGRA DE OURO -- entrega SEMPRE em blocos de código (copy-paste)

O conteúdo-produto final DEVE sair dentro de **blocos de código markdown cercados por ```**, em texto simples, para o usuário copiar e colar direto no campo do marketplace. Regras:
- **Um bloco de código por unidade copiável.** Para anúncio: blocos SEPARADOS para (a) **título / variações de título**, (b) **descrição completa**, (c) **bloco de keywords**, (d) **bullets**. Nunca junte tudo num bloco só.
- **Texto explicativo / conversa fica FORA dos blocos; o conteúdo-produto fica DENTRO.** Cabeçalho, contagens de caracteres, status e comentários ficam fora; o que o usuário cola no marketplace fica dentro.
- **NUNCA** entregue o conteúdo final só como markdown renderizado ou prosa solta -- sempre dentro do code block.
- O bloco **"## Suposições e dados a confirmar" fica FORA** dos code blocks (é meta -- não é colável no marketplace).
- A tabela de qualidade 5D e o cabeçalho (produto/marketplace/score/status) ficam fora dos blocos (são meta de apresentação).

## Template de entrega (estrutura geral)

```markdown
# Anúncio: {melhor_titulo}

**Marketplace**: {marketplace} | **Score**: {overall}/10 | **Status**: {APROVADO|REVISAR}

---
## Títulos
1. [OK|REVISAR] **{titulo_1}** ({n} chars)
2. [OK|REVISAR] **{titulo_2}** ({n} chars)
3. [OK|REVISAR] **{titulo_3}** ({n} chars)

---
## Keywords ({n1} + {n2} = {total})
### Bloco 1 (Comercial / transacional)
{kw1, kw2, kw3, ...}   <- 115-120 termos
### Bloco 2 (Informacional)
{kw1, kw2, kw3, ...}   <- 115-120 termos

---
## Bullets (10 -- origem real)
1. [FEATURE] {texto do bullet} ({n} chars)
2. [PAIN_POINT] {texto do bullet} ({n} chars)
... (10 itens, cada **250-299 chars** em ML; etiqueta = origem: FEATURE | PAIN_POINT | GAP | SPEC)

---
## Descrição ({n} chars -- mínimo 5000 em ML)
{texto limpo, 6 folds mobile-first -- SEM rótulos de framework, SEM preço (R$)}

---
## Ficha Técnica
| Atributo | Valor |
|----------|-------|
| Material | ... |
| Cor | ... |
| ... | ... |

---
## Perguntas Frequentes (FAQs)
**P: {pergunta}**
R: {resposta}
(3-5 FAQs)

---
## Qualidade 5D (dimensões de produção V5)
| Dimensão | Score | Status |
|----------|-------|--------|
| Titulo | {x.x} | [OK|!] |
| Keywords | {x.x} | [OK|!] |
| Descricao | {x.x} | [OK|!] |
| Bullets | {x.x} | [OK|!] |
| Factual (anti-fabricação) | {x.x} | [OK|!] |

---
## Suposições e dados a confirmar
- {dado inferido / placeholder [PREENCHER: x] / claim que precisa de prova}
- (SEMPRE presente -- nunca omita este bloco, mesmo que vazio: escreva "Nenhuma -- todos os dados vieram do input.")
```

## Exemplo concreto da entrega final (como o usuário VÊ -- blocos coláveis)

Texto explicativo fica fora; cada unidade copiável vai no seu próprio bloco de código.

**Anúncio: Caixa de Areia Fechada para Gatos | Mercado Livre · Score 9.1/10 · APROVADO**

(a) Título / variações (cole o escolhido no campo "Título"):

````text
Caixa Areia Fechada Gato Banheiro Sanitario com Pa Cinza  (58 chars) [OK]
Banheiro Gato Fechado Caixa Areia Sanitario com Tampa Pa  (57 chars) [OK]
Caixa Sanitaria Fechada Gato Areia Banheiro Pa Inclusa    (56 chars) [OK]
````

(b) Descrição completa (cole no campo "Descrição"):

````text
Seu gato merece um banheiro discreto e a sua casa merece ficar livre de odor.
A caixa fechada cria um ambiente reservado que deixa o pet a vontade...
(texto limpo, 6 folds mobile-first, >= 5000 chars em ML, sem rotulos, sem R$)
````

(c) Bloco de keywords (cole nas tags / search terms):

````text
Bloco 1 (comercial): caixa de areia gato, banheiro gato fechado, sanitario gato, ...
Bloco 2 (informacional): como limpar caixa de areia, gato nao usa banheiro, ...
````

(d) Bullets (cole na ficha / bullet points):

````text
[FEATURE] Estrutura fechada com tampa que mantem a areia no lugar e... (271 chars)
[PAIN_POINT] Cansou do cheiro pela casa? O design fechado contem o odor... (288 chars)
... (10 bullets em ML, cada 250-299 chars; etiqueta = origem real)
````

> **Como produzir os blocos acima:** use ``` (3 crases) para cada unidade. No exemplo acima usei 4 crases (````) só para que este arquivo-conhecimento exiba os blocos internos sem quebrar; na entrega real ao usuário, use 3 crases por bloco.

## Campos do contrato (espelha o objeto `result.content` real do pipeline V5)
- `titles`: list[{text, char_count, valid, value_proposition}] -- 3 variações; `valid` = dentro do limite.
- `keywords_block_1`: list[str] -- 115-120 comerciais (cada < 60 chars).
- `keywords_block_2`: list[str] -- 115-120 informacionais (zero overlap > 15% com bloco 1).
- `bullets`: list[{text, char_count, source, trigger_type, valid}] -- 10 itens, 250-299 chars (ML).
- `description`: str -- texto limpo (>= 5000 chars ML); `description_char_count`: int.
- `html_description`: str -- versão HTML pronta para ML (`<h2>/<p>/<table>` + ficha + FAQ).
- `faqs`: list[{question, answer, category, source}] -- 5-7.
- `technical_specs`: {specifications, dimensions, weight, materials, colors} -- **só dados reais**.
- `emotional_content`: dict -- sempre vazio em V5 (mantido por compat; não fabrique).
- `quality_5d` / `overall_score`: dimensões {titulo, keywords, descricao, bullets, factual} + score 0-10.
- `passed`: bool (overall >= 8.0); `retry_count`: int.
- `erp_fields` / `baselinker_export`: SKU/EAN/NCM/peso/dimensões -- campos não fornecidos ficam como placeholder.
- `head_terms` / `competitor_gaps` / `suggested_price`: quando houver handoff de pesquisa.

> **CEXAI:** validação completa do shape em [[cexai/validation_schema_anuncio_output]].

## Formato específico por marketplace (estágio erp_formatting)
- **Mercado Livre:** `titulo` (58-60), `descricao` (>= 5000 chars + HTML), bullets 250-299, `ficha_tecnica` (pares nome/valor -- só dados reais), `keywords_tags` (até 10).
- **Shopee:** `name` (100-120), `description` (texto puro 500-3000, emojis OK), bullets 100-250, atributos da categoria.
- **Amazon BR:** `title` (150-200, marca primeiro), `bullet_points` (EXATAMENTE 5, 100-500 chars), `description` (A+ 500-2000), `search_terms` (<= 250 bytes).
- **Magalu:** título 30-150, descrição 500-4000, 10 bullets 100-500.

## Regras de apresentação
- **Entregue o conteúdo-produto SEMPRE em blocos de código** (```), um bloco por unidade copiável: título(s), descrição, keywords, bullets em blocos separados. Veja a REGRA DE OURO no topo.
- Sempre mostre a **contagem de caracteres** ao lado de cada título e de cada bullet (bullets ML 250-299) -- pode ficar dentro do bloco como sufixo `(n chars)` ou em texto explicativo fora.
- Marque cada título/bullet como válido/inválido conforme o limite do marketplace.
- Etiquete cada bullet com sua **origem** (FEATURE/PAIN_POINT/GAP/SPEC).
- Termine com a tabela de qualidade 5D (fora dos blocos), o status final e o bloco "## Suposições e dados a confirmar" (fora dos blocos -- é meta).
- Tudo em PT-BR, colável direto no marketplace.

## Related CEXAI artifacts

- [[response-format-builder]] -- typed output schema
