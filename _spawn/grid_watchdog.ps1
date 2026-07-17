# CEX Grid Watchdog -- runaway circuit breaker for LIVE boot-grid demos.
#
# WHY: 2026-06-03 a 2-cell grid under Anthropic Max rate-limit ballooned to
# ~24 claude.exe + ~196 node.exe (orphan -NoExit wrappers + manual retries +
# MCP node fan-out). This watchdog polls process counts and hard-kills the
# WHOLE grid the moment it explodes, so an on-camera demo cannot run away.
#
# It does NOT spawn anything. It only WATCHES and (on trip) calls the existing
# tree-killer _spawn/spawn_stop.ps1 -All. Safe to run when nothing is happening:
# counts stay low and it clean-exits at -MaxMinutes.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/grid_watchdog.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/grid_watchdog.ps1 -ClaudeCeiling 12 -NodeCeiling 100
#   powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/grid_watchdog.ps1 -MaxMinutes 0.05 -PollSeconds 1   # self-test
#
# Exit codes:
#   0 - clean exit (MaxMinutes elapsed OR stop-file appeared). No trip.
#   2 - TRIP: runaway detected, grid tree-killed, marker written.

param(
    [int]$ClaudeCeiling = 12,
    [int]$NodeCeiling = 100,
    [double]$PollSeconds = 3,
    [int]$TripConsecutive = 2,
    [double]$MaxMinutes = 20,
    [string]$Session = $env:CEX_SESSION_ID
)

$ErrorActionPreference = "Continue"

$root      = Split-Path $PSScriptRoot -Parent
$runtime   = Join-Path $root ".cex\runtime"
$stopFile  = Join-Path $runtime "grid_watchdog_stop"
$tripFile  = Join-Path $runtime "grid_watchdog_trip.json"
$stopScript = Join-Path $PSScriptRoot "spawn_stop.ps1"

# Ensure runtime dir exists (so marker write never fails).
if (-not (Test-Path $runtime)) {
    New-Item -ItemType Directory -Force -Path $runtime | Out-Null
}

# Fresh run: clear any stale trip marker from a previous run so the launcher's
# post-run "did it trip?" check reflects THIS run only.
if (Test-Path $tripFile) { Remove-Item $tripFile -Force -EA SilentlyContinue }

function Get-ProcCount {
    param([string]$Name)
    $procs = @(Get-Process -Name $Name -ErrorAction SilentlyContinue)
    return $procs.Count
}

$sessLabel = if ($Session) { $Session } else { "none" }
Write-Output "[WATCHDOG] start ceil claude=$ClaudeCeiling node=$NodeCeiling poll=${PollSeconds}s trip-after=$TripConsecutive max=${MaxMinutes}min session=$sessLabel"

$start          = Get-Date
$deadline       = $start.AddMinutes($MaxMinutes)
$breachStreak   = 0

while ($true) {
    $now     = Get-Date
    $elapsed = [math]::Round(($now - $start).TotalSeconds, 1)

    # --- Clean-exit conditions (checked BEFORE counting so a finished grid that
    # dropped the stop-file exits immediately) ---
    if (Test-Path $stopFile) {
        Write-Output "[WATCHDOG] clean exit (stop-file) t=${elapsed}s"
        exit 0
    }
    if ($now -ge $deadline) {
        Write-Output "[WATCHDOG] clean exit (max ${MaxMinutes}min reached) t=${elapsed}s"
        exit 0
    }

    # --- Count ---
    $claude = Get-ProcCount -Name "claude"
    $node   = Get-ProcCount -Name "node"

    $breached = ($claude -gt $ClaudeCeiling) -or ($node -gt $NodeCeiling)
    if ($breached) { $breachStreak++ } else { $breachStreak = 0 }

    $flag = if ($breached) { " BREACH($breachStreak/$TripConsecutive)" } else { "" }
    Write-Output "[WATCHDOG] claude=$claude node=$node (ceil $ClaudeCeiling/$NodeCeiling) t=${elapsed}s$flag"

    # --- Trip ---
    if ($breachStreak -ge $TripConsecutive) {
        Write-Output "[TRIP] runaway detected claude=$claude node=$node (ceil $ClaudeCeiling/$NodeCeiling) after $breachStreak consecutive polls"

        # On-camera safety beats session-scoping: full tree-kill of ALL CEX nuclei.
        if (Test-Path $stopScript) {
            Write-Output "[TRIP] invoking $stopScript -All (full tree-kill)"
            & powershell -NoProfile -ExecutionPolicy Bypass -File $stopScript -All
        } else {
            Write-Output "[TRIP] [FAIL] spawn_stop.ps1 not found at $stopScript -- cannot tree-kill"
        }

        $marker = [ordered]@{
            tripped   = $true
            claude    = $claude
            node      = $node
            ceil_claude = $ClaudeCeiling
            ceil_node   = $NodeCeiling
            streak    = $breachStreak
            session   = $sessLabel
            timestamp = (Get-Date -Format o)
        }
        $marker | ConvertTo-Json | Set-Content $tripFile -Encoding UTF8
        Write-Output "[TRIP] marker written: $tripFile"
        exit 2
    }

    Start-Sleep -Seconds $PollSeconds
}
