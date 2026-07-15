#!/usr/bin/env bash
# starter -- launcher do repo soberano (Mac/Linux/Git-Bash). Menu de boot:
# escolha o que abrir ao vivo (vitrine / admin / API / tudo). ASCII-only. R-363.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

open_url() {
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 &
  elif command -v open >/dev/null 2>&1; then open "$1" >/dev/null 2>&1 &
  elif command -v start >/dev/null 2>&1; then start "$1" >/dev/null 2>&1 &
  else echo "  abra no navegador: $1"; fi
}

ensure_node() { [ -d "$1/node_modules" ] || { echo "[setup] instalando deps (~1-2 min)..."; (cd "$1" && npm install --no-audit --no-fund); }; }

run_storefront() {
  ensure_node "$ROOT/apps/public_site"
  echo "[vitrine] subindo em http://localhost:3000 ..."
  (cd "$ROOT/apps/public_site" && NEXT_PUBLIC_FIXTURES=1 NEXT_PUBLIC_ADMIN_URL=http://localhost:3001 PORT=3000 npm run dev >/tmp/starter_vitrine.log 2>&1 &)
  sleep 7; open_url "http://localhost:3000/t/starter"
  echo "[vitrine] aberto: http://localhost:3000/t/starter"
}
run_admin() {
  ensure_node "$ROOT/apps/dashboard_web"
  echo "[admin] subindo em http://localhost:3001 ..."
  (cd "$ROOT/apps/dashboard_web" && PORT=3001 npm run dev >/tmp/starter_admin.log 2>&1 &)
  sleep 7; open_url "http://localhost:3001"
}
run_api() {
  echo "[api] subindo em http://localhost:8000 (precisa Python + pip install -r apps/dashboard_api/requirements.txt) ..."
  (cd "$ROOT" && uvicorn apps.dashboard_api.main:app --port 8000 >/tmp/starter_api.log 2>&1 &)
  sleep 4; open_url "http://localhost:8000/capabilities"
}

while true; do
  echo ""
  echo "==================== starter -- Repo Soberano ===================="
  echo "  1) Rodar a VITRINE (site publico)      -> localhost:3000  + abre navegador"
  echo "  2) Rodar o ADMIN (dashboard do tenant) -> localhost:3001  + abre navegador"
  echo "  3) Rodar a API (capacidades)           -> localhost:8000"
  echo "  4) Rodar TUDO (vitrine + admin + API)"
  echo "  5) Abrir a vitrine no navegador (se ja rodando)"
  echo "  0) Sair"
  echo "==================================================================="
  read -rp "Escolha: " c
  case "$c" in
    1) run_storefront ;;
    2) run_admin ;;
    3) run_api ;;
    4) run_storefront; run_admin; run_api ;;
    5) open_url "http://localhost:3000/t/starter" ;;
    0) echo "Ate logo."; exit 0 ;;
    *) echo "Opcao invalida." ;;
  esac
done
