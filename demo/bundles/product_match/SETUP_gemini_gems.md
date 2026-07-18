# SETUP -- Gemini Gems

Setup do bundle `product_match` (Product Match + Catalog Audit) em Gemini Gems. Este bundle não
depende de nenhuma extension nem ferramenta externa -- é puramente Knowledge + instrução. ~5
minutos.

## Pré-requisitos

- Conta Google + acesso a **gemini.google.com**.
- ZERO extensions ou chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Product Match + Catalog Audit`.
4. Description: `Casamento visual de registros (record-linkage) fornecedor x marketplace, com
   auditoria de catálogo offline`.

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

Diferente de bundles que dependem de busca ao vivo, `product_match` não precisa de nenhuma
extension (nem Google Search, nem `url_context`) -- o contrato inteiro é especificação +
conhecimento estático. Deixe as extensions desligadas, a menos que você queira usá-las para
outro propósito dentro da mesma conversa.

### 5. Preencha a marca antes de usar

Substitua cada placeholder `[fornecer: ...]` (nome da marca, tom de voz, valores) pela
informação real da sua marca no texto colado nas Instructions. Enquanto não preenchido, o agente
deve continuar emitindo o placeholder explicitamente -- nunca adivinhar.

### 6. Teste

Em uma conversa do Gem:

> `Quero casar um item do meu fornecedor (foto, dimensão e código informados) com um anúncio de
> marketplace. Como funciona o contrato de match e a auditoria de catálogo?`

O Gem deve:
1. Confirmar o contrato de entrada de 6 campos (items, match_join_keys, match_engine,
   match_confidence_floor, audit_enabled, audit_min_photo_px).
2. Explicar que EAN/GTIN/código de barras são excluídos por design (todo revendedor os
   recodifica).
3. Entregar as 4 seções de saída na ordem congelada: Resultado do match, Auditoria de catálogo,
   Proveniência, Veredito.
4. Nunca fabricar um match SIM/PARCIAL -- com `match_engine=none` (o padrão), toda linha é um
   NAO honesto em confiança 0.0.

## Fidelidade declarada: FULL

| Por quê | Detalhe |
|---|---|
| Sem dependência de Actions/extensions | O contrato inteiro é Knowledge + instrução |
| O motor de match real já é offline-honest-null | `match_engine=none` é o comportamento padrão documentado -- Gemini Gems reproduz o mesmo, sem degradar nada |
| Os 12 pillars sobem sem adaptação | Nenhuma seção precisa ser cortada ou resumida para caber no Gem |

## Vantagens do Gemini para este bundle

- **Janela de contexto grande** (mais de 1M tokens em modelos recentes) -- folga ampla para os
  12 pillars + o histórico da conversa.
- **Multi-modal nativo**: se a sua auditoria de catálogo envolve olhar fotos de produto (por
  exemplo, para confirmar a divergência texto-vs-foto descrita em `P01_knowledge.md`), você pode
  anexar a imagem diretamente na conversa e pedir para o Gem descrevê-la.

## Solução de problemas

- **"O Gem inventou um resultado de match"** -> reforce: "enquanto match_engine=none, toda linha
  é NAO em confiança 0.0 -- nunca invente um SIM/PARCIAL" (ver `P01_knowledge.md`).
- **"O Gem reordenou as 4 seções de saída"** -> reforce: "a ordem Resultado do match -> Auditoria
  de catálogo -> Proveniência -> Veredito é congelada" (ver `P06_schema.md`).
- **"O Gem tratou EAN/GTIN/código de barras como chave de join"** -> reforce a exclusão
  estrutural (ver `P09_config.md`).
- **Quero analisar fotos de produto para a auditoria** -> anexe a imagem no chat e peça
  explicitamente para o Gem descrever divergências texto-vs-foto; o multi-modal nativo do
  Gemini é bom nisso, mesmo sem nenhum motor de match ao vivo conectado.
- **Quero um motor de match real (reverse-image, embedding, manual)** -> nenhum dos três tem
  implementação hoje em nenhuma plataforma (ver `P01_knowledge.md`); este bundle documenta o
  contrato honestamente, não substitui a implementação real.
