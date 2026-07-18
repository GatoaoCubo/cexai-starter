# SETUP -- Claude Projects

Setup do bundle `product_match` (Product Match + Catalog Audit) em Claude Projects. Este bundle
não precisa de nenhum MCP bridge nem Action -- é puramente Knowledge + instrução. ~5 minutos.

## Pré-requisitos

- Conta Claude (Free, Pro, ou Team) com Projects habilitado.
- ZERO chaves de API ou MCP servers necessários.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Product Match + Catalog Audit`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral, ícone de engrenagem).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos deste bundle:

- `P01_knowledge.md`
- `P02_model.md`
- `P03_prompt.md`
- `P04_tools.md`
- `P05_output.md`
- `P06_schema.md`
- `P07_evals.md`
- `P08_architecture.md`
- `P09_config.md`
- `P10_memory.md`
- `P11_feedback.md`
- `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho total do projeto, bem
acima do que estes 12 arquivos ocupam).

### 4. Preencha a marca antes de usar

Todo campo `[fornecer: ...]` em `system_instruction.md` (nome da marca, tom de voz, valores) é
um placeholder honesto -- sem dado real ainda. Edite o texto colado nas Project Instructions
substituindo cada `[fornecer: ...]` pela informação real da sua marca antes do uso em produção.
Não deixe o placeholder no lugar esperando que o modelo "adivinhe" -- ele foi instruído
explicitamente a nunca fazer isso (ver seção LIMITES DE SEGURANÇA).

### 5. Teste

Em uma conversa do Project:

> `Quero casar um item do meu fornecedor (código SUP-4471) com um anúncio no Mercado Livre.
> Explique o contrato de match e rode a auditoria de catálogo.`

O agente deve:
1. Confirmar o contrato de entrada de 6 campos (items, match_join_keys, match_engine,
   match_confidence_floor, audit_enabled, audit_min_photo_px).
2. Explicar que EAN/GTIN/código de barras estão excluídos por design.
3. Entregar as 4 seções de saída na ordem congelada: Resultado do match, Auditoria de catálogo,
   Proveniência, Veredito.
4. Declarar honestamente que, com `match_engine=none` (o padrão), toda linha de match é um NAO em
   confiança 0.0 -- nunca fabricar um SIM/PARCIAL.

## Fidelidade declarada: FULL

Diferente de bundles com Actions/MCP (onde a fidelidade pode cair para `partial` sem wiring
externo), `product_match` não perde nenhuma capacidade em Claude Projects: o contrato inteiro é
Knowledge + instrução, e o próprio motor de match real já é offline-honest-null por design (ver
`P01_knowledge.md`, Matriz de Status do Motor de Match).

## Vantagens do Claude Projects para este bundle

| Aspecto | Claude Projects |
|---------|----------------|
| Limite de arquivos de Knowledge | Sem limite de contagem (limite por tamanho total) |
| Janela de contexto | Ampla o suficiente para os 12 pillars inteiros + o histórico da conversa |
| Chamadas de ferramenta em paralelo | Nativo via tool_use -- irrelevante aqui, já que este bundle não declara nenhuma ferramenta |
| Custo | Plano Free já cobre o uso básico deste bundle |

## Solução de problemas

- **"Ele inventou um resultado de match"** -> reforce: "enquanto match_engine=none, toda linha é
  NAO em confiança 0.0 -- nunca invente um SIM/PARCIAL" (ver `P01_knowledge.md`).
- **"Ele reordenou ou renomeou as 4 seções de saída"** -> reforce: "a ordem Resultado do match ->
  Auditoria de catálogo -> Proveniência -> Veredito é congelada" (ver `P06_schema.md`).
- **"Ele tratou EAN/GTIN/código de barras como chave de join"** -> reforce a exclusão estrutural
  (ver `P09_config.md`).
- **"Os placeholders [fornecer: ...] continuam aparecendo na saída"** -> isso é esperado e
  correto enquanto você não preencheu a marca real; é o comportamento honest-null por design,
  não um bug.
- **Quero conectar um motor de match real (reverse-image, embedding, etc.)** -> hoje nenhum dos
  três tem implementação -- este bundle documenta o contrato honestamente para o dia em que um
  motor ao vivo existir, não substitui a implementação real.
