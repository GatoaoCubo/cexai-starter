# SETUP -- Gemini Gems -- OAuth Connect

Setup do bundle `oauth_connect` em Gemini Gems. Mesma lógica dos outros
runtimes: como este agente não depende de nenhuma ferramenta externa, o Gem
funciona com fidelidade total só com Instructions + Knowledge. ~5 minutos.

## Pré-requisitos

- Conta Google + acesso a **gemini.google.com** com Gems habilitado.
- ZERO extensions obrigatórias -- Search/Code execution são opcionais e
  NÃO são necessárias para este agente funcionar.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `OAuth Connect ([sua marca])`.
4. Description: `Gera configuração tipada de app OAuth (client id/secret, escopos, redirect URIs, token endpoints) para integrações com terceiros.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Extensions -- nenhuma é necessária

Diferente de agentes que buscam dados ao vivo, o `oauth_connect` não precisa
de **Google Search** nem de **url_context**: toda a produção vem do que você
descreve na conversa mais o conhecimento OAuth2/PKCE/OpenID Connect já
incluído nos 12 pilares. Pode deixar as extensions desligadas.

### 5. Teste

Em uma conversa do Gem:

> `Configurar uma conexão OAuth com o Bling para o nosso ERP: preciso de
> escopo de leitura e escrita de pedidos, redirect URI
> https://app.minhaempresa.com.br/callback/bling, e access token de 1 hora.`

O Gem deve:
1. Seguir o processo de P03 (pesquisa dos requisitos -> composição dos
   campos -> validação contra o schema).
2. Perguntar ou marcar `[fornecer: ...]` para qualquer dado não informado
   (nunca inventa `client_id`/`client_secret`/`redirect_uri`).
3. Aplicar os HARD gates de P07 (PKCE, tempo de vida de token, refresh
   policy).
4. Entregar o artefato `oauth_app_config` em YAML.

## Fidelidade declarada: FULL

Sem tiers de coleta, sem Actions, sem graceful degradation: o
comportamento do Gem é idêntico ao dos demais runtimes deste bundle.

## Vantagens do Gemini para este bundle

- **Context window grande** (>1M tokens em modelos recentes) -- folga
  enorme para os 12 pilares + o histórico da conversa.
- **Multi-modal nativo**: se você quiser colar um print da tela de
  configuração do provedor (ex.: painel de developer do Bling/Mercado
  Pago) para o Gem conferir os campos, ele pode ler a imagem diretamente.

## Limitações

- **Sem Actions nativas**: não aplicável aqui -- este bundle nunca
  precisou de Actions.
- **MCP não suportado em Gems** (a partir de 2026-05; pode mudar) -- também
  não aplicável, pois este agente não usa MCP em nenhum runtime.

## Solução de problemas

- **"Ele inventou um client_secret"** -> reforce o guardrail de P11 +
  `system_instruction.md`: campo sem dado real vira `[fornecer: ...]`.
- **O Gem tentou usar Google Search para "procurar a API do provedor"** ->
  redirecione: ele deve pedir os dados direto a você (scopes, redirect URI,
  client id/secret), não inferir de uma busca externa.
- **Quero conferir o YAML final** -> o schema formal (campos obrigatórios,
  ID Pattern, restrições) está em `P06_schema.md`.
