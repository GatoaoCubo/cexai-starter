#!/usr/bin/env bash
# CEX nucleus boot wrapper -- cross-platform (Mac / Linux / WSL / Git-Bash)
#
# Bash mirror of boot/n0X.ps1 family. Single parameterized script that
# handles all 7 nuclei (n01..n07). PowerShell variants stay primary on
# Windows; this is for non-Windows contributors.
#
# Usage:
#   bash boot/cex_nucleus.sh n03                    # boot N03 with default model
#   bash boot/cex_nucleus.sh n03 --cli claude       # explicit CLI
#   bash boot/cex_nucleus.sh n03 --runtime ollama   # use OLLAMA.md entry
#
# Reads:
#   .cex/config/nucleus_models.yaml -- which CLI + model per nucleus
#   .cex/runtime/handoffs/<nuc>_task.md -- current task

set -euo pipefail

NUCLEUS="${1:-}"
if [[ ! "$NUCLEUS" =~ ^n0[1-7]$ ]]; then
  echo "Usage: bash boot/cex_nucleus.sh <n01..n07> [--cli claude|gemini|codex|ollama] [--runtime claude|codex|gemini|ollama]"
  exit 1
fi
shift

CLI=""
RUNTIME="claude"  # which runtime entry file to reference (CLAUDE.md, AGENTS.md, GEMINI.md, OLLAMA.md)
while [ $# -gt 0 ]; do
  case "$1" in
    --cli) CLI="$2"; shift 2 ;;
    --runtime) RUNTIME="$2"; shift 2 ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

# Repo root = script's parent dir's parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CEX_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$CEX_ROOT"

export CEX_NUCLEUS="$(echo "$NUCLEUS" | tr 'a-z' 'A-Z')"
export CEX_ROOT

# --- Resolve CLI + model via boot pipeline (yaml-driven, 5min cache) ---
# Try cex_boot_pipeline.py first (handles intent resolver + router + cache).
# Fall back to direct yaml awk if pipeline unavailable. Boot must never break.
PIPELINE_JSON=""
if command -v python >/dev/null 2>&1; then
  PIPELINE_JSON=$(python _tools/cex_boot_pipeline.py --nucleus "$NUCLEUS" --json 2>/dev/null || echo "")
fi

if [ -n "$PIPELINE_JSON" ] && command -v python >/dev/null 2>&1; then
  if [ -z "$CLI" ]; then
    CLI=$(printf '%s' "$PIPELINE_JSON" | python -c "import json,sys; print(json.load(sys.stdin).get('cli','claude'))" 2>/dev/null || echo "claude")
  fi
  MODEL=$(printf '%s' "$PIPELINE_JSON" | python -c "import json,sys; print(json.load(sys.stdin).get('model','opus'))" 2>/dev/null || echo "opus")
else
  # Fallback: direct yaml awk read (legacy path)
  if [ -z "$CLI" ]; then
    CLI=$(awk -v nuc="$NUCLEUS" '
      $0 ~ "^"nuc":" { in_block=1; next }
      in_block && /^[a-z]/ && !/^  / { in_block=0 }
      in_block && /^  cli:/ { print $2; exit }
    ' .cex/config/nucleus_models.yaml 2>/dev/null || echo "claude")
  fi
  MODEL=$(awk -v nuc="$NUCLEUS" '
    $0 ~ "^"nuc":" { in_block=1; next }
    in_block && /^[a-z]/ && !/^  / { in_block=0 }
    in_block && /^  model:/ { print $2; exit }
  ' .cex/config/nucleus_models.yaml 2>/dev/null || echo "opus")
fi

# Map runtime to entry file
case "$RUNTIME" in
  claude)  ENTRY_FILE="CLAUDE.md" ;;
  codex)   ENTRY_FILE="AGENTS.md" ;;
  gemini)  ENTRY_FILE="GEMINI.md" ;;
  ollama)  ENTRY_FILE="OLLAMA.md" ;;
  *) echo "Invalid --runtime: $RUNTIME (use claude|codex|gemini|ollama)"; exit 1 ;;
esac

# Sin lookup (per nucleus_def files)
case "$NUCLEUS" in
  n01) SIN="Analytical Envy" ;;
  n02) SIN="Creative Lust" ;;
  n03) SIN="Inventive Pride" ;;
  n04) SIN="Knowledge Gluttony" ;;
  n05) SIN="Gating Wrath" ;;
  n06) SIN="Strategic Greed" ;;
  n07) SIN="Orchestrating Sloth" ;;
esac

# Handoff: the task lives in a file, never on the command line (avoids
# nested-quote hell). Written by _spawn/spawn_solo.ps1 / spawn_grid.ps1 (or by
# hand for a direct run).
HANDOFF_REL=".cex/runtime/handoffs/${NUCLEUS}_task.md"

# Inline system prompt (mirrors PowerShell boots)
SYS_PROMPT="You are driven by ${SIN}. 8F pipeline mandatory. You are ${CEX_NUCLEUS} of CEX. Read ${ENTRY_FILE} (runtime entry) then .claude/rules/${NUCLEUS}-*.md (your nucleus rules). IF ${HANDOFF_REL} EXISTS, READ AND EXECUTE IMMEDIATELY."

INITIAL_MSG="Read ${HANDOFF_REL} and execute. If no handoff, report ready."

echo "==============================================="
echo "  [*] ${CEX_NUCLEUS} -- ${SIN}"
echo "  ${CLI} | ${MODEL} | runtime=${RUNTIME} | entry=${ENTRY_FILE}"
echo "==============================================="

# --- Launch CLI ---
case "$CLI" in
  claude)
    # --append-system-prompt is LAST-WINS across repeats (same CLI fact the
    # claude_boot.sh family guards against) -- 2 separate flags here meant only
    # $SYS_PROMPT ever reached the model; "${NUCLEUS^^}" was silently dropped
    # (low practical impact since $SYS_PROMPT already embeds "You are ${CEX_NUCLEUS}
    # of CEX", but still dead code repeating the same bug class). Combine into one.
    exec claude \
      --dangerously-skip-permissions \
      --permission-mode bypassPermissions \
      --model "$MODEL" \
      --append-system-prompt "$(printf '%s\n\n%s' "${NUCLEUS^^}" "$SYS_PROMPT")" \
      "$INITIAL_MSG"
    ;;
  gemini)
    exec gemini --yolo --model "$MODEL" -p "$SYS_PROMPT $INITIAL_MSG"
    ;;
  codex)
    exec codex --dangerously-bypass-approvals-and-sandbox -m "$MODEL" "$SYS_PROMPT $INITIAL_MSG"
    ;;
  ollama)
    exec ollama run "$MODEL" "$SYS_PROMPT $INITIAL_MSG"
    ;;
  *)
    echo "Unknown CLI: $CLI"
    exit 1
    ;;
esac
