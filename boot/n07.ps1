# CEX N07 orchestrator boot -- self-contained launcher (Windows / PowerShell).
# No dependency on boot/_shared/*.ps1. Resolves repo root from its own location.
# Model default: reads THIS repo's .cex/config/nucleus_models.yaml (n07 entry, full
# claude-* ids only) with a degrade-never fallback to the hardcoded default below.
# System prompt: sin identity + agent card + context_self_select + nucleus_kinds_n07 +
# constitution_manifest CONTENT all merge into ONE file passed via a single
# content-carrying append flag -- never the literal-path form, never last-wins repeats.
# This script lives in <root>/boot/ -- repo root is its parent directory.
#
# Sibling of boot/cex.ps1 (same launcher, same conventions) but named for the
# _spawn/spawn_solo.ps1 / _spawn/spawn_grid.ps1 "boot/${nucleus}.ps1" dispatch
# convention, with the handoff auto-discovery n01-n06 siblings use: a dispatched
# nucleus is launched with NO extra args, so the boot script itself instructs it
# to read its handoff. Run boot/cex.ps1 directly for an ad hoc interactive session
# with your own initial prompt; run this one (or dispatch through it) when the
# task should come from .cex/runtime/handoffs/n07_task.md.

$ErrorActionPreference = "Stop"

# --- Resolve repo root (script dir is <root>/boot; root is one level up) ---
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
$cexRoot = Split-Path -Parent $scriptDir

Set-Location $cexRoot

# --- Environment ---
$env:CEX_NUCLEUS = "N07"
$env:CEX_ROOT = $cexRoot

# --- Model (yaml-with-fallback, degrade-never) ---
# Precedence: CEX_MODEL_OVERRIDE env > nucleus_models.yaml n07 model (full claude-* id
# only) > hardcoded default below. Shorthand aliases (fable/opus/sonnet) need Central's
# resolver stack (model_aliases + FABLE_SELF_HEAL), which this self-contained launcher
# deliberately does not depend on. For money-touching / irreversible / client-ship
# verify sessions, override with $env:CEX_MODEL_OVERRIDE = "claude-opus-4-8" or pass
# --model on the CLI.
$model = "claude-sonnet-4-6"
$modelsYaml = Join-Path $cexRoot ".cex/config/nucleus_models.yaml"
if (Test-Path $modelsYaml) {
    try {
        $inN07 = $false
        foreach ($line in @(Get-Content $modelsYaml)) {
            if ($line -match '^n07:\s*$') { $inN07 = $true; continue }
            if ($inN07 -and $line -match '^\S') { break }   # next top-level key ends the block
            if ($inN07 -and $line -match '^  model:\s*([A-Za-z0-9._:/-]+)') {
                if ($Matches[1] -like "claude-*") { $model = $Matches[1] }
                break
            }
        }
    } catch {}
}
if ($env:CEX_MODEL_OVERRIDE) { $model = $env:CEX_MODEL_OVERRIDE }
$card = "N07_admin/P08_architecture/agent_card_n07.md"

# --- Handoff detection (mission title only -- N07 reads the body itself) ---
$mission = ""
$handoffRel = ".cex/runtime/handoffs/n07_task.md"
$handoff = Join-Path $cexRoot ($handoffRel -replace '/', '\')
if (Test-Path $handoff) {
    foreach ($line in @(Get-Content $handoff -Head 10 -EA SilentlyContinue)) {
        if ($line -match "^mission:\s*(.+)$") { $mission = $Matches[1].Trim(); break }
    }
}

Write-Host ""
Write-Host "  CEX N07 orchestrator (Orchestrating Sloth)" -ForegroundColor Cyan
Write-Host "  root  : $cexRoot" -ForegroundColor DarkGray
Write-Host "  model : $model" -ForegroundColor DarkGray
if ($mission) { Write-Host "  mission: $mission" -ForegroundColor DarkGray }
Write-Host ""

# --- Pre-flight: Claude Code CLI must be on PATH ---
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] 'claude' CLI not found on PATH. Install Claude Code first." -ForegroundColor Red
    exit 1
}

# --- System prompt: ONE merged append (sin identity + agent card + L1 docs) ---
# claude CLI facts: (1) the path-string form of --append-system-prompt injects the
# literal PATH text, never file content -- only the -file form injects CONTENT;
# (2) both forms are LAST-WINS across repeats; (3) the two forms are mutually
# exclusive. So the sin identity + the agent card + context_self_select +
# nucleus_kinds_n07 + constitution_manifest CONTENT all merge into ONE file,
# passed as a single flag. Degrade-never: a missing source only shrinks the merge;
# a failed write skips the append entirely -- boot itself never breaks.
$sysPrompt = "You are driven by Orchestrating Sloth -- you delegate perfectly and never build directly. You are the N07 Orchestrator of this CEX tenant. Read CLAUDE.md and .claude/rules/n07-orchestrator.md before acting."
$appendFile = $null
try {
    $parts = @()
    $cardPath = Join-Path $cexRoot $card
    if (Test-Path $cardPath) {
        $parts += (Get-Content -Raw $cardPath)
    } else {
        Write-Host "[WARN] agent card not found: $card (merged append carries the identity only)" -ForegroundColor Yellow
    }
    $contextSelectPath = Join-Path $cexRoot ".cex/P09_config/context_self_select.md"
    if (Test-Path $contextSelectPath) {
        $parts += (Get-Content -Raw $contextSelectPath)
    } else {
        Write-Host "[WARN] context_self_select.md not found (merged append skips it)" -ForegroundColor Yellow
    }
    $nucleusKindsPath = Join-Path $cexRoot ".cex/P09_config/nucleus_kinds_n07.md"
    if (Test-Path $nucleusKindsPath) {
        $parts += (Get-Content -Raw $nucleusKindsPath)
    } else {
        Write-Host "[WARN] nucleus_kinds_n07.md not found (merged append skips it)" -ForegroundColor Yellow
    }
    $constitutionPath = Join-Path $cexRoot ".cex/P09_config/constitution_manifest.md"
    if (Test-Path $constitutionPath) {
        $parts += (Get-Content -Raw $constitutionPath)
    } else {
        Write-Host "[WARN] constitution_manifest.md not found (merged append skips it)" -ForegroundColor Yellow
    }
    $parts += $sysPrompt
    $cacheDir = Join-Path $cexRoot ".cex/cache/boot"
    New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
    $appendFile = Join-Path $cacheDir "append_final_n07.md"
    # UTF-8 WITHOUT BOM: the CLI append-file reader is byte-oriented (a BOM would leak U+FEFF).
    [System.IO.File]::WriteAllText($appendFile, ($parts -join "`n`n"), (New-Object System.Text.UTF8Encoding($false)))
} catch {
    $appendFile = $null
    Write-Host "[WARN] merged system-prompt append failed (launching without it)" -ForegroundColor Yellow
}

# --- Initial message: a dispatched N07 self-discovers its own handoff ---
# spawn_solo.ps1 / spawn_grid.ps1 launch this script with NO extra args -- the task
# lives in the handoff file, never on the command line (avoids nested-quote hell).
$initialMsg = "Read $handoffRel and execute. If no handoff, report ready."

# --- Build args (array elements avoid PowerShell operator parsing of flags) ---
$cliArgs = @(
    "--dangerously-skip-permissions",
    "--permission-mode", "bypassPermissions",
    "--model", $model
)
if ($appendFile) {
    $cliArgs += "--append-system-prompt-file", $appendFile
}
# Forward any extra args (e.g. an ad hoc initial prompt for a direct, non-dispatched run).
if ($args.Count -gt 0) { $cliArgs += $args } else { $cliArgs += $initialMsg }

& claude @cliArgs
exit $LASTEXITCODE
