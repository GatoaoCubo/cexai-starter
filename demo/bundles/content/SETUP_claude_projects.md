# SETUP -- Claude Projects

Setup do bundle `content` (agent de knowledge_card, arquitetura CEXAI) em
Claude Projects. ~5 minutos.

## Pre-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- Preencha os campos `[fornecer: ...]` de `system_instruction.md` com o
  nome, o tom de voz e os valores da sua marca antes de subir.

## Passo a passo

### 1. Crie o Project

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: o nome da sua marca seguido de "Content".

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral, ou "Set
   custom instructions").
2. Copie TODO o conteudo de `system_instruction.md`.
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects nao tem limite de 20 arquivos (o limite e por tamanho total
do projeto, bem acima do que estes 12 arquivos ocupam).

### 4. Teste

Em uma conversa do Project:

> `Documentar o processo de integracao de novos funcionarios como um knowledge card`

O agent deve:
1. Confirmar o processo/topico exato.
2. Classificar o card como `domain_kc` (conhecimento externo) ou `meta_kc`
   (interno a sua empresa) -- ver `P06_schema.md`.
3. Produzir o knowledge_card completo, seguindo a estrutura de `P05_output.md`.
4. Rodar a autoavaliacao contra os portoes HARD antes de entregar (ver
   `P07_evals.md`).

## Vantagens do Claude Projects

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|----------------|
| Context window | 128K | 200K |
| Limite de arquivos | 20 por GPT | sem limite de contagem (so de tamanho total, ~30MB) |
| Custo | Plus ($20/mes) | Pro ($20/mes) ou Free (com limites de uso) |
| Tool calls paralelas | Sequencial | Nativo via tool_use |

## Fidelidade declarada: completa

Este bundle nao depende de Actions, MCP, nem chaves de API -- os 12 arquivos
de pilar + `system_instruction.md` sao o agent inteiro. Nao ha degradacao
neste runtime.

## Solucao de problemas

- **"O agent inventou um dado"** -> reforce as SALVAGUARDAS de
  `system_instruction.md`: "sem dado real, use `[fornecer: ...]`".
- **Quero anexar mais conhecimento (KCs reais da sua empresa)** -> suba
  arquivos adicionais em Knowledge; o agent vai preferir o conhecimento real
  ao generico dos 12 arquivos de pilar.
- **Resposta generica demais** -> confirme que voce preencheu os
  `[fornecer: ...]` de `system_instruction.md` com dados reais da sua marca
  antes de colar nas Project Instructions.
- **Quero reusar este Project para varios processos** -> normal; o agent
  produz um knowledge_card por conversa, um topico por card (regra de
  atomicidade em `P02_model.md`).
