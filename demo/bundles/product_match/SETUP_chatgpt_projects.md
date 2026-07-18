# SETUP -- ChatGPT (Custom GPT e Projects)

Setup do bundle `product_match` (Product Match + Catalog Audit) no ChatGPT. Este bundle é só
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

Marque conforme a tabela abaixo (nenhuma delas é necessária para este bundle funcionar; o motor
de match em si roda offline-honest-null por design, ver `P01_knowledge.md`):

| Capability | Recomendação |
|---|---|
| Web Browsing | Opcional -- não é usado pelo contrato do product_match |
| Code Interpreter | Opcional -- útil se você quiser consolidar várias auditorias em uma planilha |
| DALL-E | Desligado -- não usado por este agente |

### 5. Conversation starters

Adicione a sugestão do campo `conversation_starters` de `customgpt_instructions.json`:

- `Casar <itens do fornecedor> com anúncios de marketplace por foto + dimensão + código`

### 6. Salvar + publicar

1. Clique em **Create/Update**.
2. Escolha a visibilidade: **Only me** (privado, recomendado para testar), **Anyone with a
   link**, ou **Public**.

## Opção B -- ChatGPT Projects (mais rápido para uso pessoal)

Projects não tem o campo de Actions nem os campos extras de metadata do Custom GPT -- mas como
este bundle não usa nenhum dos dois, a fidelidade é a mesma.

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Product Match + Catalog Audit`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o conteúdo de `system_instruction.md`.
3. Cole nas Instructions do projeto.

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os **12 arquivos** `P01_knowledge.md` até `P12_orchestration.md`.

### 4. Teste

Inicie uma conversa dentro do projeto:

> `Quero casar um item do meu fornecedor (código SUP-4471, foto e dimensão informados) com um
> anúncio existente no Mercado Livre. Como funciona o contrato de match?`

O agente deve:
1. Explicar o contrato de entrada (items, match_join_keys, match_engine, match_confidence_floor,
   audit_enabled, audit_min_photo_px) sem inventar campos.
2. Deixar claro que EAN/GTIN/código de barras são excluídos por design (todo revendedor
   recodifica esses valores).
3. Entregar as 4 seções de saída na ordem correta: Resultado do match, Auditoria de catálogo,
   Proveniência, Veredito.
4. Nunca fabricar um match SIM/PARCIAL -- enquanto `match_engine=none` (o padrão), toda linha é
   um NAO honesto em confiança 0.0.

## Fidelidade declarada: FULL (nas duas opções)

| Por quê | Detalhe |
|---|---|
| Sem Actions no contrato | O bundle inteiro é Knowledge + instrução; nenhuma capacidade depende de ferramenta externa |
| O motor de match já é offline-honest-null por design | `match_engine=none` é o padrão real do gerador -- Custom GPT e Projects reproduzem o mesmo comportamento honesto, sem degradar nada |
| Custom GPT e Projects sobem os mesmos 12 arquivos | Nenhum pillar fica de fora em nenhuma das duas opções |

## Solução de problemas

- **"Ele inventou um resultado de match com confiança alta"** -> reforce: "enquanto
  match_engine=none, toda linha é NAO em confiança 0.0 -- nunca invente um SIM/PARCIAL" (ver
  `P01_knowledge.md`, Matriz de Status do Motor de Match).
- **"Ele reordenou as seções de saída"** -> reforce: "a ordem Resultado do match -> Auditoria de
  catálogo -> Proveniência -> Veredito é congelada; nunca reordene, renomeie, ou troque o
  layout" (ver `P06_schema.md` e `P09_config.md`).
- **"Ele tratou EAN/GTIN/código de barras como chave de join"** -> reforce: "esses campos são
  estruturalmente excluídos -- todo revendedor os recodifica" (ver `P09_config.md`).
- **Quero ativar de fato um motor de reverse-image/embedding/manual** -> hoje nenhum dos três
  tem implementação real (ver `P01_knowledge.md`, Matriz de Status do Motor de Match); este
  bundle documenta o contrato honestamente, não substitui o gerador real.
- **Custom GPT recusou publicar** -> confira se você está numa conta ChatGPT Plus; sem Plus,
  use a Opção B (Projects) ou mantenha o Custom GPT como **Only me**.
