"""Selective prediction via self-consistency vote count (Section 4.4, Fig 5).

PAPER-SPECIFIED: 41 CoT decodes on MedQA; uncertainty = (#decodes agreeing with
the plurality answer) / 41; sweep the deferral fraction; report accuracy on the
retained (1 - d) fraction.
"""
from __future__ import annotations

from pathlib import Path

from ..inference.self_consistency import plurality
from ..utils import io


def curve(pred_path: str | Path, deferral_grid: list[float]) -> dict:
    rows = [r for r in io.read_jsonl(pred_path) if r.get("gold")]
    scored = []
    for r in rows:
        win, meta = plurality(r["parsed"])
        n_total = len(r["parsed"])
        agree = meta["top_count"] / n_total if n_total else 0.0
        scored.append({"uid": r["uid"], "pred": win, "gold": r["gold"],
                       "correct": win == r["gold"], "confidence": agree})
    # rank by confidence ascending; defer the least-confident fraction d
    scored.sort(key=lambda x: x["confidence"])
    n = len(scored)
    points = []
    for d in deferral_grid:
        keep = scored[int(round(d * n)):]
        if not keep:
            points.append({"deferral": d, "n_kept": 0, "accuracy": None})
            continue
        acc = sum(x["correct"] for x in keep) / len(keep)
        points.append({"deferral": round(d, 3), "n_kept": len(keep),
                       "accuracy": round(acc, 4)})
    return {"n": n, "n_decodes": len(rows[0]["parsed"]) if rows else 0,
            "points": points,
            "monotonic_non_decreasing": all(
                (points[i]["accuracy"] or 0) <= (points[i + 1]["accuracy"] or 0) + 1e-9
                for i in range(len(points) - 1) if points[i + 1]["accuracy"] is not None)}
