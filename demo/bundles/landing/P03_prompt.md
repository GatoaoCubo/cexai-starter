---
id: bld_instruction_landing_page
kind: instruction
pillar: P03
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Instrução Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords: [construção de landing page, instrução landing page, landing_page, builder, examples, pipeline de construção de landing page, usar tailwind, open graph, opções de stack, app router]
density_score: 0.90
llm_function: REASON
related:
  - landing-page-builder
  - kc_landing_page
  - bld_architecture_landing_page
  - bld_schema_landing_page
---
# Instrução: Pipeline de Construção de Landing Page

## Etapas
1. **BRIEF** -- Reúna: brand_config OU input do usuário (produto, público, objetivo, tom de voz, preferência de stack)
2. **STRUCTURE** -- Escolha a ordem das seções com base no objetivo:
   - Produto SaaS: HERO > FEATURES > SOCIAL-PROOF > PRICING > FAQ > CTA
   - Serviço/Agência: HERO > PROBLEM > SOLUTION > HOW-IT-WORKS > TESTIMONIALS > CTA
   - Curso/Infoproduto: HERO > PROBLEM > TRANSFORMATION > MODULES > PRICING > FAQ > CTA > GUARANTEE
   - Portfólio: HERO > WORK > ABOUT > TESTIMONIALS > CONTACT
3. **DESIGN TOKENS** -- Extraia do brand_config ou defina:
   - Cores: primary, secondary, accent, bg, text, muted
   - Fontes: heading (display), body (sans), mono
   - Espaçamento: padding das seções, gaps entre componentes
   - Border radius, profundidade de shadow
4. **BUILD** -- Gere cada seção como um bloco autocontido:
   - Cada seção tem: id, aria-label, classes responsivas, CTA ou interação
   - Use classes utilitárias do Tailwind (CSS customizado somente quando inevitável)
   - Componentes shadcn/ui para elementos interativos (accordion, dialog, tabs)
5. **ASSEMBLE** -- Combine em um único arquivo com:
   - DOCTYPE, html lang, head (meta, fontes, Tailwind CDN), body
   - Smooth scroll, scroll-margin para nav ancorada
   - JS: toggle do menu mobile, accordion do FAQ, animações de scroll (IntersectionObserver)
6. **OPTIMIZE** -- Adicione:
   - Meta tags de Open Graph (title, description, image, url)
   - Dados estruturados JSON-LD (Organization ou Product)
   - Atributos de dados GTM/GA4 nos CTAs
   - Lazy loading nas imagens abaixo da dobra
   - Stylesheet básico de impressão
7. **VALIDATE** -- Verifique:
   - Todas as 12 seções presentes (ou omissão justificada)
   - Responsivo no mobile (sem rolagem horizontal)
   - Todos os CTAs têm href ou onclick
   - Todas as imagens têm texto alternativo (alt)
   - Contraste de cor passa no WCAG AA

## Opções de Stack
| Stack | Quando | Saída |
|-------|------|--------|
| HTML + Tailwind CDN | Padrão, zero build | Um único arquivo .html |
| React + Tailwind | Usuário tem projeto React | Componente .tsx |
| Next.js App Router | Usuário tem Next.js | page.tsx + layout.tsx |
| Astro | Usuário quer saída estática | Página .astro |

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[landing-page-builder]] | downstream | 0.49 |
| [[kc_landing_page]] | upstream | 0.45 |
| [[bld_architecture_landing_page]] | downstream | 0.42 |
| [[bld_schema_landing_page]] | downstream | 0.36 |

<!-- cex:domain_contract:start -->
## Domain Contract -- Enforced Rules (real law from the generator)

> Source: `_tools/capability_generators/landing.py`'s `domain_contract()` -- read directly from the generator's own module constants (never re-typed by hand, never fabricated). Injected by `_tools/cex_bundle_deepen.py`; re-running regenerates this section idempotently.

**Contract Version**: 1.0.0

### Enums
- **goal**: download, lead_capture, trial, venda_direta, webinar
- **register**: bold, playful, warm
- **funnel_stage**: awareness, consideration, decision

### Cta Formula By Funnel Stage
| Key | Value |
|-----|-------|
| awareness | Soft call (Saiba mais / Descubra / Explorar) -- sem pressao de compra |
| consideration | Value-proof call (Ver como funciona / Comparar / Agendar demo) |
| decision | Close call (Comprar agora / Garantir desconto / Comecar hoje) |

### Section Structure By Funnel Stage
| Funnel Stage | Order | Section | Breaks Objection |
|-----|-----|-----|-----|
| awareness | 1 | Hero | Objecao: 'Por que devo me importar?' -- headline estabelece relevancia em <5s |
| awareness | 2 | Problema | Objecao: 'Voce nao entende meu problema' -- nomear a dor com precisao |
| awareness | 3 | Solucao | Objecao: 'Isso e so mais uma promessa' -- o mecanismo (como funciona de fato) |
| awareness | 4 | Prova social | Objecao: 'Funciona para pessoas como eu?' -- depoimento com nome + resultado |
| awareness | 5 | FAQ | Objecao: 'Tenho duvidas antes de continuar' -- 3-5 perguntas que bloqueiam acao |
| awareness | 6 | CTA suave | Objecao: 'Ainda nao estou pronto' -- opcao de baixa fricao (newsletter, ebook) |
| consideration | 1 | Hero | Objecao: 'Ja vi isso antes' -- diferenciar pelo mecanismo, nao pelo produto |
| consideration | 2 | Comparativo | Objecao: 'Por que voce e nao o concorrente?' -- matriz de comparacao honesta |
| consideration | 3 | Demo / trial | Objecao: 'Quero testar antes de comprar' -- CTA de baixo risco |
| consideration | 4 | Prova de ROI | Objecao: 'Vale o investimento?' -- calculadora ou caso de negocio |
| consideration | 5 | Garantia | Objecao: 'E se nao funcionar?' -- reversao de risco explicita |
| consideration | 6 | CTA | Objecao: 'Proximo passo nao e claro' -- uma acao, destaque visual |
| decision | 1 | Hero urgencia | Objecao: 'Posso deixar para depois' -- prazo ou escassez real |
| decision | 2 | Oferta | Objecao: 'O preco e alto' -- valor + preco + comparativo de custo |
| decision | 3 | Prova definitiva | Objecao: 'Preciso de mais evidencia' -- numero + fonte + cliente logo |
| decision | 4 | Garantia | Objecao: 'Risco de arrepender' -- politica de devolucao clara |
| decision | 5 | CTA final | Objecao: 'Uma ultima duvida' -- responder + botao de compra imediato |
| decision | 6 | Bump / upsell | Objecao: 'So isso?' -- oferta complementar de alta aceitacao |

### Voice Mode By Register
| Key | Value |
|-----|-------|
| warm | Hero=Empatia, Body=Benefit, Proof=Testemunho, CTA=Convite |
| bold | Hero=Founder/Desafio, Body=Mecanismo, Proof=VP-dados, CTA=Skeptic |
| playful | Hero=Hook-viral, Body=Storytelling, Proof=Social, CTA=FOMO |

### Forbidden Words
| Word | Replacement |
|-----|-----|
| incrivel | resultado especifico + metrica |
| trusted by | nome do cliente + cargo + resultado real |
| game-changer | o mecanismo que muda especificamente |
| superlativo sem fonte | sempre par com ranking + data + fonte auditavel |

### Compliance Gates
- Claim verificavel: toda afirmacao de resultado precisa de fonte e data
- Sem superlativo nao-comprovado: 'melhor', 'n1', 'lider' so com ranking auditavel
- Prova social real: depoimentos com nome completo, cargo, empresa (sem anon)
- LGPD: politica de privacidade linkada no header + footer + formulario
- Pixel de retargeting: consentimento informado antes de ativar rastreamento
- Garantia: politica de devolucao descrita com clareza (prazo + processo)

### Llm Fallback Scaffold
| Key | Value |
|-----|-------|
| hero_h1_a_template | [H1-A: resultado para %s sem mencionar produto] (generation_pending) |
| hero_h1_b_template | [H1-B: provocacao de dor especifica de %s] (generation_pending) |
| hero_winner_default | A |
| cta_sub_default | Sem cartao de credito. Cancele quando quiser. (generation_pending) |
| section_proof_template | [Prova para '%s': dado verificavel + fonte] (generation_pending) |
<!-- cex:domain_contract:end -->
