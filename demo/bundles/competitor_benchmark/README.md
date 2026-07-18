# Pacote de capacidade CEXAI: Matriz de Benchmark de Concorrentes (`competitive_matrix`)

O **contrato de 12 pilares** para o kind `competitive_matrix`, mais a configuração de setup.
Nucleus N01 . kind `competitive_matrix` . pillar P01.

Esta é a forma "12 ISO" da CEXAI -- um arquivo de especificação por pilar
(P01-P12), exatamente o pacote mostrado no vídeo do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrução,
e ele se torna um agente funcional de Matriz de Benchmark de Concorrentes.

## Conteúdo (19 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato de builder para este kind: uma especificação por pilar, P01-P12).
- `customgpt_instructions.json` -- a config do Custom GPT: nome, descrição,
  a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução como system prompt pronto
  para colar (para Claude Projects ou qualquer modelo).
- `README.md` -- este arquivo.
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT Projects.
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia geral combinado (visão de todos os runtimes).

## Upload (funciona em qualquer IA)

1. **Crie o container**: um Custom GPT (ChatGPT), um Project (ChatGPT ou
   Claude) ou um Gem (Gemini). Veja o guia específico do seu runtime na
   tabela abaixo.
2. **Cole a instrução**: use o campo `instructions` de
   `customgpt_instructions.json` (ou o conteúdo integral de
   `system_instruction.md`, são equivalentes) no campo de instruções/system
   prompt do seu runtime.
3. **Suba os 12 arquivos de conhecimento**: `P01_knowledge.md` até
   `P12_orchestration.md`, como Knowledge/Files/context do seu runtime.
4. **Teste** com o conversation starter: "Comparar `<produto>` com
   `<concorrentes>` em preço, funcionalidades e posicionamento".

| Runtime | Guia dedicado | Esforço |
|---------|----------------|--------|
| **ChatGPT (Custom GPT)** | Explore GPTs -> Create -> Configure. Suba os 12 arquivos `P0X_*.md` como Knowledge. Cole o campo `instructions` de `customgpt_instructions.json` na caixa de Instructions. | ~10 min |
| **ChatGPT (Projects, plano free)** | `SETUP_chatgpt_projects.md` | ~5 min |
| **Claude (Project)** | `SETUP_claude_projects.md` | ~10 min |
| **Gemini (Gems)** | `SETUP_gemini_gems.md` | ~5 min |
| **Qualquer IA (fallback universal)** | Cole `system_instruction.md` como system prompt; anexe os 12 arquivos como contexto/arquivos se o runtime suportar. | ~5 min |

Para uma visão combinada dos 4 caminhos acima, veja `SETUP_pt-br.md`.

## Procedência / honestidade
Nunca fabricar: todo marcador `[fornecer: ...]` é um campo sem entrada real
-- preencha com a sua própria marca antes de usar. Os 12 ISOs de pilar são
o contrato de builder genérico e público para `competitive_matrix` -- sem
dados de nenhum tenant.
