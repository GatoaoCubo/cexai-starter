# SETUP -- Claude Projects

Setup do bundle `media_photo` (agente Mídia e Foto) em Claude Projects.
Sem MCP, sem Actions -- apenas Project Instructions + Knowledge. ~5 minutos.

## Pré-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO integrações externas necessárias -- o agente não chama nenhuma
  ferramenta; produz o BRIEF inteiramente a partir do texto das Instructions
  + do conhecimento carregado.

## Passo a passo

### 1. Crie o Project no Claude

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome sugerido: `Mídia e Foto (media_photo)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project instructions** (painel lateral, "Custom
   instructions" / "Set custom instructions").
2. Copie TODO o conteúdo de `system_instruction.md`.
3. Cole nas Project Instructions.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca antes de publicar o Project para o time.

### 3. Suba os 12 arquivos de Knowledge

Em **Project knowledge**, anexe os 12 arquivos de pilar deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho total
do conhecimento do projeto) -- os 12 arquivos deste bundle cabem com folga.

### 4. Capabilities

Nenhuma configuração adicional é necessária:
- Não há Actions nem MCP servers a conectar (diferente de bundles de
  pesquisa que dependem de scraping externo).
- Se o seu plano Claude tiver acesso a ferramentas nativas (busca na web,
  execução de código), elas são OPCIONAIS aqui -- o agente `media_photo` não
  depende de nenhuma delas para funcionar.

### 5. Teste

Em uma conversa do Project:

> `Criar um brief de foto para <cena/assunto>`

O agente deve:
1. Confirmar a cena/assunto (ou pedir detalhes se a descrição for vaga).
2. Produzir um artefato `multimodal_prompt`: modalidades, descrição da cena,
   parâmetros técnicos relevantes.
3. Respeitar a voz e os valores de marca configurados.
4. Nunca inventar dado de marca ausente -- manter `[fornecer: ...]` explícito.

## Fidelidade declarada: FULL

Este bundle não tem uma camada de Actions/MCP a perder -- toda a capacidade
do agente (produzir o brief de imagem/foto) vem do texto das Instructions +
dos 12 arquivos de Knowledge, os dois presentes de forma completa em Claude
Projects. Não há degradação em relação a nenhuma outra plataforma.

## Vantagens do Claude Projects para este bundle

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|----------------|
| Project Knowledge | limite de 20 arquivos | sem limite por arquivo (limite por tamanho total) |
| Context window | menor | maior (bom para briefs mais longos/detalhados) |
| Setup | cole `instructions` + suba 12 arquivos | cole `system_instruction.md` + suba 12 arquivos |

## Solução de problemas

- **"Ele não seguiu a voz de marca"** -> confirme que os placeholders
  `[fornecer: ...]` de Tom/Valores foram preenchidos nas Project instructions
  (um placeholder vazio é esperado até você configurar sua marca).
- **"Ele tentou gerar a imagem de verdade"** -> fora de escopo; reforce que o
  agente entrega o BRIEF (texto), não a imagem renderizada (ver seção PAPEL).
- **Quero a versão combinada com todas as plataformas** -> veja `SETUP_pt-br.md`.
