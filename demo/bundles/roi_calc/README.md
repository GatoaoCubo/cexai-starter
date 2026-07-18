# Pacote de capacidade CEXAI: Calculadora de ROI (`roi_calc`)

O **contrato de 12 pilares** para o kind `roi_calculator`, mais a
configuração de setup pronta para uso.
Nucleus N06 . kind `roi_calculator` . pillar P11.

Este é o formato "12 ISO" do CEXAI -- um arquivo de especificação por
pilar (P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os
12 arquivos de pilar como Knowledge em qualquer assistente, cole a
instrução, e ele vira um agente Calculadora de ROI funcional.

## Conteúdo (19 arquivos)

- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato de builder para este kind: uma especificação por pilar, P01-P12).
- `customgpt_instructions.json` -- a configuração para Custom GPT: name,
  description, a string `instructions` para colar, e os conversation
  starters.
- `system_instruction.md` -- a mesma instrução pronta para colar como
  system prompt (para Claude Projects, Gemini Gems ou qualquer modelo).
- `README.md` -- este arquivo.
- `SETUP_chatgpt_projects.md` -- guia de setup para ChatGPT Projects.
- `SETUP_claude_projects.md` -- guia de setup para Claude Projects.
- `SETUP_gemini_gems.md` -- guia de setup para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado (visão geral + as 4 opções + fluxo +
  solução de problemas).

## Upload (passo a passo, qualquer IA)

1. **Escolha o runtime** e siga o guia de setup correspondente:

   | Runtime | Guia | Precisa de chave de API? |
   |---------|------|---------------------------|
   | **ChatGPT (Custom GPT)** | resumo abaixo + `SETUP_pt-br.md` | Não |
   | **ChatGPT (Projects)** | `SETUP_chatgpt_projects.md` | Não |
   | **Claude (Project)** | `SETUP_claude_projects.md` | Não |
   | **Gemini (Gem)** | `SETUP_gemini_gems.md` | Não |
   | **Qualquer outra IA** | seção "Qualquer IA" abaixo | Não |

2. **Cole a instrução**: copie o conteúdo de `system_instruction.md` (ou o
   campo `instructions` de `customgpt_instructions.json`, e o mesmo texto)
   no campo de instruções/system prompt do seu assistente.
3. **Suba os 12 pilares**: anexe `P01_knowledge.md` até
   `P12_orchestration.md` como Knowledge/Files do seu assistente.
4. **Preencha os placeholders**: substitua todo `[fornecer: ...]` (nome da
   marca, tom de voz, valores) pelos dados reais da sua marca antes de usar
   em produção.
5. **Teste**: "Monte um caso de ROI para `<comprador/segmento>` -- tamanho
   da equipe, valor da hora, esforço atual".

### ChatGPT (Custom GPT) -- resumo rápido

Explore GPTs -> Create -> aba Configure. Suba os 12 arquivos `P0X_*.md`
como Knowledge. Cole o campo `instructions` de `customgpt_instructions.json`
no campo Instructions. Nenhuma capability é necessária (web browsing, code
interpreter e DALL-E ficam desligados).

### Claude (Project) -- resumo rápido

Cole `system_instruction.md` nas Custom Instructions; anexe os 12 arquivos
de pilar ao Project knowledge. Detalhe completo: `SETUP_claude_projects.md`.

### Qualquer IA -- resumo rápido

Cole `system_instruction.md` como system prompt e anexe (ou cole no
contexto) os 12 arquivos de pilar. Funciona em qualquer assistente que
aceite texto de instrução + anexos -- este agente não depende de nenhuma
ferramenta externa.

## Provenance / honestidade

Nunca fabricar: qualquer marcador `[fornecer: ...]` é um campo sem entrada
real -- preencha com os dados da sua marca antes de usar. Os 12 ISOs de
pilar são o contrato de builder genérico e público do `roi_calculator` --
nenhum dado de tenant.
