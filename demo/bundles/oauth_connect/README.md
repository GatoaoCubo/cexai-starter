# Bundle CEXAI: OAuth Connect (`oauth_connect`)

O **contrato de 12 pilares** para a kind `oauth_app_config`, mais a config
de setup pronta para colar. Nucleus N03 . kind `oauth_app_config` . pillar P04.

Este é o formato "12 ISO" do CEXAI -- um arquivo de especificação por pilar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrução, e
ele vira um agente OAuth Connect funcional.

## O que este agente faz

Você descreve, em linguagem natural, a integração OAuth que precisa
configurar (provedor, escopos, redirect URI, política de refresh). O agente
devolve um artefato `oauth_app_config` tipado: slots de client id/secret
(nunca inventados -- viram `[fornecer: ...]` quando faltam), escopos,
redirect URIs e parâmetros de token endpoint, seguindo OAuth 2.0/2.1, PKCE
(RFC 7636) e OpenID Connect. Ele não depende de nenhuma Action, MCP ou busca
web -- toda a produção vem do que você descreve + do conhecimento de domínio
já embutido nos 12 pilares.

## Conteúdo (19 arquivos)

- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato do builder para esta kind: uma especificação por pilar, P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descrição,
  a string de `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução como system prompt pronto
  para colar (Claude Projects, Gemini Gems, ChatGPT Projects, ou qualquer
  outro modelo).
- `SETUP_chatgpt_projects.md` -- guia de setup para ChatGPT (Custom GPT e
  Projects).
- `SETUP_claude_projects.md` -- guia de setup para Claude Projects.
- `SETUP_gemini_gems.md` -- guia de setup para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado (visão geral + pointer para os 3 acima).
- `README.md` -- este arquivo.

## Upload passo a passo (em qualquer IA)

O padrão é o mesmo em qualquer assistente: **colar a instrução** + **subir
os 12 arquivos de pilar como conhecimento**. Nenhuma chave de API é
necessária -- este agente não usa Actions nem ferramentas externas.

1. **Escolha o runtime** e abra o guia específico:
   - ChatGPT (Custom GPT ou Projects) -> `SETUP_chatgpt_projects.md`
   - Claude (Project) -> `SETUP_claude_projects.md`
   - Gemini (Gem) -> `SETUP_gemini_gems.md`
   - Visão geral combinada -> `SETUP_pt-br.md`
2. **Cole a instrução**:
   - ChatGPT Custom GPT: cole o campo `instructions` de
     `customgpt_instructions.json` na caixa de Instructions.
   - Qualquer outro runtime (Claude, Gemini, ChatGPT Projects, ou qualquer
     outro modelo): cole o conteúdo inteiro de `system_instruction.md` como
     system prompt / Project Instructions / Gem Instructions.
3. **Suba os 12 arquivos de conhecimento**: `P01_knowledge.md` até
   `P12_orchestration.md`, como Knowledge (ChatGPT/Claude) ou como base de
   conhecimento do Gem (Gemini).
4. **Preencha os placeholders**: antes de usar, troque todo
   `[fornecer: ...]` pelos dados reais da sua marca/integração (nome da
   marca, tom de voz, valores). O que você não preencher, o agente mantém
   como placeholder explícito -- ele nunca inventa esses dados.
5. **Teste** com um pedido real, por exemplo:
   > `Configurar uma conexão OAuth com o Bling para o nosso ERP: preciso de
   > escopo de leitura e escrita de pedidos, redirect URI
   > https://app.minhaempresa.com.br/callback/bling, e access token de 1 hora.`

   O agente deve confirmar os campos que faltam, validar contra os HARD
   gates de `P07_evals.md` (PKCE obrigatório, tempo de vida de token dentro
   do limite, refresh policy `rotating`), e entregar o artefato
   `oauth_app_config` em YAML no formato de `P05_output.md`.

## Procedência / honestidade

Nunca-fabricar: qualquer marcador `[fornecer: ...]` é um campo sem dado real
-- preencha com a sua marca antes de usar. Os 12 ISOs de pilar são o
contrato de builder genérico e público para `oauth_app_config` -- sem dado
de nenhum tenant.
