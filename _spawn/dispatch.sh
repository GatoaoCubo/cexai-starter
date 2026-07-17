#!/bin/bash
# CEX Dispatch -- bash wrapper for claude/N07
#
# Usage:
#   bash _spawn/dispatch.sh solo n03 "task"              # dispatch 1 nucleus (default model)
#   bash _spawn/dispatch.sh solo n03 -m claude-sonnet-4-6  # dispatch with model override
#   bash _spawn/dispatch.sh solo n03 "task" -m sonnet    # task + model override
#   bash _spawn/dispatch.sh solo n03 -cli gemini "task"  # per-cell runtime: boot n03_gemini.ps1 (WS5.0)
#   bash _spawn/dispatch.sh solo n03 -cli gemini "task" --dry-run  # show routing, spawn nothing
#   bash _spawn/dispatch.sh grid MISSION                 # dispatch up to 6 parallel
#   bash _spawn/dispatch.sh grid-haiku MISSION           # grid with haiku model
#   bash _spawn/dispatch.sh status                       # monitor running nuclei
#   bash _spawn/dispatch.sh stop                         # stop MY session's nuclei only
#   bash _spawn/dispatch.sh stop n03                     # stop only N03
#   bash _spawn/dispatch.sh stop --all                   # stop ALL CEX nuclei (DANGEROUS)
#   bash _spawn/dispatch.sh stop --dry-run               # preview what would be killed
#   bash _spawn/dispatch.sh swarm <kind> <N> "<task>"    # N parallel worktrees
#   bash _spawn/dispatch.sh solo n03 "task" -w <id>      # run in isolated worktree
#   bash _spawn/dispatch.sh grid MISSION -w              # grid with worktree per cell

# --- Session ID: stable identifier for this orchestrator ---
# Each claude/N07 session sets CEX_SESSION_ID once. All dispatch calls inherit it.
# If not set, generate from timestamp (stable within same second).
# IMPORTANT: For multi-N07, set CEX_SESSION_ID before first dispatch.
if [ -z "$CEX_SESSION_ID" ]; then
    SESSION_FILE=".cex/runtime/pids/.my_session"
    if [ -f "$SESSION_FILE" ]; then
        _val=$(cat "$SESSION_FILE")
        if [[ "$_val" =~ ^s[0-9]+$ ]]; then
            export CEX_SESSION_ID="$_val"
        else
            CEX_SESSION_ID="s$(date +%s)"
            export CEX_SESSION_ID
            echo "$CEX_SESSION_ID" > "$SESSION_FILE"
        fi
    else
        mkdir -p .cex/runtime/pids
        CEX_SESSION_ID="s$(date +%s)"
        export CEX_SESSION_ID
        echo "$CEX_SESSION_ID" > "$SESSION_FILE"
    fi
fi
export CEX_SESSION_ID

MODE="${1:-solo}"
shift

# --- Parse -w / --worktree flag (BORIS_MERGE B8 + spec_n07_per_cell_worktrees) ---
# Scans remaining args, strips the flag, exports CEX_WORKTREE for downstream boot wrappers.
#
# Per-cell semantics (spec_n07_per_cell_worktrees.md, Wave 1):
#   - solo mode + -w  -> single shared worktree (legacy behavior, unchanged)
#   - grid mode + -w  -> ONE worktree PER cell (one per matching handoff),
#                        provisioned by _tools/cex_worktree_manager.py.
#                        Each cell gets its own .git/index, eliminating the
#                        staged-file race observed on 2026-05-02.
#
# We only run the legacy single-worktree creation when MODE != "grid" so the
# grid branch can call cex_worktree_manager.py with the discovered nucleus list.
WORKTREE_ID=""
WORKTREE_FLAG_PRESENT=0
_new_args=()
while [ $# -gt 0 ]; do
    case "$1" in
        -w|--worktree)
            WORKTREE_FLAG_PRESENT=1
            shift
            WORKTREE_ID="${1:-auto}"
            [ "$WORKTREE_ID" = "auto" ] && WORKTREE_ID="wt_$(date +%s)"
            ;;
        *)
            _new_args+=("$1")
            ;;
    esac
    shift || true
done
set -- "${_new_args[@]}"
if [ -n "$WORKTREE_ID" ] && [ "$MODE" != "grid" ]; then
    # Legacy single-shared-worktree path (solo / swarm / etc).
    _WT_DIR=".cex/worktrees/$WORKTREE_ID"
    if [ ! -d "$_WT_DIR" ]; then
        # R-211: stderr AND exit status used to be fully suppressed
        # (`>/dev/null 2>&1 || true`), so a failed `git worktree add` left
        # CEX_WORKTREE_DIR exported and used downstream as if isolation had
        # been established, with no signal that it had not. Capture both now;
        # on failure, WARN with the real git error and leave CEX_WORKTREE /
        # CEX_WORKTREE_DIR UNSET (honest un-isolated fallback -- downstream
        # boot scripts already treat "unset" as legacy/shared-repo mode).
        _WT_ERR=$(git worktree add -b "worktree/$WORKTREE_ID" "$_WT_DIR" HEAD 2>&1)
        _WT_RC=$?
        if [ "$_WT_RC" -ne 0 ] || [ ! -d "$_WT_DIR" ]; then
            echo "[DISPATCH] WARN: worktree creation failed for $_WT_DIR (git exit $_WT_RC) -- proceeding WITHOUT isolation (shared repo)"
            if [ -n "$_WT_ERR" ]; then
                echo "$_WT_ERR" | sed 's/^/[DISPATCH]   git: /'
            fi
            unset CEX_WORKTREE
            unset CEX_WORKTREE_DIR
            _WT_DIR=""
        fi
    fi
    if [ -n "$_WT_DIR" ]; then
        export CEX_WORKTREE="$WORKTREE_ID"
        export CEX_WORKTREE_DIR="$_WT_DIR"
        echo "[DISPATCH] Worktree isolation: $CEX_WORKTREE_DIR"
    fi
fi

# --- Pre-flight: Autonomous Capability Router (ACR) ---
# Bakes the prerequisite capabilities the resolved kind needs (external context as
# ACTION 0, the spec-kit reflex, ...) INTO the handoff before boot, idempotently,
# under a "## Prerequisites (auto-resolved by ACR)" section. Runs for ALL dispatch
# modes (interactive + headless). The router is a complete no-op for kinds with no
# autonomy block AND no requires_external_context, so this NEVER regresses the ~297
# other kinds. If the router cannot run (import/exec failure), we fall back to the
# legacy MCP-only gather so dispatch is never broken.
_preflight_mcp() {
    local nucleus="$1"
    local handoff="$2"
    if [ ! -f "$handoff" ]; then
        return 0
    fi
    if ! command -v python &>/dev/null; then
        return 0
    fi
    # ACR preflight: resolves the handoff kind and appends the prerequisites
    # section in place (idempotent -- a second run is a byte-for-byte no-op).
    if python _tools/cex_capability_router.py --preflight \
            --nucleus "$nucleus" --handoff "$handoff" 2>/dev/null; then
        return 0
    fi
    # --- Thin fallback: legacy Phase 0 MCP gather (router unavailable) ---
    echo "[PREFLIGHT] ACR unavailable -- falling back to legacy MCP gather"
    local kind
    kind=$(python -c "
import re, sys
text = open('$handoff', encoding='utf-8', errors='ignore').read()
m = re.search(r'kind[=:]\s*(\w+)', text, re.IGNORECASE)
print(m.group(1) if m else '')
" 2>/dev/null)
    if [ -z "$kind" ]; then
        return 0
    fi
    # Check if kind needs external context
    local needs
    needs=$(python _tools/cex_router_v2.py --check-kind "$kind" --json 2>/dev/null | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('requires_external_context', False))" 2>/dev/null)
    if [ "$needs" = "True" ]; then
        local task_text
        task_text=$(head -20 "$handoff" | grep -v '^---' | head -5 | tr '\n' ' ')
        echo "[PREFLIGHT] Phase 0 MCP gather for $nucleus (kind=$kind)"
        python _tools/cex_preflight_mcp.py --nucleus "$nucleus" --kind "$kind" \
            --task "$task_text" --gather 2>/dev/null || true
    fi
}

# --- C29 wrapper-death confirm (ops refinement) ---------------------------------
# The kill phases live in PowerShell (spawn_stop.ps1 STEP 1 + spawn_solo.ps1
# kill-before-respawn), both via `taskkill /F /PID <pid> /T`. Wrappers occasionally
# survive as idle powershell windows (observed exit-255 leftovers). These helpers
# collect the SAME candidate set the PS killers target -- read from the PID file
# BEFORE the killer runs (it rewrites the file) -- then confirm each PID is really
# dead: poll up to ~6s (3x2s), ONE taskkill escalation (//-form so Git-Bash does
# not path-mangle the flags), re-check, WARN on survival. Never hangs, never exits
# nonzero, and NEVER touches a PID outside the set collected here.

_PID_FILE=".cex/runtime/pids/spawn_pids.txt"

_wrapper_alive() {
    # CSV form yields an exact quoted-PID token when alive; an INFO line when dead.
    tasklist //FI "PID eq $1" //FO CSV //NH 2>/dev/null | grep -q "\"$1\""
}

_strip_pid_line() {
    # Normalize a PID-file line written by PowerShell (CRLF + possible UTF-8 BOM).
    _LINE="${1//$'\r'/}"
    _LINE="${_LINE#$'\xef\xbb\xbf'}"
}

_collect_nucleus_pids() {
    # Mirror spawn_solo.ps1 kill-before-respawn: every PID-file entry whose nucleus
    # field matches. Its regex requires a field AFTER the nucleus token, so a bare
    # 2-field line is skipped here too (under-collect, never over-kill).
    local nuc="$1" line p n c out=""
    [ -f "$_PID_FILE" ] || { printf '%s' ""; return 0; }
    while IFS= read -r line || [ -n "$line" ]; do
        _strip_pid_line "$line"
        # shellcheck disable=SC2086
        set -- $_LINE
        p="${1:-}"; n="${2:-}"; c="${3:-}"
        case "$p" in ''|*[!0-9]*) continue ;; esac
        if [ "$n" = "$nuc" ] && [ -n "$c" ]; then out="$out $p"; fi
    done < "$_PID_FILE"
    printf '%s' "$out"
}

_collect_stop_pids() {
    # Mirror spawn_stop.ps1 STEP 1 selection exactly (reads STOP_ALL / STOP_NUC /
    # STOP_SESS set by the stop arg parser + CEX_SESSION_ID exported above).
    local tsess="" line p n s out=""
    [ -f "$_PID_FILE" ] || { printf '%s' ""; return 0; }
    if [ -n "$STOP_SESS" ]; then
        tsess="$STOP_SESS"
    elif [ -z "$STOP_ALL" ] && [ -z "$STOP_NUC" ]; then
        tsess="$CEX_SESSION_ID"
    fi
    while IFS= read -r line || [ -n "$line" ]; do
        _strip_pid_line "$line"
        # shellcheck disable=SC2086
        set -- $_LINE
        p="${1:-}"; n="${2:-}"; s="${4:-unknown}"
        case "$p" in ''|*[!0-9]*) continue ;; esac
        [ -n "$n" ] || continue
        if [ -n "$STOP_ALL" ]; then
            out="$out $p"
        elif [ -n "$STOP_NUC" ] && [ "$n" = "$STOP_NUC" ]; then
            if [ -z "$tsess" ] || [ "$s" = "$tsess" ]; then out="$out $p"; fi
        elif [ -z "$STOP_NUC" ] && [ -n "$tsess" ] && [ "$s" = "$tsess" ]; then
            out="$out $p"
        fi
    done < "$_PID_FILE"
    printf '%s' "$out"
}

_confirm_wrappers_dead() {
    # For each just-killed wrapper PID: poll up to ~6s (3x2s) for death; if still
    # alive -> ONE escalation (the same force+tree kill the PS killers use); then
    # re-check; a survivor only WARNs. Always returns 0 -- teardown never hangs
    # and never fails the dispatch over a zombie wrapper.
    local pid tries
    for pid in "$@"; do
        case "$pid" in ''|*[!0-9]*) continue ;; esac
        tries=0
        while [ "$tries" -lt 3 ] && _wrapper_alive "$pid"; do
            sleep 2
            tries=$((tries + 1))
        done
        if _wrapper_alive "$pid"; then
            taskkill //F //PID "$pid" //T >/dev/null 2>&1 || true
            sleep 2
            if _wrapper_alive "$pid"; then
                echo "[WARN] wrapper $pid survived teardown"
            fi
        fi
    done
    return 0
}

# --- Rate-limit budget guard preflight (LEVERAGE_A1, kind=backpressure_policy) ---
# OFF by default (CEX_RATELIMIT_GUARD unset) -> immediate no-op; the dispatch path
# below is BYTE-IDENTICAL to pre-A1. ON (CEX_RATELIMIT_GUARD=1) -> ADVISORY: it
# emits best-effort cost_log events (restoring the instrumentation) + prints the
# 5h/weekly-opus headroom + concurrency-governor verdict, then PROCEEDS. It hard-
# blocks (rc=3) ONLY when the guard itself returns rc=3, which happens solely
# under CEX_RATELIMIT_ENFORCE=1 + an `over` verdict. Degrade-never: any other rc
# (python missing, guard bug, timeout) -> return 0 (proceed). The guard tool also
# fails open internally, so a guard error never reaches an enforced block.
# Args: <mode> <model> <cells> <nuclei-csv> <mission>
_ratelimit_preflight() {
    [ "${CEX_RATELIMIT_GUARD:-0}" = "1" ] || return 0
    command -v python >/dev/null 2>&1 || return 0
    local _mode="${1:-solo}" _model="${2:-opus}" _cells="${3:-1}"
    local _nuclei="${4:-}" _mission="${5:-}"
    local _args="preflight --mode $_mode --model $_model --cells $_cells --emit-cost --handoff-dir .cex/runtime/handoffs"
    if [ -n "$_nuclei" ]; then _args="$_args --nuclei $_nuclei"; fi
    if [ -n "$_mission" ]; then _args="$_args --mission $_mission"; fi
    # shellcheck disable=SC2086
    python _tools/cex_ratelimit_guard.py $_args
    if [ "$?" = "3" ]; then
        echo "[DISPATCH] rate-limit guard: ENFORCE block (over budget). Aborting dispatch (unset CEX_RATELIMIT_ENFORCE to override)."
        return 3
    fi
    return 0
}

# --- A2 AUTOROUTE: cheapest-competent path resolver (LEVERAGE_A2, kind=router) ---
# Gated by CEX_AUTOROUTE -- DEFAULT-ON since mission GRAD (2026-06-14, founder-
# approved from the STRESS_OPT measurements: 100% routing-correct, 0% unsafe-cheap,
# 75.3% Opus-call cut). Explicit OFF (CEX_AUTOROUTE=0/false) -> the helpers below
# are never reached and every dispatch mode stays BYTE-IDENTICAL to pre-A2.
# ON (default / unset) -> a plain `solo n0X "task"` (no -m / -cli override) resolves
# the cheapest COMPETENT path via `cex_router_v2.py --exec-path` and dispatches it:
#   decompose   -> bash dispatch.sh decompose n0X "task"        (structured kinds)
#   sonnet_solo -> bash dispatch.sh solo n0X -m sonnet "task"   (mid structural)
#   mode_a_opus -> bash dispatch.sh solo n0X "task"             (complex/uncertain; the SAFE default)
# fail-OPEN: any resolver error -> mode_a_opus (the SAFE strong default).
# CEX_AUTOROUTE_ACTIVE guards the child dispatches against re-entry (no recursion).
_autoroute_enabled() {
    # Default-ON (graduated mission GRAD 2026-06-14): UNSET -> enabled. An explicit
    # CEX_AUTOROUTE=0/false/no/off -> disabled (legacy byte-identical Opus boot).
    case "${CEX_AUTOROUTE:-1}" in
        0|false|FALSE|no|NO|off|OFF) return 1 ;;
        *) return 0 ;;
    esac
}

_autoroute_json_get() {  # <json> <key> -> value ("" on any failure)
    printf '%s' "$1" | python -c "
import sys, json
try:
    print(json.load(sys.stdin).get('$2', ''))
except Exception:
    print('')
" 2>/dev/null
}

_autoroute_dispatch() {
    # <nucleus> <task> <dry-flag-or-empty>. Resolve the exec path + dispatch via
    # the chosen mode. Returns the child's exit code. Fail-open: resolver
    # unavailable -> Mode-A Opus solo (today's default path).
    local nuc="$1" task="$2" dry="$3"
    local handoff=".cex/runtime/handoffs/${nuc}_task.md"
    local json path kind reason
    json=$(python _tools/cex_router_v2.py --exec-path --task "$handoff" --intent "$task" --json 2>/dev/null)
    path=$(_autoroute_json_get "$json" path)
    kind=$(_autoroute_json_get "$json" kind)
    reason=$(_autoroute_json_get "$json" reason)
    if [ -z "$path" ]; then
        path="mode_a_opus"
        reason="resolver unavailable (fail-open -> Mode-A Opus)"
    fi
    echo "[DISPATCH] AUTOROUTE: $nuc kind=${kind:-?} -> $path"
    echo "[DISPATCH]   why: $reason"
    case "$path" in
        decompose)
            CEX_AUTOROUTE_ACTIVE=1 bash "$0" decompose "$nuc" "$task" $dry
            ;;
        sonnet_solo)
            CEX_AUTOROUTE_ACTIVE=1 bash "$0" solo "$nuc" -m sonnet "$task" $dry
            ;;
        *)  # mode_a_opus or any unexpected value -> today's default (opus solo)
            CEX_AUTOROUTE_ACTIVE=1 bash "$0" solo "$nuc" "$task" $dry
            ;;
    esac
}

_autoroute_solo_intercept() {
    # Top-of-`solo` hook (only when CEX_AUTOROUTE=1 and not already a child).
    # Args = the solo args ($@, nucleus first). RETURNS 1 (no side effects) to
    # fall through to legacy solo when an explicit -m/-cli override is present.
    # Otherwise dispatches via _autoroute_dispatch and EXITs with its code.
    local nuc="${1:-n03}"; shift || true
    local task="" dry="" a
    for a in "$@"; do
        case "$a" in
            -m|--model|-cli|--cli) return 1 ;;   # explicit override -> legacy solo
        esac
    done
    while [ $# -gt 0 ]; do
        case "$1" in
            --dry-run) dry="--dry-run"; shift ;;
            *) task="$1"; shift ;;
        esac
    done
    _autoroute_dispatch "$nuc" "$task" "$dry"
    exit $?
}

case "$MODE" in
    solo)
        # --- A2 AUTOROUTE interception (flag-gated; inert + byte-identical when off) ---
        # Autoroute (default-ON) makes the cheap path the DEFAULT: resolve {decompose |
        # sonnet_solo | mode_a_opus} from the handoff kind and dispatch via it.
        # Skipped when CEX_AUTOROUTE=0/false (this whole branch is unreachable)
        # or when already inside an autoroute child (CEX_AUTOROUTE_ACTIVE set), so
        # an explicit -m/-cli override and the legacy path stay byte-identical.
        if _autoroute_enabled && [ -z "${CEX_AUTOROUTE_ACTIVE:-}" ]; then
            _autoroute_solo_intercept "$@" || true
        fi
        NUCLEUS="${1:-n03}"
        shift || true
        # Parse optional flags: -m MODEL, -cli PROVIDER, --dry-run (remaining positional = TASK)
        # WS5.0 per-cell routing fix: -cli {claude|gemini|codex|ollama|litellm} boots the
        # matching boot/n0X_<cli>.ps1 variant (via spawn_solo.ps1, which already honors -cli).
        # When -cli is ABSENT, no -cli is forwarded and spawn_solo.ps1 resolves the CLI from
        # nucleus_models.yaml exactly as before -- zero regression for the default path.
        MODEL=""
        CLI=""
        TASK=""
        SOLO_DRY=""
        while [ $# -gt 0 ]; do
            case "$1" in
                -m|--model) shift; MODEL="${1:-}"; shift || true ;;
                -cli|--cli) shift; CLI="${1:-}"; shift || true ;;
                --dry-run)  SOLO_DRY="1"; shift ;;
                *) TASK="$1"; shift ;;
            esac
        done
        echo "[DISPATCH] Solo: $NUCLEUS -> $TASK${MODEL:+ (model=$MODEL)}${CLI:+ (cli=$CLI)}${SOLO_DRY:+ [dry-run]}"
        _MODEL_ARG=""
        if [ -n "$MODEL" ]; then _MODEL_ARG="-Model $MODEL"; fi
        _CLI_ARG=""
        if [ -n "$CLI" ]; then _CLI_ARG="-cli $CLI"; fi
        # --- Spawn-free routing proof (--dry-run): print the EXACT boot the solo path would
        # launch, including per-cell -cli routing, WITHOUT spawning a real runtime. Mirrors
        # spawn_solo.ps1's variant logic (cliSuffix). Lets N07 verify routing at zero quota cost
        # (WS5.0 PROIBIDO: no real dispatch). Matches the auto/decompose --dry-run convention. ---
        if [ -n "$SOLO_DRY" ]; then
            echo "[DISPATCH] (dry-run) would spawn: spawn_solo.ps1 -nucleus $NUCLEUS -task \"$TASK\"${_MODEL_ARG:+ $_MODEL_ARG}${_CLI_ARG:+ $_CLI_ARG} -interactive"
            if [ -n "$CLI" ]; then
                if [ "$CLI" = "claude" ]; then
                    echo "[DISPATCH] (dry-run) boot variant: boot/${NUCLEUS}.ps1 (cli=claude)"
                else
                    echo "[DISPATCH] (dry-run) boot variant: boot/${NUCLEUS}_${CLI}.ps1 (cli=$CLI)"
                fi
            else
                echo "[DISPATCH] (dry-run) boot variant: resolved from nucleus_models.yaml (no -cli flag -- default routing)"
            fi
            exit 0
        fi
        # --- T09: Agent spawn pre-flight validation ---
        if command -v python &>/dev/null; then
            if ! python _tools/cex_agent_spawn.py --validate --nucleus "$NUCLEUS" 2>/dev/null; then
                echo "[DISPATCH] WARN: Agent validation failed for $NUCLEUS (proceeding anyway)"
            fi
        fi
        # --- ACR preflight (P0 FIX b): bake prerequisites into the handoff before boot.
        # The interactive Claude path now hits the same preflight as the headless modes. ---
        _preflight_mcp "$NUCLEUS" ".cex/runtime/handoffs/${NUCLEUS}_task.md"
        # Rate-limit budget guard (advisory unless CEX_RATELIMIT_ENFORCE=1; no-op
        # unless CEX_RATELIMIT_GUARD=1). cells=1 for solo -> only `over` under a
        # near-exhausted 5h/weekly-opus window can enforce-block.
        if ! _ratelimit_preflight "solo" "${MODEL:-opus}" 1 "$NUCLEUS" ""; then exit 3; fi
        # C29: spawn_solo.ps1 kill-before-respawn targets this nucleus's PID-file
        # entries -- collect them BEFORE it runs, confirm death AFTER it returns.
        _C29_SET=$(_collect_nucleus_pids "$NUCLEUS")
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_solo.ps1 -nucleus "$NUCLEUS" -task "$TASK" $_MODEL_ARG $_CLI_ARG -interactive
        _C29_RC=$?
        # shellcheck disable=SC2086
        _confirm_wrappers_dead $_C29_SET
        exit $_C29_RC
        ;;
    autoroute)
        # A2 LEVERAGE_A2 -- explicit cheapest-competent single-artifact routing.
        # Same resolver as the CEX_AUTOROUTE=1 solo interception, callable directly
        # (and without flipping the env flag), e.g. to verify routing at zero cost:
        #   bash _spawn/dispatch.sh autoroute n03 "create kc_react_patterns"
        #   bash _spawn/dispatch.sh autoroute n03 "create kc_x" --dry-run
        # Resolves the handoff kind -> decompose | sonnet_solo | mode_a_opus, prints
        # the chosen path + why, then dispatches. Fail-open to Mode-A Opus.
        NUCLEUS="${1:-n03}"
        shift || true
        AR_TASK=""
        AR_DRY=""
        while [ $# -gt 0 ]; do
            case "$1" in
                --dry-run) AR_DRY="--dry-run"; shift ;;
                *) AR_TASK="$1"; shift ;;
            esac
        done
        _autoroute_dispatch "$NUCLEUS" "$AR_TASK" "$AR_DRY"
        ;;
    auto)
        # MAX_LEVERAGE P2.3 INTEGRATION -- make the gated swarm the DEFAULT path.
        # Consults the W4 route_task guard (cex_router_v2.route_dispatch_topology):
        #   bulk-similar batch (N>=10 AND cohesive)  -> GATED mentor-student swarm
        #                                               (cex_mentor_swarm: W2 gate + W5 ladder)
        #   single / heterogeneous request           -> Mode A (the existing solo path)
        # ADDITIVE: solo / grid / decompose / swarm stay byte-for-byte unchanged.
        #
        #   bash _spawn/dispatch.sh auto n04 "create kc_x" --batch N04_knowledge/ --n 3
        #   bash _spawn/dispatch.sh auto n03 "build one agent"          # single -> Mode A
        NUCLEUS="${1:-n03}"
        shift || true
        AUTO_TASK=""
        BATCH_SPEC=""
        AUTO_N="3"
        AUTO_DRY=""
        while [ $# -gt 0 ]; do
            case "$1" in
                --batch)   shift; BATCH_SPEC="${1:-}"; shift || true ;;
                --n)       shift; AUTO_N="${1:-3}"; shift || true ;;
                --dry-run) AUTO_DRY="1"; shift ;;
                *)         AUTO_TASK="$1"; shift ;;
            esac
        done
        # Consult the router for the DEFAULT-path topology decision (no spawn yet).
        _ROUTER_ARGS="--dispatch-auto --min-batch 10 --json"
        if [ -n "$BATCH_SPEC" ]; then _ROUTER_ARGS="$_ROUTER_ARGS --batch-dir $BATCH_SPEC"; fi
        # shellcheck disable=SC2086
        _ROUTER_JSON=$(python _tools/cex_router_v2.py $_ROUTER_ARGS 2>/dev/null)
        TOPOLOGY=$(printf '%s' "$_ROUTER_JSON" | python -c "
import sys, json
try:
    print(json.load(sys.stdin).get('topology', 'mode_a'))
except Exception:
    print('mode_a')
" 2>/dev/null)
        [ -z "$TOPOLOGY" ] && TOPOLOGY="mode_a"
        if [ "$TOPOLOGY" = "swarm" ]; then
            echo "[DISPATCH] auto -> GATED SWARM (bulk-similar): $NUCLEUS x$AUTO_N -> $AUTO_TASK"
            if [ -n "$AUTO_DRY" ]; then
                python _tools/cex_mentor_swarm.py --nucleus "$NUCLEUS" --task "$AUTO_TASK" --n "$AUTO_N" --dry-run
            else
                python _tools/cex_mentor_swarm.py --nucleus "$NUCLEUS" --task "$AUTO_TASK" --n "$AUTO_N"
            fi
        else
            echo "[DISPATCH] auto -> MODE A (single/heterogeneous): solo $NUCLEUS -> $AUTO_TASK"
            # Reuse the EXISTING solo Mode-A path verbatim (interactive boot).
            _preflight_mcp "$NUCLEUS" ".cex/runtime/handoffs/${NUCLEUS}_task.md"
            if [ -n "$AUTO_DRY" ]; then
                echo "[DISPATCH] (dry-run) would spawn: spawn_solo.ps1 -nucleus $NUCLEUS -task \"$AUTO_TASK\" -interactive"
            else
                if ! _ratelimit_preflight "auto" "opus" 1 "$NUCLEUS" "auto"; then exit 3; fi
                powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_solo.ps1 -nucleus "$NUCLEUS" -task "$AUTO_TASK" -interactive
            fi
        fi
        ;;
    swarm)
        KIND="${1:-agent}"
        N="${2:-3}"
        TASK="${3:-build one $KIND}"
        echo "[DISPATCH] Swarm: $N parallel $KIND (worktree per cell)"
        # Rate-limit governor: N parallel cells vs the cap (swarm is the widest
        # fan-out CEX has). Advisory unless CEX_RATELIMIT_ENFORCE=1; no-op off.
        if ! _ratelimit_preflight "swarm" "opus" "$N" "" "swarm_$KIND"; then exit 3; fi
        bash _spawn/spawn_swarm.sh "$KIND" "$N" "$TASK"
        ;;
    crew)
        # Composable-crew dispatch (spec 06 P4 -- the GATED mechanism).
        #   bash _spawn/dispatch.sh crew <name> [--charter PATH] [--dry-run]
        # Shells the crew control plane (cex_crew.py run --control-plane). DEFAULT =
        # OFFLINE: prompt-gen + the resolved plan + the charter gate, with the live
        # tool_resolver UNBOUND (no LLM spend). The --execute live lane is honored
        # ONLY when CEX_CREW_LIVE=1 is ALSO set; otherwise it FALLS BACK to the
        # offline run with a clear [GATED] message. FAIL-CLOSED: a missing/half-set
        # flag never produces a silent live run (the binding in cex_crew.py is the
        # real gate -- this case just refuses to forward --execute without the flag).
        # Each irreversible crew role passes through the agent loop's HITL gate
        # (cexai.governance.hitl.FileApprovalGate) even on the live lane.
        # Parse flags in ANY order; the first NON-flag token is the crew name.
        CREW_NAME=""
        CREW_CHARTER=""
        CREW_DRY=""
        CREW_EXECUTE=""
        while [ $# -gt 0 ]; do
            case "$1" in
                --charter)  shift; CREW_CHARTER="${1:-}"; shift || true ;;
                --dry-run)  CREW_DRY="1"; shift ;;
                --execute)  CREW_EXECUTE="1"; shift ;;
                *)          CREW_NAME="${CREW_NAME:-$1}"; shift ;;
            esac
        done
        if [ -z "$CREW_NAME" ]; then
            echo "[DISPATCH] FAIL: crew requires a <name> (try: python _tools/cex_crew.py list)"
            exit 1
        fi
        if ! command -v python >/dev/null 2>&1; then
            echo "[DISPATCH] FAIL: python not found on PATH"
            exit 1
        fi
        _CREW_ARGS="run $CREW_NAME --control-plane"
        if [ -n "$CREW_CHARTER" ]; then _CREW_ARGS="$_CREW_ARGS --charter $CREW_CHARTER"; fi
        # Decide the lane. --execute is the live request; honor it ONLY if the
        # CEX_CREW_LIVE kill-switch is truthy AND the caller did not force --dry-run.
        _CREW_LANE="offline (dry / prompt-gen, tool_resolver UNBOUND)"
        if [ -n "$CREW_EXECUTE" ] && [ -z "$CREW_DRY" ]; then
            case "${CEX_CREW_LIVE:-}" in
                1|true|TRUE|yes|YES|on|ON)
                    _CREW_ARGS="$_CREW_ARGS --execute"
                    _CREW_LANE="LIVE (CEX_CREW_LIVE set; irreversible roles HITL-gated)"
                    ;;
                *)
                    echo "[GATED] live crew requires CEX_CREW_LIVE=1 + founder approval -- running OFFLINE (dry)."
                    ;;
            esac
        fi
        echo "[DISPATCH] Crew: $CREW_NAME${CREW_CHARTER:+ (charter=$CREW_CHARTER)} -> $_CREW_LANE"
        # shellcheck disable=SC2086
        python _tools/cex_crew.py $_CREW_ARGS
        ;;
    decompose)
        # 3-stage 8F decompose dispatch:
        #   Stage 1 (Opus reasoning) -> prompt_package
        #   Stage 2 (cheap model F6) -> raw artifact
        #   Stage 3 (tools) -> doctor + compile + commit + signal
        # Spec: _docs/specs/spec_8f_decompose.md  (section 5: dispatch.sh integration)
        # Tier config: .cex/config/nucleus_models.yaml (tiers.decompose)
        NUCLEUS="${1:-n03}"
        shift || true
        DECOMP_TASK=""
        DECOMP_S1=""
        DECOMP_S2=""
        DECOMP_DRY=""
        DECOMP_SKIP3=""
        while [ $# -gt 0 ]; do
            case "$1" in
                -1|--stage-1-model) shift; DECOMP_S1="${1:-}"; shift || true ;;
                -2|--stage-2-model) shift; DECOMP_S2="${1:-}"; shift || true ;;
                --dry-run)          DECOMP_DRY="--dry-run"; shift ;;
                --skip-stage-3)     DECOMP_SKIP3="--skip-stage-3"; shift ;;
                *)                  DECOMP_TASK="$1"; shift ;;
            esac
        done
        if [ -z "$DECOMP_TASK" ]; then
            DECOMP_TASK="create artifact for $NUCLEUS"
        fi
        echo "[DISPATCH] Decompose: $NUCLEUS -> $DECOMP_TASK${DECOMP_S1:+ (s1=$DECOMP_S1)}${DECOMP_S2:+ (s2=$DECOMP_S2)}${DECOMP_DRY:+ [dry-run]}"
        _S1_ARG=""
        _S2_ARG=""
        if [ -n "$DECOMP_S1" ]; then _S1_ARG="--stage-1-model $DECOMP_S1"; fi
        if [ -n "$DECOMP_S2" ]; then _S2_ARG="--stage-2-model $DECOMP_S2"; fi
        # shellcheck disable=SC2086
        python _tools/cex_decompose.py \
            --nucleus "$NUCLEUS" \
            --task "$DECOMP_TASK" \
            $_S1_ARG $_S2_ARG $DECOMP_DRY $DECOMP_SKIP3
        ;;
    grid)
        MISSION="${1:-DEFAULT}"
        shift || true
        # --- Parse --cli-map flag (per-cell runtime override, mission SHOWOFF_V2+) ---
        # Format: --cli-map <path-to-json>
        # JSON shape: { "n01": {"cli": "claude", "model": "..."}, ... }
        # Convention fallback: if .cex/runtime/cli_maps/{MISSION}.json exists, auto-use it.
        # Each cell's cli + model is read by spawn_grid.ps1's Launch-Nucleus and
        # overrides the global -cli and CEX_MODEL_OVERRIDE for that one cell only.
        CLI_MAP_PATH=""
        GRID_CHARTER=""
        _new_grid_args=()
        while [ $# -gt 0 ]; do
            case "$1" in
                --cli-map) shift; CLI_MAP_PATH="${1:-}"; shift || true ;;
                --charter) shift; GRID_CHARTER="${1:-}"; shift || true ;;
                *) _new_grid_args+=("$1"); shift ;;
            esac
        done
        set -- "${_new_grid_args[@]}"
        # Convention fallback
        if [ -z "$CLI_MAP_PATH" ]; then
            _convention_path=".cex/runtime/cli_maps/${MISSION}.json"
            if [ -f "$_convention_path" ]; then
                CLI_MAP_PATH="$_convention_path"
                echo "[DISPATCH] Auto-loaded cli-map from convention: $CLI_MAP_PATH"
            fi
        fi
        if [ -n "$CLI_MAP_PATH" ]; then
            if [ ! -f "$CLI_MAP_PATH" ]; then
                echo "[DISPATCH] FAIL: --cli-map file not found: $CLI_MAP_PATH"
                exit 1
            fi
            # Convert to absolute path so child PS process can find it regardless of cwd
            export CEX_GRID_CLIMAP=$(python -c "import os,sys; print(os.path.abspath(sys.argv[1]))" "$CLI_MAP_PATH")
            echo "[DISPATCH] Per-cell cli-map active: $CEX_GRID_CLIMAP"
        fi
        # --- Handoff filename parser (DISPATCH_FIX spec_dispatch_grid_fix v1.0.0) ---
        # The legacy `${base##*_}` heuristic returned "task" for any handoff that
        # ended in `_task.md`, which broke -w worktree provisioning + ACR preflight
        # + same-nucleus parallelism. This helper extracts BOTH the nucleus token
        # (n0X anywhere in the basename) and the cell_slug (everything between the
        # mission prefix and the optional _task suffix) so same-nucleus parallel
        # grids land in distinct `wt_<cell_slug>` worktrees.
        #
        # Usage:
        #   _parse_handoff_cell "<basename-no-ext>" "<MISSION>"
        #   -> sets globals _OUT_NUC (e.g. "n03") and _OUT_SLUG (e.g. "n03_anuncio")
        #
        # Test matrix:
        #   INIT_WAVE_A_n04           -> nuc=n04 slug=n04         (legacy, no _task)
        #   DISPATCH_FIX_n03_task     -> nuc=n03 slug=n03         (newer, single cell)
        #   CODEXA_V2_WAVE_B_n03_anuncio_task -> nuc=n03 slug=n03_anuncio (cell-disc'd)
        _parse_handoff_cell() {
            local _base="$1"
            local _mission="$2"
            local _cs="${_base#${_mission}_}"
            _cs="${_cs%_task}"
            local _nuc=""
            local _p
            local _parts
            IFS='_' read -ra _parts <<< "$_cs"
            for _p in "${_parts[@]}"; do
                if [[ "$_p" =~ ^n[0-9]+$ ]]; then
                    _nuc="$_p"
                    break
                fi
            done
            _OUT_NUC="$_nuc"
            _OUT_SLUG="$_cs"
        }
        # --- Per-cell worktree provisioning (spec_n07_per_cell_worktrees, Wave 1) ---
        # When -w is passed, discover the cell list from matching handoffs and
        # call cex_worktree_manager.py to create one worktree per cell before
        # spawn_grid.ps1 launches. Cell-slug-based worktrees (wt_<cell_slug>) let
        # same-nucleus parallel cells (3x n03 with discriminators anuncio/pesquisa/
        # imagens) each land in their own `.cex/worktrees/wt_n03_anuncio/` etc.
        # For legacy `MISSION_n0X.md` handoffs (no discriminator), cell_slug ==
        # nucleus, so the worktree path stays `wt_n0X` (no breaking change).
        if [ "$WORKTREE_FLAG_PRESENT" = "1" ]; then
            HANDOFF_DIR=".cex/runtime/handoffs"
            _CELL_LIST=""
            _NUC_LIST=""
            _HANDOFF_COUNT=0
            for hf in "$HANDOFF_DIR"/${MISSION}_*.md; do
                [ -f "$hf" ] || continue
                _HANDOFF_COUNT=$((_HANDOFF_COUNT + 1))
                base=$(basename "$hf" .md)
                _parse_handoff_cell "$base" "$MISSION"
                if [ -n "$_OUT_NUC" ]; then
                    _NUC_LIST="$_NUC_LIST $_OUT_NUC"
                    _CELL_LIST="$_CELL_LIST $_OUT_SLUG"
                fi
            done
            if [ "$_HANDOFF_COUNT" -eq 0 ]; then
                # Truly empty -- normal no-op when nobody wrote handoffs yet.
                echo "[DISPATCH] -w passed but no handoffs found for ${MISSION}_*.md -- skipping worktree provisioning"
            elif [ -z "$_NUC_LIST" ]; then
                # Handoffs exist but none contain a parseable n0X token.
                echo "[DISPATCH] WARN: -w passed; $_HANDOFF_COUNT handoff(s) found but none contain n0X token -- skipping worktree provisioning"
            else
                echo "[DISPATCH] Per-cell worktrees for cells:$_CELL_LIST"
                # R-199: CEX_GRID_PERCELL_WORKTREE must only be exported when
                # provisioning actually SUCCEEDED for the full cell list -- the
                # export used to sit outside this branch and fire even on the
                # zero-handoff / no-n0X-token / create-failed degrade paths,
                # silently defeating the race-condition guarantee -w exists to
                # provide. On failure here, leave the flag UNSET (honest
                # fallback to the pre-P7 shared-worktree behavior) instead of
                # telling spawn_grid.ps1 per-cell isolation is active when it
                # is not.
                # shellcheck disable=SC2086
                if python _tools/cex_worktree_manager.py create $_CELL_LIST; then
                    # Wave 2: tell spawn_grid.ps1 to wire CEX_WORKTREE_DIR per
                    # cell. spawn_grid's Launch-Nucleus reads this sentinel and
                    # sets CEX_WORKTREE_DIR + CEX_WORKTREE_BRANCH for each
                    # spawned boot script.
                    export CEX_GRID_PERCELL_WORKTREE=1
                    echo "[DISPATCH] Per-cell worktree mode active (CEX_GRID_PERCELL_WORKTREE=1)"
                else
                    echo "[DISPATCH] WARN: cex_worktree_manager create reported errors (see above) -- per-cell worktree mode NOT active, falling back to shared-worktree behavior"
                fi
            fi
        fi
        # --- ACR preflight per cell (P0 FIX b): bake prerequisites into each mission
        # handoff BEFORE boot. spawn_grid.ps1 copies ${MISSION}_${nuc}.md to the
        # per-nucleus boot pointer (and the worktree mirror), so appending the
        # prerequisites here reaches the booting nucleus. Idempotent per file. ---
        _GRID_CELLS=0
        _GRID_NUC_CSV=""
        for hf in .cex/runtime/handoffs/${MISSION}_*.md; do
            [ -f "$hf" ] || continue
            base=$(basename "$hf" .md)
            _parse_handoff_cell "$base" "$MISSION"
            if [ -n "$_OUT_NUC" ]; then
                _preflight_mcp "$_OUT_NUC" "$hf"
                _GRID_CELLS=$((_GRID_CELLS + 1))
                if [ -n "$_GRID_NUC_CSV" ]; then
                    _GRID_NUC_CSV="$_GRID_NUC_CSV,$_OUT_NUC"
                else
                    _GRID_NUC_CSV="$_OUT_NUC"
                fi
            fi
        done
        [ "$_GRID_CELLS" -eq 0 ] && _GRID_CELLS=1
        # --- team_charter enforcement (spec 06 P7 TEAMS) -----------------------------
        # ADDITIVE: only runs when --charter <path> is passed. ABSENT --charter -> this
        # whole block is skipped and the grid path is BYTE-IDENTICAL to pre-P7 (zero
        # regression). When present, cex_team_charter:
        #   inject   -> the `## CHARTER (enforced)` block (budget + quality_gate +
        #               termination_criteria) into every per-cell handoff (idempotent;
        #               reflects the REAL charter, never fabricated values), so the
        #               booting nuclei receive the enforced envelope.
        #   snapshot -> a replayable team_def `.cex/runtime/decisions/team_<MISSION>.yaml`
        #               (which nuclei + which charter the mission used -- cross-session
        #               replay). The wave loop's `check` reads the same charter to gate
        #               elapsed wall-clock + committed cells vs the ceilings.
        # degrade-never: a missing tool / unreadable charter -> a WARN, dispatch PROCEEDS.
        if [ -n "$GRID_CHARTER" ]; then
            if [ ! -f "$GRID_CHARTER" ]; then
                echo "[DISPATCH] WARN: --charter file not found: $GRID_CHARTER (proceeding without charter)"
            elif ! command -v python >/dev/null 2>&1; then
                echo "[DISPATCH] WARN: python not found -- cannot enforce charter (proceeding)"
            else
                echo "[DISPATCH] Charter (enforced): $GRID_CHARTER -> $MISSION"
                python _tools/cex_team_charter.py inject --charter "$GRID_CHARTER" --mission "$MISSION" \
                    || echo "[DISPATCH] WARN: charter inject reported errors (proceeding)"
                _CHARTER_NUCLEI=$(printf '%s' "$_GRID_NUC_CSV" | tr ',' ' ')
                # shellcheck disable=SC2086
                python _tools/cex_team_charter.py snapshot --charter "$GRID_CHARTER" --mission "$MISSION" \
                    --nuclei $_CHARTER_NUCLEI \
                    || echo "[DISPATCH] WARN: charter snapshot reported errors (proceeding)"
            fi
        fi
        # Provider quota gate FIRST: refresh the quota cache (cache-first, only
        # re-probes if stale > 600s; short timeout; fail-open) so the governor
        # preflight below reads fresh provider state. Refresh cron-style with
        # `cex_quota_check.py --all --cache`.
        if [ "${CEX_RATELIMIT_GUARD:-0}" = "1" ] && command -v python >/dev/null 2>&1; then
            python _tools/cex_quota_check.py --all --use-cache 600 --cache --json --timeout 8 >/dev/null 2>&1 || \
                echo "[DISPATCH] quota gate: provider probe inconclusive (fail-open, proceeding)"
        fi
        # Rate-limit governor: cells x subagent_multiplier vs the empirical cap +
        # rolling-5h/weekly-opus headroom + the fresh quota cache. A wide Opus grid
        # is the classic 429 trigger -- this warns (advisory) or, under
        # CEX_RATELIMIT_ENFORCE=1 + over, enforce-blocks BEFORE spawn.
        if ! _ratelimit_preflight "grid" "opus" "$_GRID_CELLS" "$_GRID_NUC_CSV" "$MISSION"; then exit 3; fi
        if [ -n "$CEX_GRID_CLIMAP" ]; then
            echo "[DISPATCH] Grid: $MISSION (cli=per-cell-map)${GRID_CHARTER:+ (charter=$GRID_CHARTER)}"
        else
            echo "[DISPATCH] Grid: $MISSION (cli=claude)${GRID_CHARTER:+ (charter=$GRID_CHARTER)}"
        fi
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_grid.ps1 -mission "$MISSION" -cli claude -interactive
        ;;
    grid-haiku)
        MISSION="${1:-DEFAULT}"
        _RESOLVED_MODEL=$(python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from _tools.cex_model_resolver import get_preflight_model
    print(get_preflight_model('cloud').get('model', 'claude-haiku-4-5-20251001'))
except Exception:
    print('claude-haiku-4-5-20251001')
" 2>/dev/null || echo "claude-haiku-4-5-20251001")
        MODEL="${2:-$_RESOLVED_MODEL}"
        echo "[DISPATCH] Grid: $MISSION (cli=claude, model=$MODEL)"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_grid.ps1 -mission "$MISSION" -cli claude -interactive -Model "$MODEL"
        ;;
    grid-gemini)
        MISSION="${1:-DEFAULT}"
        echo "[DISPATCH] Grid: $MISSION (cli=gemini)"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_grid.ps1 -mission "$MISSION" -cli gemini -interactive
        ;;
    grid-aider)
        MISSION="${1:-DEFAULT}"
        echo "[DISPATCH] Grid: $MISSION (cli=aider, model=ollama/qwen3:14b, cost=\$0)"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_grid_aider.ps1 -mission "$MISSION"
        ;;
    grid-codex)
        MISSION="${1:-DEFAULT}"
        echo "[DISPATCH] Grid: $MISSION (cli=codex)"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_grid.ps1 -mission "$MISSION" -cli codex -interactive
        ;;
    grid-ollama)
        # Interactive 3x2 tiled windows, each running boot/n0X_ollama.ps1 -> ollama_nucleus.py
        MISSION="${1:-DEFAULT}"
        MODEL="${2:-qwen3:8b}"
        echo "[DISPATCH] Grid: $MISSION (cli=ollama, model=$MODEL, interactive, cost=\$0)"
        export OLLAMA_MODEL="$MODEL"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_grid.ps1 -mission "$MISSION" -cli ollama -interactive
        ;;
    solo-ollama)
        # Interactive single window, boot/n0X_ollama.ps1 -> ollama_nucleus.py
        NUCLEUS="${1:-n03}"
        MODEL="${2:-qwen3:8b}"
        TASK="${3:-}"
        echo "[DISPATCH] Solo-Ollama: $NUCLEUS via $MODEL (interactive)"
        _preflight_mcp "$NUCLEUS" ".cex/runtime/handoffs/${NUCLEUS}_task.md"
        export OLLAMA_MODEL="$MODEL"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_solo.ps1 -nucleus "$NUCLEUS" -task "$TASK" -cli ollama -interactive
        ;;
    solo-codex)
        # Interactive single window, boot/n0X_codex.ps1 -> codex CLI
        NUCLEUS="${1:-n03}"
        TASK="${2:-}"
        echo "[DISPATCH] Solo-Codex: $NUCLEUS (interactive)"
        _preflight_mcp "$NUCLEUS" ".cex/runtime/handoffs/${NUCLEUS}_task.md"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_solo.ps1 -nucleus "$NUCLEUS" -task "$TASK" -cli codex -interactive
        ;;
    solo-gemini)
        # Interactive single window, boot/n0X_gemini.ps1 -> gemini CLI
        NUCLEUS="${1:-n03}"
        TASK="${2:-}"
        echo "[DISPATCH] Solo-Gemini: $NUCLEUS (interactive)"
        _preflight_mcp "$NUCLEUS" ".cex/runtime/handoffs/${NUCLEUS}_task.md"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_solo.ps1 -nucleus "$NUCLEUS" -task "$TASK" -cli gemini -interactive
        ;;
    grid-litellm)
        # Interactive 3x2 tiled, each window runs boot/n0X_litellm.ps1 -> litellm proxy
        # Proxy must be running: powershell -File boot/litellm_proxy.ps1
        MISSION="${1:-DEFAULT}"
        echo "[DISPATCH] Grid: $MISSION (cli=litellm, proxy=:4000, interactive)"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_grid.ps1 -mission "$MISSION" -cli litellm -interactive
        ;;
    solo-litellm)
        # Interactive single window, boot/n0X_litellm.ps1 -> litellm proxy
        NUCLEUS="${1:-n03}"
        TASK="${2:-}"
        echo "[DISPATCH] Solo-LiteLLM: $NUCLEUS (model alias cex-$NUCLEUS, interactive)"
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_solo.ps1 -nucleus "$NUCLEUS" -task "$TASK" -cli litellm -interactive
        ;;
    status)
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_monitor.ps1
        # Signal-without-deliverable gate (8F_DECOMPOSE integration)
        if command -v python &>/dev/null; then
            SIGNAL_CHECK=$(python _tools/cex_doctor.py --signals 2>/dev/null)
            if [ $? -ne 0 ] || echo "$SIGNAL_CHECK" | grep -q "FAIL"; then
                echo ""
                echo "  [WARN] Signal-without-deliverable detected:"
                echo "$SIGNAL_CHECK" | grep "FAIL" | sed 's/^/    /'
            fi
        fi
        ;;
    stop)
        # Parse stop arguments (C29: mirror the flags bash-side for the confirm step)
        STOP_ARGS=""
        STOP_ALL=""; STOP_DRY=""; STOP_NUC=""; STOP_SESS=""
        for arg in "$@"; do
            case "$arg" in
                --all)     STOP_ARGS="$STOP_ARGS -All"; STOP_ALL=1 ;;
                --dry-run) STOP_ARGS="$STOP_ARGS -DryRun"; STOP_DRY=1 ;;
                n0[1-7])   STOP_ARGS="$STOP_ARGS -Nucleus $arg"; STOP_NUC="$arg" ;;
                s*)        STOP_ARGS="$STOP_ARGS -Session $arg"; STOP_SESS="$arg" ;;
            esac
        done
        # C29: collect the PIDs spawn_stop.ps1 will target (same STEP 1 filter)
        # BEFORE it runs -- it rewrites the PID file. Dry-run kills nothing, so
        # there is nothing to confirm (and nothing to escalate on).
        _C29_SET=""
        if [ -z "$STOP_DRY" ]; then
            _C29_SET=$(_collect_stop_pids)
        fi
        # shellcheck disable=SC2086
        powershell -NoProfile -ExecutionPolicy Bypass -File _spawn/spawn_stop.ps1 $STOP_ARGS
        _C29_RC=$?
        # shellcheck disable=SC2086
        _confirm_wrappers_dead $_C29_SET
        exit $_C29_RC
        ;;
    ollama)
        # Headless dispatch via 8F pipeline + Ollama (no Claude Code CLI needed)
        NUCLEUS="${1:-n03}"
        MODEL="${2:-qwen3:8b}"
        HANDOFF="${3:-}"
        echo "[DISPATCH] Ollama: $NUCLEUS via $MODEL"
        # Read task from handoff file or n0x_task.md
        if [ -z "$HANDOFF" ]; then
            HANDOFF=".cex/runtime/handoffs/${NUCLEUS}_task.md"
        fi
        if [ ! -f "$HANDOFF" ]; then
            echo "[FAIL] No handoff found: $HANDOFF"
            exit 1
        fi
        _preflight_mcp "$NUCLEUS" "$HANDOFF"
        # Run 8F pipeline with Ollama model
        INTENT=$(head -1 "$HANDOFF" | sed 's/^#* *//')
        python _tools/cex_8f_runner.py \
            --execute \
            --model "ollama/$MODEL" \
            --nucleus "$NUCLEUS" \
            --context-file "$HANDOFF" \
            "$INTENT"
        echo "[DONE] $NUCLEUS via Ollama/$MODEL"
        ;;
    ollama-grid)
        # Parallel Ollama dispatch (all nuclei via local models)
        MISSION="${1:-DEFAULT}"
        MODEL="${2:-qwen3:8b}"
        echo "[DISPATCH] Ollama Grid: $MISSION via $MODEL"
        HANDOFF_DIR=".cex/runtime/handoffs"
        # Pre-flight MCP for all handoffs before parallel launch
        for hf in "$HANDOFF_DIR"/${MISSION}_n0*.md; do
            if [ -f "$hf" ]; then
                NUC_PF=$(echo "$hf" | grep -o 'n0[1-7]')
                _preflight_mcp "$NUC_PF" "$hf"
            fi
        done
        PIDS=""
        for hf in "$HANDOFF_DIR"/${MISSION}_n0*.md; do
            if [ -f "$hf" ]; then
                NUC=$(echo "$hf" | grep -o 'n0[1-7]')
                echo "  [>>] Starting $NUC..."
                INTENT=$(head -1 "$hf" | sed 's/^#* *//')
                python _tools/cex_8f_runner.py \
                    --execute \
                    --model "ollama/$MODEL" \
                    --nucleus "$NUC" \
                    --context-file "$hf" \
                    "$INTENT" &
                PIDS="$PIDS $!"
            fi
        done
        if [ -z "$PIDS" ]; then
            echo "[FAIL] No handoffs found for mission: $MISSION"
            exit 1
        fi
        echo "[WAIT] Waiting for $PIDS..."
        # shellcheck disable=SC2086
        wait $PIDS
        echo "[DONE] Ollama Grid complete: $MISSION"
        ;;
    *)
        echo "Usage: bash _spawn/dispatch.sh {solo|autoroute|auto|grid|grid-gemini|grid-codex|grid-ollama|solo-ollama|solo-codex|solo-gemini|grid-litellm|solo-litellm|ollama|ollama-grid|swarm|decompose|crew|status|stop} [args]"
        echo ""
        echo "  solo n03 \"task\"           Spawn 1 Claude Code nucleus (interactive)"
        echo "  solo n03 -cli gemini \"task\"  Per-cell runtime: boot n03_gemini.ps1 (WS5.0)"
        echo "                            -cli {claude|gemini|codex|ollama|litellm}; absent -> nucleus_models.yaml"
        echo "  autoroute n03 \"task\"      A2: pick cheapest competent path by kind complexity"
        echo "                            structured -> decompose; mid -> sonnet solo; complex -> Mode-A Opus"
        echo "                            (plain 'solo' AUTO-ROUTES by default; CEX_AUTOROUTE=0 forces legacy Opus boot)"
        echo "  auto n04 \"task\" --batch DIR --n 3"
        echo "                            DEFAULT-path router (P2.3): bulk-similar batch"
        echo "                            (N>=10, cohesive) -> gated swarm; else Mode A (solo)"
        echo "  grid MISSION              Spawn up to 6 Claude Code nuclei (interactive 3x2)"
        echo "  grid-gemini MISSION       Spawn up to 6 Gemini CLI nuclei"
        echo "  grid-codex MISSION        Spawn up to 6 Codex CLI nuclei"
        echo "  solo-ollama n04 qwen3:8b \"task\"  Spawn 1 Ollama nucleus (interactive window)"
        echo "  grid-ollama MISSION qwen3:8b     Spawn up to 6 Ollama nuclei (interactive 3x2, free)"
        echo "  solo-litellm n04 \"task\"          Spawn 1 LiteLLM nucleus (proxy decides backend)"
        echo "  grid-litellm MISSION             Spawn up to 6 LiteLLM nuclei (interactive 3x2, proxy)"
        echo "  ollama n03 qwen3:8b       Run 1 nucleus via Ollama headless (cex_8f_runner)"
        echo "  ollama-grid MISSION ...   Run all nuclei via Ollama headless"
        echo "  status                    Monitor running nuclei"
        echo "  stop                      Stop MY session's nuclei only"
        echo "  stop n03                  Stop only N03"
        echo "  stop --all                Stop ALL CEX nuclei (DANGEROUS)"
        echo "  stop --dry-run            Preview what would be killed"
        echo "  swarm <kind> <N> \"task\"   Spawn N parallel builders of same kind in worktrees"
        echo "  decompose n0X \"task\"      3-stage 8F: Opus reasoning -> cheap F6 -> tools (Stage 3)"
        echo "                            Flags: -1 model | -2 model | --dry-run | --skip-stage-3"
        echo "  crew <name> [--charter P] Run a composable crew (control plane). OFFLINE by default;"
        echo "                            --execute is GATED behind CEX_CREW_LIVE=1 (else falls back to dry)"
        echo ""
        echo "Flags (apply to solo/grid):"
        echo "  -w, --worktree [id]       Run in isolated git worktree (auto-creates if missing)"
        echo "Flags (grid):"
        echo "  --charter <path>          Enforce a team_charter (spec 06 P7): inject the budget/"
        echo "                            quality/termination envelope into each cell handoff +"
        echo "                            snapshot a replayable team_def. Absent -> no charter."
        echo "Flags (solo):"
        echo "  -cli <provider>           Per-cell runtime override (claude|gemini|codex|ollama|litellm)"
        echo "  -m, --model <model>       Model override (CEX_MODEL_OVERRIDE)"
        echo "  --dry-run                 Print the boot the solo path would launch; spawn nothing"
        ;;
esac
