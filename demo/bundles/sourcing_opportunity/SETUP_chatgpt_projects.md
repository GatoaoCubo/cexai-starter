# SETUP -- ChatGPT (Custom GPT e Projects)

Setup do bundle `sourcing_opportunity` (Sourcing Opportunity Matrix) no ChatGPT. Este bundle é só
Knowledge + instrução -- sem Actions, sem chave de API, sem tier de fidelidade parcial. Os dois
caminhos abaixo (Custom GPT ou Projects) entregam exatamente a mesma capacidade. ~5 minutos.

## Pré-requisitos

- Conta ChatGPT (o plano free já é suficiente para Projects; Custom GPT com publicação exige
  ChatGPT Plus, mas testar em modo privado funciona no free também).
- ZERO chaves de API necessárias -- este bundle não tem nenhuma Action.

## Opção A -- Custom GPT (recomendado se você quer publicar/compartilhar)

### 1. Crie o Custom GPT

1. Acesse **chatgpt.com** -> menu lateral -> **Explore GPTs** -> **+ Create**.
2. Vá na aba **Configure**.
3. **Name**: cole o campo `name` de `customgpt_instructions.json` (substitua o placeholder
   `[fornecer: nome da marca ...]` pelo nome real da sua marca).
4. **Description**: cole o campo `description` de `customgpt_instructions.json`.

### 2. Cole as Instructions

1. Abra `customgpt_instructions.json` deste bundle.
2. Copie todo o conteúdo do campo `instructions` (a string já vem pronta para colar, com quebras
   de linha).
3. Cole no campo **Instructions** do Custom GPT.

### 3. Suba os 12 arquivos de Knowledge

1. Clique em **Upload files**.
2. Suba os **12 arquivos** `P01_knowledge.md` até `P12_orchestration.md`.
3. Confirme que os 12 aparecem na lista (Custom GPT permite até 20 arquivos por GPT -- 12 fica
   bem dentro do limite).

### 4. Capabilities

Marque conforme a tabela abaixo (nenhuma delas é necessária para este bundle funcionar; o
gerador real roda offline-determinístico por design, ver `P01_knowledge.md`):

| Capability | Recomendação |
|---|---|
| Web Browsing | Opcional -- útil se você quiser que o agente ajude a interpretar preços de mercado que você mesmo colar na conversa; não é usado pelo contrato do opportunity_matrix em si |
| Code Interpreter | Opcional -- útil se você quiser consolidar várias matrizes de oportunidade numa planilha |
| DALL-E | Desligado -- não usado por este agente |

### 5. Conversation starters

Adicione a sugestão do campo `conversation_starters` de `customgpt_instructions.json`:

- `Encontrar os melhores produtos para sourcing a partir de <catálogo de fornecedor> -- custo vs margem de mercado`

### 6. Salvar + publicar

1. Clique em **Create/Update**.
2. Escolha a visibilidade: **Only me** (privado, recomendado para testar), **Anyone with a
   link**, ou **Public**.

## Opção B -- ChatGPT Projects (mais rápido para uso pessoal)

Projects não tem o campo de Actions nem os campos extras de metadata do Custom GPT -- mas como
este bundle não usa nenhum dos dois, a fidelidade é a mesma.

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Sourcing Opportunity Matrix`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o conteúdo de `system_instruction.md`.
3. Cole nas Instructions do projeto.

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os **12 arquivos** `P01_knowledge.md` até `P12_orchestration.md`.

### 4. Teste

Inicie uma conversa dentro do projeto:

> `Tenho um catálogo de fornecedor com custo por SKU (coluna "custo_unitario") e quero saber quais
> produtos valem a pena trazer, cruzando contra preço e demanda de mercado. Como funciona o
> contrato de entrada e quais seções você entrega?`

O agente deve:
1. Explicar o contrato de entrada de 9 campos (catalog_sources, cost_source_strategy, tax_pct,
   region, demand_signal_basis, fee_model, freight_model, verify_top_n, show_net_margin) sem
   inventar campos.
2. Deixar claro que EAN/GTIN/código de barras são excluídos por design como chave de join entre
   marketplaces (todo revendedor recodifica esses valores).
3. Entregar as 8 seções de saída na ordem correta: Resumo executivo, Matriz de oportunidade,
   Leitura por categoria, Cobertura, Verificacao (top-N), Match / auditoria, Proveniencia,
   Veredito + proximos passos.
4. Nunca fabricar um preço de mercado ou nível de demanda -- sem uma credencial de dados de
   demanda ao vivo, toda célula de mercado/demanda deve renderizar honestamente `"nao pesquisado"`
   e o gate `sourcing_confiavel` fica BLOQUEADO.

## Fidelidade declarada: FULL (nas duas opções)

| Por quê | Detalhe |
|---|---|
| Sem Actions no contrato | O bundle inteiro é Knowledge + instrução; nenhuma capacidade depende de ferramenta externa |
| O gerador real já é offline-honest-null por design | Sem credencial de demanda ao vivo, o próprio gerador `sourcing_opportunity.py` renderiza honest-null -- Custom GPT e Projects reproduzem o mesmo comportamento honesto, sem degradar nada |
| Custom GPT e Projects sobem os mesmos 12 arquivos | Nenhum pillar fica de fora em nenhuma das duas opções |

## Solução de problemas

- **"Ele inventou um preço de mercado ou nível de demanda"** -> reforce: "sem uma credencial de
  demanda ao vivo, toda célula de mercado/demanda é honest-null (`nao pesquisado`) -- nunca
  invente um valor" (ver `P01_knowledge.md`, Armadilhas).
- **"Ele reordenou ou renomeou as 8 seções de saída"** -> reforce: "a ordem Resumo executivo ->
  Matriz de oportunidade -> Leitura por categoria -> Cobertura -> Verificacao (top-N) -> Match /
  auditoria -> Proveniencia -> Veredito + proximos passos é congelada; nunca reordene, renomeie,
  ou troque o layout" (ver `P06_schema.md` e `P09_config.md`).
- **"Ele tratou EAN/GTIN/código de barras como chave de join"** -> reforce: "esses campos são
  estruturalmente excluídos -- todo revendedor os recodifica" (ver `P01_knowledge.md` e
  `P02_model.md`).
- **"Ele declarou sourcing_confiavel sem as 4 condições"** -> reforce: "o gate precisa das 4
  condições explicitadas (margem_bruta_top >= 25%, top-N verificado, nenhum item crítico sem
  preço, frescor != RED), não só o valor true/false" (ver `P05_output.md` e `P07_evals.md`).
- **Custom GPT recusou publicar** -> confira se você está numa conta ChatGPT Plus; sem Plus,
  use a Opção B (Projects) ou mantenha o Custom GPT como **Only me**.
