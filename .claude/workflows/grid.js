export const meta = {
  name: 'grid',
  description:
    'Mode W grid dispatch: in-session Workflow fan-out for a same-runtime, single-session mission. Reads existing handoff files under .cex/runtime/handoffs/{mission}_*.md, runs one subagent per nucleus cell to execute its handoff end to end (8F, compile, signal), returns structured per-cell results for the N07 keystone verify.',
  whenToUse:
    'Default path for same-runtime (Claude-only), single-session, bounded-duration grid dispatch once handoff files already exist (produced by /guide + /spec, or written directly). Requires args {mission: string}. No per-cell git commit -- N07 consolidates after reviewing the returned results. Companion, not a replacement, for Mode X: cross-runtime cells (gemini/codex/ollama), multi-hour detached/overnight autonomy, and founder-launched OS windows still route through bash _spawn/dispatch.sh grid MISSION [-w] -- see .claude/rules/n07-orchestrator.md and docs/ARCHITECTURE_NOTES.md (Tier 2, register row R-008).',
  phases: [
    { title: 'Discovery', detail: 'one agent lists .cex/runtime/handoffs/{mission}_*.md and resolves each match to a {nucleus, handoff_path} cell' },
    { title: 'Execute', detail: 'one subagent per cell reads its handoff and runs it end to end (8F, compile, signal); parallel fan-out, optional per-cell worktree isolation' },
  ],
}

// args: the caller (a mode-resolving /grid step, or N07 directly) passes these.
// This script never touches the filesystem -- cells do their own file work via
// their own tools (Glob/Read/Bash/Edit/Write).
const SAFE = /^[A-Za-z0-9][A-Za-z0-9_-]*$/

// Defensive: some call paths deliver args as a JSON-encoded STRING instead of an
// object (observed live on the first smoke, 2026-07-02). Normalize before validating.
let ARGS = args
if (typeof ARGS === 'string') {
  try { ARGS = JSON.parse(ARGS) } catch (e) { ARGS = null }
}

const mission = ARGS && ARGS.mission
if (!mission || typeof mission !== 'string' || !SAFE.test(mission))
  throw new Error(`grid workflow requires args: {mission: "<MISSION_TOKEN>", nuclei?: string[], worktrees?: boolean, model?: string} -- mission must match ${SAFE}`)

const nucleiFilter = Array.isArray(ARGS && ARGS.nuclei) ? ARGS.nuclei : null
if (nucleiFilter) {
  for (const n of nucleiFilter) {
    if (typeof n !== 'string' || !SAFE.test(n)) throw new Error(`Unsafe nuclei entry ${JSON.stringify(n)} -- must match ${SAFE}`)
  }
}
const worktrees = Boolean(ARGS && ARGS.worktrees)
const model = (ARGS && ARGS.model) || 'sonnet'

// ---- schemas ----------------------------------------------------------------
const DISCOVERY_SCHEMA = {
  type: 'object',
  required: ['cells'],
  properties: {
    cells: {
      type: 'array',
      items: {
        type: 'object',
        required: ['nucleus', 'handoff_path'],
        properties: {
          nucleus: { type: 'string', description: 'nucleus token parsed from the filename, e.g. n01-n07' },
          handoff_path: { type: 'string', description: 'repo-relative path, e.g. .cex/runtime/handoffs/MISSION_n03.md' },
        },
      },
    },
    note: { type: 'string', description: 'set when zero handoffs were found, or other discovery caveats' },
  },
}

const CELL_SCHEMA = {
  type: 'object',
  required: ['nucleus', 'ok', 'summary'],
  properties: {
    nucleus: { type: 'string' },
    ok: { type: 'boolean', description: 'true only if the handoff ran end to end: deliverables produced, compiled, and signaled' },
    deliverables: { type: 'array', items: { type: 'string' }, description: 'paths of artifacts produced or compiled' },
    summary: { type: 'string', description: '1-3 sentences: what this cell did' },
    issues: { type: 'array', items: { type: 'string' }, description: 'gates failed, files missing, or follow-ups needed' },
  },
}

// ---- Phase: Discovery ---------------------------------------------------------
phase('Discovery')
const handoffGlob = `.cex/runtime/handoffs/${mission}_*.md`
const scopeNote = nucleiFilter
  ? ` Only include cells whose nucleus token is one of: ${nucleiFilter.join(', ')} -- skip any other matching file.`
  : ' Include every matching file.'

const discovery = await agent(
  `List every file matching ${handoffGlob} (use your own read-only tools -- this script has no filesystem access).${scopeNote}
For each match, extract the nucleus token: a lowercase "n" followed by digits (n01-n07), found among the underscore-separated parts of the filename after the "${mission}_" prefix and before an optional trailing "_task" suffix. Skip any file with no such token (a shared context file like ${mission}_COMMON.md is not a cell).
Return the repo-relative handoff_path exactly as found. If zero files match, return an empty cells array and say so honestly in note -- never fabricate a cell.`,
  { label: `discover:${mission}`, phase: 'Discovery', model: 'sonnet', schema: DISCOVERY_SCHEMA },
)

const cells = (discovery && discovery.cells) || []
if (cells.length === 0) {
  log(`No handoffs found for ${handoffGlob} -- nothing to dispatch.`)
  const note = (discovery && discovery.note) || 'no matching handoff files (or discovery agent returned no result)'
  return { mission, cells_ok: 0, cells_total: 0, results: [], note }
}
log(`Discovered ${cells.length} cell(s) for mission ${mission}: ${cells.map(c => c.nucleus).join(', ')}`)

if (budget && budget.total && typeof budget.remaining === 'function' && budget.remaining() < 20000) {
  log(`Warning: token budget nearly exhausted (${Math.round(budget.remaining() / 1000)}k left) before fanning out ${cells.length} cell(s) -- proceeding, individual cells may fail.`)
}

// ---- Phase: Execute -------------------------------------------------------------
phase('Execute')
const isolation = worktrees ? 'worktree' : undefined

const results = await parallel(
  cells.map(cell => () =>
    agent(
      `You are nucleus ${cell.nucleus} cell for mission ${mission}. Read your handoff at ${cell.handoff_path} and execute it FULLY per 8F (F1 CONSTRAIN through F8 COLLABORATE) and the handoff's own contract: produce every deliverable it specifies, compile the artifact(s) (python _tools/cex_compile.py <path>), do NOT git commit -- N07 consolidates after the whole wave -- then signal completion exactly as the handoff / 8F F8 step specifies, e.g.:
  python -c "from _tools.signal_writer import write_signal; write_signal('${cell.nucleus}', 'complete', <your_F7_score>, '${mission}')"
If the handoff cannot be read or a required gate fails, do not fabricate success: skip the complete signal (or send status='partial') and report ok=false with why in issues below.`,
      { label: `${mission}:${cell.nucleus}`, phase: 'Execute', model, isolation, schema: CELL_SCHEMA },
    ).then(r => r || {
      nucleus: cell.nucleus,
      ok: false,
      deliverables: [],
      summary: 'cell returned no structured result (skipped or errored before producing one)',
      issues: ['agent() resolved falsy -- see the workflow run log for the underlying error'],
    }),
  ),
)

const cellsOk = results.filter(r => r && r.ok).length
log(`${cellsOk}/${cells.length} cell(s) reported ok for mission ${mission}`)

// ---- Return ---------------------------------------------------------------------
// N07 reads this as the keystone-verify input (Consolidate Protocol, n07-orchestrator.md).
// This script never writes files or commits.
return {
  mission,
  cells_ok: cellsOk,
  cells_total: cells.length,
  results,
  ...(discovery && discovery.note ? { note: discovery.note } : {}),
}
