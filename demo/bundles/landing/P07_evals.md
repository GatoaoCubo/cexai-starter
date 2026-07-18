---
id: bld_quality_gate_landing_page
kind: quality_gate
pillar: P07
builder: landing-page-builder
version: 1.0.0
quality: null
title: "Portão de Qualidade Landing Page"
author: n03_builder
tags: [landing_page, builder, examples]
tldr: "Exemplos de referência e contraexemplos para a construção de landing page, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de landing page"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F7_govern"
keywords: [construção de landing page, quality gate landing page, landing_page, builder, examples, quality gate, landing page builder, open graph, google fonts, comando de pontuação]
density_score: 0.90
llm_function: GOVERN
related:
  - landing-page-builder
---
## Portão de Qualidade

# Portão de Qualidade: Landing Page Builder

## Gates HARD (devem passar, senão o artefato é rejeitado)
1. H01: Frontmatter tem id, kind, title, version, created, quality:null, stack
2. H02: Saída é HTML/JSX sintaticamente válido (sem tags não fechadas)
3. H03: Pelo menos 6 seções presentes (hero + 4 de conteúdo + footer, no mínimo)
4. H04: CTA primário visível acima da dobra (primeira seção)
5. H05: Responsivo: sem larguras fixas > 100vw, usa relative/flex/grid
6. H06: Todas as imagens têm atributo alt
7. H07: DOCTYPE, atributo html lang, meta charset presentes (saída HTML)

## Gates SOFT (avisos, não bloqueiam)
1. S01: Todas as 12 seções presentes
2. S02: Classes/variáveis de dark mode incluídas
3. S03: Meta tags de Open Graph presentes
4. S04: Dados estruturados JSON-LD presentes
5. S05: Atributos de dados de analytics nos CTAs
6. S06: Lazy loading nas imagens abaixo da dobra
7. S07: Labels ARIA em elementos interativos (accordion, menu, dialog)
8. S08: Google Fonts carregadas com display=swap
9. S09: Contraste de cor >= 4.5:1 (WCAG AA)
10. S10: Stylesheet de impressão ou estrutura print-friendly

## Rubrica de Pontuação
| Dimensão | Peso | O que significa 10/10 |
|-----------|--------|-------------|
| Completude | 20% | Todas as 12 seções, todos os metas, todos os hooks de analytics |
| Qualidade Visual | 20% | Design profissional, espaçamento consistente, polido |
| Responsividade | 20% | Pixel-perfect em 375px, 768px, 1024px, 1440px |
| Performance | 15% | Carregamento < 2s, imagens lazy, CSS crítico inline |
| Conversão | 15% | CTA acima da dobra, proposta de valor clara, elementos de urgência |
| Acessibilidade | 10% | WCAG AA, navegação por teclado, compatível com leitor de tela |

## Comando de Pontuação

```bash
python _tools/cex_score.py --apply --verbose target.md
```

```bash
python _tools/cex_score.py --apply N0*/*.md
```

## Exemplos

# Exemplos: Landing Page Builder

## Exemplo 1: Produto SaaS (HTML + Tailwind)

**Input**: "Crie uma landing page para o CodeForge, uma ferramenta de IA para testes de desenvolvedores"

**Esboço da saída** (abreviado -- a saída real é HTML completo):
```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CodeForge — Tests First. Code Fearless.</title>
  <meta name="description" content="AI that writes tests before you write code. Ship faster with confidence.">
  <meta property="og:title" content="CodeForge — Tests First. Code Fearless.">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
  <!-- HERO -->
  <section id="hero" aria-label="Hero" class="min-h-screen flex items-center">
    <div class="max-w-7xl mx-auto px-4 text-center">
      <h1 class="text-5xl md:text-7xl font-bold">Tests First. Code Fearless.</h1>
      <p class="mt-6 text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
        AI that writes your tests before you write code. Ship 3x faster with full coverage.
      </p>
      <a href="#pricing" data-track="hero-cta"
         class="mt-8 inline-block px-8 py-4 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700 transition">
        Start Free Trial
      </a>
    </div>
  </section>
  <!-- ... 11 more sections ... -->
</body>
</html>
```

## Exemplo 2: Infoproduto/Curso (PT-BR)

**Input**: "Crie uma landing page para curso de automação com IA, R$497, 8 módulos"

**Ordem das seções** (modelo de infoproduto):
HERO (transformação) > PROBLEMA (dor do processo manual) > TRANSFORMAÇÃO (antes/depois) >
MÓDULOS (8 cards) > DEPOIMENTOS > GARANTIA (7 dias) > PRICING (R$497 ou 12x) >
FAQ > CTA FINAL > FOOTER

## Contraexemplo
```html
<!-- BAD: Not a landing page, just a wireframe -->
<div>
  <h1>Title here</h1>
  <p>Description here</p>
  <button>CTA</button>
</div>
<!-- Missing: responsive, dark mode, SEO, a11y, sections, styling, EVERYTHING -->
```

## Requisitos do Exemplar

1. Pontuação 9.0+ para qualificar como referência few-shot
2. Demonstrar a estrutura ideal para este kind de artefato
3. Preencher todos os campos de frontmatter com valores realistas
4. Usar conteúdo específico do domínio, não placeholders genéricos
5. Permitir recuperação via tags e correspondência TF-IDF

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `examples` |
| Pillar | P01 |
| Domain | construção de landing page |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

### H_RELATED: Verificação de Referências Cruzadas (HARD)
- [ ] campo de frontmatter `related:` preenchido (mínimo 3 entradas)
- [ ] seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJEITA se < 3 entradas (auto-preenchido pelo cex_wikilink.py em F6.5)

### S_RELATED: Verificação de Referências Cruzadas (SOFT)
- [ ] campo de frontmatter `related:` preenchido (3 a 15 entradas)
- [ ] seção `## Artefatos Relacionados` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a conexão)
