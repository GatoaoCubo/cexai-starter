# SETUP -- Gemini Gems

Setup do bundle CEXAI "Conhecimento e Documentacao" (capacidade `docs`, kind
`knowledge_card`) em Gemini Gems. ~5 minutos, sem chaves de API.

## Pre-requisitos

- Conta Google com acesso a **gemini.google.com** e a funcionalidade Gems
  habilitada.
- ZERO chaves de API necessarias -- este agente nao usa extensions nem
  ferramentas externas, so Knowledge + Instructions.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Va em **Gems** -> **+ Create new Gem**.
3. Nome: `Conhecimento e Documentacao ([sua marca])`.
4. Description: copie o campo `description` de `customgpt_instructions.json`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteudo.
3. Cole no campo **Instructions** do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos P0X deste bundle:
`P01_knowledge.md` ... `P12_orchestration.md`.

### 4. Extensions

Nenhuma extension precisa ser ativada (Google Search, url_context etc.) --
este agente nao depende de busca ao vivo. Ele produz o artefato
`knowledge_card` diretamente a partir do que voce descrever e do
material-fonte que voce colar na conversa.

### 5. Preencha os placeholders

Antes de usar, edite a copia colada de `system_instruction.md` e troque
cada `[fornecer: ...]` pelo dado real da sua marca. Lista completa em
`SETUP_pt-br.md`.

### 6. Teste

Em uma conversa do Gem:

> `Documentar nossa politica de garantia como knowledge_card`

O Gem deve:
1. Confirmar o assunto e pedir o material-fonte, se ainda nao foi colado.
2. Produzir o artefato `knowledge_card` completo, inteiramente em pt-BR.
3. Usar `[fornecer: ...]` para qualquer dado que nao foi informado -- nunca
   inventar.

## Vantagens e limitacoes

- **Context window grande**: os modelos Gemini recentes passam de 1M
  tokens -- folga para colar bastante material-fonte na mesma conversa.
- **Multi-modal nativo**: se o seu material-fonte for uma imagem (print de
  tela, diagrama, foto de documento), anexe a imagem e peca para o Gem
  extrair o conteudo antes de destilar o knowledge_card.
- **Sem Actions/MCP**: este bundle nao depende disso, entao nao ha perda de
  fidelidade aqui (diferente de bundles que dependem de ferramentas
  externas para coletar dados ao vivo).

## Solucao de problemas

- **"O Gem nao usou os arquivos de Knowledge"** -> confirme que os 12
  arquivos aparecem na lista de Knowledge do Gem, com upload processado e
  sem erro.
- **"A saida veio em ingles"** -> confirme que a linha "Idioma: pt-BR"
  sobreviveu na copia colada nas Instructions.
- **"Quero usar no app do Gemini (celular)"** -> Gems criados no site
  aparecem tambem no app; nenhuma configuracao extra e necessaria.
- **"Quero anexar uma imagem como fonte"** -> normal, o Gem e multi-modal;
  anexe a imagem na conversa e peca a extracao antes de gerar o card.
