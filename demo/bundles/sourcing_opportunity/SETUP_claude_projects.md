# SETUP -- Claude Projects

Setup do bundle `sourcing_opportunity` (Sourcing Opportunity Matrix) em Claude Projects. Este
bundle não precisa de nenhum MCP bridge nem Action -- é puramente Knowledge + instrução. ~5
minutos.

## Pré-requisitos

- Conta Claude (Free, Pro, ou Team) com Projects habilitado.
- ZERO chaves de API ou MCP servers necessários.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Sourcing Opportunity Matrix`.

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
explicitamente a nunca fazer isso (ver a seção LIMITES DE SEGURANÇA).

### 5. Teste

Em uma conversa do Project:

> `Tenho um catálogo de fornecedor (CSV com custo por SKU) e quero ranquear os produtos por
> margem, cruzando contra preço e demanda de mercado. Explique o contrato de entrada e monte a
> matriz de oportunidade.`

O agente deve:
1. Confirmar o contrato de entrada de 9 campos (catalog_sources, cost_source_strategy, tax_pct,
   region, demand_signal_basis, fee_model, freight_model, verify_top_n, show_net_margin).
2. Explicar que EAN/GTIN/código de barras estão excluídos por design como chave de join entre
   marketplaces.
3. Entregar as 8 seções de saída na ordem congelada: Resumo executivo, Matriz de oportunidade,
   Leitura por categoria, Cobertura, Verificacao (top-N), Match / auditoria, Proveniencia,
   Veredito + proximos passos.
4. Declarar honestamente que, sem uma credencial de dados de demanda ao vivo, toda célula de
   mercado/demanda é honest-null (`"nao pesquisado"`) e o gate `sourcing_confiavel` fica
   BLOQUEADO -- nunca fabricar um preço de mercado ou nível de demanda.

## Fidelidade declarada: FULL

Diferente de bundles com Actions/MCP (onde a fidelidade pode cair para `partial` sem wiring
externo), `sourcing_opportunity` não perde nenhuma capacidade em Claude Projects: o contrato
inteiro é Knowledge + instrução, e o próprio gerador real já é offline-determinístico e
honest-null por design (ver `P01_knowledge.md`).

## Vantagens do Claude Projects para este bundle

| Aspecto | Claude Projects |
|---------|----------------|
| Limite de arquivos de Knowledge | Sem limite de contagem (limite por tamanho total) |
| Janela de contexto | Ampla o suficiente para os 12 pillars inteiros + o histórico da conversa (útil se você colar um catálogo grande na conversa) |
| Chamadas de ferramenta em paralelo | Nativo via tool_use -- irrelevante aqui, já que este bundle não declara nenhuma ferramenta |
| Custo | Plano Free já cobre o uso básico deste bundle |

## Solução de problemas

- **"Ele inventou um preço de mercado ou nível de demanda"** -> reforce: "sem credencial de
  demanda ao vivo, toda célula de mercado/demanda é honest-null (`nao pesquisado`) -- nunca
  invente um valor" (ver `P01_knowledge.md`).
- **"Ele reordenou ou renomeou as 8 seções de saída"** -> reforce: "a ordem Resumo executivo ->
  Matriz de oportunidade -> Leitura por categoria -> Cobertura -> Verificacao (top-N) -> Match /
  auditoria -> Proveniencia -> Veredito + proximos passos é congelada" (ver `P06_schema.md`).
- **"Ele tratou EAN/GTIN/código de barras como chave de join"** -> reforce a exclusão estrutural
  (ver `P09_config.md` e `P02_model.md`).
- **"Os placeholders [fornecer: ...] continuam aparecendo na saída"** -> isso é esperado e
  correto enquanto você não preencheu a marca real; é o comportamento honest-null por design,
  não um bug.
- **"Ele declarou sourcing_confiavel sem as condições"** -> reforce que as 4 condições booleanas
  (margem_bruta_top >= 25%, top-N verificado, nenhum item crítico sem preço, frescor != RED)
  precisam aparecer explicitadas, não só o resultado true/false (ver `P05_output.md`).
- **Quero conectar uma fonte de dados de demanda real (preço/reviews de marketplace ao vivo)** ->
  isso exige uma credencial + `demand_sources` no lado do gerador real -- este bundle documenta o
  contrato honestamente para esse caso, não substitui a implementação real.
