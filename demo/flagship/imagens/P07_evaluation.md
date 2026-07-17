---
agent_id: codexa_imagens
pillar: P07
pillar_name: evaluation
lang: pt-BR
cexai_reference_kind: [scoring_rubric, eval_metric, llm_judge]
source: codexa-core (FAT_ADW_PHOTO_V2.md Quality Gates per stage, api/core/compliance_checker.py _calculate_score)
fidelity: full
---

# P07 -- Quality Gates e Self-Check

Cada estagio do pipeline tem gate **>= 8.0**. O agente nao avanca de estagio sem
passar. Se reprovar, corrige e re-testa (max. 2 tentativas) antes de seguir.

> CEXAI typed kinds: [[scoring_rubric]] (per-stage 8.0 gate) + 4x [[eval_metric]]
> (dimensions/background/fill/format) + [[llm_judge]] (anti-hallucination final pass).

## 1. Gate por estagio (do FAT V2)

> CEXAI typed kind: [[scoring_rubric]] -- 4-stage rubric.

### Estagio 1 -- Analise (gate >= 8.0)
- [ ] Tipo de material identificado corretamente
- [ ] Categoria de tamanho apropriada
- [ ] Recomendacao de iluminacao coerente com o material (P01 sec. 1)
- [ ] >= 2 sugestoes de estilo

### Estagio 2 -- Prompt (gate >= 8.0)
- [ ] Prompt primario >= 50 palavras (detalhado)
- [ ] Inclui quality tags (>= 4)
- [ ] Negative prompt presente
- [ ] Settings adequados ao estilo
- [ ] 3+ variacoes geradas

### Estagio 3 -- Estilo (gate >= 8.0)
- [ ] 9 angulos de cena definidos
- [ ] Paleta coerente com a marca
- [ ] Settings de camera realistas
- [ ] Props relevantes ao produto

### Estagio 4 -- Composicao (gate >= 8.0)
- [ ] Regra de composicao por cena
- [ ] Specs da plataforma incluidas
- [ ] Passos de pos-producao definidos
- [ ] Requisitos de resolucao atendidos

## 2. Rubrica de score de compliance (imagem gerada)

> CEXAI typed kind: 4 x [[eval_metric]] -- dimensions, background, fill, format.

Replica `_calculate_score` do backend. Pesos:

| Check | Peso | Pass | Warn | Kind |
|-------|------|------|------|------|
| dimensoes | 30 | atende min | 80-100% do min | eval_metric_dimensions |
| fundo branco | 30 | dist <= tolerancia | <= 2x tolerancia | eval_metric_background |
| preenchimento | 25 | >= min % | >= 80% do min | eval_metric_fill |
| formato | 15 | aceito + preferido | aceito nao-preferido | eval_metric_format |

Score = (pontos ganhos / peso total) x 100. **Aprovado = score >= 70 e nenhum
check em "fail".** Warn vale 60% do peso.

## 3. Self-check final (antes de entregar)
- [ ] Os 4 blocos de P05 estao presentes e rotulados
- [ ] Bloco C2PA presente quando imagem foi gerada
- [ ] Prompts em ingles, em code fences
- [ ] Direcao em PT-BR
- [ ] Iluminacao NAO contradiz a matriz de material (P01 sec. 1)
- [ ] Compliance da plataforma alvo respeitada (P01 sec. 7, P09)
- [ ] Negative prompt presente em todos os motores
- [ ] Limitacoes declaradas quando relevante (sem visao L1/L4, DALL-E 1-a-1) -- P11
- [ ] Defaults usados foram explicitados ao usuario

## 4. Como pontuar (heuristica rapida)
Para cada checklist de estagio: itens marcados / total x 10. Abaixo de 8.0,
identifique o item faltante, corrija, re-pontue. Acima de 8.0, avance.

## 5. Auto-checagem anti-alucinacao (OBRIGATORIO antes de entregar)

> CEXAI typed kind: [[llm_judge]] -- anti-hallucination final review pass.

Revise CADA numero e CADA atributo do prompt e da direcao:
- [ ] Cada cor/material/tamanho/forma/acabamento no prompt veio do INPUT do usuario?
      Se nao -> remover, perguntar, ou marcar `[PREENCHER: <campo>]`.
- [ ] Nenhum numero fabricado (peso, volume, voltagem, validade, dimensao do produto)?
- [ ] Nenhuma certificacao/claim/marca/origem inventada para "enriquecer" o prompt?
- [ ] Inferencias de foto do chat marcadas com "(confirme)"?
- [ ] Paletas/estilos sugeridos rotulados como SUGESTAO, nao como cor da marca?
- [ ] Bloco final "AVISO Suposicoes e dados a confirmar" presente quando houve
      inferencia, placeholder ou default nao confirmado?
- [ ] Bloco C2PA presente quando uma imagem efetivamente foi gerada?

Regra: enriquecer o PROMPT com tecnica fotografica (luz, lente, composicao,
quality tags) e sempre permitido. Enriquecer com ATRIBUTOS factuais do produto
que o usuario nao deu e PROIBIDO.

## 6. Score de fidelidade do bundle
Lembre-se: a parte de **prompt/direcao** e fidelidade FULL (=produz output igual
ao backend). A geracao varia por runtime e por opt-in de lanes (ver manifest
fidelity table). Ao reportar, seja honesto:
"O prompt e a direcao estao completos; a geracao via DALL-E e imagem unica;
para o grid 9-em-1 unico voce precisa da lane L2 opcional (Gemini Gems native
ou MCP Claude com GEMINI_API_KEY)."

## 7. Cross-link com CEXAI typed kinds

- [[scoring_rubric-builder]] -- 4-stage gate
- [[eval_metric-builder]] -- 4 compliance metrics
- [[llm_judge-builder]] -- anti-hallucination final pass

## Related CEXAI artifacts

- [[scoring-rubric-builder]] -- quality scoring criteria
- [[eval-metric-builder]] -- single eval metric
- [[llm-judge-builder]] -- LLM-as-judge config
