# CEXAI tenant run-launcher -- brings up the 3 local apps with ONE command (Windows / PowerShell).
#   public_site   -> Next dev (NEXT_PUBLIC_FIXTURES=1) on :3000
#   dashboard_web -> Next dev on :3001
#   dashboard_api -> uvicorn on :8000 (only if the Python deps are installed)
# Drop this at the tenant repo root (next to apps/). Also works if it lives in /boot/.
# Each app launches in its own console window so logs stay visible; close a window to stop that app.

$ErrorActionPreference = "Stop"

# --- Resolve repo root (the directory that contains apps/) ---
$root = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not (Test-Path (Join-Path $root "apps"))) {
    $up = Split-Path -Parent $root
    if ($up -and (Test-Path (Join-Path $up "apps"))) { $root = $up }
}

# --- Pre-flight: node + npm must be on PATH (both web apps need them) ---
foreach ($bin in "node", "npm") {
    if (-not (Get-Command $bin -ErrorAction SilentlyContinue)) {
        Write-Host "[FAIL] '$bin' not found on PATH. Install Node.js 18.17+ (https://nodejs.org) and retry." -ForegroundColor Red
        exit 1
    }
}

# Spawn child consoles with the same PowerShell host that is running us (pwsh on PS7, else powershell).
$psExe = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }

# --- public_site -> :3000 (fixtures on) ---
$site    = Join-Path $root "apps/public_site"
$siteCmd = "if (-not (Test-Path 'node_modules')) { npm install }; `$env:NEXT_PUBLIC_FIXTURES='1'; `$env:PORT='3000'; npm run dev"
Start-Process $psExe -WorkingDirectory $site -ArgumentList "-NoExit", "-Command", $siteCmd

# --- dashboard_web -> :3001 ---
$web    = Join-Path $root "apps/dashboard_web"
$webCmd = "if (-not (Test-Path 'node_modules')) { npm install }; `$env:NEXT_PUBLIC_FIXTURES='1'; `$env:NEXT_PUBLIC_TENANT='starter'; `$env:NEXT_PUBLIC_BRAND_NAME='starter'; `$env:PORT='3001'; npm run dev"
Start-Process $psExe -WorkingDirectory $web -ArgumentList "-NoExit", "-Command", $webCmd

# --- dashboard_api -> :8000 (only if uvicorn + fastapi import cleanly) ---
$apiOk = $false
if (Get-Command python -ErrorAction SilentlyContinue) {
    try {
        $null  = & python -c "import uvicorn, fastapi" 2>&1
        $apiOk = ($LASTEXITCODE -eq 0)
    } catch {
        $apiOk = $false
    }
}
if ($apiOk) {
    $apiCmd = "python -m uvicorn apps.dashboard_api.main:app --port 8000 --reload"
    Start-Process $psExe -WorkingDirectory $root -ArgumentList "-NoExit", "-Command", $apiCmd
} else {
    Write-Host "[i] dashboard_api skipped -- Python deps not installed. To enable the API:" -ForegroundColor Yellow
    Write-Host "      pip install -r apps/dashboard_api/requirements.txt"
    Write-Host "      python -m uvicorn apps.dashboard_api.main:app --port 8000 --reload"
}

Write-Host ""
Write-Host "Site http://localhost:3000/t/starter | Admin http://localhost:3001 | API http://localhost:8000" -ForegroundColor Green
