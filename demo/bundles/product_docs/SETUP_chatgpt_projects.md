# SETUP -- ChatGPT Projects

Setup do bundle `product_docs` no ChatGPT Projects (funciona no plano
free). Este bundle não usa Actions nem chaves de API -- é o formato CEXAI
"12 ISO": 12 arquivos de pilar (P01-P12) mais uma instrução para colar.
~5 minutos.

## Pré-requisitos

- Conta ChatGPT (o plano free é suficiente -- Projects não exige Plus).
- ZERO chaves de API necessárias (este agente não usa Actions nem
  ferramentas externas).

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome sugerido: `Product Docs -- [sua marca]`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Instructions do projeto.
4. Substitua os marcadores `[fornecer: ...]` pelos dados reais da sua marca
   (nome, tom de voz, valores) antes de usar em produção -- nunca deixe o
   agente adivinhar esses campos.

### 3. Suba os 12 arquivos de Knowledge

Em **Files** do projeto, suba os **12 arquivos** de pilar deste bundle:

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

Confirme que os 12 aparecem na lista de Files do projeto.

### 4. Capabilities

Nenhuma capability especial é necessária -- este agente não navega na web,
não executa código e não gera imagem. Ele trabalha 100% a partir dos 12
arquivos de conhecimento carregados e do que você descrever na conversa.

### 5. Teste

Inicie uma conversa dentro do project:

> `Documente a funcionalidade de exportação CSV do meu produto`

O agente deve:
1. Confirmar (ou assumir, se óbvio) qual produto/funcionalidade documentar.
2. Usar o que você já descreveu sobre features, setup e uso.
3. Produzir um knowledge_card estruturado (frontmatter completo + corpo
   denso, com tabelas e bullets, seguindo os 12 pilares carregados).
4. Nunca inventar dado que você não forneceu -- em vez disso, marcar
   `[A CONFIRMAR]` ou `[fornecer: ...]`.

## Fidelidade declarada: FULL

| Motivo | Detalhe |
|-------|---------|
| Sem Actions no escopo deste agente | O bundle não depende de ferramentas externas -- é um contrato de conhecimento + instrução |
| ChatGPT Projects cobre 100% do que o bundle precisa | Instructions + Knowledge files e tudo que este agente usa |
| Nenhuma funcionalidade é perdida no plano free | Diferente de bundles de pesquisa com Actions, aqui não existe "tier 3" a perder |

## Upgrade path para Custom GPT

Um Custom GPT (ChatGPT Plus) funciona de forma idêntica, com duas
vantagens: um nome/ícone próprios e a possibilidade de publicar ou
compartilhar como GPT. Se quiser essa rota:

1. **Explore GPTs** -> **Create** -> **Configure**.
2. Cole o campo `instructions` de `customgpt_instructions.json` (e o
   mesmo texto de `system_instruction.md`, já empacotado para o campo
   Instructions do Custom GPT).
3. Suba os mesmos 12 arquivos como Knowledge.
4. Use o `conversation_starters` de `customgpt_instructions.json` como
   sugestão de conversa inicial.

O Project no plano free continua funcionando em paralelo.

## Solução de problemas

- **"Ele inventou uma funcionalidade que eu não descrevi"** -> reforce nas
  Instructions: "nunca fabrique fatos, preços, nomes ou dados; onde faltar
  informação, emita `[fornecer: ...]`" (já está no `system_instruction.md`,
  mas reforçar ajuda em sessões longas).
- **O agente respondeu em inglês** -> lembre-o do campo `Idioma: pt-BR` das
  instructions; peça explicitamente para responder em português.
- **Faltou tabela ou estrutura no knowledge_card gerado** -> aponte para os
  pilares P05 (template de saída) e P06 (schema) carregados como Knowledge
  e peça para seguir a estrutura exata.
- **Quero publicar como um GPT próprio** -> veja "Upgrade path" acima.
