# SETUP -- OAuth Connect -- guia combinado PT-BR

Guia geral do bundle `oauth_connect`. Para o passo a passo detalhado por
runtime, veja os arquivos específicos:

- **ChatGPT (Custom GPT e Projects)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `full` em qualquer runtime. Este agente produz UM artefato
> (a configuração de app OAuth) a partir do texto que você descreve + do
> conhecimento dos 12 pilares -- ele não depende de nenhuma Action, MCP ou
> busca web ao vivo, então não existe "versão enxuta" nem degradação entre
> plataformas ou planos (free vs. pago).

## O que este bundle faz

Você descreve, em linguagem natural, a integração OAuth que precisa (com
qual provedor, quais escopos, qual redirect URI, qual política de refresh).
O agente devolve um artefato `oauth_app_config` tipado e pronto para uso:
client id/secret (como slots -- nunca inventados), escopos, redirect URIs e
parâmetros de token endpoint, seguindo os padrões OAuth 2.0/2.1, PKCE
(RFC 7636) e OpenID Connect.

## Arquivos do bundle (15 no total)

```
oauth_connect/
  P01_knowledge.md ... P12_orchestration.md   <- os 12 pilares (P01-P12):
                                                  o contrato completo do
                                                  builder para a kind
                                                  oauth_app_config
  customgpt_instructions.json                  <- config pronta para Custom
                                                  GPT (name/description/
                                                  instructions/conversation
                                                  starters)
  system_instruction.md                        <- a mesma instrução, como
                                                  system prompt pronto para
                                                  colar (Claude Projects,
                                                  Gemini Gems, ChatGPT
                                                  Projects, ou qualquer
                                                  outro modelo)
  README.md                                    <- visão geral + passo a
                                                  passo de upload
  SETUP_*.md                                   <- este arquivo + os 3
                                                  guias específicos por
                                                  runtime
```

## Os 12 pilares -- o que cada um cobre

| Pilar | Cobre |
|-------|-------|
| P01 knowledge | Visão geral do domínio OAuth2/PKCE, conceitos-chave (scopes, redirect URIs, token lifetime, PKCE), RFCs, padrões e armadilhas comuns |
| P02 model | Identidade do builder: especialização, capacidades, roteamento e regras SEMPRE/NUNCA |
| P03 prompt | Processo passo a passo: pesquisa dos requisitos -> composição dos campos -> checklist de validação |
| P04 tools | Ferramentas de produção e validação de referência + links externos (OAuthlib, OpenID Connect) |
| P05 output | Template YAML exato do artefato final, com a tabela de campos e um exemplo de comando CLI |
| P06 schema | Schema formal -- campos obrigatórios/recomendados, ID Pattern, estrutura do corpo, restrições |
| P07 evals | Quality gate: 10 HARD gates (H01-H10), 7 dimensões de pontuação SOFT, exemplo golden + 2 anti-exemplos |
| P08 architecture | Mapa de componentes e dependências; posição arquitetural do oauth_app_config |
| P09 config | Convenção de nomenclatura, caminhos de saída, limites de tamanho e casos de borda |
| P10 memory | Padrões aprendidos (evidência de 15 configurações revisadas) e recomendações |
| P11 feedback | 6 anti-padrões NUNCA, 4 modos de falha comuns, protocolo de correção em 3 passos |
| P12 orchestration | Papel do agente em uma crew: o que recebe, o que produz, e a fronteira com SSO/segredos |

## Como usar (fluxo típico, em qualquer runtime)

1. Descreva a integração: `Configurar uma conexão OAuth com o Bling para o
   nosso ERP: preciso de escopo de leitura e escrita de pedidos, redirect
   URI https://app.minhaempresa.com.br/callback/bling, e access token de
   1 hora.`
2. O agente confirma (ou pergunta) os campos que faltam: `client_id`,
   `client_secret`, `redirect_uris`, `scopes`, tempo de vida do token,
   política de refresh.
3. Ele valida contra os HARD gates de P07 (PKCE S256 obrigatório para o
   fluxo authorization_code, tempo de vida de access token <= 3600s,
   refresh_policy do tipo `rotating`, grant_types restritos a
   authorization_code/client_credentials/refresh_token -- nunca
   implicit/ROPC).
4. Entrega o artefato `oauth_app_config` em YAML, seguindo exatamente o
   template de `P05_output.md`.
5. Qualquer campo sem dado real vem marcado `[fornecer: ...]` -- nunca
   inventado.

## Regras inquebráveis (detalhe em P02 + P07 + P11)

1. **NUNCA** invente `client_id`, `client_secret`, `redirect_uri` ou
   qualquer outro dado sensível -- campo sem informação real vira
   `[fornecer: ...]`.
2. **NUNCA** trate SSO (identidade corporativa/workforce) ou armazenamento
   de credenciais brutas -- isso é escopo de outro agente (`sso_config`,
   `secret_config`).
3. **SEMPRE** exija HTTPS nos redirect URIs; nunca aceite `http://` sem
   marcar como violação.
4. **SEMPRE** aplique PKCE (S256) para o fluxo authorization_code.
5. **SEMPRE** limite o tempo de vida do access token e use `refresh_policy`
   do tipo `rotating` (nunca refresh token estático e reutilizável).
6. **NUNCA** publique a configuração final sem passar pelos 10 HARD gates
   de `P07_evals.md`.

## Solução de problemas (comum aos 3 runtimes)

- **"Ele inventou um client_secret"** -> P02/P07/P11 proíbem. Reforce:
  "todo campo sem dado real vira `[fornecer: ...]`, nunca um valor
  inventado".
- **"Ele confundiu OAuth com SSO"** -> aponte para o Boundary de P12/P02:
  este builder é explicitamente proibido de tratar SSO/workforce.
- **"Aceitou um redirect_uri em HTTP"** -> isso viola H05/P07; reforce que
  redirect URIs devem ser HTTPS e corresponder a domínios registrados.
- **Quero validar o YAML final** -> o schema formal (campos, ID Pattern,
  restrições) está em `P06_schema.md`; use qualquer validador YAML/JSON
  Schema externo se quiser uma checagem automatizada.
- **Qual runtime escolher?** -> os 3 têm fidelidade `full` idêntica; escolha
  pelo ecossistema que você já usa (ChatGPT, Claude ou Gemini). Veja o guia
  específico de cada um para o passo a passo de upload.

## Diferença para bundles de pesquisa/coleta de dados

Se você já configurou outro bundle CEXAI que coleta dados de mercado (ex.:
pesquisa de concorrentes), vai notar que este bundle é mais simples: não há
tiers de coleta (paste/browsing/actions), não há chaves de API, não há MCP
para conectar. O `oauth_connect` é um agente de **produção de artefato
único** -- toda a inteligência vem do conhecimento de domínio OAuth já
embutido nos 12 pilares, aplicado ao que você descreve na conversa.
