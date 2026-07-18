# SETUP -- Gemini Gems

Setup do bundle `product_docs` em Gemini Gems. Como o agente não depende
de Actions/tools externos, o setup é simples: Instructions + Knowledge.
~5 minutos.

## Pré-requisitos

- Conta Google com acesso a gemini.google.com.
- ZERO extensions ou chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Product Docs -- [sua marca]`.
4. Description: `Agente que documenta produtos e funcionalidades como knowledge_card pronto para RAG`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.
4. Substitua os marcadores `[fornecer: ...]` pelos dados reais da sua
   marca antes de usar em produção.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos de pilar deste bundle:

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

### 4. Extensions

Nenhuma extension é necessária -- este agente não pesquisa na web nem
executa código. Deixe Search e Code execution desligadas, se preferir
manter o Gem restrito ao conhecimento carregado.

### 5. Teste

Em uma conversa do Gem:

> `Documente a funcionalidade de exportação CSV do meu produto`

O Gem deve:
1. Usar o que você descreveu sobre a funcionalidade.
2. Produzir um knowledge_card estruturado, seguindo os 12 pilares
   carregados.
3. Marcar `[fornecer: ...]` em qualquer campo sem dado real -- nunca
   inventar.

## Fidelidade declarada: FULL

Este bundle não depende de Actions, scraping ou ferramentas externas -- o
Gemini Gems entrega 100% da capacidade do agente usando somente
Instructions + Knowledge.

## Vantagens do Gemini

- **Context window grande** (acima de 1M tokens nos modelos mais recentes)
  -- espaço de sobra para os 12 pilares mais o histórico da conversa.
- **Multi-modal nativo** -- se você quiser documentar a partir de uma
  captura de tela do produto, o Gem pode analisar a imagem diretamente.

## Solução de problemas

- **O Gem não aparece na lista depois de criado** -> recarregue
  gemini.google.com e verifique em **Gems** -> **My Gems**.
- **Respostas genéricas demais** -> confirme que os 12 arquivos de pilar
  foram todos carregados (não apenas 1 ou 2).
- **Ele inventou um dado** -> reforce a instrução "nunca fabrique fatos,
  preços, nomes ou dados" e peça para usar `[fornecer: ...]`
  explicitamente.
- **Respondeu em inglês** -> reforce o campo `Idioma: pt-BR` das
  Instructions do Gem.
