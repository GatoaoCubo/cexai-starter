# CEX LiteLLM Proxy Boot Script
# Starts LiteLLM as unified routing proxy for all nuclei
#
# Usage: powershell -File boot/litellm_proxy.ps1
# Test:  curl http://localhost:4000/health
# Docs:  http://localhost:4000/docs (Swagger UI)
#
# Every nucleus calls: POST http://localhost:4000/v1/chat/completions
# with model: "cex-n0X" -- LiteLLM routes to correct provider.

$cexRoot = Split-Path -Parent $PSScriptRoot
# Config lives at .cex/config/ (NOT .cex/P09_config/ -- that dir holds .md context
# files only). Fixing the stale path so the proxy boots; flagged in WHITEPAPER B.5.
$configPath = "$cexRoot\.cex\config\litellm_config.yaml"
$venvPython = "$cexRoot\.venv_litellm\Scripts\python.exe"

if (-not (Test-Path $configPath)) {
    Write-Host "[FAIL] LiteLLM config not found: $configPath" -ForegroundColor Red
    exit 1
}

# Prefer dedicated 3.12 venv (orjson has no 3.14 wheel)
# Invoke python -m (avoids Windows App Control blocking unsigned .exe shims)
if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = "python"
    try {
        & $pythonExe -c "import litellm.proxy" 2>$null
        if ($LASTEXITCODE -ne 0) { throw "missing" }
    } catch {
        Write-Host "[FAIL] litellm[proxy] not installed. Create venv:" -ForegroundColor Red
        Write-Host "  py -3.12 -m venv .venv_litellm" -ForegroundColor Yellow
        Write-Host "  .venv_litellm\Scripts\python.exe -m pip install 'litellm[proxy]' pyyaml" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CEX LiteLLM Proxy" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Config: $configPath"
Write-Host "Port:   4000"
Write-Host "Health: http://localhost:4000/health"
Write-Host "Docs:   http://localhost:4000/docs"
Write-Host ""

# R-112/R-142 fix (2026-07-05): this banner used to hardcode "cex-n07/n03 -> opus,
# cex-n01/02/04/05/06 -> sonnet" -- stale vs $configPath, which actually routes ALL 7
# cex-n0X entries to ollama/gemma2:9b (FREE MODE profile, see the file's own header).
# Read model_list from the real config file AT PRINT-TIME so the banner can never
# drift from routing again. Regex-based (no YAML-parser dependency -- same philosophy
# as boot/_shared/resolve_model.ps1's Get-YamlField); degrades to "(unknown -- see
# $configPath)" per nucleus if the file is missing/reshaped, never throws.
function Get-CexLiteLLMRouting {
    param([Parameter(Mandatory=$true)][string]$ConfigPath)
    $routing = @{}
    try {
        if (-not (Test-Path $ConfigPath)) { return $routing }
        $content = Get-Content $ConfigPath -Raw -Encoding UTF8
        foreach ($n in @("n01","n02","n03","n04","n05","n06","n07")) {
            # Block style (current file):
            #   - model_name: cex-nXX
            #     litellm_params:
            #       model: ollama/gemma2:9b
            if ($content -match "-\s*model_name:\s*cex-${n}\s*\r?\n\s*litellm_params:\s*\r?\n\s*model:\s*(\S+)") {
                $routing[$n] = $Matches[1]
                continue
            }
            # Flow style: - model_name: cex-nXX / litellm_params: { model: ..., ... }
            if ($content -match "-\s*model_name:\s*cex-${n}\s*\r?\n\s*litellm_params:\s*\{[^}]*model:\s*([^,}\s]+)") {
                $routing[$n] = $Matches[1]
            }
        }
    } catch {}
    return $routing
}
$cexDomains = [ordered]@{
    n07 = "orchestration"; n03 = "building"; n01 = "research"; n02 = "marketing"
    n04 = "knowledge";     n05 = "operations"; n06 = "commercial"
}
$liteLLMRouting = Get-CexLiteLLMRouting -ConfigPath $configPath
Write-Host "Models routed (read from $configPath at print-time):" -ForegroundColor Yellow
foreach ($n in $cexDomains.Keys) {
    $routedModel = if ($liteLLMRouting.ContainsKey($n)) { $liteLLMRouting[$n] } else { "(unknown -- see $configPath)" }
    Write-Host "  cex-$n -> $routedModel ($($cexDomains[$n]))"
}
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor DarkGray
Write-Host ""

# Force UTF-8 (LiteLLM banner has Unicode; Windows cp1252 default crashes)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Skip prisma entirely so the proxy binds immediately (we run keyless / no DB).
# litellm 1.83.7 treats an EMPTY DATABASE_URL as "present" and retries prisma
# ~160s before binding -- so the var must be UNSET (Python None), not "". Remove
# it from the process env (no-op if it was never set). The repo .env carries no
# DATABASE_URL, so nothing re-adds it; a stale Railway URL would also be dropped.
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:LITELLM_DB_URL -ErrorAction SilentlyContinue

# Start LiteLLM proxy via python -m (avoids signed-EXE policy)
& $pythonExe -m litellm.proxy.proxy_cli --config $configPath --port 4000 --detailed_debug
