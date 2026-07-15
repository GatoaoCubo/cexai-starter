# starter -- launcher do repo soberano (Windows). Menu de boot: escolha o que
# abrir ao vivo (vitrine / admin / API / tudo). ASCII-only (house rule). R-363.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Ensure-Node($dir) {
  if (-not (Test-Path (Join-Path $dir "node_modules"))) {
    Write-Host "[setup] instalando dependencias (primeira vez, ~1-2 min)..." -ForegroundColor Yellow
    Push-Location $dir; npm install --no-audit --no-fund | Out-Host; Pop-Location
  }
}

function Start-InWindow($title, $dir, $inner) {
  # abre em nova janela para o servidor seguir rodando enquanto o menu continua
  $cmd = "cd '$dir'; $inner"
  Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd | Out-Null
}

function Open-Url($url) { Start-Process $url | Out-Null }

function Run-Storefront {
  $dir = Join-Path $root "apps\public_site"
  Ensure-Node $dir
  Write-Host "[vitrine] subindo em http://localhost:3000 ..." -ForegroundColor Cyan
  Start-InWindow "vitrine" $dir "`$env:NEXT_PUBLIC_FIXTURES='1'; `$env:NEXT_PUBLIC_ADMIN_URL='http://localhost:3001'; `$env:PORT='3000'; npm run dev"
  Start-Sleep 7; Open-Url "http://localhost:3000/t/starter"
  Write-Host "[vitrine] http://localhost:3000/t/starter aberto no navegador." -ForegroundColor Green
}

function Run-Admin {
  $dir = Join-Path $root "apps\dashboard_web"
  Ensure-Node $dir
  Write-Host "[admin] subindo em http://localhost:3001 ..." -ForegroundColor Cyan
  Start-InWindow "admin" $dir "`$env:PORT='3001'; npm run dev"
  Start-Sleep 7; Open-Url "http://localhost:3001"
}

function Run-Api {
  Write-Host "[api] subindo em http://localhost:8000 (precisa Python + pip install -r apps/dashboard_api/requirements.txt) ..." -ForegroundColor Cyan
  Start-InWindow "api" $root "uvicorn apps.dashboard_api.main:app --port 8000"
  Start-Sleep 4; Open-Url "http://localhost:8000/capabilities"
}

while ($true) {
  Write-Host ""
  Write-Host "==================== starter -- Repo Soberano ====================" -ForegroundColor Blue
  Write-Host "  1) Rodar a VITRINE (site publico)      -> localhost:3000  + abre navegador"
  Write-Host "  2) Rodar o ADMIN (dashboard do tenant) -> localhost:3001  + abre navegador"
  Write-Host "  3) Rodar a API (capacidades)           -> localhost:8000"
  Write-Host "  4) Rodar TUDO (vitrine + admin + API)"
  Write-Host "  5) Abrir a vitrine no navegador (se ja estiver rodando)"
  Write-Host "  0) Sair"
  Write-Host "===================================================================" -ForegroundColor Blue
  $c = Read-Host "Escolha"
  switch ($c) {
    "1" { Run-Storefront }
    "2" { Run-Admin }
    "3" { Run-Api }
    "4" { Run-Storefront; Run-Admin; Run-Api }
    "5" { Open-Url "http://localhost:3000/t/starter" }
    "0" { Write-Host "Ate logo."; break }
    default { Write-Host "Opcao invalida." -ForegroundColor Red }
  }
}
