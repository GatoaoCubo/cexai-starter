# SETUP -- Gemini Gems

Setup do bundle `leadgen` (Captação de Leads) em Gemini Gems. Os mesmos 12
arquivos de pillar entram como Knowledge do Gem; a busca ao vivo depende da
extension nativa de Search do Gemini. ~5 minutos.

## Pré-requisitos

- Conta Google + acesso a gemini.google.com.
- (Opcional) Extension **Google Search** habilitada, para o agente tentar
  localizar leads na web em vez de depender apenas do que você cola na
  conversa.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome sugerido: `Captação de Leads (leadgen)`.
4. Description: `Encontra leads de <perfil> a partir de uma seed -- marketplace, CNPJ, social`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie todo o conteúdo.
3. Cole no campo Instructions do Gem.
4. Substitua os marcadores `[fornecer: ...]` pelo nome, tom de voz e
   valores reais da sua marca.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos de pillar deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Gemini Gems aceita arquivos de knowledge; o limite de tamanho total varia
conforme o plano da sua conta.

### 4. (Opcional) Habilite a extension de Search

Em **Extensions** do Gem, habilite **Google Search** para permitir que o
agente tente localizar leads (perfis públicos, listagens de marketplace,
menções sociais) diretamente na web.

### 5. Teste

Em uma conversa do Gem:

> `Encontre leads para dentistas em Curitiba a partir de "clínica odontológica" -- marketplace, CNPJ, social`

O Gem deve:
1. Confirmar o perfil e a seed.
2. Declarar quais canais consegue percorrer com a extension de Search
   (quando habilitada) e quais exigem que você cole os dados.
3. Nunca inventar um contato -- todo canal sem confirmação entra como
   `bloqueado` ou `pulado` na lista final.
4. Entregar a lista tipada de leads + veredito go/no-go.

## Fidelidade declarada: PARCIAL (sem Search) / BOA (com Search)

| Motivo | Detalhe |
|-------|---------|
| Sem a extension Google Search | O Gem só estrutura e verifica os dados que você colar na conversa |
| Com Google Search habilitada | O Gem também tenta localizar leads públicos diretamente na web |
| Bases pagas / autenticadas (CNPJ, redes sociais logadas) | Continuam exigindo que você cole os dados -- nenhuma plataforma contorna isso automaticamente |

## Vantagens do Gemini

- **Janela de contexto grande** (mais de 1M tokens nos modelos recentes) --
  útil se você for colar listas grandes de leads para estruturar de uma vez.
- **Google Search nativo** cobre bem buscas públicas gerais.
- **Multi-modal nativo**: se você tem um print de uma listagem ou perfil,
  pode anexar a imagem e pedir para o Gem extrair os dados.

## Limitações

- **Sem Actions nativas**: não é possível subir specs OpenAPI como no
  Custom GPT.
- **MCP não suportado** (a partir de 2026-05; pode mudar).
- Bases que exigem login ou API paga (CNPJ oficial, redes sociais
  autenticadas) continuam fora do alcance de qualquer busca automática --
  sempre vão exigir dado colado por você.

## Como usar (fluxo típico)

1. Diga o perfil e a seed: `Encontre leads para <perfil> a partir de <seed>`.
2. O Gem confirma o perfil e os canais que vai tentar percorrer.
3. Com Search habilitado, ele busca e retorna o que encontrar, citando a
   origem de cada lead.
4. Para canais que exigem login/API paga, ele avisa e pede que você cole
   os dados (planilha, export de CRM, print de listagem).
5. Entrega a lista tipada de leads + status honesto por fonte + veredito
   go/no-go, pronta para alimentar o CRM.

## Solução de problemas

- **Search não retorna nada para o nicho** -> tente uma seed mais específica
  (nome de produto/serviço exato em vez de uma categoria ampla).
- **"Ele inventou um contato"** -> reforce: "todo lead precisa de origem
  real (busca/paste/CNPJ oficial); o que não tiver confirmação, marque
  como bloqueado ou pulado".
- **Quero buscar em bases pagas (CNPJ, etc.)** -> nenhuma das 4 plataformas
  faz isso automaticamente; cole o export da base paga na conversa para o
  Gem estruturar.
- **Multi-modal**: se quiser extrair leads de um print ou PDF de listagem,
  anexe o arquivo no chat e peça para o Gem extrair os campos.
