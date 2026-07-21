#!/bin/sh
# CEX tenant N07 orchestrator boot -- self-contained launcher (Mac / Linux / WSL).
# No dependency on boot/_shared/*.sh. Resolves repo root from its own location.
# Model default (R-126): reads the tenant's OWN .cex/config/nucleus_models.yaml (n07 entry,
# full claude-* ids only) with a degrade-never fallback to the hardcoded default below.
# System prompt (R-022): sin identity + agent card CONTENT merge into ONE file passed via a
# single content-carrying append flag -- never the literal-path form, never last-wins repeats.
# This script lives in <root>/boot/ -- repo root is its parent directory.
set -eu

# --- Resolve repo root (script dir is <root>/boot; root is one level up) ---
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd -P)
CEX_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)

cd "$CEX_ROOT"

# --- Environment ---
CEX_NUCLEUS=N07
export CEX_NUCLEUS
export CEX_ROOT

# --- Model (R-126: yaml-with-fallback, degrade-never) ---
# Precedence: CEX_MODEL_OVERRIDE env > nucleus_models.yaml n07 model > hardcoded default.
# The yaml n07 `model:` value is honored ONLY when it is a FULL Anthropic model id
# (claude-*). Shorthand aliases (fable / opus / sonnet) need Central's resolver stack
# (model_aliases + FABLE_SELF_HEAL), which this self-contained launcher deliberately does
# not depend on -- honoring them naively could pass a CLI-unknown alias or silently
# upgrade tenant N07 past the SONNET5_DEFAULT_POLICY (2026-07-01) tenant-boot Sonnet
# default. Absent / unparseable yaml, or a non-full-id value -> the hardcode. For
# money-touching / irreversible / client-ship verify sessions override with:
# CEX_MODEL_OVERRIDE=claude-opus-4-8 before launch, or pass --model on the CLI.
MODEL="claude-sonnet-4-6"
MODELS_YAML="$CEX_ROOT/.cex/config/nucleus_models.yaml"
if [ -f "$MODELS_YAML" ]; then
  YAML_MODEL=$(awk '/^n07:[ \t\r]*$/ { in07 = 1; next }
    in07 && /^[^ \t\r]/ { exit }
    in07 && /^  model:/ { sub(/\r$/, "", $2); print $2; exit }' "$MODELS_YAML" 2>/dev/null) || YAML_MODEL=""
  case "$YAML_MODEL" in
    claude-*) MODEL="$YAML_MODEL" ;;
  esac
fi
MODEL="${CEX_MODEL_OVERRIDE:-$MODEL}"
CARD="N07_admin/P08_architecture/agent_card_n07.md"

printf '\n  CEX N07 orchestrator (tenant)\n  root  : %s\n  model : %s\n\n' "$CEX_ROOT" "$MODEL"

# --- Pre-flight: Claude Code CLI must be on PATH ---
command -v claude >/dev/null 2>&1 || { echo "[FAIL] 'claude' CLI not found on PATH. Install Claude Code first." >&2; exit 1; }

# --- System prompt: ONE merged append (R-022, cex_write_boot_append idiom inlined) ---
# claude CLI facts, proven on disk (see boot/_shared/claude_boot.sh in Central):
# (1) the path-string form of the append flag injects the literal PATH, never file
# content -- only the -file form injects CONTENT; (2) both forms are LAST-WINS across
# repeats; (3) the two forms are mutually exclusive. So the sin identity + the agent
# card CONTENT merge into ONE file under the boot cache, passed as a single flag.
# Degrade-never: a missing card only shrinks the merge; a failed write skips the
# append entirely -- the boot itself never breaks.
SYS_PROMPT="You are driven by Orchestrating Sloth -- you delegate perfectly and never build directly. You are the N07 Orchestrator of this CEX tenant. Read CLAUDE.md and .claude/rules/n07-orchestrator.md before acting."
APPEND_FILE="$CEX_ROOT/.cex/cache/boot/append_final_n07.md"
if mkdir -p "$CEX_ROOT/.cex/cache/boot" 2>/dev/null && : > "$APPEND_FILE" 2>/dev/null; then
  if [ -f "$CARD" ]; then
    cat "$CARD" >> "$APPEND_FILE" 2>/dev/null || true
    printf '\n\n' >> "$APPEND_FILE" 2>/dev/null || true
  else
    echo "[WARN] agent card not found: $CARD (merged append carries the identity only)" >&2
  fi
  # R-422 (boot consciousness): 3 more G8 sources, same guarded-append idiom as the agent card
  # above -- mirrors Central's own boot/n07.ps1 $appendSources order (minus dispatch_catalog.md,
  # which is N07-only/Central-only and deliberately never carried into any tenant tree -- see
  # cex_distill.py's _emit_invariant/_emit_variable R-422 carry comments).
  for extra in \
    ".cex/P09_config/context_self_select.md" \
    ".cex/P09_config/nucleus_kinds_n07.md" \
    ".cex/P09_config/constitution_manifest.md"
  do
    if [ -f "$extra" ]; then
      cat "$extra" >> "$APPEND_FILE" 2>/dev/null || true
      printf '\n\n' >> "$APPEND_FILE" 2>/dev/null || true
    else
      echo "[WARN] boot-consciousness source not found: $extra (merged append shrinks by one source)" >&2
    fi
  done
  printf '%s' "$SYS_PROMPT" >> "$APPEND_FILE" 2>/dev/null || true
else
  APPEND_FILE=""
  echo "[WARN] merged system-prompt append failed (launching without it)" >&2
fi

# --- Launch (exec replaces this shell; forward extra args as an initial prompt) ---
if [ -n "$APPEND_FILE" ]; then
  exec claude \
    --dangerously-skip-permissions \
    --permission-mode bypassPermissions \
    --model "$MODEL" \
    --append-system-prompt-file "$APPEND_FILE" \
    "$@"
else
  exec claude \
    --dangerously-skip-permissions \
    --permission-mode bypassPermissions \
    --model "$MODEL" \
    "$@"
fi
