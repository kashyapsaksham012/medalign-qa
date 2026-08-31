"""Self-consistency plurality vote + selective-prediction uncertainty score.

PAPER-SPECIFIED (Section 4.4):
  - self-consistency: 11 decodes, take the majority/plurality answer (line ~854)
  - selective prediction: 41 decodes, uncertainty = #decodes agreeing with the
    chosen answer; defer the most-uncertain fraction (line ~868-874, Fig 5)
REPLICATION ASSUMPTION (RA-04): ties broken by first-seen order.
"""
from __future__ import annotations

from collections import Counter


def plurality(votes: list[str | None]) -> tuple[str | None, dict]:
    counts = Counter(v for v in votes if v is not None)
    if not counts:
        return None, {"counts": {}, "n_valid": 0, "n_total": len(votes)}
    top = max(counts.values())
    # first-seen tie-break (RA-04)
    winner = next(v for v in votes if v is not None and counts[v] == top)
    return winner, {"counts": dict(counts), "n_valid": sum(counts.values()),
                    "n_total": len(votes), "top_count": top}


def uncertainty_score(votes: list[str | None]) -> tuple[str | None, float]:
    """Return (chosen_answer, agreement_fraction) for selective prediction (Fig 5)."""
    winner, meta = plurality(votes)
    frac = (meta["top_count"] / meta["n_total"]) if meta["n_total"] else 0.0
    return winner, frac
