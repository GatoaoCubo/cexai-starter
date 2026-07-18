# SETUP -- Claude Projects

Setup do bundle CEXAI `ads` (Ads and Copy) em Claude Projects. Este bundle
não precisa de MCP nem de tools externas -- é um agente de geração de texto
puro. ~5 minutos.

## Pré-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO chaves de API ou MCP servers necessários.
- Os 15 arquivos do núcleo deste bundle baixados em uma pasta local.

## Passo a passo

### 1. Crie o Project

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Ads and Copy`.

### 2. Cole as Custom Instructions

1. Abra o projeto -> **Project knowledge** / **Custom instructions** (no
   painel lateral do projeto).
2. Copie TODO o conteúdo de `system_instruction.md`.
3. Cole nas Custom instructions do projeto.
4. Substitua os marcadores `[fornecer: ...]` (nome da marca, tom de voz,
   valores) pelos dados reais da sua marca.

### 3. Suba os 12 arquivos de Knowledge

Em **Project knowledge**, anexe os 12 arquivos de pilar:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite por contagem de arquivo (o limite é por
tamanho total do projeto), então você também pode anexar `README.md` e
`customgpt_instructions.json` como referência extra, se quiser.

### 4. Teste

Em uma conversa dentro do projeto:

> Escreva a copy de anúncio para tênis de corrida visando corredores
> iniciantes de 25-40 anos

Claude deve responder com um artefato `prompt_template` (hooks, CTAs e
variantes por tamanho de plataforma) na voz de marca configurada, sem
inventar dados que não foram fornecidos.

## Vantagens do Claude Projects para este bundle

| Aspecto | Detalhe |
|---------|---------|
| Context window | 200K tokens -- os 12 arquivos de pilar cabem com folga |
| Project knowledge | Sem limite por contagem de arquivo (limite é por tamanho total) |
| Sem Actions/MCP | Este bundle não precisa de nenhuma ferramenta externa |

## Solução de problemas

- **Claude inventa nome de marca, tom ou valores** -> reforce nas Custom
  instructions: "NUNCA fabrique fatos; use [fornecer: ...] quando faltar dado".
- **A saída não parece um `prompt_template`** -> confirme que os 12 arquivos
  P0X estão em Project knowledge (Claude usa `P03_prompt.md` +
  `P05_output.md` + `P06_schema.md` para saber o formato esperado).
- **Quero usar em uma conversa avulsa (sem Project)** -> cole o conteúdo de
  `system_instruction.md` diretamente como a primeira mensagem, ou use o
  campo de system prompt se estiver usando a API.
