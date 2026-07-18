# SETUP -- Claude Projects -- OAuth Connect

Setup do bundle `oauth_connect` em Claude Projects. Como este agente não usa
nenhuma ferramenta externa (nenhuma Action, nenhum MCP, nenhuma busca web --
ele só precisa do texto da sua solicitação + os 12 pilares de conhecimento),
o setup é o mais simples dos quatro runtimes: colar as instructions + subir
os 12 arquivos. ~5 minutos.

## Pré-requisitos

- Conta Claude com Projects habilitado (Pro ou Team; o plano Free do
  Claude.ai não tem Projects).
- ZERO chaves de API, ZERO MCP server -- não há nada para conectar.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `OAuth Connect ([sua marca])`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho total
de conhecimento do projeto, e 12 arquivos de poucos KB cada ficam bem
abaixo dele).

### 4. Nenhum wiring adicional é necessário

Ao contrário de bundles que dependem de dados ao vivo (preço de mercado,
resultado de busca, etc.), o `oauth_connect` **não precisa de MCP server,
Action ou qualquer tool externa**. Ele produz a configuração OAuth
inteiramente a partir do que você descreve na conversa + do conhecimento de
domínio OAuth2/PKCE/OpenID Connect que já vem nos 12 arquivos. Se algum
outro bundle seu usar MCP, essa etapa fica isolada por Project -- não
interfere aqui.

### 5. Teste

Em uma conversa do Project:

> `Configurar uma conexão OAuth com o Bling para o nosso ERP: preciso de
> escopo de leitura e escrita de pedidos, redirect URI
> https://app.minhaempresa.com.br/callback/bling, e access token de 1 hora.`

O agente deve:
1. Aplicar as regras do P02 (identidade do builder) e P03 (processo passo a
   passo: pesquisa -> composição -> validação).
2. Perguntar ou marcar `[fornecer: ...]` para qualquer dado que você não
   informou (nunca inventa `client_id`/`client_secret`).
3. Validar contra os HARD gates de P07 (PKCE obrigatório, tempo de vida de
   token dentro do limite, `refresh_policy` do tipo `rotating`).
4. Entregar o artefato `oauth_app_config` em YAML.

## Fidelidade declarada: FULL

Não há tiers, não há Actions, não há graceful degradation a documentar --
o comportamento em Claude Projects é idêntico ao de qualquer outro runtime
deste bundle, porque a capacidade inteira vive no par
instructions + knowledge, não em ferramentas externas.

## Vantagens do Claude Projects para este bundle

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|------------------|
| Limite de arquivos de Knowledge | 20 arquivos | sem limite por arquivo (limite é por tamanho total) |
| Context window | 128K | 200K |
| Setup de ferramenta externa | Nenhum (não aplicável) | Nenhum (não aplicável) |
| Custo | Plus ($20/mês) | Pro ($20/mês) |

## Solução de problemas

- **"Ele inventou um redirect_uri"** -> reforce o guardrail (P11 +
  `system_instruction.md`): sem dado real, o campo vira `[fornecer: ...]`.
- **Quero anexar meus próprios exemplos de config OAuth** -> pode subir
  arquivos adicionais de Knowledge no mesmo Project; o agente vai priorizar
  os 12 pilares como fonte de verdade estrutural, mas pode referenciar seus
  exemplos para tom/formato.
- **O agente confundiu OAuth com SSO** -> aponte para P02 (Boundary): este
  builder é explicitamente proibido de tratar SSO/workforce (isso é um
  agente separado); reforce a pergunta com "isto é app OAuth de terceiro,
  não SSO corporativo".
- **Quero validar o YAML de saída** -> o schema formal está em
  `P06_schema.md` (campos obrigatórios + ID Pattern).
