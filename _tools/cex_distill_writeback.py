#!/usr/bin/env python3
"""cex_distill_writeback -- W3 WIRE_DORMANT: distillation write-back on escalation.

The escalate -> re-produce -> re-gate ladder (cex_mentor_swarm.escalate_record)
was wired, but when a stronger (TEACHER) tier fixed what a cheap (STUDENT) tier
failed, nothing wrote a REUSABLE corrective procedure -- so the next cheap run
repeated the mistake. This module is that missing write-back.

  distill_on_escalation(...)  GATED on the teacher's self-eval passing, emits a
    typed learning_record (JSON) under .cex/learning_records/ -- WHERE the ACR P4
    memory_recall reflex + cex_memory.load_learning_records already look --
    capturing the corrective PROCEDURE (what the student got wrong, what the
    teacher changed, the generalizable rule), NOT just the artifact diff.

  recall_distillations(query)  ranks past distillations for a NEW similar task via
    the ACR P4 memory_recall reflex (cexai.memory.recall, offline FakeEmbedder),
    degrading to a local token-overlap ranker when cexai is absent.

degrade-never:
  - kill-switch CEX_DISTILL_WRITEBACK=0 (false/no/off) -> distill_on_escalation is a
    no-op returning None (byte-identical: nothing written).
  - OFF when the student is already SOTA: no escalation, teacher did not beat the
    student, or the teacher self-eval did not clear the floor -> nothing written.
  - never raises into the swarm; a write/recall failure degrades to None / [].

ASCII-only (.py rule). Status tags use [OK]/[WARN].
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cex_shared import CEX_ROOT

LEARNING_DIR = CEX_ROOT / ".cex" / "learning_records"

_ENV_FLAG = "CEX_DISTILL_WRITEBACK"
_OFF_VALUES = frozenset({"0", "false", "no", "off"})
_DEFAULT_FLOOR = 8.0

_WORD_RE = re.compile(r"[a-z0-9]+")
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def is_enabled() -> bool:
    """Whether distillation write-back is active (opt-out via CEX_DISTILL_WRITEBACK=0)."""
    return os.environ.get(_ENV_FLAG, "1").strip().lower() not in _OFF_VALUES


def _slug(text: str, n: int = 40) -> str:
    s = _SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return (s[:n].strip("-")) or "task"


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _utc_stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S_%f")


def distill_on_escalation(
    task: str,
    nucleus: str,
    student_model: str,
    student_score: Optional[float],
    teacher_model: str,
    teacher_score: Optional[float],
    *,
    gate_ok: bool,
    floor: float = _DEFAULT_FLOOR,
    escalation_path: Optional[list] = None,
    student_weakest: str = "",
    task_kind: str = "",
) -> Optional[Path]:
    """Emit a distillation learning_record IFF a teacher tier fixed a student
    failure AND the teacher's self-eval passed. Returns the written path, or None
    when the gate blocks the write (or the kill-switch is off). Never raises.

    The GATE (teacher self-eval passing -- mirrors the gate-before-persist pattern
    in cex_apex_daemon.verify_merge): write only when
      enabled
      AND gate_ok                       (the teacher artifact passed the W2 gate)
      AND a real escalation happened     (student_model != teacher_model)
      AND scores are present
      AND teacher_score > student_score  (the teacher actually improved it)
      AND teacher_score >= floor         (the teacher CLEARED the floor: confident)
      AND student_score <  floor         (the student genuinely FAILED the floor)
    Any miss -> None (nothing persisted). 'student already SOTA' is the no-escalation
    / teacher-did-not-beat-student case and is skipped here automatically."""
    if not is_enabled():
        return None
    try:
        # No task context -> the record could never be recalled by a "similar task"
        # (intent is the recall key) -> nothing worth distilling. This also keeps
        # escalate_record unit tests (which pass no task) side-effect-free.
        if not task or not task.strip():
            return None
        if not gate_ok:
            return None
        if student_score is None or teacher_score is None:
            return None
        if not student_model or not teacher_model or student_model == teacher_model:
            return None
        if float(teacher_score) <= float(student_score):
            return None
        if float(teacher_score) < float(floor):
            return None
        if float(student_score) >= float(floor):
            return None
    except (TypeError, ValueError):
        return None

    path_list = list(escalation_path or [student_model, teacher_model])
    weak = student_weakest or "quality below floor"
    record = {
        "timestamp": _utc_now_iso(),
        "kind": "learning_record",
        "record_type": "distillation",
        # 'intent' is the recall key: a later SIMILAR task matches on this text.
        "intent": task,
        "task_kind": task_kind,
        "nucleus": nucleus,
        "passed": True,
        "student_model": student_model,
        "student_score": round(float(student_score), 3),
        "teacher_model": teacher_model,
        "teacher_score": round(float(teacher_score), 3),
        "floor": round(float(floor), 3),
        "escalation_path": path_list,
        "what_student_got_wrong": (
            "%s (%s) scored %.2f < floor %.2f; weakest: %s"
            % (student_model, path_list[0] if path_list else student_model,
               float(student_score), float(floor), weak)
        ),
        "what_teacher_changed": (
            "escalated %s -> %s; %s produced a gate-clean artifact scoring %.2f"
            % (path_list[0] if path_list else student_model,
               path_list[-1] if path_list else teacher_model,
               teacher_model, float(teacher_score))
        ),
        "generalizable_rule": (
            "For %s tasks like '%s', when %s output is below floor on '%s', "
            "escalate to %s -- it cleared the floor here."
            % (nucleus or "this nucleus", (task or "")[:80], student_model, weak,
               teacher_model)
        ),
        "source": "cex_mentor_swarm.escalate_record",
    }
    try:
        LEARNING_DIR.mkdir(parents=True, exist_ok=True)
        out = LEARNING_DIR / ("lr_distill_%s_%s.json" % (_utc_stamp(), _slug(task)))
        out.write_text(
            json.dumps(record, indent=2, ensure_ascii=True), encoding="utf-8"
        )
        return out
    except Exception:
        return None


def _load_distillations() -> List[dict]:
    """All distillation learning_records on disk (best-effort, never raises)."""
    out: List[dict] = []
    try:
        if not LEARNING_DIR.exists():
            return out
        for f in sorted(LEARNING_DIR.glob("lr_distill_*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("record_type") == "distillation":
                    data["_path"] = str(f)
                    out.append(data)
            except (json.JSONDecodeError, OSError):
                continue
    except Exception:
        pass
    return out


def _recall_text(rec: dict) -> str:
    """The text a NEW task is matched against (intent + the corrective rule)."""
    return " ".join(str(rec.get(k, "")) for k in
                     ("intent", "task_kind", "generalizable_rule", "what_student_got_wrong"))


def _local_rank(query: str, recs: List[dict], top_k: int) -> List[dict]:
    """Deterministic token-overlap fallback (used when cexai.memory is absent)."""
    q = set(_WORD_RE.findall((query or "").lower()))
    if not q:
        return []
    scored = []
    for rec in recs:
        toks = set(_WORD_RE.findall(_recall_text(rec).lower()))
        if not toks:
            continue
        overlap = len(q & toks)
        if overlap:
            scored.append((overlap / float(len(q | toks)), rec))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [
        {"id": r.get("_path", ""), "score": round(s, 6), "rank": i + 1,
         "intent": r.get("intent", ""), "rule": r.get("generalizable_rule", ""),
         "path": r.get("_path", ""), "fallback": True}
        for i, (s, r) in enumerate(scored[:top_k])
    ]


def recall_distillations(query: str, top_k: int = 5) -> List[dict]:
    """Rank past distillations for a NEW similar task via the ACR P4 memory_recall
    reflex (cexai.memory.recall, offline FakeEmbedder); degrade to a local
    token-overlap ranker when cexai is unavailable. Returns [] for empty corpus /
    empty query. Never raises."""
    if not query or not query.strip():
        return []
    recs = _load_distillations()
    if not recs:
        return []
    try:
        root = str(CEX_ROOT / "cexai")
        if root not in sys.path:
            sys.path.insert(0, root)
        from cexai.memory import recall as _recall
        from cexai.memory._shared.types import MemoryRecord
        from cexai.memory.vector import FakeEmbedder

        corpus = []
        for rec in recs:
            corpus.append(MemoryRecord(
                rec.get("_path", ""),
                _recall_text(rec),
                "learning_record",
                rec.get("_path", ""),
                rec.get("timestamp", _utc_now_iso()),
                {"nucleus": rec.get("nucleus", ""), "record_type": "distillation"},
            ))
        hits = _recall(query, top_k=top_k, records=corpus, embedder=FakeEmbedder())
        if not hits:
            return []
        by_path = {r.get("_path", ""): r for r in recs}
        out = []
        for h in hits:
            rec = by_path.get(h.get("id", ""), {})
            out.append({
                "id": h.get("id", ""), "score": h.get("score", 0.0),
                "rank": h.get("rank", 0), "intent": rec.get("intent", ""),
                "rule": rec.get("generalizable_rule", ""),
                "path": h.get("source_path", ""), "fallback": h.get("fallback", False),
            })
        return out
    except Exception:
        return _local_rank(query, recs, top_k)


if __name__ == "__main__":
    # Tiny CLI: recall past distillations for a task string.
    import argparse

    ap = argparse.ArgumentParser(description="W3 distillation recall")
    ap.add_argument("--recall", metavar="QUERY", default="",
                    help="Rank past distillation learning_records for QUERY")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()
    if args.recall:
        for h in recall_distillations(args.recall, top_k=args.top):
            print("[OK] %.4f  %s" % (h["score"], h["intent"]))
            print("       rule: %s" % h["rule"])
    else:
        ap.print_help()
