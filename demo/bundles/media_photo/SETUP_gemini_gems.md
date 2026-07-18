# SETUP -- Gemini Gems

Setup do bundle `media_photo` (agente Mídia e Foto) em Gemini Gems.
Sem extensions, sem Actions -- apenas Gem instructions + Knowledge. ~5 minutos.

## Pré-requisitos

- Conta Google + acesso a gemini.google.com com Gems habilitado.
- ZERO extensions necessárias -- o agente não busca nada ao vivo; produz o
  BRIEF inteiramente a partir do texto das instructions + do conhecimento
  carregado.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome sugerido: `Mídia e Foto (media_photo)`.
4. Description: `Agente que produz briefs de imagem/foto (multimodal prompt) para a marca.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca antes de usar o Gem em produção.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos de pilar deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Extensions

Nenhuma extension é necessária para este Gem. Diferente de agentes de
pesquisa (que usam Google Search para coleta ao vivo), o `media_photo` só
precisa do texto das Instructions + da Knowledge -- pode deixar todas as
extensions desligadas.

### 5. Teste

Em uma conversa do Gem:

> `Criar um brief de foto para <cena/assunto>`

O Gem deve:
1. Confirmar a cena/assunto (ou perguntar detalhes se faltar contexto).
2. Produzir um artefato `multimodal_prompt` estruturado.
3. Respeitar a voz e os valores de marca configurados nas Instructions.
4. Nunca inventar dado de marca ausente -- manter `[fornecer: ...]` explícito.

## Fidelidade declarada: FULL

Este bundle não depende de nenhuma extension/Action para funcionar -- a
capacidade inteira do agente (produzir o brief de imagem/foto) está contida
no texto das Instructions + nos 12 arquivos de Knowledge, ambos suportados
nativamente por Gemini Gems.

## Vantagens do Gemini para este bundle

- **Multi-modal nativo**: se você quiser anexar uma imagem de referência à
  conversa (ex.: "gere o brief a partir desta foto de inspiração"), o Gemini
  lida bem com isso nativamente -- útil para um agente de briefs visuais.
- **Contexto grande**: Gems em modelos recentes aceitam janelas de contexto
  bem maiores, o que ajuda quando você acumula muitos briefs na mesma
  conversa.

## Solução de problemas

- **"Ele gerou a imagem em vez do brief"** -> fora de escopo deste agente;
  reforce nas Instructions que a saída é o BRIEF (texto estruturado), não a
  imagem renderizada.
- **"Ele não respeitou a marca"** -> confirme que os placeholders
  `[fornecer: ...]` foram preenchidos com os dados reais antes do teste.
- **Quero a versão combinada com todas as plataformas** -> veja `SETUP_pt-br.md`.
