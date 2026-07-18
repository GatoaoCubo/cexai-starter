# SETUP -- ChatGPT Projects

Setup do bundle `leadgen` (Captação de Leads) em ChatGPT Projects. Esta
variante usa os mesmos 12 arquivos de pillar do Custom GPT -- o bundle
`leadgen` não depende de nenhuma Action/API externa, então nada de
capacidade é perdido ao usar Projects em vez de um Custom GPT publicado.
~5 minutos.

## Pré-requisitos

- Conta ChatGPT (o plano free já é suficiente para Projects).
- ZERO chaves de API necessárias (este bundle não usa Actions).

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome sugerido: `Captação de Leads (leadgen)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie todo o conteúdo de `system_instruction.md` deste bundle (ou o
   campo `instructions` de `customgpt_instructions.json`).
3. Cole nas Instructions do projeto.
4. Substitua os marcadores `[fornecer: ...]` pelo nome, tom de voz e
   valores reais da sua marca.

### 3. Suba os 12 arquivos de Knowledge

Em **Files** do projeto, suba os 12 arquivos de pillar deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Projects não tem limite de 20 arquivos (o limite é por tamanho total), então
os 12 arquivos cabem sem problema.

### 4. Capabilities

Este bundle não usa Actions, então não há nada para configurar além do
modelo em si:

- Se quiser que o agente tente localizar leads na web diretamente, escolha
  um modelo com **web search / browsing** habilitado.
- **Code interpreter** é opcional, útil apenas se você for consolidar
  listas grandes de leads coladas manualmente.

### 5. Teste

Inicie uma conversa dentro do project:

> `Encontre leads para dentistas em Curitiba a partir de "clínica odontológica" -- marketplace, CNPJ, social`

O agente deve:
1. Confirmar o perfil e a seed informados.
2. Percorrer os canais disponíveis (marketplace B2C, CNPJ B2B, social UGC)
   e declarar o status real de cada um (ok / bloqueado / pulado) -- nunca
   inventando um contato.
3. Entregar uma lista tipada de leads e um veredito de avançar ou não
   (go/no-go).

## Fidelidade declarada: FULL

| Motivo | Detalhe |
|-------|---------|
| Sem Actions no bundle | O `leadgen` não depende de nenhuma API externa configurada via Action |
| Os mesmos 12 arquivos do Custom GPT | Knowledge idêntica entre Projects e Custom GPT |
| Única diferença real | Se o modelo escolhido tem ou não web search/browsing habilitado |

## Como usar (fluxo típico)

1. Diga o perfil e a seed: `Encontre leads para <perfil> a partir de <seed>`.
2. O agente confirma o perfil, a seed e os canais que vai percorrer.
3. Para canais que o modelo consegue alcançar (web search ligado), ele
   busca e retorna dados reais, sempre citando a origem.
4. Para canais que exigem acesso que o modelo não tem (ex.: CNPJ em bases
   pagas, redes sociais autenticadas), ele marca o status como `bloqueado`
   ou `pulado` -- nunca inventa um lead para preencher a lacuna.
5. Se você já tem uma lista de contatos ou uma planilha exportada, cole o
   conteúdo na conversa; o agente estrutura os leads no formato tipado.
6. No fim, você recebe a lista tipada de leads + o veredito go/no-go,
   pronta para alimentar o seu CRM.

## Solução de problemas

- **"Ele inventou um contato"** -> reforce: "todo lead precisa de origem
  real (busca/paste/CNPJ oficial); o que não tiver confirmação, marque
  como bloqueado ou pulado".
- **Web search não acha nada em um canal** -> esperado para fontes que
  exigem login ou base paga (ex.: consulta de CNPJ). Cole os dados que
  você já tem, ou aceite o canal como `pulado` no relatório.
- **Quero capacidades extras (busca ao vivo mais robusta, MCP)** -> veja
  `SETUP_claude_projects.md`, onde é possível conectar ferramentas MCP.
- **Os placeholders `[fornecer: ...]` continuam aparecendo na resposta** ->
  volte nas Instructions e preencha nome da marca, tom de voz e valores
  antes de usar o agente com clientes reais.
