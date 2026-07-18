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
related:
  - bld_prompt_brandbook
  - kc_brandbook
  - bld_schema_brandbook
---

## Contrato de Saída

### Nomenclatura de Arquivo
`p05_bb_{brand_slug}.md`

### Frontmatter (obrigatório)
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

### 8 Seções (layout fixo)

1. **Identidade da Marca** -- layout: campos
   Linhas: Nome da marca, Essência, Proposta de valor, Posicionamento, Missão, Valores

2. **Paleta de Cores** -- layout: tabela
   Colunas: Função | Hex | Contraste | Uso principal
   Linhas: Primária, Secundária, Destaque, Neutra, Fundo

3. **Tipografia** -- layout: campos
   Linhas: Primária (títulos), Secundária (corpo), Display/especial, Escala de tamanhos

4. **Persona da Marca** -- layout: campos
   Linhas: Arquétipo, Voz da marca, Tom geral, Tom em crises,
           Exemplo de copy 1 (headline), Exemplo de copy 2 (benefício), Exemplo de copy 3 (CTA)

5. **Uso do Logotipo** -- layout: lista
   Itens: versão principal, versão escura, espaço de proteção, tamanho mínimo,
          distorções proibidas, versões não aprovadas

6. **Estilo de Imagem** -- layout: campos
   Linhas: Mood geral, Estilo de fotografia, Paleta de filtros, Elementos proibidos

7. **Framework de Mensagem** -- layout: tabela
   Colunas: Mensagem | Público-alvo | Canal | Prioridade

8. **Faça e Não Faça** -- layout: tabela
   Colunas: Fazer | Não Fazer

### Convenção do Placeholder Honesto
Qualquer campo sem dado de origem: `[fornecer: {description}]`
Exemplo: `[fornecer: essência em 1 frase -- ex. 'Conforto premium para pets']`

### Garantia Nunca-Fabricar
- Nenhuma cor de marca inventada
- Nenhum nome de fonte inventado
- Nenhum exemplo de copy inventado
- Nenhuma métrica de conversão inventada

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_brandbook]] | upstream | 0.23 |
| [[kc_brandbook]] | related | 0.19 |
| [[bld_schema_brandbook]] | downstream | 0.18 |
