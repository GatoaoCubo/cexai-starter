---
kind: instruction
id: bld_instruction_multimodal_prompt
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para multimodal_prompt
quality: null
title: "Instruction Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, instruction]
tldr: "Processo de produção passo a passo para multimodal_prompt"
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [construção de multimodal_prompt, instruction multimodal prompt, multimodal_prompt, builder, instruction, modalidades, visão, áudio, texto, cross_ref]
density_score: 0.85
related:
  - multimodal-prompt-builder
---
## Fase 1: PESQUISA
1. Identificar as modalidades-alvo (visão/áudio/texto) e suas interdependências.
2. Analisar datasets específicos do domínio em busca de correlações cross-modais.
3. Revisar benchmarks multimodais existentes para checar consistência de padrão.
4. Mapear restrições técnicas (ex.: limites de resolução, taxas de amostragem).
5. Documentar casos de uso que exigem injeção simultânea de modalidades.
6. Avaliar templates de prompt anteriores quanto à adaptabilidade.

## Fase 2: COMPOSIÇÃO
1. Inicializar o schema com o array `modalities` (ref.: bld_schema_multimodal_prompt.md).
2. Definir parâmetros de `vision`: resolução, rótulos de objeto, relações espaciais.
3. Definir parâmetros de `audio`: duração, faixas de frequência, tags semânticas.
4. Definir parâmetros de `text`: idioma, sentimento, referências de entidade.
5. Alinhar modalidades via chaves `cross_ref` (ex.: `vision.id == audio.object_id`).
6. Estruturar o prompt usando a sintaxe `INJECT` (ref.: bld_output_template_multimodal_prompt.md).
7. Incorporar triplas de exemplo: `<modality>:<value>:<context>`.
8. Validar a conformidade do schema com as regras de validação de bld_schema_multimodal_prompt.md.
9. Finalizar com placeholders específicos de modalidade para injeção em runtime.

## Fase 3: VALIDAÇÃO
[ ] Todas as modalidades presentes no array `modalities`
[ ] Referências cross-modais resolvem de forma consistente
[ ] Restrições técnicas compatíveis com as capacidades do dataset
[ ] Triplas de exemplo alinhadas aos casos de uso do domínio
[ ] Saída em conformidade com a estrutura de bld_output_template_multimodal_prompt.md

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[multimodal-prompt-builder]] | related | 0.44 |
| [[bld_knowledge_multimodal_prompt]] | upstream | 0.39 |
| bld_instruction_multi_modal_config | sibling | 0.38 |
| bld_collaboration_multi_modal_config | downstream | 0.37 |

<!-- cex:domain_contract:start -->
## Domain Contract -- Enforced Rules (real law from the generator)

> Source: `_tools/capability_generators/media_photo.py`'s `domain_contract()` -- read directly from the generator's own module constants (never re-typed by hand, never fabricated). Injected by `_tools/cex_bundle_deepen.py`; re-running regenerates this section idempotently.

**Contract Version**: 1.0.0

### Enums
- **style**: editorial, lifestyle, minimalista, packshot
- **register**: bold, playful, warm

### Aspect Ratio Platform Intent
| Key | Value |
|-----|-------|
| 4:5 | Feed principal (Instagram/Facebook) -- produto hero |
| 9:16 | Stories/Reels -- formato vertical imersivo |
| 1:1 | Grid quadrado / packshot e-commerce |
| 16:9 | Banner web / YouTube thumbnail |
| 3:4 | Pinterest / portrait editorial |

### Lighting Camera By Register
| Register | Parameter | Value |
|-----|-----|-----|
| warm | Luz | Natural difusa, janela lateral ou reflector branco |
| warm | Lente | 50mm f/1.8 -- bokeh suave para aconchego |
| warm | Angulo | Eye-level ou ligeiramente acima -- perspectiva do tutor |
| warm | Fundo | Parede neutra ou sofa claro, planta desfocada |
| warm | Temperatura | 5500K -- luz do dia, branco quente |
| bold | Luz | Estudio com softbox lateral + fill light minimo |
| bold | Lente | 35mm f/2.8 -- campo aberto, produto dominante |
| bold | Angulo | 3/4 frontal baixo -- produto heroico |
| bold | Fundo | Fundo preto ou cinza escuro, alto contraste |
| bold | Temperatura | 6500K -- frio e preciso |
| playful | Luz | Natural brilhante + rebatedor colorido lateral |
| playful | Lente | 24mm f/2.8 -- wide, movimento e energia |
| playful | Angulo | Levemente abaixo ou nivel do pet -- dinamico |
| playful | Fundo | Cores vibrantes ou estampas geometricas |
| playful | Temperatura | 6000K -- vivido, saturado |

### Mood By Register
| Key | Value |
|-----|-------|
| warm | Aconchego domestico -- luz natural, texturas, conexao emocional com o pet |
| bold | Hero de produto -- alto contraste, foco tecnico, autoridade visual |
| playful | Energia e cor -- movimento, alegria, vibes de redes sociais |

### Negative Prompt By Register
- **warm**: corte abrupto ou enquadramento tenso, cores saturadas ou neon, flash direto
- **bold**: fundo poluido ou desfocado demais, suavidade excessiva, angulo neutro
- **playful**: tons neutros/acinzentados sem pop, composicao estatica, fundo branco simples

### Negative Prompt Universal
- Claim de saude ou terapeutico no texto sobreposto sem aprovacao
- Promessa visual nao-verificavel (ex: produto maior do que e na realidade)
- Sombras duras nao intencionais que escondem detalhes do produto

### Compliance Gates
- Direitos de imagem: fotos de clientes reais so com consentimento escrito assinado
- Sem marca de terceiro visivel sem autorizacao de uso de marca
- Rotulo 'imagem ilustrativa' quando a foto diferir do produto entregue ao cliente
- Animal welfare: nenhum pet deve ser forcado a posicao desconfortavel para o shot
- Nao usar foto de pet alheio sem permissao explicita do tutor

### Default Aspect Ratios By Register
- **warm**: 4:5, 1:1
- **bold**: 4:5, 9:16, 1:1
- **playful**: 9:16, 4:5, 1:1

### Shot List Scaffold
| Label | Intent |
|-----|-----|
| Shot 1 -- produto isolado | Estabelecer produto como hero: forma + material + escala |
| Shot 2 -- pet interagindo | Prova de uso: gato no produto, comportamento natural |
| Shot 3 -- ambiente lifestyle | Contexto emocional: produto integrado ao lar |
| Shot 4 -- detalhe de material | Credibilidade tecnica: sisal, estrutura, acabamento |
| Shot 5 -- CTA visual | Shot de conversao: produto + preco/oferta visivel |
| Shot 6 -- angulo criativo | Diferenciar: perspectiva incomum, composicao ousada |
| Shot 7 -- embalagem + unboxing | Confianca de compra online: o que o cliente recebe |
| Shot 8 -- comparativo de escala | Contextualizar tamanho: produto + item conhecido |
<!-- cex:domain_contract:end -->
