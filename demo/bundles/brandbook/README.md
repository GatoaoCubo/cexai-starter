# Bundle de capacidade CEXAI: Manual de Marca (`brandbook`)

O **contrato de 12 pilares** para o kind `brandbook`, mais a configuração de
setup. Nucleus N06 . kind `brandbook` . pillar P05.

Esta é a forma "12 ISO" da CEXAI -- um arquivo de especificação por pilar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrução, e
ele vira um agente de Manual de Marca funcional.

## O que este agente faz

A partir do nome da marca (obrigatório) e, opcionalmente, essência,
materiais (texto/URL/PDF colado) e paleta de cores, o agente monta um
**Manual de Marca completo em 8 seções**:

1. Identidade da Marca
2. Paleta de Cores
3. Tipografia
4. Persona da Marca
5. Uso do Logotipo
6. Estilo de Imagem
7. Framework de Mensagem
8. Faça e Não Faça

Onde não houver dado real, o agente emite um placeholder honesto
`[fornecer: ...]` em vez de inventar -- essa é a regra Nunca-Fabricar, e ela
cobre toda cor de marca, nome de fonte, exemplo de copy e métrica de
conversão.

## Conteúdo (19 arquivos)

**Conhecimento (12 arquivos, suba como Knowledge/Files):**
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato do builder para este kind: uma especificação por pilar, P01-P12).

**Instruções e config (3 arquivos):**
- `system_instruction.md` -- a instrução em formato de prompt de sistema
  pronto para colar (Claude Projects, Gemini Gems, ou qualquer modelo).
- `customgpt_instructions.json` -- a config de Custom GPT: name,
  description, o texto `instructions` para colar, e conversation starters.
- `README.md` -- este arquivo.

**Guias de setup (4 arquivos):**
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT (Projects ou
  Custom GPT).
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado: overview + as 3 plataformas + solução
  de problemas.

## Passo a passo de upload (qualquer IA)

1. **Escolha a plataforma** e abra o guia correspondente para o passo a
   passo completo:
   | Plataforma | Guia |
   |------------|------|
   | ChatGPT (Projects ou Custom GPT) | `SETUP_chatgpt_projects.md` |
   | Claude Projects | `SETUP_claude_projects.md` |
   | Gemini Gems | `SETUP_gemini_gems.md` |
   | Não sabe por onde começar / quer o overview geral | `SETUP_pt-br.md` |

2. **Cole a instrução**: copie o conteúdo de `system_instruction.md` (ou o
   campo `instructions` de `customgpt_instructions.json` -- é o mesmo
   texto) no campo de instruções/prompt de sistema da plataforma escolhida.

3. **Suba os 12 arquivos de conhecimento**: `P01_knowledge.md` até
   `P12_orchestration.md`, como Knowledge (Claude/Gemini) ou Files
   (ChatGPT).

4. **Teste**: envie `Monte o manual de marca para <nome da marca>` e cole a
   essência e qualquer material que você tiver. O agente entrega as 8
   seções em Markdown, prontas para copiar.

Nenhuma chave de API, Action ou integração externa é necessária -- este
bundle é 100% instruções + conhecimento, e funciona de forma idêntica
(fidelidade `full`) em qualquer uma das 3 plataformas.

## Proveniência / honestidade

Nunca-fabricar: qualquer marcador `[fornecer: ...]` é um campo sem input
real -- preencha com dado da sua própria marca antes de usar. Os 12 ISOs de
pilar são o contrato genérico e público do builder para `brandbook` -- sem
dado de nenhum tenant.

`P04_tools.md`, `P08_architecture.md` e `P10_memory.md` trazem, cada um, uma
"Nota de Portabilidade" explicando o que é exclusivo do CEXAI interno
(a crew de 3 papéis `brand_discovery`, os scripts `brand_*.py`, o MCP de
scraping/conversão, a memória persistente entre sessões) e o que o agente
standalone deste bundle efetivamente executa em uma única conversa.
