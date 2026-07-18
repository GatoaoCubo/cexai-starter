# SETUP -- ChatGPT (Custom GPT e Projects) -- OAuth Connect

Setup do bundle `oauth_connect` no ChatGPT. Este bundle é um agente de
**produção de artefato único** (você descreve a integração, ele devolve UMA
configuração de app OAuth tipada) -- não depende de nenhuma Action, busca
web ou ferramenta externa para funcionar. Por isso o setup é idêntico em
qualquer plano: **Custom GPT** (ChatGPT Plus) ou **Projects** (funciona até
no plano free). ~5 minutos.

## Pré-requisitos

- Conta ChatGPT (o plano free já cobre a Opção B; Custom GPT exige Plus).
- ZERO chaves de API -- este bundle não usa Actions.

## Opção A -- Custom GPT (ChatGPT Plus)

### 1. Crie o Custom GPT

1. Acesse **chatgpt.com** -> **Explore GPTs** -> **Create** -> aba **Configure**.
2. Preencha os campos usando `customgpt_instructions.json` (abra o arquivo,
   cada chave mapeia direto para um campo da UI):
   - **Name** <- campo `name` (troque o placeholder `[fornecer: ...]` pelo
     nome real da sua marca antes de colar).
   - **Description** <- campo `description`.
   - **Instructions** <- campo `instructions` (cole o texto inteiro).
   - **Conversation starters** <- itens de `conversation_starters`.

### 2. Suba os 12 arquivos de Knowledge

Em **Knowledge**, suba os 12 arquivos de pilar deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 3. Capabilities -- deixe tudo DESLIGADO

Este agente não precisa de nenhuma capability nativa do ChatGPT: ele produz
a configuração OAuth só com raciocínio + o conhecimento dos 12 pilares.
Mantenha (igual ao bloco `capabilities` do JSON):

- Web Browsing: **desligado**
- Code Interpreter: **desligado**
- DALL-E: **desligado**

### 4. Salve e publique

Salve como privado (uso próprio) ou gere o link "Only me" / "Anyone with
the link", conforme sua necessidade.

## Opção B -- ChatGPT Projects (plano free)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `OAuth Connect ([sua marca])`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Instructions do projeto.

### 3. Suba os 12 arquivos de Files

Em **Files** do projeto, suba os mesmos 12 arquivos `P01_knowledge.md` ...
`P12_orchestration.md`.

### 4. Modelo

Qualquer modelo padrão serve -- não é necessário um modelo com web
search/browsing habilitado, porque este agente não busca nada na internet.

## Teste (funciona igual nas duas opções)

Inicie uma conversa:

> `Configurar uma conexão OAuth com o Bling para o nosso ERP: preciso de
> escopo de leitura e escrita de pedidos, redirect URI
> https://app.minhaempresa.com.br/callback/bling, e access token de 1 hora.`

O agente deve:
1. Confirmar (ou perguntar) `client_id`/`client_secret` -- se você não
   informou, ele emite `[fornecer: ...]` em vez de inventar.
2. Montar o array de `scopes` e o `redirect_uris`.
3. Aplicar as regras de P06/P07 (PKCE S256, tempo de vida de token dentro
   dos limites, `refresh_policy` válida).
4. Entregar o artefato `oauth_app_config` em YAML, pronto para colar no seu
   pipeline de configuração.

## Fidelidade declarada: FULL (nas duas opções)

| Motivo | Detalhe |
|--------|---------|
| Sem Actions no bundle | Este agente não tem TIER de coleta externa -- ele só raciocina sobre o `intent` que você descreve + os 12 pilares de conhecimento |
| Custom GPT e Projects entregam o mesmo resultado | A única diferença é a tela de configuração; nenhuma capability é perdida no plano free |
| 12/12 pilares presentes nas duas opções | Nenhum arquivo é cortado ou dobrado (ao contrário de bundles de pesquisa, que têm uma variante "enxuta") |

## Solução de problemas

- **"Ele inventou um client_id"** -> reforce o guardrail: "todo campo sem
  dado real vira `[fornecer: ...]`, nunca um valor inventado" (já está em
  P11_feedback.md e no `system_instruction.md`).
- **Quero as duas coisas (Custom GPT + Projects)** -> sim, pode ter as
  duas; elas não conflitam, só consomem os mesmos 12 arquivos duas vezes.
- **Custom GPT não aceita todos os 12 arquivos** -> o limite do ChatGPT é
  por número de arquivos de Knowledge (20) e por tamanho total; 12 arquivos
  de poucos KB cada ficam bem dentro do limite.
- **Quero validar o YAML gerado** -> cole a saída em qualquer validador
  YAML/JSON Schema; o schema formal está documentado em `P06_schema.md`.
