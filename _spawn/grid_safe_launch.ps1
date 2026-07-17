# CEX Grid Safe Launch -- the gated launcher a LIVE boot-grid demo calls.
#
# Orchestrates a runaway-proof grid dispatch:
#   STEP 1  QUOTA GATE   -- probe claude via cex_quota_check.py; REFUSE if throttled.
#   STEP 2  WATCHDOG     -- start _spawn/grid_watchdog.ps1 as a background process.
#   STEP 3  DISPATCH     -- bash _spawn/dispatch.sh grid <Mission> (static, <=6 cells).
#   STEP 4  TEARDOWN     -- drop the watchdog stop-file, wait, report trip status.
#
# It REUSES (does not reimplement):
#   - _tools/cex_quota_check.py   (writes .cex/runtime/quota_cache.json)
#   - _spawn/grid_watchdog.ps1    (the circuit breaker)
#   - _spawn/dispatch.sh grid     (the real spawn entry; spawn_grid runs STATIC
#                                   for <=6 handoffs = one launch per cell, no
#                                   re-dispatch -- so no respawn runaway)
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/grid_safe_launch.ps1 -Mission MY_AUDIT
#   powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/grid_safe_launch.ps1 -Mission MY_AUDIT -ClaudeCeiling 12 -NodeCeiling 100
#   powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/grid_safe_launch.ps1 -Mission REHEARSAL -SkipQuotaGate
#   powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/grid_safe_launch.ps1 -Mission SELFTEST -SkipQuotaGate -DryRun
#
# -DryRun: exercises STEP 2 + STEP 4 wiring (watchdog start + stop-file teardown
#          + trip report) but SKIPS the real STEP 3 spawn. Required for safe
#          self-test, because spawn_grid.ps1 falls back to ALL handoffs when a
#          mission matches none -- a real run on a bogus mission would spawn the
#          entire stale-handoff backlog (exactly the runaway we guard against).
#
# Exit codes:
#   0 - grid dispatched (or dry-run completed); watchdog did NOT trip.
#   1 - REFUSED at quota gate (Anthropic Max throttled).
#   2 - watchdog TRIPPED during the run (runaway was caught + killed).

param(
    [Parameter(Mandatory = $true)]
    [string]$Mission,
    [int]$ClaudeCeiling = 12,
    [int]$NodeCeiling = 100,
    [switch]$SkipQuotaGate,
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"

$root        = Split-Path $PSScriptRoot -Parent
$runtime     = Join-Path $root ".cex\runtime"
$quotaCache  = Join-Path $runtime "quota_cache.json"
$stopFile    = Join-Path $runtime "grid_watchdog_stop"
$tripFile    = Join-Path $runtime "grid_watchdog_trip.json"
$watchdog    = Join-Path $PSScriptRoot "grid_watchdog.ps1"
$quotaTool   = Join-Path $root "_tools\cex_quota_check.py"

if (-not (Test-Path $runtime)) {
    New-Item -ItemType Directory -Force -Path $runtime | Out-Null
}

Write-Output "============================================================"
Write-Output "[SAFE-LAUNCH] mission=$Mission ceil claude=$ClaudeCeiling node=$NodeCeiling skip-quota=$($SkipQuotaGate.IsPresent) dry-run=$($DryRun.IsPresent)"
Write-Output "============================================================"

# ---------------------------------------------------------------------------
# STEP 1: QUOTA GATE
# ---------------------------------------------------------------------------
if ($SkipQuotaGate) {
    Write-Output "[GATE] SKIPPED (-SkipQuotaGate). Rehearsal mode -- not probing Anthropic Max."
} else {
    Write-Output "[GATE] probing claude via cex_quota_check.py (timeout 60s -- claude cold-start ~26s) ..."
    # cex_quota_check.py: --cli claude probes; --cache writes quota_cache.json.
    # --timeout 60: default 15s FALSE-TIMEOUTS on a healthy Max (cold-start loads MCP ~26s).
    # 60s lets a healthy cold-start pass while a real throttle (hangs) still trips -> refuse.
    & python $quotaTool --cli claude --timeout 60 --cache | Out-Null

    $claudeStatus = "unknown"
    if (Test-Path $quotaCache) {
        try {
            $cache = Get-Content $quotaCache -Raw | ConvertFrom-Json
            if ($cache.claude -and $cache.claude.status) {
                $claudeStatus = [string]$cache.claude.status
            }
        } catch {
            $claudeStatus = "unreadable"
        }
    } else {
        $claudeStatus = "no-cache"
    }

    if ($claudeStatus -ne "healthy") {
        Write-Output ""
        Write-Output "############################################################"
        Write-Output "## [GATE] Anthropic Max appears throttled (status=$claudeStatus)."
        Write-Output "## REFUSING boot-grid. Use the native-subagent fallback instead."
        Write-Output "############################################################"
        Write-Output ""
        exit 1
    }
    Write-Output "[GATE] quota OK -> proceeding (status=$claudeStatus)"
}

# ---------------------------------------------------------------------------
# STEP 2: START WATCHDOG (background)
# ---------------------------------------------------------------------------
# Remove any stale stop-file so the fresh watchdog does not insta-exit.
if (Test-Path $stopFile) {
    Remove-Item $stopFile -Force -EA SilentlyContinue
    Write-Output "[SAFE-LAUNCH] cleared stale stop-file"
}
# Remove any stale trip marker so the post-run check reflects THIS run.
if (Test-Path $tripFile) {
    Remove-Item $tripFile -Force -EA SilentlyContinue
}

Write-Output "[SAFE-LAUNCH] starting watchdog (background): claude>$ClaudeCeiling or node>$NodeCeiling => tree-kill"

# SAFETY (2026-06-04): belt-and-suspenders with spawn_stop's --print filter.
# When the watchdog trips it calls `spawn_stop -All`, whose blind orphan sweep
# could (in a broken-ancestry launch) reach the LIVE orchestrator (N07 claude).
# Export the N07 claude PID as CEX_PROTECT_PID into the watchdog's environment so
# spawn_stop's ProtectedPids guard can never tree-kill it. Resolve it by walking
# OUR ancestry (this script runs as N07 claude -> bash -> powershell) for the
# first interactive claude.exe. If the walk fails (Bash-tool launches break the
# chain), fall back to ANY interactive (non --print) claude PID. If still none,
# preserve any caller-set CEX_PROTECT_PID and move on (the watchdog inherits it).
$priorProtect = $env:CEX_PROTECT_PID
$n07Pid = $null
$__cur = $PID
for ($__i = 0; $__i -lt 20; $__i++) {
    $__p = Get-CimInstance Win32_Process -Filter "ProcessId=$__cur" -EA SilentlyContinue
    if (-not $__p) { break }
    if (($__p.Name -replace '\.exe$','').ToLower() -eq 'claude') { $n07Pid = [int]$__p.ProcessId; break }
    $__cur = [int]$__p.ParentProcessId
    if ($__cur -eq 0) { break }
}
if (-not $n07Pid) {
    # Ancestry walk missed it (e.g. Bash-tool launch). Fall back to the interactive
    # claude.exe (CommandLine without --print -- a --print process is a quota probe,
    # not the orchestrator).
    $cand = Get-CimInstance Win32_Process -Filter "Name='claude.exe'" -EA SilentlyContinue |
        Where-Object { -not ($_.CommandLine -match '--print') } |
        Select-Object -First 1
    if ($cand) { $n07Pid = [int]$cand.ProcessId }
}
$protectList = @()
if ($priorProtect) { $protectList += ($priorProtect -split '[,; ]+' | Where-Object { $_ -match '^\d+$' }) }
if ($n07Pid) {
    $protectList += "$n07Pid"
    Write-Output "[SAFE-LAUNCH] orchestrator PID:$n07Pid -> CEX_PROTECT_PID (watchdog will not tree-kill it)"
} else {
    # TODO(2026-06-04): could not resolve the live N07 claude PID via ancestry or
    # interactive-process scan. The watchdog still relies on spawn_stop's own
    # ancestry-based ProtectedPids guard for self-protection.
    Write-Output "[SAFE-LAUNCH] WARN: could not resolve N07 claude PID -- relying on spawn_stop ancestry guard only"
}
$env:CEX_PROTECT_PID = ($protectList | Select-Object -Unique) -join ','

$wdArgs = @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $watchdog,
    "-ClaudeCeiling", $ClaudeCeiling,
    "-NodeCeiling", $NodeCeiling
)
$wdProc = Start-Process -FilePath "powershell" -ArgumentList $wdArgs -PassThru -WindowStyle Hidden
Write-Output "[SAFE-LAUNCH] watchdog PID:$($wdProc.Id)"

# Restore our own CEX_PROTECT_PID so the rest of this script's environment is
# unchanged (the watchdog already captured its snapshot at Start-Process time).
if ($priorProtect) { $env:CEX_PROTECT_PID = $priorProtect }
else { Remove-Item Env:CEX_PROTECT_PID -ErrorAction SilentlyContinue }

# ---------------------------------------------------------------------------
# STEP 3: REAL DISPATCH
# ---------------------------------------------------------------------------
if ($DryRun) {
    Write-Output "[SAFE-LAUNCH] [DRY] would run: bash _spawn/dispatch.sh grid $Mission"
    Write-Output "[SAFE-LAUNCH] [DRY] skipping real spawn (self-test wiring check only)"
    Start-Sleep -Seconds 2
} else {
    Write-Output "[SAFE-LAUNCH] dispatching: bash _spawn/dispatch.sh grid $Mission"
    # spawn_grid runs STATIC for <=6 handoffs: each cell launched exactly once.
    & bash _spawn/dispatch.sh grid $Mission
    $dispatchRc = $LASTEXITCODE
    Write-Output "[SAFE-LAUNCH] dispatch returned rc=$dispatchRc"
}

# ---------------------------------------------------------------------------
# STEP 4: TEARDOWN -- signal watchdog to exit cleanly, wait, report.
# ---------------------------------------------------------------------------
Write-Output "[SAFE-LAUNCH] grid dispatch finished -> dropping watchdog stop-file"
Set-Content -Path $stopFile -Value "stop" -Encoding ASCII

# Give the watchdog up to ~8s to notice the stop-file and exit.
$waited = 0
while ($waited -lt 8) {
    if ($wdProc.HasExited) { break }
    Start-Sleep -Seconds 1
    $waited++
}
if (-not $wdProc.HasExited) {
    Write-Output "[SAFE-LAUNCH] [WARN] watchdog still alive after ${waited}s -- forcing stop"
    Stop-Process -Id $wdProc.Id -Force -EA SilentlyContinue
}

$tripped = $false
$wdExit  = if ($wdProc.HasExited) { $wdProc.ExitCode } else { "n/a" }
if (Test-Path $tripFile) {
    $tripped = $true
}

# Clean up our stop-file so the next launch starts fresh.
if (Test-Path $stopFile) { Remove-Item $stopFile -Force -EA SilentlyContinue }

Write-Output "============================================================"
Write-Output "[SAFE-LAUNCH] SUMMARY"
Write-Output "  mission       : $Mission"
Write-Output "  quota gate    : $(if ($SkipQuotaGate) { 'skipped' } else { 'passed (healthy)' })"
Write-Output "  watchdog PID  : $($wdProc.Id) (exit=$wdExit)"
Write-Output "  ceilings      : claude>$ClaudeCeiling node>$NodeCeiling"
Write-Output "  dry-run       : $($DryRun.IsPresent)"
if ($tripped) {
    Write-Output "  result        : [TRIP] watchdog caught a runaway -- grid was tree-killed ($tripFile)"
} else {
    Write-Output "  result        : [OK] no runaway; watchdog clean exit"
}
Write-Output "============================================================"

if ($tripped) { exit 2 } else { exit 0 }
