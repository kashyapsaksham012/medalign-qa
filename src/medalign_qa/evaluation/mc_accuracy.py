"""Score a prediction JSONL (single-decode or self-consistency) -> accuracy + CI."""
from __future__ import annotations

from pathlib import Path

from ..inference.self_consistency import plurality
from ..utils import io, paths
from .stats import wilson_ci


def score(pred_path: str | Path) -> dict:
    pred_path = Path(pred_path)
    rows = [r for r in io.read_jsonl(pred_path) if r.get("gold")]
    n = len(rows)
    if n == 0:
        return {"path": str(pred_path), "n": 0}

    multi = not all("parsed_single" in r for r in rows)
    n_parsed = n_correct = 0
    per_uid = {}
    for r in rows:
        if multi:
            pred, _ = plurality(r["parsed"])
        else:
            pred = r["parsed_single"]
        n_parsed += pred is not None
        ok = pred == r["gold"]
        n_correct += ok
        per_uid[r["uid"]] = ok
    lo, hi = wilson_ci(n_correct, n)
    return {
        "path": str(pred_path.relative_to(paths.ROOT)) if paths.ROOT in pred_path.parents else str(pred_path),
        "n": n, "n_correct": n_correct, "accuracy": n_correct / n,
        "parse_rate": n_parsed / n, "n_parsed": n_parsed,
        "wilson95_lo": lo, "wilson95_hi": hi,       # beyond paper
        "mode": "self_consistency" if multi else "single",
        "_per_uid_correct": per_uid,
    }


def find_predictions(strategy: str) -> list[Path]:
    d = paths.DERIVED / "predictions" / strategy
    return sorted(d.glob("*.jsonl")) if d.exists() else []
