# SETUP -- ChatGPT Projects (plano free)

Setup do bundle `brandbook` (Manual de Marca) no ChatGPT Projects. Não exige
plano Plus, não exige nenhuma chave de API -- é só colar as Instructions e
subir os 12 arquivos de conhecimento. ~5 minutos.

## Pré-requisitos

- Conta ChatGPT (plano free é suficiente).
- ZERO chaves de API necessárias (este bundle não usa Actions).

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome: `Manual de Marca (brandbook)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o conteúdo de `system_instruction.md` deste bundle (ou o campo
   `instructions` de `customgpt_instructions.json` -- é o mesmo texto).
3. Cole nas Instructions do projeto.

### 3. Suba os 12 arquivos de Knowledge

Em **Files** do projeto, suba os **12 arquivos** deste bundle:

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

Não suba `README.md`, `customgpt_instructions.json` nem os arquivos
`SETUP_*.md` -- são material de referência deste bundle, não conhecimento
para o agente.

### 4. Capabilities

Este bundle não depende de nenhuma capability especial:

- **Web browsing** -- opcional. Só é útil se você quiser colar uma URL do
  site da marca em `brand_materials`; o agente tenta lê-la se a navegação
  estiver habilitada no modelo escolhido. Sem isso, cole o texto direto.
- **Code interpreter** -- não usado por este agente.
- **DALL-E** -- não usado por este agente.

### 5. Teste

Inicie uma conversa dentro do project:

> `Monte o manual de marca para Café Aurora -- essência: cafeteria de bairro, aconchegante e artesanal`

O agente deve:
1. Confirmar `brand_name` (obrigatório) e perguntar por `brand_essence` /
   `brand_materials` / `brand_materials_palette` se não foram fornecidos.
2. Produzir as 8 seções (Identidade da Marca, Paleta de Cores, Tipografia,
   Persona da Marca, Uso do Logotipo, Estilo de Imagem, Framework de
   Mensagem, Faça e Não Faça).
3. Preencher com dado real onde você forneceu, e `[fornecer: ...]` honesto
   onde não forneceu -- nunca inventar cor, fonte, copy ou métrica.

## Fidelidade declarada: full

Diferente de bundles com Actions (ex.: pesquisa de mercado), o `brandbook`
não tem nenhuma dependência externa -- é 100% instructions + conhecimento.
Rodando em ChatGPT Projects, você tem a MESMA capacidade de geração das 8
seções que em qualquer outro runtime. Não há degradação de tier.

O que o Project **não** replica é a parte interna do CEXAI (a crew de 3
papéis `brand_discovery`, os scripts `brand_*.py`, o MCP `fetch` /
`markitdown` / `canva`) -- descrita em `P04_tools.md` e `P08_architecture.md`
como contexto de arquitetura, não como algo que o agente exportado executa.
Veja a "Nota de Portabilidade" nesses dois arquivos.

## Custom GPT em vez de Project?

Se você tem ChatGPT Plus e prefere um Custom GPT nomeado e compartilhável
por link (em vez de um Project privado):

1. **Explore GPTs** -> **+ Create** -> aba **Configure**.
2. Cole o campo `instructions` de `customgpt_instructions.json` nas
   Instructions do GPT (é o mesmo texto de `system_instruction.md`).
3. Suba os mesmos 12 arquivos como Knowledge.
4. Use o campo `conversation_starters` do JSON como sugestão inicial.

Não há ganho de capacidade -- é a mesma geração de 8 seções. A diferença é
só de organização/compartilhamento (Project privado vs GPT com link público).

## Como usar (fluxo típico)

1. Diga o nome da marca: `Monte o manual de marca para <nome da marca>`.
2. Cole a essência (1 frase) e qualquer material que você tenha (texto do
   site, paleta em hex, descrição do logotipo).
3. O agente monta as 8 seções, com `[fornecer: ...]` nos campos sem dado.
4. Preencha os `[fornecer: ...]` que restarem com informação real da sua
   marca antes de usar o manual internamente ou com fornecedores.

## Solução de problemas

- **"Ele inventou uma cor/fonte"** -> reforce: "não invente -- onde não há
  dado, use `[fornecer: ...]`" (o agente nunca deveria fazer isso; se
  fizer, é uma violação da regra Nunca-Fabricar do `system_instruction.md`).
- **Quer que ele leia o site da marca** -> ative Web Browsing no modelo do
  Project e cole a URL em `brand_materials`; se a leitura falhar (comum em
  sites com proteção anti-bot), cole o texto manualmente.
- **Muitos `[fornecer: ...]` no resultado** -> normal na primeira rodada.
  Responda preenchendo os campos que você souber e peça para o agente
  regenerar a seção.
- **Quer editar as 12 seções depois** -> os 12 arquivos `P0X_*.md` são o
  contrato completo (builder ISOs); edite-os e resuba se quiser mudar o
  comportamento do agente.
