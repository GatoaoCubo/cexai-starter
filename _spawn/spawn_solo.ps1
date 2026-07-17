# CEX Spawn Solo v4.1 -- reads nucleus_models.yaml (single source of truth)
# v4.1: added -Model param for orchestrator override (sets CEX_MODEL_OVERRIDE)
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('n01','n02','n03','n04','n05','n06','n07')]
    [string]$nucleus,
    [string]$task = "",
    [string]$Model = "",    # Model override -- sets CEX_MODEL_OVERRIDE env var
    [switch]$interactive,
    [ValidateSet('claude','gemini','codex','ollama','litellm','auto')]
    [string]$cli = ""   # if empty, read from nucleus_models.yaml
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int W, int H, bool r);
}
"@

# Dynamic grid: detect screen size, adaptive layout
# Supports N01-N07. Taskbar-aware via WorkingArea.
# Layout adapts: 3x2 for N01-N06, 4x2 when N07 included.
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$ox = $screen.X; $oy = $screen.Y

# Adaptive cell map -- 4x2 grid supports all 7 nuclei
# When N07 is absent, columns 0-2 of row 0-1 fill a 3x2 naturally.
#
# +--------+--------+--------+--------+
# |  N01   |  N02   |  N03   |  N07   |  row 0
# +--------+--------+--------+--------+
# |  N04   |  N05   |  N06   |        |  row 1
# +--------+--------+--------+--------+
#
$fixedCells = @{
    n01 = @{col=0; row=0}
    n02 = @{col=1; row=0}
    n03 = @{col=2; row=0}
    n04 = @{col=0; row=1}
    n05 = @{col=1; row=1}
    n06 = @{col=2; row=1}
    n07 = @{col=3; row=0}
}

# Auto-detect grid dimensions from which nuclei are active
# Check PID file for nuclei in current session + the one being spawned
$activeNuclei = @($nucleus)
$tmpPidFile = "$runtimeDir\pids\spawn_pids.txt"  # declared below, but path is predictable
$tmpPidFile = "$(Split-Path $PSScriptRoot -Parent)\.cex\runtime\pids\spawn_pids.txt"
if (Test-Path $tmpPidFile) {
    foreach ($pidLine in Get-Content $tmpPidFile) {
        if ($pidLine -match "^\s*(\d+)\s+(n0[1-7])") {
            $pNuc = $matches[2]
            $pPid = [int]$matches[1]
            if ((Get-Process -Id $pPid -EA SilentlyContinue) -and $pNuc -ne $nucleus) {
                $activeNuclei += $pNuc
            }
        }
    }
}
$hasN07 = $activeNuclei -contains "n07"
$cols = if ($hasN07) { 4 } else { 3 }
$rows = 2
$cellW = [math]::Floor($screen.Width / $cols)
$cellH = [math]::Floor($screen.Height / $rows)

# Build position map
$grid = @{}
foreach ($nuc in $fixedCells.Keys) {
    $c = $fixedCells[$nuc]
    $grid[$nuc] = @{x=$ox + $c.col * $cellW; y=$oy + $c.row * $cellH}
}

$root = Split-Path $PSScriptRoot -Parent
$pos = $grid[$nucleus]
$upper = $nucleus.ToUpper()
$runtimeDir = "$root\.cex\runtime"

New-Item -ItemType Directory -Force -Path "$runtimeDir\handoffs","$runtimeDir\signals","$runtimeDir\pids" | Out-Null

# -- CLI selection --
# If -cli was passed explicitly, honor it (enables `dispatch.sh solo-ollama n04`).
# Otherwise read from nucleus_models.yaml (single source of truth).
if (-not $cli) {
    $cli = "claude"  # fallback
    $modelsFile = "$root\.cex\config\nucleus_models.yaml"
    if (Test-Path $modelsFile) {
        $inNucleus = $false
        foreach ($line in Get-Content $modelsFile) {
            if ($line -match "^${nucleus}:") { $inNucleus = $true; continue }
            if ($inNucleus -and $line -match "^\w" -and $line -notmatch "^\s") { break }
            if ($inNucleus -and $line -match "^\s+cli:\s*(.+)") {
                $cli = $matches[1].Trim()
                break
            }
        }
    }
    Write-Output "[$upper] CLI from nucleus_models: $cli"
} else {
    Write-Output "[$upper] CLI from -cli arg: $cli"
}

# Write handoff if task provided
if ($task) {
    $handoffPath = "$runtimeDir\handoffs\${nucleus}_task.md"

    # --- HANDOFF GUARD BEGIN (handoff-clobber fix 2026-06-11) ---
    # BUG (root-caused live, feedback_grid_git_race_and_dispatch_stub): this block
    # used to write the stub UNCONDITIONALLY, clobbering a FULL handoff the
    # orchestrator pre-placed at n0X_task.md before dispatch (wave-5 drift:
    # 3/5 nuclei executed stub tasks instead of the real spec).
    # GUARD: preserve the existing file when it looks like a real handoff
    # (length > 400 bytes OR a line matching '^task: dispatch') AND it is fresh
    # (LastWriteTime within the last 30 minutes). Anything else falls through to
    # the stub write -- the stub IS the correct fallback when no fresh real
    # handoff exists.
    $preserveExisting = $false
    if (Test-Path $handoffPath) {
        $handoffItem = Get-Item $handoffPath
        $handoffBytes = [long]$handoffItem.Length
        $handoffAgeMin = ((Get-Date) - $handoffItem.LastWriteTime).TotalMinutes
        $looksFull = ($handoffBytes -gt 400)
        if (-not $looksFull) {
            # BOM-tolerant marker scan: a UTF-8 BOM can surface as U+FEFF on the
            # first decoded line; strip it before matching (mirrors dispatch.sh
            # _strip_pid_line, which normalizes the same BOM on PID-file lines).
            foreach ($hLine in @(Get-Content -Path $handoffPath -ErrorAction SilentlyContinue)) {
                $hClean = $hLine.TrimStart([char]0xFEFF)
                if ($hClean -match '^task:\s*dispatch') { $looksFull = $true; break }
            }
        }
        if ($looksFull -and $handoffAgeMin -le 30) {
            $preserveExisting = $true
            $handoffAgeStr = [math]::Round($handoffAgeMin, 1)
            Write-Output "[SPAWN] existing handoff preserved (${handoffBytes}B, ${handoffAgeStr}min old)"
        }
    }
    # --- HANDOFF GUARD END ---

    if ($preserveExisting) {
        # WS5.0: variant boots (gemini/codex/ollama/litellm) read
        # n0X_task_<cli>.md, NOT the unsuffixed file. Mirror the PRESERVED
        # handoff there so the variant boot still receives the real task
        # (skipping entirely would regress WS5.0 back to "no dispatched task").
        if ($cli -and $cli -ne "claude") {
            $variantHandoff = "$runtimeDir\handoffs\${nucleus}_task_${cli}.md"
            Copy-Item -Path $handoffPath -Destination $variantHandoff -Force
            Write-Output "[$upper] Handoff (variant, preserved): $variantHandoff"
        }
    } else {
        # Check if decision manifest exists
        $manifestPath = "$runtimeDir\decisions\decision_manifest.yaml"
        $manifestBlock = ""
        if (Test-Path $manifestPath) {
            $manifestBlock = @"

## DECISIONS (from user -- DO NOT re-ask)
Read: .cex/runtime/decisions/decision_manifest.yaml
All subjective decisions were already made with the user.
Execute using those decisions. Do NOT override them.
"@
        }

        $handoffContent = @"
---
nucleus: $upper
task: dispatch
created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
---
# Task for $upper

$task
$manifestBlock

## ON COMPLETION
1. Commit your work: git add -A ; git commit -m "[$upper] <description>"
2. Signal complete:

## SIGNAL
python -c "from _tools.signal_writer import write_signal; write_signal('$nucleus', 'complete', 9.0)"
"@
        # Claude path: unsuffixed handoff (byte-identical to legacy behavior).
        $handoffContent | Set-Content -Path $handoffPath -Encoding UTF8
        Write-Output "[$upper] Handoff: $handoffPath"
        # WS5.0 fix (lr_runtime_failure_n04_gemini_boot_20260609): the variant boots
        # (gemini/codex/ollama/litellm) read ${nucleus}_task_<cli>.md. spawn_solo previously
        # wrote ONLY the unsuffixed file, so `solo -cli <cli>` left the variant boot with no
        # dispatched task (it fell back to a stale package). When -cli != claude, ALSO write
        # the suffixed copy so the variant boot finds the REAL task.
        if ($cli -and $cli -ne "claude") {
            $variantHandoff = "$runtimeDir\handoffs\${nucleus}_task_${cli}.md"
            $handoffContent | Set-Content -Path $variantHandoff -Encoding UTF8
            Write-Output "[$upper] Handoff (variant): $variantHandoff"
        }
    }
}

# Kill-before-spawn (roadmap principle 6)
$pidFile = "$runtimeDir\pids\spawn_pids.txt"
if (Test-Path $pidFile) {
    $surviving = @()
    foreach ($line in Get-Content $pidFile) {
        if ($line -match "^\s*(\d+)\s+$nucleus\s") {
            $oldPid = [int]$matches[1]
            Write-Output "[$upper] Killing existing PID:$oldPid before respawn"
            & taskkill /F /PID $oldPid /T 2>$null
        } else {
            $surviving += $line
        }
    }
    if ($surviving.Count -gt 0) {
        $surviving | Set-Content $pidFile -Encoding UTF8
    } else {
        Remove-Item $pidFile -Force
    }
}

# Boot script -- PowerShell-only stack (sin-aware UX: colors, sizing, banner)
# Per-CLI suffix: claude -> n0X.ps1 | gemini -> n0X_gemini.ps1 | ollama -> n0X_ollama.ps1
$cliSuffix = if ($cli -eq "claude") { "" } else { "_$cli" }
$bootPs1 = "$root\boot\${nucleus}${cliSuffix}.ps1"

if (Test-Path $bootPs1) {
    # Model override: set env var that resolve_model.ps1 checks (highest priority)
    if ($Model) {
        $env:CEX_MODEL_OVERRIDE = $Model
        Write-Output "[$upper] Model override: $Model (via CEX_MODEL_OVERRIDE)"
    }
    # Signal boot script to skip self-sizing (spawn_solo controls window position)
    $env:CEX_GRID = "1"
    $env:CEX_GRID_W = "$cellW"
    $env:CEX_GRID_H = "$cellH"
    Write-Output "[$upper] Boot: PowerShell (sin-aware UX)"
    $proc = Start-Process powershell -ArgumentList @(
        "-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass",
        "-File", $bootPs1
    ) -WorkingDirectory $root -PassThru
} else {
    Write-Output "[$upper] ERROR: no boot script at $bootPs1"; exit 1
}

# Position window in fixed grid cell (retry loop for window handle)
if ($proc -and $pos) {
    $hwnd = [IntPtr]::Zero
    for ($i = 0; $i -lt 10; $i++) {
        Start-Sleep -Milliseconds 500
        try { $proc.Refresh() } catch {}
        $hwnd = $proc.MainWindowHandle
        if ($hwnd -ne [IntPtr]::Zero) { break }
    }
    if ($hwnd -ne [IntPtr]::Zero) {
        [Win32]::MoveWindow($hwnd, $pos.x, $pos.y, $cellW, $cellH, $true) | Out-Null
    } else {
        Write-Output "[$upper] WARN: no window handle after 5s -- window not positioned"
    }
}

# Record PID with session tracking
# Session ID = PID of the PowerShell/pi that called us (our parent orchestrator)
$sessionId = $env:CEX_SESSION_ID
if (-not $sessionId) {
    # Auto-detect: use parent process PID as session identifier
    $myPid = $PID
    $parentPid = (Get-CimInstance Win32_Process -Filter "ProcessId=$myPid" -EA SilentlyContinue).ParentProcessId
    $sessionId = "s$parentPid"
}
$timestamp = Get-Date -Format "yyyy-MM-dd_HH:mm:ss"
"$($proc.Id) $nucleus $cli $sessionId $timestamp" | Add-Content $pidFile
Write-Output "[$upper] Spawned PID:$($proc.Id) CLI:$cli Session:$sessionId at ($($pos.x),$($pos.y))"
