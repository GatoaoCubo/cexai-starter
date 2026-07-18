# CEX N03 Ollama -- CEX-N03-BUILDER (Aider + Ollama)
# Mirrors boot/n03.ps1 but uses direct Ollama API via _tools/ollama_nucleus.py
# CLI: python | Model: qwen3:8b (default) -- aider replaced 2026-04-13
# Sin: Inventive Pride (Inventive Pride)

# --- UX: Window title with mission + sin + status ---
. $PSScriptRoot/_shared/vt_enable.ps1  # Enable ANSI/VT for TUI (claude/gemini/codex/ollama)
. $PSScriptRoot/_shared/fix_pathext.ps1  # Guard: .PS1 before .CMD breaks npx-based MCP servers
. $PSScriptRoot/_shared/emit_exit_signal.ps1
. $PSScriptRoot/_shared/run_with_timeout.ps1
$cexRoot = Split-Path -Parent $PSScriptRoot
$nucleus = "n03"
. $PSScriptRoot/_shared/theme.ps1  # Per-nucleus theme (bg color, scrollback)
$sinName = "Inventive Pride"

# Detect model (env override or default)
$ollamaModel = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "qwen3:8b" }
$modelShort = "ollama/$ollamaModel"

# Detect mission from handoff file. TENANT-SCOPED (R-042): 'runtime' is a
# per-tenant surface, so a tenant session reads/writes its OWN handoff
# (.cex/tenants/<tid>/runtime/handoffs/), never the global/central one --
# stops a tenant nucleus from colliding with the central (or another
# tenant's) handoff when both run on the same machine.
$mission = ""
$handoffRel = if ($env:CEX_TENANT_ID) { ".cex/tenants/$($env:CEX_TENANT_ID)/runtime/handoffs/${nucleus}_task_ollama.md" } else { ".cex/runtime/handoffs/${nucleus}_task_ollama.md" }
$handoff = Join-Path $cexRoot ($handoffRel -replace '/', '\')
if (-not (Test-Path $handoff)) {
    $handoffRel = if ($env:CEX_TENANT_ID) { ".cex/tenants/$($env:CEX_TENANT_ID)/runtime/handoffs/${nucleus}_task.md" } else { ".cex/runtime/handoffs/${nucleus}_task.md" }
    $handoff = Join-Path $cexRoot ($handoffRel -replace '/', '\')
}
if (Test-Path $handoff) {
    $content = Get-Content $handoff -Head 10 -EA SilentlyContinue
    foreach ($line in $content) {
        if ($line -match "^mission:\s*(.+)$") {
            $mission = $Matches[1].Trim()
            break
        }
    }
}

# Detect git repo name + branch
$gitBranch = ""
$gitRepo = ""
try {
    $gitBranch = (git rev-parse --abbrev-ref HEAD 2>$null)
    $gitRemote = (git remote get-url origin 2>$null)
    if ($gitRemote -match "[/:]([^/]+?)(?:\.git)?$") { $gitRepo = $Matches[1] }
    Clear-Host
} catch {}

function Set-CexTitle($status) {
    # window-title mechanic intentionally omitted (de-branded distribution build)
}

Set-CexTitle "BOOTING"

# --- Environment ---
$env:CEX_NUCLEUS = "N03"
$env:CEX_ROOT = $cexRoot
Set-Location $env:CEX_ROOT

# Load .env (secrets for MCP servers, LLM providers). System env wins.
. "$PSScriptRoot\_shared\load_dotenv.ps1"
. "$PSScriptRoot\_shared\check_mcp_env.ps1"  # Pre-flight: warn if MCP env vars are missing

# --- Build task file for aider --message-file ---
$sysPrompt = @'
You are N03 Builder Nucleus of CEX, driven by Inventive Pride.
Every artifact must be worthy of your signature. 8F pipeline is non-negotiable.
Quality floor: 9.0. You are the finest craftsman in the system.
Domain: artifact construction, builders, templates, scaffold, creation.
Read OLLAMA.md (Ollama runtime entry) for system-wide configuration.

IMPORTANT RULES:
1. Read your handoff task file (loaded automatically)
2. Execute the task fully and autonomously
3. All artifacts need YAML frontmatter with quality: null
4. After saving files, run: python _tools/cex_compile.py <path>
5. Commit with: git add <files> ; git commit -m "[N03] <description>"
6. Signal complete: python -c "from _tools.signal_writer import write_signal; write_signal('n03', 'complete', 9.0)"
'@

$taskContent = ""
if (Test-Path $handoff) {
    $taskContent = Get-Content $handoff -Raw -EA SilentlyContinue
}

# Write combined prompt to temp file
$tempDir = "$cexRoot\.cex\runtime\tmp"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
$taskFile = "$tempDir\n03_ollama_task.md"

$combined = @"
$sysPrompt

---

## TASK (from handoff)

$taskContent

---

Read the task above and execute it now. If no task content, report ready.
"@
$combined | Set-Content $taskFile -Encoding utf8

# --- Probe model availability ---
# R-056/R-141: canonical env OLLAMA_HOST wins; absent -> unchanged default
$ollamaBase = if ($env:OLLAMA_HOST) { $env:OLLAMA_HOST } else { 'http://localhost:11434' }
if ($ollamaBase -notmatch '^https?://') { $ollamaBase = "http://$ollamaBase" }
$ollamaBase = $ollamaBase.TrimEnd('/')
$modelToUse = "ollama/$ollamaModel"
Write-Host "  [>>] Probing Ollama for $ollamaModel..." -ForegroundColor DarkGray
$ollamaUp = $false
try {
    $resp = Invoke-RestMethod -Uri "$ollamaBase/api/tags" -TimeoutSec 5 -EA Stop
    $ollamaUp = $true
    $available = $resp.models | ForEach-Object { $_.name }
    if ($available -notcontains $ollamaModel -and $available -notcontains "${ollamaModel}:latest") {
        Write-Host "  [WARN] $ollamaModel not found, falling back to qwen3:14b" -ForegroundColor Yellow
        $modelToUse = "ollama/qwen3:14b"
    } else {
        Write-Host "  [OK] $ollamaModel available" -ForegroundColor Green
    }
} catch {
    Write-Host "  [FAIL] Ollama not responding at $ollamaBase" -ForegroundColor Red
    Write-Host "  Start Ollama first: ollama serve" -ForegroundColor Red
    Set-CexTitle "FAIL - NO OLLAMA"
    return
}

# --- Launch direct API wrapper (ollama_nucleus.py) ---
# aider replaced 2026-04-13: aider cannot parse full-file LLM output (expects SEARCH/REPLACE)
$env:CEX_TASK_FILE = $handoff

Write-Host "  [>>] Launching ollama_nucleus.py with $ollamaModel" -ForegroundColor Blue
Write-Host ""

Set-CexTitle "RUNNING"
$cex_start_time = Get-Date
$watchdog = Start-CexWatchdog
& python "$cexRoot\_tools\ollama_nucleus.py" --nucleus N03 --model $ollamaModel --task-file $handoff
$exitStatus = Stop-CexWatchdog $watchdog
Set-CexTitle "DONE"
Emit-ExitSignal -StartTime $cex_start_time -Status $exitStatus
