# CEX N03 Engineering boot -- self-contained launcher (Windows / PowerShell).
# No dependency on boot/_shared/*.ps1. Resolves repo root from its own location.
# Model default: reads THIS repo's .cex/config/nucleus_models.yaml (n03 entry, full
# claude-* ids only) with a degrade-never fallback to the hardcoded default below.
# System prompt: sin identity + agent card CONTENT merge into ONE file passed via a
# single content-carrying append flag -- never the literal-path form, never last-wins repeats.
# This script lives in <root>/boot/ -- repo root is its parent directory.
# Dispatched by _spawn/spawn_solo.ps1 / _spawn/spawn_grid.ps1 (boot/n03.ps1 convention);
# also safe to run directly for a one-off interactive session in this nucleus.

$ErrorActionPreference = "Stop"

# --- Resolve repo root (script dir is <root>/boot; root is one level up) ---
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
$cexRoot = Split-Path -Parent $scriptDir

Set-Location $cexRoot

# --- Environment ---
$env:CEX_NUCLEUS = "N03"
$env:CEX_ROOT = $cexRoot

# --- Model (yaml-with-fallback, degrade-never) ---
# Precedence: CEX_MODEL_OVERRIDE env > nucleus_models.yaml n03 model (full claude-* id
# only) > hardcoded default below. Shorthand aliases (sonnet/opus) in the yaml need
# Central's resolver stack (model_aliases), which this self-contained launcher
# deliberately does not depend on -- a shorthand value falls through to the hardcoded
# default, which already matches this nucleus's model-economy tier.
$model = "claude-sonnet-4-6"
$modelsYaml = Join-Path $cexRoot ".cex/config/nucleus_models.yaml"
if (Test-Path $modelsYaml) {
    try {
        $inBlock = $false
        foreach ($line in @(Get-Content $modelsYaml)) {
            if ($line -match '^n03:\s*$') { $inBlock = $true; continue }
            if ($inBlock -and $line -match '^\S') { break }   # next top-level key ends the block
            if ($inBlock -and $line -match '^  model:\s*([A-Za-z0-9._:/-]+)') {
                if ($Matches[1] -like "claude-*") { $model = $Matches[1] }
                break
            }
        }
    } catch {}
}
if ($env:CEX_MODEL_OVERRIDE) { $model = $env:CEX_MODEL_OVERRIDE }
$card = "N03_engineering/P08_architecture/agent_card_n03.md"

# --- Handoff detection (mission title only -- the nucleus reads the body itself) ---
$mission = ""
$handoffRel = ".cex/runtime/handoffs/n03_task.md"
$handoff = Join-Path $cexRoot ($handoffRel -replace '/', '\')
if (Test-Path $handoff) {
    foreach ($line in @(Get-Content $handoff -Head 10 -EA SilentlyContinue)) {
        if ($line -match "^mission:\s*(.+)$") { $mission = $Matches[1].Trim(); break }
    }
}

Write-Host ""
Write-Host "  CEX N03 Inventive Pride (Engineering)" -ForegroundColor Cyan
Write-Host "  root  : $cexRoot" -ForegroundColor DarkGray
Write-Host "  model : $model" -ForegroundColor DarkGray
if ($mission) { Write-Host "  mission: $mission" -ForegroundColor DarkGray }
Write-Host ""

# --- Pre-flight: Claude Code CLI must be on PATH ---
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] 'claude' CLI not found on PATH. Install Claude Code first." -ForegroundColor Red
    exit 1
}

# --- System prompt: ONE merged append (sin identity + agent card CONTENT) ---
# claude CLI facts: (1) the path-string form of --append-system-prompt injects the
# literal PATH text, never file content -- only the -file form injects CONTENT;
# (2) both forms are LAST-WINS across repeats; (3) the two forms are mutually
# exclusive. So the sin identity + the agent card CONTENT merge into ONE file,
# passed as a single flag. Degrade-never: a missing card only shrinks the merge;
# a failed write skips the append entirely -- boot itself never breaks.
$sysPrompt = "You are driven by Inventive Pride -- technical excellence and precision -- 8F is mandatory on every build. You are the N03 Engineering nucleus of this CEX tenant. Read CLAUDE.md and N03_engineering/rules/n03-builder.md before acting."
$appendFile = $null
try {
    $parts = @()
    $cardPath = Join-Path $cexRoot $card
    if (Test-Path $cardPath) {
        $parts += (Get-Content -Raw $cardPath)
    } else {
        Write-Host "[WARN] agent card not found: $card (merged append carries the identity only)" -ForegroundColor Yellow
    }
    $parts += $sysPrompt
    $cacheDir = Join-Path $cexRoot ".cex/cache/boot"
    New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
    $appendFile = Join-Path $cacheDir "append_final_n03.md"
    # UTF-8 WITHOUT BOM: the CLI append-file reader is byte-oriented (a BOM would leak U+FEFF).
    [System.IO.File]::WriteAllText($appendFile, ($parts -join "`n`n"), (New-Object System.Text.UTF8Encoding($false)))
} catch {
    $appendFile = $null
    Write-Host "[WARN] merged system-prompt append failed (launching without it)" -ForegroundColor Yellow
}

# --- Initial message: a dispatched nucleus self-discovers its own handoff ---
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
