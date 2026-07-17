---
id: bld_output_brandbook
kind: response_format
pillar: P05
builder: brandbook-builder
version: 1.0.0
quality: null
title: Output Format -- brandbook
author: n06_commercial
tags: [response_format, brandbook, P05, output]
llm_function: PRODUCE
created: 2026-06-22
updated: 2026-06-22
---

## Output Contract

### File Naming
`p05_bb_{brand_slug}.md`

### Frontmatter (required)
```yaml
---
id: p05_bb_{brand_slug}
kind: brandbook
pillar: P05
nucleus: N06
brand_name: {brand_name}
version: 1.0.0
quality: null
created: {YYYY-MM-DD}
---
```

### 8 Sections (frozen layout)

1. **Identidade da Marca** -- layout: fields
   Rows: Nome da marca, Essencia, Proposta de valor, Posicionamento, Missao, Valores

2. **Paleta de Cores** -- layout: table
   Columns: Funcao | Hex | Contraste | Uso principal
   Rows: Primaria, Secundaria, Destaque/Accent, Neutra, Fundo

3. **Tipografia** -- layout: fields
   Rows: Primaria (headings), Secundaria (corpo), Display/especial, Escala de tamanhos

4. **Persona da Marca** -- layout: fields
   Rows: Arquetipo, Voz da marca, Tom geral, Tom em crises,
         Copy sample 1 (headline), Copy sample 2 (beneficio), Copy sample 3 (CTA)

5. **Uso do Logotipo** -- layout: list
   Items: versao principal, versao escura, espaco protecao, tamanho minimo,
          distorcoes proibidas, versoes nao aprovadas

6. **Estilo de Imagem** -- layout: fields
   Rows: Mood geral, Estilo de fotografia, Paleta de filtros, Elementos proibidos

7. **Framework de Mensagem** -- layout: table
   Columns: Mensagem | Publico-alvo | Canal | Prioridade

8. **Dos e Nao-Faca** -- layout: table
   Columns: Fazer | Nao Fazer

### Honest Placeholder Convention
Any field without source data: `[fornecer: {description}]`
Example: `[fornecer: essencia em 1 frase -- ex. 'Conforto premium para pets']`

### Never-Fabricate Guarantee
- No invented brand colors
- No invented font names
- No invented copy samples
- No invented conversion metrics
