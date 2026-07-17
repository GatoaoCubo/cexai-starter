# CEX Spawn Grid v1.0 -- Launch multiple nucleus builders
# Usage:
#   powershell -File _spawn/spawn_grid.ps1 -mission NAME -interactive
#   powershell -File _spawn/spawn_grid.ps1 -mission NAME -mode continuous

param(
    [string]$mission = "",
    [ValidateSet('auto','static','continuous')]
    [string]$mode = "auto",
    [switch]$interactive,
    [int]$pollSeconds = 30,
    [int]$maxMinutes = 45,
    [int]$maxSlots = 6,
    [ValidateSet('claude','gemini','codex','ollama','litellm','auto')]
    [string]$cli = "claude",
    [string]$Model = ""
)

# -Model overrides model in boot/n0X.ps1 via CEX_MODEL_OVERRIDE env.
# Used by grid-haiku to run Haiku instead of default Opus.
if ($Model) {
    $env:CEX_MODEL_OVERRIDE = $Model
    Write-Output "[GRID] Model override active: CEX_MODEL_OVERRIDE=$Model"
}

# Multi-CLI config (3 routing levels):
#   L1 explicit: -cli claude|gemini|codex -- operator override, global for this grid
#   L2 auto:     -cli auto -- resolver picks per-nucleus from nucleus_models.yaml
#                              (primary + fallback_chain, binary pre-check). The
#                              resolver now ALSO consults persisted health signal
#                              (W2): a runtime with recorded failures / quota
#                              exhaustion is demoted. Record outcomes with:
#                              python _tools/cex_cli_resolver.py --record <cli> [--fail] [--ms N]
#                              Opt out: CEX_HEALTH_ROUTER=0 (byte-identical L2).
#   L3 router:   cex_router.py -- the scoring/EMA engine the L2 resolver wires in;
#                              also used directly by cex_mission_runner.py.
#
# Per-CLI boot + handoff suffix mapping:
#   claude -> boot/n0X.ps1        + handoff copy .cex/runtime/handoffs/n0X_task.md
#   gemini -> boot/n0X_gemini.ps1 + handoff copy .cex/runtime/handoffs/n0X_task_gemini.md
#   codex  -> boot/n0X_codex.ps1  + handoff copy .cex/runtime/handoffs/n0X_task_codex.md
$globalCli = $cli
$cliSuffix = if ($cli -eq "claude") { "" }
             elseif ($cli -eq "auto") { "" }  # placeholder; real suffix resolved per-nucleus
             else { "_$cli" }

# --- Per-cell cli-map (SHOWOFF_V2+) ---
# When CEX_GRID_CLIMAP env var points at a JSON file, each cell's cli + model
# come from the map (per nucleus key) instead of the global -cli flag.
# Format: { "n01": {"cli": "claude", "model": "..."}, "n02": {"cli": "gemini", "model": "..."}, ... }
# Set by dispatch.sh via --cli-map flag or .cex/runtime/cli_maps/{MISSION}.json convention.
$cliMap = @{}
if ($env:CEX_GRID_CLIMAP -and (Test-Path $env:CEX_GRID_CLIMAP)) {
    try {
        $cliMapJson = Get-Content $env:CEX_GRID_CLIMAP -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($prop in $cliMapJson.PSObject.Properties) {
            $cliMap[$prop.Name.ToLower()] = @{
                cli = if ($prop.Value.cli) { $prop.Value.cli } else { "claude" }
                model = if ($prop.Value.model) { $prop.Value.model } else { "" }
            }
        }
        Write-Output "[GRID] cli-map loaded: $($cliMap.Count) entries from $($env:CEX_GRID_CLIMAP)"
        foreach ($k in $cliMap.Keys) {
            Write-Output "  [$($k.ToUpper())] cli=$($cliMap[$k].cli) model=$($cliMap[$k].model)"
        }
    } catch {
        Write-Output "[GRID] WARN: failed to parse cli-map $($env:CEX_GRID_CLIMAP): $_"
        $cliMap = @{}
    }
}

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Grid {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int W, int H, bool r);
}
"@

$root = Split-Path $PSScriptRoot -Parent
$handoffDir = "$root\.cex/runtime/handoffs"
$signalDir = "$root\.cex/runtime/signals"
$pidFile = "$root\.cex\runtime\pids\spawn_pids.txt"

New-Item -ItemType Directory -Force -Path $handoffDir,$signalDir,"$root\.cex\runtime\pids" | Out-Null

# Dynamic grid: detect screen size, adapt layout to nucleus count
Add-Type -AssemblyName System.Windows.Forms
$scr = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$gOx = $scr.X; $gOy = $scr.Y

# gridPos is computed AFTER handoff discovery (see below)
$gridPos = @{}

# Discover handoffs for mission
$handoffs = @()
if ($mission) {
    $handoffs = @(Get-ChildItem "$handoffDir\${mission}_*.md" -EA SilentlyContinue | Sort-Object Name)
    # RUNAWAY GUARD (2026-06-04): a NAMED mission that matches ZERO handoffs must
    # ABORT -- NOT fall back to globbing every *.md in the handoff dir. The glob-all
    # fallback is the documented fork-bomb: 195 stale handoffs -> mass launch. Only
    # the unnamed (no -mission) case may glob-all (it is the explicit "launch
    # whatever is queued" path).
    if ($handoffs.Count -eq 0) {
        Write-Output "[GRID] ABORT: mission '$mission' matched 0 handoffs ($handoffDir\${mission}_*.md)."
        Write-Output "[GRID] Refusing glob-all fallback (would mass-launch every stale handoff -- the documented runaway)."
        Write-Output "[GRID] Write the mission's handoffs first, or fix the mission name."
        exit 1
    }
} else {
    $handoffs = @(Get-ChildItem "$handoffDir\*.md" -EA SilentlyContinue | Sort-Object Name)
}

if ($handoffs.Count -eq 0) {
    Write-Output "[GRID] No handoffs found in $handoffDir"
    exit 1
}

# Auto-detect mode
if ($mode -eq "auto") {
    $mode = if ($handoffs.Count -gt $maxSlots) { "continuous" } else { "static" }
}
# Adaptive grid layout -- each nucleus has a PERMANENT cell
# Layout adapts: 3x2 for N01-N06, 4x2 when N07 is included
#
#   3x2 (default):                4x2 (with N07):
#   +------+------+------+       +-----+-----+-----+-----+
#   | N01  | N02  | N03  |       | N01 | N02 | N03 | N07 |
#   +------+------+------+       +-----+-----+-----+-----+
#   | N04  | N05  | N06  |       | N04 | N05 | N06 |     |
#   +------+------+------+       +-----+-----+-----+-----+
#
$n = $handoffs.Count

# Fixed cell map: nucleus -> (col, row) -- stable identity by position
$fixedCells = @{
    "n01" = @{col=0; row=0}
    "n02" = @{col=1; row=0}
    "n03" = @{col=2; row=0}
    "n04" = @{col=0; row=1}
    "n05" = @{col=1; row=1}
    "n06" = @{col=2; row=1}
    "n07" = @{col=3; row=0}
}

# Auto-detect: if any handoff targets N07, use 4 columns.
# DISPATCH_FIX (spec_dispatch_grid_fix v1.0.0): scan ALL segments for n07,
# not just the last one -- handoffs like MISSION_n07_celldisc_task.md would
# otherwise be missed (parts[-1] = "task" or "celldisc").
$hasN07 = $false
foreach ($h in $handoffs) {
    $parts = [System.IO.Path]::GetFileNameWithoutExtension($h.Name) -split '_'
    foreach ($p in $parts) {
        if ($p -eq "n07") { $hasN07 = $true; break }
    }
    if ($hasN07) { break }
}
$gCols = if ($hasN07) { 4 } else { 3 }
$gRows = 2
$gW = [math]::Floor($scr.Width / $gCols)
$gH = [math]::Floor($scr.Height / $gRows)

# Build position map from fixed cells.
# DISPATCH_FIX (spec_dispatch_grid_fix v1.0.0): scan all segments for n0X token,
# not just $parts[-1] -- the last-segment heuristic returned "task" for handoffs
# like MISSION_n03_anuncio_task.md and stacked every cell at (0,0).
foreach ($h in $handoffs) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($h.Name)
    $parts = $base -split '_'
    $nuc = ""
    foreach ($p in $parts) {
        if ($p -match '^n[0-9]+$') { $nuc = $p; break }
    }
    if (-not $nuc) { $nuc = $parts[-1] }  # legacy fallback
    $cell = $fixedCells[$nuc]
    if ($cell) {
        $gridPos[$nuc] = @{x=$gOx + $cell.col * $gW; y=$gOy + $cell.row * $gH}
    } else {
        # Unknown nucleus -- fallback to first empty cell
        $gridPos[$nuc] = @{x=$gOx; y=$gOy}
    }
}

Write-Output "[GRID] Mission: $mission | Mode: $mode | Handoffs: $n | Layout: ${gCols}x${gRows}"

# Extract nucleus from handoff filename.
# DISPATCH_FIX (spec_dispatch_grid_fix v1.0.0): scan for n0X token anywhere in
# the basename. The old `$parts[-1]` heuristic broke when handoffs ended in
# `_task.md` (cell-discriminated grid like CODEXA_V2_WAVE_B_n03_anuncio_task.md
# returned "task" instead of "n03"). Supported patterns:
#   MISSION_n0X.md                      -> n0X      (legacy)
#   MISSION_n0X_task.md                 -> n0X      (single cell, _task suffix)
#   MISSION_n0X_celldisc_task.md        -> n0X      (cell-discriminated parallel)
function Get-NucleusFromHandoff($filename) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($filename)
    $parts = $base -split '_'
    foreach ($p in $parts) {
        if ($p -match '^n[0-9]+$') { return $p }
    }
    return $parts[-1]  # legacy fallback (should not happen for valid handoffs)
}

# Extract cell_slug from handoff filename: everything between MISSION_ prefix
# and optional _task suffix. Used to derive a unique worktree path per cell so
# same-nucleus parallel grids (3x n03) land in `wt_n03_anuncio`, `wt_n03_pesquisa`,
# `wt_n03_imagens` instead of colliding on `wt_n03`.
#   INIT_WAVE_A_n04               -> n04         (legacy, no _task; slug == nucleus)
#   DISPATCH_FIX_n03_task         -> n03         (single cell with _task)
#   CODEXA_V2_WAVE_B_n03_anuncio_task -> n03_anuncio  (cell-disc'd)
function Get-CellSlugFromHandoff($filename, $missionName) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($filename)
    if ($missionName -and $base.StartsWith("${missionName}_")) {
        $base = $base.Substring($missionName.Length + 1)
    }
    if ($base.EndsWith('_task')) {
        $base = $base.Substring(0, $base.Length - 5)
    }
    return $base
}

# Walk process tree recursively from a parent PID, return all descendant PIDs
# Fix for "wrapper PID pitfall" -- Start-Process -PassThru returns the wrapper
# powershell.exe PID, NOT the actual worker (claude.exe/codex.exe/node.exe).
# We need the grandchildren/great-grandchildren to track real liveness.
function Get-DescendantPids($parentId) {
    $allProcs = Get-CimInstance Win32_Process -EA SilentlyContinue
    $result = @()
    $queue = [System.Collections.Queue]::new()
    $queue.Enqueue($parentId)
    while ($queue.Count -gt 0) {
        $current = $queue.Dequeue()
        $kids = $allProcs | Where-Object { $_.ParentProcessId -eq $current }
        foreach ($k in $kids) {
            $result += [PSCustomObject]@{
                Id = [int]$k.ProcessId
                Name = ($k.Name -replace '\.exe$','').ToLower()
                Parent = [int]$current
            }
            $queue.Enqueue([int]$k.ProcessId)
        }
    }
    return $result
}

# Resolve CLI for a nucleus via YAML fallback chain + binary pre-check.
# Called when $globalCli -eq "auto". Returns hashtable @{cli=..; model=..; flags=..; chain_step=..}
# or $null if no working CLI in the chain.
function Resolve-NucleusCli($nucleus) {
    $resolverScript = "$root\_tools\cex_cli_resolver.py"
    if (-not (Test-Path $resolverScript)) {
        Write-Output "  [WARN] resolver missing, falling back to claude: $resolverScript"
        return @{cli="claude"; chain_step="default"}
    }
    try {
        $raw = & python $resolverScript --nucleus $nucleus --pre-check --json 2>&1
        $json = $raw -join "`n" | ConvertFrom-Json
        if ($json.error) {
            Write-Output "  [WARN] resolver error for ${nucleus}: $($json.error)"
            return $null
        }
        return @{
            cli = $json.cli
            model = $json.model
            flags = $json.flags
            chain_step = $json.chain_step
        }
    } catch {
        Write-Output "  [WARN] resolver failed for ${nucleus}: $_"
        return @{cli="claude"; chain_step="default"}
    }
}

# Find worker PIDs (claude/codex/gemini/node) that are descendants of a wrapper.
# Returns comma-separated PID list, "-" if none found.
function Find-WorkerPids($wrapperPid, $cli) {
    $targetNames = switch ($cli) {
        "claude"  { @("claude","node") }
        "gemini"  { @("gemini","node") }
        "codex"   { @("codex") }
        "ollama"  { @("python") }
        "litellm" { @("python") }
        "openai"  { @("powershell") }  # image-gen runs in the wrapper itself, no separate worker
        default   { @("claude","codex","gemini","node","python","powershell") }
    }
    $descendants = Get-DescendantPids $wrapperPid
    $workers = $descendants | Where-Object { $targetNames -contains $_.Name }
    if ($workers.Count -eq 0) { return "-" }
    return ($workers | ForEach-Object { $_.Id }) -join ","
}

# Launch a single nucleus with handoff
function Launch-Nucleus($handoff) {
    $nucleus = Get-NucleusFromHandoff $handoff.Name
    $upper = $nucleus.ToUpper()
    $pos = $gridPos[$nucleus]
    if (-not $pos) { $pos = @{x=0; y=0} }

    # Resolve CLI: cli-map (L1.5) > explicit (L1) > auto YAML (L2)
    $effectiveCli = $globalCli
    $effectiveModel = ""  # per-cell model from cli-map (overrides CEX_MODEL_OVERRIDE for THIS cell only)
    $chainStep = "explicit"
    if ($cliMap.ContainsKey($nucleus)) {
        $effectiveCli = $cliMap[$nucleus].cli
        $effectiveModel = $cliMap[$nucleus].model
        $chainStep = "cli-map"
    } elseif ($globalCli -eq "auto") {
        $resolved = Resolve-NucleusCli $nucleus
        if (-not $resolved) {
            Write-Output "[$upper] SKIP: no working CLI in fallback chain"
            return $null
        }
        $effectiveCli = $resolved.cli
        $chainStep = $resolved.chain_step
    }
    $effectiveSuffix = if ($effectiveCli -eq "claude") { "" } else { "_$effectiveCli" }

    # Per-CLI boot script: claude -> n0X.ps1, gemini -> n0X_gemini.ps1, codex -> n0X_codex.ps1
    $bootPs1 = "$root\boot\${nucleus}${effectiveSuffix}.ps1"
    if (-not (Test-Path $bootPs1)) {
        # Auto fallback: if resolved CLI lacks a boot script, try claude
        if ($globalCli -eq "auto" -and $effectiveCli -ne "claude") {
            Write-Output "[$upper] WARN: no boot script for $effectiveCli ($bootPs1), falling back to claude"
            $effectiveCli = "claude"
            $effectiveSuffix = ""
            $chainStep = "boot_fallback"
            $bootPs1 = "$root\boot\${nucleus}.ps1"
        }
        if (-not (Test-Path $bootPs1)) {
            Write-Output "[$upper] SKIP: no boot script ($bootPs1)"
            return $null
        }
    }
    $bootScript = $bootPs1
    $bootType = "ps1"

    Write-Output "[$upper] Boot via $effectiveCli ($chainStep)"

    # Write per-nucleus + per-CLI handoff pointer so boot script picks it up.
    # Race fix: remove stale file first (may be locked by dying process from
    # previous wave), then copy with verification. Without this, fast models
    # (Haiku) boot before the filesystem syncs the new content.
    $nucleusHandoff = "$handoffDir\${nucleus}_task${effectiveSuffix}.md"
    if (Test-Path $nucleusHandoff) { Remove-Item $nucleusHandoff -Force -EA SilentlyContinue }
    Copy-Item $handoff.FullName -Destination $nucleusHandoff -Force
    if (-not (Test-Path $nucleusHandoff)) {
        Write-Output "[$upper] WARN: handoff copy failed, retrying..."
        Start-Sleep -Milliseconds 500
        Copy-Item $handoff.FullName -Destination $nucleusHandoff -Force
    }
    # Flush: NTFS lazy-write can delay visibility to child processes on fast boot
    [System.IO.File]::ReadAllBytes($nucleusHandoff) | Out-Null

    # Set env var so boot scripts skip their own WindowSize override
    $env:CEX_GRID = "1"
    $env:CEX_GRID_W = "$gW"
    $env:CEX_GRID_H = "$gH"

    # --- Per-cell worktree wiring (spec_n07_per_cell_worktrees, Wave 2) ---
    # When dispatch.sh grid was called with -w, it exports CEX_GRID_PERCELL_WORKTREE=1
    # Each cell then gets its own .cex/worktrees/wt_<cell_slug> dir + matching branch
    # (created earlier by Wave 1's cex_worktree_manager.py call).
    # boot/_shared/resolve_worktree.ps1 reads these env vars and cd's the boot
    # script into its assigned worktree before claude.exe starts.
    #
    # DISPATCH_FIX (spec_dispatch_grid_fix v1.0.0): cell_slug replaces bare nucleus
    # in the worktree path so same-nucleus parallel cells (3x n03) get distinct
    # worktrees wt_n03_anuncio / wt_n03_pesquisa / wt_n03_imagens instead of
    # racing on wt_n03. Legacy `MISSION_n0X.md` handoffs produce slug == nucleus,
    # so the path stays wt_n0X (no breaking change for Wave A pattern).
    $cellSlug = Get-CellSlugFromHandoff $handoff.Name $mission
    if ($env:CEX_GRID_PERCELL_WORKTREE -eq "1") {
        $wtDir = ".cex/worktrees/wt_$cellSlug"
        $wtBranch = "worktree/wt_$cellSlug"
        $wtAbsDir = Join-Path $root $wtDir
        if (Test-Path $wtAbsDir) {
            $env:CEX_WORKTREE_DIR = $wtDir
            $env:CEX_WORKTREE_BRANCH = $wtBranch
            Write-Output "[$upper] Worktree assigned: $wtDir (branch: $wtBranch)"
        } else {
            Write-Output "[$upper] WARN: per-cell worktree expected at $wtDir but missing -- launching in repo root"
            Remove-Item Env:CEX_WORKTREE_DIR -ErrorAction SilentlyContinue
            Remove-Item Env:CEX_WORKTREE_BRANCH -ErrorAction SilentlyContinue
        }
    } else {
        # Clear in case sibling launch left it set (per-cell mode is opt-in)
        Remove-Item Env:CEX_WORKTREE_DIR -ErrorAction SilentlyContinue
        Remove-Item Env:CEX_WORKTREE_BRANCH -ErrorAction SilentlyContinue
    }

    # (Wave 5 -- spec_n07_per_cell_worktrees) Mirror handoff into worktree's
    # .cex/runtime/handoffs/ so claude.exe in worktree cwd can find it via the
    # relative path the system prompt uses. .cex/runtime/ is gitignored, so it
    # does NOT exist inside the worktree by default. Without this mirror,
    # nuclei boot in worktree cwd but cannot find their handoff (Wave 4 bug).
    # MUST run AFTER the per-cell worktree env-var wiring above so
    # $env:CEX_WORKTREE_DIR is set for THIS nucleus.
    if ($env:CEX_GRID_PERCELL_WORKTREE -eq "1" -and $env:CEX_WORKTREE_DIR) {
        $wtRuntimeDir = Join-Path $env:CEX_WORKTREE_DIR ".cex/runtime/handoffs"
        if (-not (Test-Path $wtRuntimeDir)) {
            New-Item -ItemType Directory -Path $wtRuntimeDir -Force | Out-Null
        }
        $wtHandoffPath = Join-Path $wtRuntimeDir "${nucleus}_task${effectiveSuffix}.md"
        Copy-Item $handoff.FullName -Destination $wtHandoffPath -Force
        [System.IO.File]::ReadAllBytes($wtHandoffPath) | Out-Null  # NTFS flush
        Write-Output "[$upper] Mirrored handoff into worktree: $wtHandoffPath"

        # Mirror prompt_package (Mode B F6 PRODUCE depends on it). The package
        # lives in main's .cex/runtime/packages/ which is gitignored, so the
        # worktree branch does NOT inherit it. Without this mirror, Haiku/Mode-B
        # cells (typical N01) report "prompt_package missing" and refuse to run.
        $missionLower = $mission.ToLower()
        $ppName = "pp_${missionLower}_${nucleus}.md"
        $ppSrc = Join-Path $root ".cex/runtime/packages/$ppName"
        if (Test-Path $ppSrc) {
            $wtPpDir = Join-Path $env:CEX_WORKTREE_DIR ".cex/runtime/packages"
            if (-not (Test-Path $wtPpDir)) {
                New-Item -ItemType Directory -Path $wtPpDir -Force | Out-Null
            }
            $wtPpPath = Join-Path $wtPpDir $ppName
            Copy-Item $ppSrc -Destination $wtPpPath -Force
            [System.IO.File]::ReadAllBytes($wtPpPath) | Out-Null
            Write-Output "[$upper] Mirrored prompt_package: $ppName"
        }

        # Mirror decision_manifest (handoff DECISIONS section references it)
        $dmName = "decision_manifest_${missionLower}.yaml"
        $dmSrc = Join-Path $root ".cex/runtime/decisions/$dmName"
        if (Test-Path $dmSrc) {
            $wtDmDir = Join-Path $env:CEX_WORKTREE_DIR ".cex/runtime/decisions"
            if (-not (Test-Path $wtDmDir)) {
                New-Item -ItemType Directory -Path $wtDmDir -Force | Out-Null
            }
            $wtDmPath = Join-Path $wtDmDir $dmName
            Copy-Item $dmSrc -Destination $wtDmPath -Force
            [System.IO.File]::ReadAllBytes($wtDmPath) | Out-Null
            Write-Output "[$upper] Mirrored decision_manifest: $dmName"
        }
    }

    # ALWAYS boot interactive -- task comes from handoff, never CLI args (avoids nested-quote hell)
    # Capture wrapper stdout+stderr to log file for post-mortem diagnostics (race conditions, crashes)
    $logDir = "$root\.cex\runtime\logs\spawn"
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $logFile = "$logDir\${nucleus}_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

    # --- Per-cell model override (cli-map only) ---
    # If cli-map provided a model for this nucleus, set CEX_MODEL_OVERRIDE before
    # Start-Process so the child window inherits THIS cell's model. Save+restore
    # the prior value so the next iteration starts clean.
    $priorModelOverride = $env:CEX_MODEL_OVERRIDE
    $priorOllamaModel = $env:OLLAMA_MODEL
    if ($effectiveModel) {
        $env:CEX_MODEL_OVERRIDE = $effectiveModel
        Write-Output "[$upper] Per-cell model: $effectiveModel"
        # Bridge: boot/n0X_ollama.ps1 reads OLLAMA_MODEL, not CEX_MODEL_OVERRIDE.
        # Without this, every ollama cell silently falls back to the default model.
        if ($effectiveCli -eq "ollama") { $env:OLLAMA_MODEL = ($effectiveModel -replace '^ollama/','') }
    }

    # Interactive mode => visible window (NO stdout redirect, Windows hides window when redirecting).
    # Non-interactive (headless) => capture stdout/stderr for post-mortem; window hidden.
    if ($interactive) {
        $proc = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -NoExit -File `"$bootScript`"" -WorkingDirectory $root -PassThru -WindowStyle Normal
    } else {
        $proc = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -NoExit -File `"$bootScript`"" -WorkingDirectory $root -PassThru -RedirectStandardOutput $logFile -RedirectStandardError "${logFile}.err"
    }

    # Restore prior model override (so next sibling cell's cli-map lookup is the
    # only thing setting it for them). Each cell's child has already inherited
    # its own snapshot at Start-Process time.
    if ($effectiveModel) {
        if ($priorModelOverride) {
            $env:CEX_MODEL_OVERRIDE = $priorModelOverride
        } else {
            Remove-Item Env:CEX_MODEL_OVERRIDE -ErrorAction SilentlyContinue
        }
        if ($effectiveCli -eq "ollama") {
            if ($priorOllamaModel) { $env:OLLAMA_MODEL = $priorOllamaModel }
            else { Remove-Item Env:OLLAMA_MODEL -ErrorAction SilentlyContinue }
        }
    }
    # Retry loop: poll for window handle (up to 5s, 500ms intervals)
    if ($proc) {
        $hwnd = [IntPtr]::Zero
        for ($i = 0; $i -lt 10; $i++) {
            Start-Sleep -Milliseconds 500
            try { $proc.Refresh() } catch {}
            $hwnd = $proc.MainWindowHandle
            if ($hwnd -ne [IntPtr]::Zero) { break }
        }
        if ($hwnd -ne [IntPtr]::Zero) {
            # bRepaint=$true: TUI needs WM_SIZE to adapt alt-screen-buffer to
            # final window dimensions. Without repaint, Claude renders at
            # initial (smaller) window size and leaves bottom/side dead zones.
            # Previous "overlap" was caused by banner+DarkBlue bg in boot scripts
            # (fixed by cex_fix_boot_banner.py), not by forced repaint itself.
            [Win32Grid]::MoveWindow($hwnd, $pos.x, $pos.y, $gW, $gH, $true) | Out-Null
        } else {
            Write-Output "[$upper] WARN: no window handle after 5s -- window not positioned"
        }
        # PID format: {wrapper_pid} {nucleus} {cli} {session_id} {timestamp} {worker_pids}
        # worker_pids is filled by Enrich-PidFile after all launches (empty = "-" here)
        # cli = effectiveCli (per-nucleus resolved, not the global -cli flag)
        $sessId = if ($env:CEX_SESSION_ID) { $env:CEX_SESSION_ID } else { "s$PID" }
        $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        "$($proc.Id) $nucleus $effectiveCli $sessId $ts -" | Add-Content $pidFile
        Write-Output "[$upper] Spawned wrapper PID:$($proc.Id) handoff:$($handoff.Name)"
    }
    return $proc
}

# Static mode: launch all at once
if ($mode -eq "static") {
    $launched = 0
    $launchedProcs = @{}
    foreach ($h in $handoffs) {
        if ($launched -ge $maxSlots) { break }
        $nucleus = Get-NucleusFromHandoff $h.Name
        $proc = Launch-Nucleus $h
        if ($proc) { $launchedProcs[$nucleus] = $proc }
        $launched++
        Start-Sleep -Seconds 4
    }
    # NOTE: Re-enforce reposition removed (2026-04-14). Previously this ran 6s
    # after launch, yanking windows mid-TUI-render. Claude TUI boots in 2-3s and
    # the WM_SIZE event from MoveWindow triggered full repaint glitches (alt
    # screen buffer desync). First MoveWindow (at launch time) is final.
    # Enrich PID file: walk descendants to capture real worker PIDs
    # (Start-Process -PassThru returned the wrapper, not the worker.)
    Write-Output "[GRID] Enriching PID file with worker PIDs..."
    Start-Sleep -Seconds 4  # let CLI workers actually start
    if (Test-Path $pidFile) {
        $lines = Get-Content $pidFile
        $newLines = @()
        foreach ($line in $lines) {
            $parts = $line.Trim() -split '\s+'
            if ($parts.Count -lt 5) { $newLines += $line; continue }
            $wPid = [int]$parts[0]; $nuc = $parts[1]; $c = $parts[2]
            $sess = $parts[3]; $t = $parts[4]
            $workerList = Find-WorkerPids $wPid $c
            $newLines += "$wPid $nuc $c $sess $t $workerList"
            Write-Output "  [$($nuc.ToUpper())] wrapper:$wPid workers:$workerList"
        }
        Set-Content $pidFile $newLines -Encoding UTF8
    }
    Write-Output "[GRID] Static: $launched/$($handoffs.Count) launched"
    exit 0
}

# Continuous mode: launch slots, monitor, re-dispatch
$queue = [System.Collections.Queue]::new()
foreach ($h in $handoffs) { $queue.Enqueue($h) }

$active = @{}
$completed = 0
$startTime = Get-Date

# Initial fill
while ($active.Count -lt $maxSlots -and $queue.Count -gt 0) {
    $h = $queue.Dequeue()
    $nucleus = Get-NucleusFromHandoff $h.Name
    $proc = Launch-Nucleus $h
    if ($proc) { $active[$nucleus] = @{proc=$proc; handoff=$h; start=Get-Date} }
    Start-Sleep -Seconds 4
}

Write-Output "[GRID] Continuous: $($active.Count) active, $($queue.Count) queued"

# Monitor loop
while ($active.Count -gt 0 -or $queue.Count -gt 0) {
    $elapsed = ((Get-Date) - $startTime).TotalMinutes
    if ($elapsed -gt $maxMinutes) {
        Write-Output "[GRID] TIMEOUT: ${maxMinutes}min exceeded"
        break
    }

    Start-Sleep -Seconds $pollSeconds

    # Check for completed signals
    $toRemove = @()
    foreach ($kv in $active.GetEnumerator()) {
        $nucleus = $kv.Key
        $info = $kv.Value
        $spawnTime = $info.start

        $sigs = Get-ChildItem "$signalDir\signal_${nucleus}_*.json" -EA SilentlyContinue |
            Where-Object { $_.LastWriteTime -gt $spawnTime }

        if ($sigs) {
            $completed++
            Write-Output "[$($nucleus.ToUpper())] COMPLETE ($completed total)"
            $toRemove += $nucleus
        }

        # Stuck detection
        $age = ((Get-Date) - $spawnTime).TotalSeconds
        if ($age -gt 5400) {  # 90min stuck threshold (was 900s=15min)
            Write-Output "[$($nucleus.ToUpper())] STUCK (${age}s)"
            $toRemove += $nucleus
        }
    }

    foreach ($n in $toRemove) {
        $active.Remove($n)
        # Re-dispatch from queue
        if ($queue.Count -gt 0) {
            $h = $queue.Dequeue()
            $nucleus = Get-NucleusFromHandoff $h.Name
            $proc = Launch-Nucleus $h
            if ($proc) { $active[$nucleus] = @{proc=$proc; handoff=$h; start=Get-Date} }
            Start-Sleep -Seconds 4
        }
    }

    Write-Output "[GRID] Active:$($active.Count) Queue:$($queue.Count) Done:$completed Elapsed:$([math]::Round($elapsed))min"
}

Write-Output "[GRID] FINISHED: $completed completed, $($queue.Count) remaining"
