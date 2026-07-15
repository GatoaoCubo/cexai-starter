# -*- coding: utf-8 -*-
"""CEX Signal Writer v2.1 -- writes to .cex/runtime/signals/ with validation"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
# A2.x tenant-path migration: resolve the signals surface through the ONE canonical resolver
# (cex_tenant_paths). With CEX_TENANT_ID unset, tenant_runtime_dir() returns the legacy global
# path, so SIGNAL_DIR stays byte-identical for single-tenant; with a tenant bound it scopes to
# .cex/tenants/<tid>/runtime/signals. Degrade-never: fall back to the legacy join if the
# resolver is not importable in this import context (single-tenant safe).
if str(_ROOT / "_tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "_tools"))
try:
    from cex_tenant_paths import tenant_runtime_dir as _tenant_runtime_dir
    SIGNAL_DIR = _tenant_runtime_dir() / "signals"
except Exception:
    SIGNAL_DIR = _ROOT / ".cex" / "runtime" / "signals"
VALID_NUCLEI = {"n01", "n02", "n03", "n04", "n05", "n06", "n07"}
MISSION_PHASE_RE = re.compile(r'^w\d+$')

def write_signal(nucleus, status="complete", quality_score=9.0, mission="", wave=None,
                 artifact_path=None, min_bytes=None, **extra):
    """Write a completion signal. Optional post-signal verification (MAINTAIN Finding #4):
    if `artifact_path` is given AND status=='complete', the signal is REJECTED when the
    artifact does not exist; if `min_bytes` is also given, signal is REJECTED when the
    file is smaller than that threshold. This catches the 'signal-without-deliverable'
    pattern observed on Ollama cells.
    """
    nucleus = nucleus.lower()
    is_mission_phase = bool(MISSION_PHASE_RE.match(nucleus))
    if not is_mission_phase and nucleus not in VALID_NUCLEI:
        raise ValueError(f"Invalid nucleus '{nucleus}'. Must be one of: {sorted(VALID_NUCLEI)} or mission_phase (w1, w2, ...)")
    if not isinstance(quality_score, (int, float)) or not (0 <= quality_score <= 10):
        raise ValueError(f"quality_score must be 0-10, got {quality_score}")
    if not re.match(r'^[a-z_]+$', status):
        raise ValueError(f"Invalid status '{status}'. Must be lowercase alpha/underscore.")

    # Post-signal verification (MAINTAIN Finding #4 remedy)
    if status == "complete" and artifact_path:
        ap = Path(artifact_path)
        if not ap.is_absolute():
            ap = Path(__file__).resolve().parent.parent / ap
        if not ap.exists():
            raise ValueError(
                f"Signal-without-deliverable rejected: artifact_path '{artifact_path}' does not exist. "
                f"Set status='partial' or write the file BEFORE signaling complete.")
        if min_bytes is not None:
            actual = ap.stat().st_size
            if actual < min_bytes:
                raise ValueError(
                    f"Signal-without-deliverable rejected: artifact at '{artifact_path}' is {actual}B "
                    f"but min_bytes={min_bytes}. Likely thin/stub output.")

    SIGNAL_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    signal = {
        "nucleus": nucleus,
        "status": status,
        "quality_score": quality_score,
        "mission": mission,
        "timestamp": now.isoformat(),
        **extra,
    }
    if is_mission_phase:
        signal["mission_phase"] = nucleus
    if wave is not None:
        signal["wave"] = wave
    ts = now.strftime('%Y%m%d_%H%M%S')
    if mission and wave is not None:
        filename = f"signal_{nucleus}_{mission.lower()}_w{wave}_{ts}.json"
    else:
        filename = f"signal_{nucleus}_{ts}.json"
    path = SIGNAL_DIR / filename
    path.write_text(json.dumps(signal, indent=2), encoding="utf-8")
    label = "mission_phase" if is_mission_phase else "nucleus"
    print(f"[SIGNAL] {label}={nucleus} -> {status} (score: {quality_score})")
    return str(path)

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    write_signal(
        args[0] if len(args) > 0 else "n03",
        args[1] if len(args) > 1 else "complete",
        float(args[2]) if len(args) > 2 else 9.0,
        args[3] if len(args) > 3 else "",
    )
