# CEX N07 orchestrator boot -- CODEX runtime (Windows / PowerShell).
# Self-contained: no dependency on boot/_shared/*.ps1. Resolves repo root from its
# own location. Codex CLI has no --append-system-prompt equivalent, so the system
# context is embedded directly in the initial message instead of a separate flag.

$ErrorActionPreference = "Continue"

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
$cexRoot = Split-Path -Parent $scriptDir

Set-Location $cexRoot

$env:CEX_NUCLEUS = "N07"
$env:CEX_ROOT = $cexRoot
$env:CEX_CLI = "codex"

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] 'codex' CLI not found on PATH." -ForegroundColor Red
    exit 1
}

# codex reads its task from _task_codex.md (per-CLI handoff suffix -- see
# _spawn/spawn_solo.ps1 / spawn_grid.ps1, which write this file when -cli codex).
$handoffRel = ".cex/runtime/handoffs/n07_task_codex.md"
$handoffPath = Join-Path $cexRoot ($handoffRel -replace '/', '\')

Write-Host ""
Write-Host "  CEX N07 orchestrator via CODEX" -ForegroundColor White
Write-Host "  root  : $cexRoot" -ForegroundColor DarkGray
Write-Host "  handoff: $handoffRel" -ForegroundColor DarkGray
Write-Host ""

# Codex does not respect .gitignore the way gemini does, and has no system-prompt
# flag -- embed the handoff body + identity directly in the initial message.
if (Test-Path $handoffPath) {
    $handoffBody = Get-Content -Raw -LiteralPath $handoffPath
} else {
    $handoffBody = "(no handoff at $handoffRel -- report ready and exit)"
}

$sysPrompt = @'
You are N07 Orchestrator of this CEX tenant. Dispatch nuclei, never build directly.
Read CLAUDE.md and .claude/rules/n07-orchestrator.md.
You are running via the CODEX CLI (multi-runtime dispatch). Your handoff task is
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

$cliArgs = @("--dangerously-bypass-approvals-and-sandbox", "-C", $cexRoot)

$initialMsg | & codex exec @cliArgs -
exit $LASTEXITCODE
