# SETUP -- Claude Projects

Setup do pacote **Matriz de Benchmark de Concorrentes** (CEXAI) em Claude
Projects. 12 arquivos de Knowledge + instrução colada -- sem MCP, sem
Actions, sem chaves de API. ~10 minutos.

## Pré-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- Nenhuma chave de API necessária.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome sugerido: `Matriz de Benchmark de Concorrentes`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.
4. Substitua os marcadores `[fornecer: ...]` pelos dados reais da sua marca
   (nome, tom de voz, valores) antes de usar em produção. Deixados sem
   preencher, eles aparecem no output tal como estão -- de propósito,
   para nunca fabricar uma marca ou um tom que você não definiu.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem um limite de contagem de arquivos -- o limite é por
tamanho total do projeto (bem acima do que estes 12 arquivos ocupam juntos).

### 4. Teste

Em uma conversa do Project:

> `Comparar [meu produto] com [concorrente A] e [concorrente B] em preço, funcionalidades e posicionamento`

O agente deve:
1. Confirmar os concorrentes e as dimensões de comparação.
2. Pedir os dados que faltam (Claude não tem uma capability de Web Browsing
   equivalente ao ChatGPT dentro de Projects -- ele trabalha com o que
   você fornecer na conversa e com os 12 arquivos de Knowledge).
3. Estruturar a feature parity grid, o posicionamento Gartner MQ, o
   battle card e a comparação de preços em tabelas.
4. Marcar qualquer dado sem fonte como `[fornecer: ...]`.

## Vantagens do Claude Projects para este pacote

| Aspecto | Detalhe |
|---------|---------|
| Limite de Knowledge | Sem limite por contagem de arquivo (só por tamanho total) -- os 12 arquivos cabem com folga |
| Context window | Até 200K tokens -- os 12 pilares + o histórico da conversa cabem sem pressão |
| Tabelas | Claude é forte em manter tabelas largas (feature parity grid com vários concorrentes) legíveis e bem formatadas |
| Sem Actions | Este pacote não precisa de nenhuma -- toda a lógica está nos 12 arquivos + na instrução |

## Como o agente evita fabricar dados

Ver `P02_model.md`, `P06_schema.md`, `P07_evals.md` e `P11_feedback.md` para
o contrato completo. Resumo:
- Toda alegação competitiva exige fonte primária + data de acesso.
- Superlativos sem citação de analista são proibidos.
- Itens de roadmap sempre rotulados com trimestre e ano.
- Sem dado real, o agente emite `[fornecer: ...]` -- nunca adivinha.

## Solução de problemas

- **"Ele inventou um dado"** -> reforce: "toda alegação precisa de fonte
  com data de acesso; sem dado real, use [fornecer: ...]".
- **"Ele não lembra o que já combinamos na conversa"** -> Claude usa o
  contexto da conversa atual; para sessões longas, resuma o que já foi
  decidido (produto, concorrentes, dimensões) no início de uma nova
  conversa dentro do mesmo Project.
- **Quero que ele pesquise a web** -> Claude Projects não tem Web Browsing
  nativo equivalente ao ChatGPT; cole os dados do concorrente diretamente
  na conversa (copie da página do concorrente, por exemplo) e o agente
  estrutura a partir daí.
- **Tabela ficou larga demais para ler** -> peça para o agente quebrar em
  duas tabelas menores (ex.: uma só de preço, outra só de funcionalidades).
