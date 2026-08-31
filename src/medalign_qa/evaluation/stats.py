"""Statistics helpers.

The paper reports essentially NO statistics for the MC results (only the single
variance figure A.2). Wilson CIs and McNemar tests below are labelled
"beyond paper" wherever they surface. The bootstrap helper mirrors the Section 4.5
human-eval machinery (100 replicas, 95th-percentile interval) -- unused for MC but
kept for completeness (RA-13).
"""
from __future__ import annotations

import math

import numpy as np


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (beyond paper)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar(both_wrong: int, a_right_b_wrong: int, a_wrong_b_right: int,
            both_right: int) -> dict:
    """McNemar's test (paired, exact binomial on discordant pairs). Beyond paper."""
    b, c = a_right_b_wrong, a_wrong_b_right
    n = b + c
    if n == 0:
        return {"statistic": 0.0, "p_value": 1.0, "discordant": 0}
    # exact two-sided binomial p on min(b, c)
    from math import comb
    k = min(b, c)
    p = 2 * sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    p = min(1.0, p)
    chi2 = (abs(b - c) - 1) ** 2 / n  # continuity-corrected
    return {"statistic": chi2, "p_value": p, "discordant": n, "b": b, "c": c}


def bootstrap_proportion_ci(labels: list, target, *, replicas: int = 100,
                            pct: float = 95.0, seed: int = 0) -> dict:
    """Non-parametric bootstrap of P(label == target). Mirrors Section 4.5 / RA-13."""
    rng = np.random.default_rng(seed)
    arr = np.array([1 if x == target else 0 for x in labels])
    n = len(arr)
    if n == 0:
        return {"point": 0.0, "lo": 0.0, "hi": 0.0}
    reps = np.array([arr[rng.integers(0, n, n)].mean() for _ in range(replicas)])
    lo = float(np.percentile(reps, (100 - pct) / 2))
    hi = float(np.percentile(reps, 100 - (100 - pct) / 2))
    return {"point": float(arr.mean()), "lo": lo, "hi": hi,
            "replicas": replicas, "interval_pct": pct}
