"""Score a prediction JSONL (single-decode or self-consistency) -> accuracy + CI."""
from __future__ import annotations

from pathlib import Path

from .. import config as run_config
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
    d = run_config.predictions_dir(strategy)
    return sorted(d.glob("*.jsonl")) if d.exists() else []


def any_predictions() -> bool:
    """True iff at least one non-empty prediction file exists under any strategy.

    Phases 12/16/17/19/20 MUST guard on this and hard-fail with NO DATA otherwise --
    they used to emit `PASS` / "replication complete" against zero predictions.
    Scoped to the active run_tag so the quarantined B1 flat-layout run does not
    count as "we have results".
    """
    d = run_config.predictions_base()
    if not d.exists():
        return False
    for p in d.glob("**/*.jsonl"):
        try:
            if any(True for _ in io.read_jsonl(p)):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False
