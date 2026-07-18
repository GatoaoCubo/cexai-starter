# SETUP -- Claude Projects

Setup do bundle `product_docs` em Claude Projects. Como o agente não
depende de nenhuma ferramenta externa (sem Actions, sem MCP), o setup é
apenas Instructions + Knowledge. ~10 minutos.

## Pré-requisitos

- Conta Claude com Projects habilitado (Free, Pro ou Team).
- ZERO chaves de API ou servidores MCP necessários -- este agente não usa
  ferramentas externas.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome sugerido: `Product Docs -- [sua marca]`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.
4. Substitua os marcadores `[fornecer: ...]` pelos dados reais da sua marca
   antes de usar em produção.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos de pilar deste bundle:

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

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho
total, ~30MB) -- os 12 arquivos deste bundle cabem com folga.

### 4. Nenhuma configuração adicional

Diferente de bundles de pesquisa com scraping, este agente não precisa de
MCP bridges, Actions ou chaves de API -- ele produz o knowledge_card a
partir do que você descrever na conversa mais os 12 pilares carregados
como Knowledge.

### 5. Teste

Em uma conversa do Project:

> `Documente a funcionalidade de exportação CSV do meu produto`

O agente deve:
1. Usar o que você descreveu sobre a funcionalidade.
2. Produzir um knowledge_card estruturado (frontmatter completo + corpo
   denso, com tabelas e bullets).
3. Marcar `[fornecer: ...]` ou `[A CONFIRMAR]` em qualquer campo sem dado
   real -- nunca inventar.

## Fidelidade declarada: FULL

Como o agente não depende de nenhuma Action ou ferramenta externa, Claude
Projects entrega 100% da capacidade do bundle -- não há "tier" perdido
como em bundles que usam scraping/pesquisa via Actions.

## Vantagens do Claude Projects

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|----------------|
| Context window | 128K | 200K |
| Limite de Knowledge | 20 arquivos | sem limite por arquivo (limite total ~30MB) |
| Custo | Plus ($20/mês) | Pro ($20/mês) |
| O que este bundle exige | Instructions + Knowledge | Instructions + Knowledge (idêntico) |

## Solução de problemas

- **O agente está vago ou genérico** -> confirme que os 12 arquivos
  `P0X_*.md` foram todos carregados como Knowledge (não apenas o
  `system_instruction.md`).
- **Ele inventou um dado que eu não dei** -> reforce a salvaguarda "nunca
  fabrique" presente nas Project Instructions.
- **Quero reusar este agente em outro projeto** -> basta copiar
  `system_instruction.md` mais os 12 `P0X_*.md` para o novo Project; não
  há nada tenant-specific além dos marcadores `[fornecer: ...]`.
- **Respondeu em inglês** -> reforce o campo `Idioma: pt-BR` das
  instructions.
