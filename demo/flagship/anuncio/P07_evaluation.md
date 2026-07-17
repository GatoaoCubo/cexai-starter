---
agent: anuncio
pillar: P07
pillar_name: evaluation
lang: pt-BR
source: api/core/anuncio_validator.py (5D dims, FABRICATION_PATTERNS, ANVISA, _basic_validate, should_retry); api/v1/anuncios.py (ISSUE_TO_FIX, RETRY_CONFIG); records/pool/workflows/fat/FAT_ADW_ANUNCIO_V2.md (Quality Gates)
fidelity: full
architecture: cexai_12p_v1
cexai_reference_kind: scoring_rubric
cexai_typed_artifacts:
  - cexai/scoring_rubric_anuncio_5d.md
  - cexai/llm_judge_anuncio_council.md
  - cexai/revision_loop_policy_anuncio.md
cexai_credit: "Powered by CEXAI architecture (300+ kinds, 12 pillars, 8 nuclei)"
---

# P07 -- Quality Gates (rubrica, self-check, thresholds)

Como o agente avalia a própria saída antes de entregar. Gate global: **>= 8.0** (escala 0-10). Espelha o `anuncio_validator` de produção (V5).

> **Camada CEXAI:** rubrica tipada com critérios explícitos por dimensão em [[cexai/scoring_rubric_anuncio_5d]]. UPGRADE LANE -- council cross-provider em [[cexai/llm_judge_anuncio_council]] (Claude/Gemini variants quando keys presentes). Política de retry em [[cexai/revision_loop_policy_anuncio]].

## Rubrica 5D de produção (V5 -- avalie cada dimensão 0 a 10)

> Atenção: a V5 substituiu as antigas dimensões (clarity/persuasion/seo/coherence) por dimensões **estruturais + factuais**, porque as antigas penalizavam a saída zero-fabricação. Use ESTAS:

| Dimensão | Peso | O que mede | Falha se... |
|----------|------|------------|-------------|
| **titulo** | 0.25 | 3 títulos no limite, sem conectores, keyword no início | fora de 58-60 (ML); conector; sem keyword |
| **keywords** | 0.20 | 2 blocos 115-120, cada < 60 chars, overlap <= 15% | bloco curto; keyword > 60 chars; overlap > 15%; frases "stuffed" |
| **descricao** | 0.20 | >= 5000 chars (ML), sem rótulos, bullets integrados | curta; rótulos de framework visíveis; R$ presente |
| **bullets** | 0.20 | 10 bullets (Amazon 5), cada 250-299 chars (ML) | quantidade errada; fora de 250-299; vazios |
| **factual** | 0.15 | ZERO claims fabricados (anti-alucinação) | qualquer padrão de fabricação detectado (-1.5 cada) |

**overall_score = soma ponderada.** Aceite `passed = overall >= 8.0`. `compliance` é alias de `factual` (compat).

## Dimensão factual (anti-fabricação) -- a mais crítica
Cada padrão fabricado detectado custa **-1.5** no score. A dimensão passa só se score >= 0.70. Padrões bloqueados (regex de produção):
- `fake_sales`: "+X vendidos", "mais de X clientes/famílias/avaliações"
- `fake_rating`: "X,X/5 estrelas"
- `fake_cert`: "certificado/INMETRO/homologado/aprovado" (exceto se o input traz `compliance_notes`)
- `fake_stock`: "apenas X unidades", "últimas restantes"
- `fake_warranty`: "garantia de X meses/anos/dias"
- `fake_gift`: "brinde/bônus/kit (de manutenção/silicone/fixação)"
- `fake_testimonial`: nomes inventados tipo "Maria S., ..."
- `emoji`, `caps_prefix` (PREFIXO:), `storybrand_label` (HERO/GUIDE/PLANO/CHAMADA...)
> Antes de pontuar: releia cada número e claim. "Veio do input? Se não, remova ou marque a confirmar."

## Self-check por bloco (cadeia de geração V5)

**input_validation**
- [ ] confiança do input calculada; campos faltantes listados
- [ ] obrigatórios presentes OU pergunta feita / `[PREENCHER]` inserido

**Títulos**
- [ ] 3 variações; cada uma dentro do limite (ML 58-60 -- conte!)
- [ ] keyword nas 3 primeiras palavras; ML sem conectores; máx. 2 repetições

**Keywords**
- [ ] Bloco 1: 115-120; Bloco 2: 115-120; cada termo < 60 chars
- [ ] overlap entre blocos <= 15%; sem frases "stuffed"

**Bullets**
- [ ] 10 bullets (Amazon 5); cada um **250-299 chars** (ML) -- conte!
- [ ] cada bullet tem origem real (feature/pain_point/gap/spec); sem placeholder; sem emoji

**Descrição**
- [ ] >= 5000 caracteres (ML); 6 folds mobile-first; bullets integrados como lista
- [ ] sem rótulos de framework no texto; sem R$; keywords integradas naturalmente

**Factual (sempre)**
- [ ] zero specs inventadas (peso/dimensão/material/voltagem não fornecidos = omitidos)
- [ ] zero claims fabricados (vendas, avaliações, certificações, estoque, garantia, brinde)
- [ ] termos ANVISA substituídos; bloco "## Suposições e dados a confirmar" presente

## Mapa de autocorreção ISSUE_TO_FIX (idêntico ao de produção)
Quando o self-check detecta um problema, injete a correção e regere só a seção (mapa completo + escalada em [[cexai/revision_loop_policy_anuncio]]):

| Código | Correção (fix injetado) |
|--------|--------------------------|
| `LONG_SENTENCES` | Quebre TODAS as frases em máx. 20 palavras. Pontos, não ponto-e-vírgula. |
| `FEW_TRIGGERS` | Inclua >= 5 gatilhos: social_proof, scarcity, authority, urgency, guarantee. |
| `LOW_DENSITY` | Repita a keyword principal a cada 2 parágrafos. Alvo 3% de densidade. |
| `TITLE_SHORT` | Título DEVE ter 58-60 chars. Some keywords de diferenciação até o mínimo. |
| `TITLE_LONG` | Título DEVE ter máx. 60 chars. Remova a palavra menos importante. |
| `SECTION_LABELS` | REMOVA todos os rótulos (HERO, GUIDE, PLAN, CTA, SUCESSO, FALHA) do texto. |
| `NO_BULLETS` | Gere EXATAMENTE a quantidade de bullets. Cada um **250-299 chars**. |
| `BULLET_SHORT` | Cada bullet DEVE ter **250-299 chars**. Expanda com detalhes de benefício. |
| `BULLET_LONG` | Cada bullet DEVE ter **250-299 chars**. Reduza o texto. |
| `NO_CTA` | Adicione CTA claro no parágrafo final. |
| `PRICE_IN_DESC` | Remova TODA referência a preço (R$) da descrição. |
| `TITLE_CONNECTORS` | Remova conectores (e, com, de, para) do título -- use separadores. |

## Política de retry (idêntica ao pipeline)
- Retry dispara se `passed = false` **OU se qualquer dimensão tem `passed: false`** -- não só pelo overall.
- **Máximo 2 retries.** Regenere só as seções da(s) dimensão(ões) que falharam (mapeamento dim->seção: seo->titulo+keywords+descricao; compliance->titulo+bullets+descricao; coherence->tudo).
- Escalada por tentativa: retry 1 (+0.1 temp), retry 2 (+0.2 temp, modelo mais forte). Na 2ª, foque cirurgicamente nos itens que falharam.
- Se ainda < 8.0 após 2 retries: entregue o melhor resultado como **REVISAR** + liste `validation_issues`.

## Upgrade lane: LLM Judge Council (Claude/Gemini variants)
Quando `${ANTHROPIC_API_KEY}` + `${GEMINI_API_KEY}` presentes, o critic pode invocar council cross-provider ([[cexai/llm_judge_anuncio_council]]) -- 3 judges independentes para a dimensão **factual**. Detecta claims sutis que o regex perde. Custom GPT permanece em self-judge (sem cross-provider).

## Related CEXAI artifacts

- [[scoring-rubric-builder]] -- quality scoring criteria
