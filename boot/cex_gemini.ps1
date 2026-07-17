# CEX N07 orchestrator boot -- GEMINI runtime (Windows / PowerShell).
# Self-contained: no dependency on boot/_shared/*.ps1. Resolves repo root from its
# own location. Gemini CLI has no --append-system-prompt equivalent, so the system
# context is embedded directly in the initial message instead of a separate flag.

$ErrorActionPreference = "Continue"

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
$cexRoot = Split-Path -Parent $scriptDir

Set-Location $cexRoot

$env:CEX_NUCLEUS = "N07"
$env:CEX_ROOT = $cexRoot
$env:CEX_CLI = "gemini"

if (-not (Get-Command gemini -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] 'gemini' CLI not found on PATH." -ForegroundColor Red
    exit 1
}

# Model: nucleus_models.yaml n07.fallback_chain[cli=gemini].model if present, else
# a safe hardcoded default. No dependency on Central's resolver stack.
$geminiModel = "gemini-2.5-flash-lite"
$modelsYaml = Join-Path $cexRoot ".cex/config/nucleus_models.yaml"
if (Test-Path $modelsYaml) {
    try {
        $inChain = $false
        foreach ($line in @(Get-Content $modelsYaml)) {
            if ($line -match '^\s*-\s*\{cli:\s*gemini,\s*model:\s*([A-Za-z0-9._:/-]+)') {
                $geminiModel = $Matches[1]
                break
            }
        }
    } catch {}
}
if ($env:CEX_MODEL_OVERRIDE) { $geminiModel = $env:CEX_MODEL_OVERRIDE }

# gemini reads its task from _task_gemini.md (per-CLI handoff suffix -- see
# _spawn/spawn_solo.ps1 / spawn_grid.ps1, which write this file when -cli gemini).
$handoffRel = ".cex/runtime/handoffs/n07_task_gemini.md"
$handoffPath = Join-Path $cexRoot ($handoffRel -replace '/', '\')

Write-Host ""
Write-Host "  CEX N07 orchestrator via GEMINI" -ForegroundColor White
Write-Host "  root  : $cexRoot" -ForegroundColor DarkGray
Write-Host "  model : $geminiModel" -ForegroundColor DarkGray
Write-Host "  handoff: $handoffRel" -ForegroundColor DarkGray
Write-Host ""

# gemini respects .gitignore for file reads, and has no system-prompt flag --
# embed the handoff body + identity directly in the initial message.
if (Test-Path $handoffPath) {
    $handoffBody = Get-Content -Raw -LiteralPath $handoffPath
} else {
    $handoffBody = "(no handoff at $handoffRel -- report ready and exit)"
}

$sysPrompt = @'
You are N07 Orchestrator of this CEX tenant. Dispatch nuclei, never build directly.
Read CLAUDE.md and .claude/rules/n07-orchestrator.md.
You are running via the GEMINI CLI (multi-runtime dispatch). Your handoff task is
embedded verbatim below (between HANDOFF BEGIN/END) -- do not try to locate or
re-read a handoff file yourself; use the embedded content directly.
Follow the 8F pipeline F1->F8. Save output, compile, commit, signal on complete.
'@

$initialMsg = @"
Execute the task described in the handoff BELOW (embedded verbatim -- do NOT try to re-read the path).
Follow its frontmatter (mission, kind, output path) exactly. Follow the 8F pipeline. Signal on complete.

=== HANDOFF BEGIN ===
$handoffBody
=== HANDOFF END ===

SYSTEM CONTEXT:
$sysPrompt
"@

$cliArgs = @("--yolo", "--model", $geminiModel, "--include-directories", $cexRoot)

& gemini @cliArgs $initialMsg
exit $LASTEXITCODE
