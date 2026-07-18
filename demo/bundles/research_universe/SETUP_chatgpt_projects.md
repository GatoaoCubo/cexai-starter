# SETUP -- ChatGPT Projects

Setup do pacote **Universo de Pesquisa (Cérebro Multi-Fonte)** (CEXAI) no
ChatGPT Projects. Funciona no plano free (não precisa de ChatGPT Plus). 12
arquivos de Knowledge, zero Actions, zero chaves de API. ~5 minutos.

## Pre-requisitos

- Conta ChatGPT (plano free é suficiente -- Projects não exige Plus).
- ZERO chaves de API necessárias (este pacote não usa Actions externas).

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome sugerido: `Universo de Pesquisa (Cérebro Multi-Fonte)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o campo `instructions` de `customgpt_instructions.json` -- ou,
   alternativamente, todo o conteúdo de `system_instruction.md` (os dois
   são o mesmo texto; use o que for mais conveniente de copiar).
3. Cole nas Instructions do projeto.
4. Antes de usar, substitua os marcadores `[fornecer: ...]` pelos dados
   reais da sua marca (nome, tom de voz, valores). Um marcador deixado
   sem preencher aparece no output como `[fornecer: ...]` -- isso é
   intencional (o agente nunca fabrica o que você não informou).

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os **12 arquivos** deste bundle:

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

Não há Actions para configurar neste pacote. Recomendado:
- **Web Browsing** -- opcional. Útil se você quiser que o agente pesquise
  dados públicos da semente (CNPJ, página de loja de app, Reclame Aqui)
  durante a conversa. Sem Web Browsing, o agente depende inteiramente dos
  dados que você colar no chat -- o que é perfeitamente válido, só mais
  manual (e cada trilha sem dado fica honestamente marcada `blocked`, nunca
  inventada).
- **Code Interpreter** -- opcional, útil para consolidar várias trilhas
  numa única tabela ou calcular a fração de cobertura (`coverage_score`).

### 5. Teste

Inicie uma conversa dentro do project:

> `Pesquise [nome da empresa ou produto] -- firmografia, social, reputação, SEO e perguntas`

O agente deve:
1. Confirmar a semente e classificar o tipo (produto, marca, CNPJ, empresa,
   palavra-chave ou `store:id`).
2. Decidir quais das 6 trilhas se aplicam a este tipo de semente.
3. Pedir os dados que faltam -- ou usar Web Browsing (se habilitado) para
   buscar informações públicas.
4. Entregar o relatório com as 6 trilhas + a Tabela de Status por Trilha
   (`ok`/`blocked`/`skipped`, cada uma com motivo quando não for `ok`).

## Como o agente evita fabricar dados

Este é o comportamento mais importante do pacote (ver P06/P07/P11):
- Toda trilha `ok` precisa de uma fonte primária com data de acesso.
- `blocked` (fonte existe, não acessível agora) e `skipped` (não se aplica
  a esta semente) são rótulos DIFERENTES -- o agente nunca confunde os dois.
- Nenhum CNPJ, índice de reputação ou volume de busca aparece sem fonte
  citada -- sem dado real, a trilha correspondente fica `blocked` em vez de
  preenchida.

## Solução de problemas

- **"Ele inventou um CNPJ ou um índice de reputação"** -> reforce na
  conversa: "toda trilha ok precisa citar uma fonte com data de acesso; sem
  dado real, marque a trilha como blocked". Isso é um NUNCA explícito do
  builder (ver `P02_model.md` e `P11_feedback.md`).
- **"Ele marcou uma trilha como skipped quando deveria ser blocked"** ->
  peça para reclassificar: `skipped` = não se aplica a esta semente;
  `blocked` = a fonte existe mas não foi acessada agora.
- **Quero que ele pesquise a web sozinho** -> habilite a capability Web
  Browsing no passo 4.
- **Arquivo não aparece na lista de Files** -> reenvie; Projects as vezes
  demora alguns segundos para indexar arquivos grandes.
- **Quero um Custom GPT publicável em vez de um Project privado** -> use
  `customgpt_instructions.json` direto em Explore GPTs -> Create (ver
  `README.md`, seção Upload).
