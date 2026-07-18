# SETUP -- Gemini Gems

Setup do bundle `sourcing_opportunity` (Sourcing Opportunity Matrix) em Gemini Gems. Este bundle
não depende de nenhuma extension nem ferramenta externa -- é puramente Knowledge + instrução.
~5 minutos.

## Pré-requisitos

- Conta Google + acesso a **gemini.google.com**.
- ZERO extensions ou chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Sourcing Opportunity Matrix`.
4. Description: `Ranking de oportunidade de sourcing buy-side -- custo de fornecedor x preço e
   demanda de mercado, com gate de go/no-go`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Gemini Gems aceita arquivos de knowledge; o tamanho combinado dos 12 pillars fica bem abaixo de
qualquer limite prático.

### 4. Extensions (não necessárias para este bundle)

Diferente de bundles que dependem de busca ao vivo, `sourcing_opportunity` não precisa de nenhuma
extension (nem Google Search, nem `url_context`) para funcionar honestamente -- o contrato inteiro
é especificação + conhecimento estático, e o próprio gerador real é offline-determinístico por
design. Se você ativar Google Search, use-a apenas para você mesmo pesquisar preços de mercado e
colar o resultado na conversa -- o agente não deve alegar que pesquisou ao vivo sozinho.

### 5. Preencha a marca antes de usar

Substitua cada placeholder `[fornecer: ...]` (nome da marca, tom de voz, valores) pela
informação real da sua marca no texto colado nas Instructions. Enquanto não preenchido, o agente
deve continuar emitindo o placeholder explicitamente -- nunca adivinhar.

### 6. Teste

Em uma conversa do Gem:

> `Tenho um catálogo de fornecedor com custo por produto. Quero uma matriz de oportunidade
> cruzando esse custo contra preço e demanda de mercado, ranqueada por margem. Como funciona o
> contrato e quais seções você entrega?`

O Gem deve:
1. Confirmar o contrato de entrada de 9 campos (catalog_sources, cost_source_strategy, tax_pct,
   region, demand_signal_basis, fee_model, freight_model, verify_top_n, show_net_margin).
2. Explicar que EAN/GTIN/código de barras são excluídos por design como chave de join entre
   marketplaces (todo revendedor os recodifica).
3. Entregar as 8 seções de saída na ordem congelada: Resumo executivo, Matriz de oportunidade,
   Leitura por categoria, Cobertura, Verificacao (top-N), Match / auditoria, Proveniencia,
   Veredito + proximos passos.
4. Nunca fabricar um preço de mercado ou nível de demanda -- sem credencial de demanda ao vivo,
   toda célula correspondente é honest-null (`"nao pesquisado"`) e o gate `sourcing_confiavel`
   fica BLOQUEADO.

## Fidelidade declarada: FULL

| Por quê | Detalhe |
|---|---|
| Sem dependência de Actions/extensions | O contrato inteiro é Knowledge + instrução |
| O gerador real já é offline-honest-null por design | Sem credencial de demanda ao vivo, o comportamento honesto é o padrão documentado -- Gemini Gems reproduz o mesmo, sem degradar nada |
| Os 12 pillars sobem sem adaptação | Nenhuma seção precisa ser cortada ou resumida para caber no Gem |

## Vantagens do Gemini para este bundle

- **Janela de contexto grande** (mais de 1M tokens em modelos recentes) -- folga ampla para os
  12 pillars + um catálogo de fornecedor extenso colado na conversa.
- **Multi-modal nativo**: se o seu catálogo de fornecedor vem como foto de planilha ou PDF
  escaneado, você pode anexar o arquivo diretamente na conversa e pedir para o Gem extrair as
  colunas de custo antes de rodar a análise.

## Solução de problemas

- **"O Gem inventou um preço de mercado ou nível de demanda"** -> reforce: "sem credencial de
  demanda ao vivo, toda célula de mercado/demanda é honest-null (`nao pesquisado`) -- nunca
  invente um valor" (ver `P01_knowledge.md`).
- **"O Gem reordenou as 8 seções de saída"** -> reforce: "a ordem Resumo executivo -> Matriz de
  oportunidade -> Leitura por categoria -> Cobertura -> Verificacao (top-N) -> Match / auditoria
  -> Proveniencia -> Veredito + proximos passos é congelada" (ver `P06_schema.md`).
- **"O Gem tratou EAN/GTIN/código de barras como chave de join"** -> reforce a exclusão
  estrutural (ver `P02_model.md` e `P09_config.md`).
- **Quero analisar fotos/PDFs do catálogo de fornecedor** -> anexe o arquivo no chat e peça
  explicitamente para o Gem extrair as colunas de custo antes de montar a matriz; o multi-modal
  nativo do Gemini é bom nisso, mesmo sem nenhuma fonte de demanda ao vivo conectada.
- **Quero conectar uma fonte de demanda de mercado real** -> isso exige uma credencial +
  `demand_sources` no lado do gerador real (ver `P01_knowledge.md`); este bundle documenta o
  contrato honestamente, não substitui a implementação real.
