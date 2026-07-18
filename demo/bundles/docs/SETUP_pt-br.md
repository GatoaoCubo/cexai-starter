# SETUP -- Conhecimento e Documentacao (docs) -- guia combinado PT-BR

Guia geral do bundle. Para o passo a passo detalhado por plataforma, veja os
arquivos especificos:

- **ChatGPT** (Custom GPT ou Projects) -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> Este bundle nao depende de nenhuma Action, chave de API, plugin ou MCP --
> funciona 100% via upload de arquivos (Knowledge) + colar um texto de
> instrucoes. Qualquer IA que aceite arquivos de contexto e um system
> prompt/instructions consegue rodar este agente.

## O que este bundle produz

Este e o contrato completo (12 pillars = 12 ISOs) do kind `knowledge_card`
da arquitetura CEXAI (nucleus N04, pillar P01, verbo document). Ao subir os
arquivos deste bundle em qualquer IA, ela se torna um agente de
"Conhecimento e Documentacao": voce descreve um assunto (uma politica, um
processo, um fato do seu produto) e o agente devolve um artefato
`knowledge_card` -- um fato atomico, pesquisavel, com frontmatter
estruturado e densidade minima de 0.80 -- pronto para alimentar um sistema
de RAG ou uma base de documentacao.

## Arquivos do bundle (overview)

```
docs/
  P01_knowledge.md ... P12_orchestration.md   <- os 12 pillars (12 ISOs) do kind knowledge_card
  system_instruction.md                        <- system prompt pronto para colar (Claude / Gemini / qualquer IA)
  customgpt_instructions.json                  <- config do Custom GPT (name, description, instructions, conversation_starters)
  README.md                                    <- visao geral + passo a passo resumido
  SETUP_chatgpt_projects.md                    <- setup detalhado ChatGPT (Custom GPT + Projects)
  SETUP_claude_projects.md                     <- setup detalhado Claude Projects
  SETUP_gemini_gems.md                         <- setup detalhado Gemini Gems
  SETUP_pt-br.md                               <- este arquivo (guia combinado)
```

## Opcao A -- ChatGPT

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo. Resumo:
1. **Custom GPT** (Plus): cole o campo `instructions` de
   `customgpt_instructions.json` nas Instructions, suba os 12 arquivos P0X
   como Knowledge.
2. **Projects** (qualquer plano): cole `system_instruction.md` nas
   Instructions do projeto, suba os 12 arquivos P0X como Files.
3. Nenhuma chave de API, nenhuma Action.

## Opcao B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo. Resumo:
1. Crie um Project.
2. Cole `system_instruction.md` nas Custom Instructions.
3. Suba os 12 arquivos P0X como Project Knowledge.

## Opcao C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo. Resumo:
1. Crie um Gem.
2. Cole `system_instruction.md` nas Instructions.
3. Suba os 12 arquivos P0X como Knowledge.

## Opcao D -- qualquer outra IA

Qualquer assistente que aceite (a) um texto de system prompt/instructions e
(b) arquivos de contexto funciona: cole `system_instruction.md` como prompt
de sistema e injete os 12 arquivos P0X como contexto (upload, RAG, ou
colados diretamente na conversa).

## Comparativo rapido

| Capability | Custom GPT | ChatGPT Projects | Claude Projects | Gemini Gems |
|------------|-----------|-------------------|------------------|-------------|
| Upload de Knowledge | ate 20 arquivos | Files (sem limite fixo divulgado) | sem limite fixo por arquivo | Knowledge (limite de tamanho varia) |
| Chave de API exigida | Nenhuma | Nenhuma | Nenhuma | Nenhuma |
| Plano minimo | Plus | Free | Free/Pro | Conta Google |
| Nome + descricao publicos | SIM (name/description) | NAO (privado ao workspace) | NAO (privado ao Project) | SIM (name/description) |

## Antes de publicar -- preencha os placeholders

Este bundle sai de fabrica generico, sem dado de nenhuma marca especifica.
Nos dois arquivos de instrucoes (`system_instruction.md` e
`customgpt_instructions.json`), troque:

- `[fornecer: nome da marca (brand_config.identity.BRAND_NAME)]` -> o nome
  real da sua empresa/produto.
- `[fornecer: tom de voz da marca (nao configurado)]` -> como sua marca fala
  (ex.: "direto e tecnico", "caloroso e consultivo").
- `[fornecer: valores da marca]` -> os valores que devem guiar o tom do
  agente (ex.: "transparencia, precisao, respeito ao tempo do cliente").

Nunca deixe o agente "adivinhar" esses campos -- a regra de honestidade do
proprio agente (secao REGRAS DE PROTECAO de `system_instruction.md`) e
nunca fabricar fatos, precos, nomes ou dados quando o campo nao foi
preenchido.

## Como usar (fluxo tipico, qualquer plataforma)

1. Descreva o assunto: `Documentar a politica de trocas como knowledge_card`
   (ou em linguagem livre: "quero registrar como funciona nosso frete
   gratis").
2. O agente confirma o topico e pede o material-fonte, se ainda nao foi
   dado (documentacao oficial, uma URL, ou o conhecimento que voce mesmo
   descrever).
3. Ele classifica o card como `domain_kc` (conhecimento externo) ou
   `meta_kc` (conhecimento interno da sua propria operacao) -- ver
   `P09_config.md` -> "Selecao do Tipo de KC".
4. Ele entrega o artefato `knowledge_card` completo: frontmatter YAML (14
   campos obrigatorios + 5 estendidos) + corpo estruturado (Referencia
   Rapida, Conceitos-Chave, Fases da Estrategia, Regras de Ouro, Fluxo,
   Comparativo, Referencias).
5. Voce revisa, preenche qualquer `[fornecer: ...]` remanescente, e salva o
   arquivo na sua base de conhecimento/RAG.

## Solucao de problemas

- **"A saida veio em ingles"** -> confirme que a linha "Idioma: pt-BR" (em
  `system_instruction.md`) sobreviveu na copia colada nas Instructions.
- **"Ele inventou um dado"** -> viola a secao REGRAS DE PROTECAO; cole o
  texto de instrucoes de novo, sem cortar aquela secao.
- **"Nao sei se e domain_kc ou meta_kc"** -> `domain_kc` e para
  conhecimento externo (uma API, uma ferramenta, um processo do mercado);
  `meta_kc` e para conhecimento interno da sua propria operacao/sistema --
  veja a tabela completa em `P09_config.md`.
- **"Quero outro tipo de artefato (nao knowledge_card)"** -> este bundle e
  especifico para o kind `knowledge_card`; a arquitetura CEXAI tem bundles
  equivalentes para outros kinds (agent, prompt_template, landing_page etc.).
- **"Os 12 arquivos parecem tecnicos demais"** -> sao o contrato interno
  (12 ISOs) que ensina a IA A CONSTRUIR um bom knowledge_card; voce nunca
  precisa le-los linha a linha, so subir todos os 12 juntos.
