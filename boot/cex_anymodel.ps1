# CEX any-model runtime profile -- run the NATIVE claude CLI against ANY model
# routed by the local LiteLLM proxy, via the ANTHROPIC_BASE_URL transport seam.
#
# This is the reference-only absorption of the free-claude-code pattern
# (see docs/RUNTIME_ANY_MODEL.md + docs/archive/WHITEPAPER_CEX_DISTILL.md B.4/B.5). CEXAI
# already ships the heavy machinery -- LiteLLM on :4000 (boot/litellm_proxy.ps1)
# + nucleus_models.yaml + fallback_chain + capability filter. This helper adds
# the ~10-line UX seam fcc proves out: keep the native claude TUI/agent/tools,
# just divert its HTTP transport to CEXAI's OWN proxy. No proxy code is copied.
#
# What it does:
#   1. start boot/litellm_proxy.ps1 (LiteLLM, OpenAI + Anthropic /v1/messages on :4000)
#   2. export ANTHROPIC_BASE_URL=http://localhost:<port>
#   3. export ANTHROPIC_AUTH_TOKEN=<sentinel>  (bypasses the native login gate)
#   4. launch native `claude` (or print the export lines with -NoLaunch)
#
# The provider/model the proxy routes to is a CONFIG choice in
# .cex/config/litellm_config.yaml -- never a code edit. See the runbook.
#
# Usage:
#   powershell -File boot/cex_anymodel.ps1                 # start proxy + launch claude
#   powershell -File boot/cex_anymodel.ps1 -NoLaunch       # just wire env, print how-to
#   powershell -File boot/cex_anymodel.ps1 -NoProxy        # proxy already running elsewhere
#   powershell -File boot/cex_anymodel.ps1 -Token mykey    # custom sentinel (= proxy master_key)
#   . boot/cex_anymodel.ps1 -NoLaunch                      # dot-source: keep vars in YOUR shell
#
# ASCII-only (cex_sanitize.py --check must pass). PowerShell 5.1+ compatible.

[CmdletBinding()]
param(
    [int]$Port = 4000,
    [string]$Token = "cex-no-auth",
    [switch]$NoLaunch,
    [switch]$NoProxy,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ClaudeArgs
)

$cexRoot = Split-Path -Parent $PSScriptRoot
$baseUrl = "http://localhost:$Port"
$healthUrl = "$baseUrl/health/liveliness"

function Test-CexProxyUp {
    try {
        Invoke-RestMethod -Uri $healthUrl -TimeoutSec 3 -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CEX any-model runtime (CLI-transport seam)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Proxy : $baseUrl"
Write-Host "  Config: .cex/config/litellm_config.yaml"
Write-Host "  Seam  : native claude CLI -> ANTHROPIC_BASE_URL -> LiteLLM -> routed model"
Write-Host "  Docs  : docs/RUNTIME_ANY_MODEL.md"
Write-Host ""

# --- 1) Ensure the proxy is up (start it if needed). ---
$up = Test-CexProxyUp
if ($up) {
    Write-Host "  [OK] proxy already healthy at $baseUrl" -ForegroundColor Green
} elseif ($NoProxy) {
    Write-Host "  [WARN] -NoProxy set but nothing healthy at $baseUrl." -ForegroundColor Yellow
    Write-Host "         Point -Port at your running proxy, or drop -NoProxy to start one." -ForegroundColor Yellow
} else {
    Write-Host "  [>>] proxy not responding -- starting boot/litellm_proxy.ps1 ..." -ForegroundColor Yellow
    # Share the sentinel as the proxy master_key so inbound auth stays FAIL-CLOSED
    # (a stronger posture than fcc's blank-disables default): the spawned proxy
    # inherits this env var and requires exactly this token; the native claude CLI
    # then sends the same token. Set -Token "" to run the proxy keyless (fail-open).
    $env:LITELLM_MASTER_KEY = $Token
    $proxyScript = Join-Path $PSScriptRoot "litellm_proxy.ps1"
    $startArgs = @{
        FilePath         = "powershell"
        ArgumentList     = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $proxyScript)
        WorkingDirectory = $cexRoot
    }
    Start-Process @startArgs | Out-Null

    # Poll for health (LiteLLM cold start can take several seconds).
    $deadline = (Get-Date).AddSeconds(45)
    while ((Get-Date) -lt $deadline) {
        if (Test-CexProxyUp) { break }
        Start-Sleep -Seconds 2
        Write-Host "  [..] waiting for proxy health ..." -ForegroundColor DarkGray
    }
    if (Test-CexProxyUp) {
        Write-Host "  [OK] proxy healthy at $baseUrl" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] proxy not confirmed healthy within 45s." -ForegroundColor Yellow
        Write-Host "         Check its window, or start manually:" -ForegroundColor Yellow
        Write-Host "           powershell -File boot/litellm_proxy.ps1" -ForegroundColor Yellow
    }
}

# --- 2+3) Wire the transport seam in THIS process (children inherit it). ---
$env:ANTHROPIC_BASE_URL = $baseUrl
$env:ANTHROPIC_AUTH_TOKEN = $Token
# Strip a stale inherited key so the sentinel is the credential the CLI sends
# (mirrors fcc stripping inherited ANTHROPIC_* before redirect).
$env:ANTHROPIC_API_KEY = ""

Write-Host ""
Write-Host "  Transport seam wired (this process + children):" -ForegroundColor Green
Write-Host "    ANTHROPIC_BASE_URL   = $baseUrl"
Write-Host "    ANTHROPIC_AUTH_TOKEN = $Token   (sentinel; skips the login gate)"
Write-Host "    ANTHROPIC_API_KEY    = (cleared for this session)"
Write-Host ""
Write-Host "  The routed provider/model is a CONFIG choice -- edit:" -ForegroundColor DarkGray
Write-Host "    .cex/config/litellm_config.yaml   (menu + recipes in docs/RUNTIME_ANY_MODEL.md)" -ForegroundColor DarkGray
Write-Host ""

# --- 4) Launch (or print copy-paste instructions). ---
if ($NoLaunch) {
    Write-Host "  -NoLaunch: env is set in THIS process only. To keep it in YOUR shell," -ForegroundColor Cyan
    Write-Host "  dot-source this script (note the leading dot), then run any client:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    . boot/cex_anymodel.ps1 -NoLaunch" -ForegroundColor White
    Write-Host "    `$env:ANTHROPIC_BASE_URL   = `"$baseUrl`"" -ForegroundColor White
    Write-Host "    `$env:ANTHROPIC_AUTH_TOKEN = `"$Token`"" -ForegroundColor White
    Write-Host "    claude        # or codex / gemini / any Anthropic-wire client" -ForegroundColor White
    Write-Host ""
    return
}

$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    Write-Host "  [WARN] 'claude' not found on PATH. The env IS set in this process;" -ForegroundColor Yellow
    Write-Host "         install the native CLI or re-run with -NoLaunch to use the seam." -ForegroundColor Yellow
    return
}

Write-Host "  [>>] launching native claude CLI against the routed model ..." -ForegroundColor Green
Write-Host ""
& claude @ClaudeArgs
