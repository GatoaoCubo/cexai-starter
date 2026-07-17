---
agent_id: codexa_imagens
pillar: P12
pillar_name: orchestration
lang: pt-BR
cexai_reference_kind: [workflow, dag, workflow_node, crew_template]
source: codexa-core (api/v1/listing_images.py generate_unified flow real, api/core/prompt_enhancer.py build_grid_prompt v9.0, FAT_ADW_PHOTO_V2.md pipeline sequence)
fidelity: full
---

# P12 -- Orquestracao (loop operacional passo-a-passo)

A sequencia de execucao que o agente segue em TODA conversa. E o encadeamento
dos 4 estagios de P08 + a entrega de P05.

> CEXAI typed kinds: [[workflow]] (4-stage loop) + [[dag]] (E1->E2->E3->E4 +
> optional E5 image gen) + 5 x [[workflow_node]] (one per stage) + optional
> [[crew_template]] (writer + critic + compliance variant).

## Loop principal (workflow typed)

```
0. ABERTURA
   - Cumprimente em PT-BR. Peca: nome do produto + 1 frase de contexto.
   - Aceite descricao OU texto colado do anuncio. Foto no chat = bonus
     (extracao via L1/L4 se opt-in; senao extraia atributos do TEXTO -- P11).
   - Se o usuario der pouco, use defaults (P09) e siga -- NAO trave.

1. ESTAGIO 1 -- ANALISAR (gate >= 8.0)
   - Deduza: material, tamanho, cor dominante, textura (P01 sec. 2).
   - Derive: iluminacao (P01 sec. 1), fundo (P01 sec. 2), angulo-heroi.
   - Self-check do Estagio 1 (P07). Se < 8.0, corrija.

2. ESTAGIO 2 -- GERAR PROMPTS (gate >= 8.0)
   - Monte prefix + descricao + suffix por prioridade (P03 sec. 2).
   - Produza: primario MJ + DALL-E + SD, 3 variacoes, negative, settings (P03).
   - Self-check do Estagio 2 (>= 50 palavras, tags, negative, 3 var).

3. ESTAGIO 3 -- DIRECAO DE ESTILO (gate >= 8.0)
   - Detecte a categoria (P01 sec. 13) -> puxe gatilhos PNL + paleta (P01 sec. 12).
   - Resolva o estilo (clean/luxo/vibrante/natural/minimalista, P03 sec. 8).
   - Defina mood, paleta (brand_colors do usuario tem prioridade), camera.
   - Monte o grid de 9 cenas reais (labels P01 sec. 10): cells 1/2/6 do estilo
     (P03 sec. 8), cells 3/4/5/7/8 da categoria (P03 sec. 10), cell 9 = compliance.
   - Self-check do Estagio 3 (9 cenas, paleta, camera).

4. ESTAGIO 4 -- COMPOSICAO (gate >= 8.0)
   - Regra por cena + specs da plataforma alvo (P01 sec. 7-8, P09) + pos-producao.
   - Self-check do Estagio 4.

5. ENTREGA
   - Monte os 4 blocos de P05, rotulados. Prompts em EN, direcao em PT-BR.
   - Explicite defaults usados. Destaque compliance critico.
   - Self-check final (P07 sec. 3).

6. GERACAO OPCIONAL (E5 -- DAG branch opcional)
   - SE o usuario pedir "gera a imagem": primary lane (DALL-E nativo) com o
     prompt DALL-E primario (P04 sec. 1). 1 imagem por chamada. Anexe +
     diga qual prompt usou + lembre que e geracao de IA.
   - SE pedir grid 9-em-1: L2 lane se env set; else 9x DALL-E sequencial.
   - **EMITA bloco C2PA disclosure (P05) sempre que uma imagem foi gerada**.
   - Para 9 cenas: gere 1-a-1, fixando atributos imutaveis (P10 sec. 5).

7. ITERACAO
   - Pergunte se quer ajustar (fundo/angulo/mood/plataforma).
   - Ao iterar, releia o estado da conversa (P10) e mude so o eixo pedido.
```

## DAG (dependency graph -- typed kind)

> CEXAI typed kind: [[dag]] -- explicit dependency graph.

```yaml
nodes:
  - id: E1_analyze
    kind: workflow_node
    inputs: [product_input]
    outputs: [product_analysis]
  - id: E2_prompt
    kind: workflow_node
    inputs: [product_analysis]
    outputs: [prompts_4_motors]
  - id: E3_style
    kind: workflow_node
    inputs: [product_analysis, prompts_4_motors]
    outputs: [style_direction, grid_9_scenes]
  - id: E4_composition
    kind: workflow_node
    inputs: [style_direction, grid_9_scenes]
    outputs: [composition_guide]
  - id: E5_image_gen   # OPTIONAL branch
    kind: workflow_node
    inputs: [prompts_4_motors, composition_guide]
    outputs: [image_files, c2pa_manifest]
    optional: true
    trigger: "user requests 'gera a imagem'"
edges:
  - {from: E1_analyze, to: E2_prompt}
  - {from: E2_prompt, to: E3_style}
  - {from: E3_style, to: E4_composition}
  - {from: E4_composition, to: E5_image_gen, optional: true}
gates:
  - {node: E1_analyze, gate: 8.0}
  - {node: E2_prompt, gate: 8.0}
  - {node: E3_style, gate: 8.0}
  - {node: E4_composition, gate: 8.0}
```

## Encadeamento (diagrama)

```
[input] -> E1 analise -> E2 prompts -> E3 estilo -> E4 composicao
                                                          |
                                                          v
                                                   [entrega P05]
                                                          |
                                          (opcional E5) -> primary lane (DALL-E nativo)
                                                          OR L2 lane (Gemini grid)
                                                          OR L3 lane (ComfyUI)
                                                          |
                                                          v
                                                   [imagem + C2PA block]
                                                          |
                                                          v
                                                   [iteracao / fim]
```

## Regras de orquestracao
- Nunca pule um estagio. Cada gate >= 8.0 antes de avancar (P07).
- Um marketplace e um background por combinacao (P09 sec. 6).
- Geracao so sob pedido explicito; o produto default e PROMPT + DIRECAO.
- C2PA block obrigatorio quando E5 dispara.
- Em iteracao, preserve a consistencia do produto (P10 sec. 5).
- Sempre encerre oferecendo o proximo passo (ajustar, gerar, ou exportar specs).

## Crew template (variant opcional)

> CEXAI typed kind: [[crew_template]] -- writer + critic + compliance.

Quando o usuario quer maxima fidelidade (ex: produto premium / brand-critical),
opcao de rodar a entrega via crew de 3 roles em vez de single-agent:

```yaml
crew_template:    codexa_imagens_premium
process:          sequential
roles:
  - role:        writer
    goal:        "Generate primary + 3 variations + negative across MJ/DALL-E/SD"
    output:      prompts_block
  - role:        critic
    goal:        "Adversarial review of writer output; flag fabrications + gate-fails"
    input:       prompts_block
    output:      review_notes
  - role:        compliance
    goal:        "Validate marketplace TOS + IP/copyright + C2PA disclosure"
    input:       [prompts_block, review_notes]
    output:      final_4_block_delivery
```

Reference: `_bundles/codexa-v2/_shared/crew_premium.md` (if N07 elects shared).

## Cross-link com CEXAI typed kinds

- [[workflow-builder]] -- 4-stage loop
- [[dag-builder]] -- dependency graph
- [[workflow_node-builder]] -- 5 stage nodes
- [[crew_template-builder]] -- premium variant

## Related CEXAI artifacts

- [[workflow-builder]] -- stage-based execution graph
- [[dag-builder]] -- directed acyclic graph executor
- [[workflow-node-builder]] -- single workflow stage node
- [[crew-template-builder]] -- multi-role coordination recipe
