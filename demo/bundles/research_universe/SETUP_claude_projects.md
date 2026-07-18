# SETUP -- Claude Projects

Setup do pacote **Universo de Pesquisa (Cérebro Multi-Fonte)** (CEXAI) em
Claude Projects. 12 arquivos de Knowledge + instrução colada -- sem MCP, sem
Actions, sem chaves de API. ~10 minutos.

## Pre-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- Nenhuma chave de API necessária.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome sugerido: `Universo de Pesquisa (Cérebro Multi-Fonte)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.
4. Substitua os marcadores `[fornecer: ...]` pelos dados reais da sua marca
   (nome, tom de voz, valores) antes de usar em produção. Deixados sem
   preencher, eles aparecem no output tal como estão -- de propósito, para
   nunca fabricar uma marca ou um tom que você não definiu.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem um limite de contagem de arquivos -- o limite é por
tamanho total do projeto (bem acima do que estes 12 arquivos ocupam juntos).

### 4. Teste

Em uma conversa do Project:

> `Pesquise [nome da empresa ou produto] -- firmografia, social, reputação, SEO e perguntas`

O agente deve:
1. Confirmar a semente e o tipo (produto, marca, CNPJ, empresa,
   palavra-chave ou `store:id`).
2. Pedir os dados que faltam (Claude não tem uma capability de Web Browsing
   equivalente ao ChatGPT dentro de Projects -- ele trabalha com o que você
   fornecer na conversa e com os 12 arquivos de Knowledge).
3. Estruturar as 6 trilhas (firmografia, sinal social, reputação,
   sentimento em PT, SEO, perguntas multi-perspectiva) em tabelas.
4. Marcar cada trilha sem dado real como `blocked` (fonte existe, não
   acessada) ou `skipped` (não se aplica a esta semente) -- nunca como `ok`
   sem fonte.

## Vantagens do Claude Projects para este pacote

| Aspecto | Detalhe |
|---------|---------|
| Limite de Knowledge | Sem limite por contagem de arquivo (só por tamanho total) -- os 12 arquivos cabem com folga |
| Context window | Até 200K tokens -- os 12 pilares + o histórico da conversa cabem sem pressão |
| Tabelas | Claude é forte em manter tabelas largas (as 6 trilhas + a Tabela de Status) legíveis e bem formatadas |
| Sem Actions | Este pacote não precisa de nenhuma -- toda a lógica está nos 12 arquivos + na instrução |

## Como o agente evita fabricar dados

Ver `P02_model.md`, `P06_schema.md`, `P07_evals.md` e `P11_feedback.md` para
o contrato completo. Resumo:
- Toda trilha `ok` exige fonte primária + data de acesso.
- `blocked` e `skipped` são rótulos distintos com causas diferentes -- o
  agente nunca troca um pelo outro.
- Sentimento em PT só aparece se há um trecho-fonte real por trás da
  classificação (vindo das trilhas Sinal Social ou Reputação).
- Sem dado real, o agente marca a trilha como `blocked` ou `skipped` --
  nunca adivinha.

## Solução de problemas

- **"Ele inventou um dado de firmografia ou reputação"** -> reforce: "toda
  trilha ok precisa de fonte com data de acesso; sem dado real, marque a
  trilha como blocked".
- **"Ele não lembra o que já combinamos na conversa"** -> Claude usa o
  contexto da conversa atual; para sessões longas, resuma o que já foi
  decidido (semente, tipo, trilhas priorizadas) no início de uma nova
  conversa dentro do mesmo Project.
- **Quero que ele pesquise a web** -> Claude Projects não tem Web Browsing
  nativo equivalente ao ChatGPT; cole os dados diretamente na conversa
  (print de app store, texto do Reclame Aqui, resultado de consulta de
  CNPJ) e o agente estrutura a partir daí.
- **Tabela ficou larga demais para ler** -> peça para o agente quebrar em
  tabelas menores (ex.: uma só de firmografia, outra só de sinal social).
