#!/usr/bin/env python
"""Phase 16 -- Statistical analysis (Wilson CIs on every accuracy; McNemar FS vs SC).

The paper reports no CIs / tests for MC results; everything here is labelled
"beyond paper". Also freezes the Phase-19 tolerance bands (RA-17).
"""
from __future__ import annotations

import json

from medalign_qa.evaluation.mc_accuracy import find_predictions, score
from medalign_qa.evaluation.stats import mcnemar, wilson_ci
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    log = get_logger("phase16")
    report = {"note": "Wilson CIs and McNemar are BEYOND PAPER (the paper reports "
                      "neither for MC).", "accuracies": {}, "mcnemar_fewshot_vs_sc": {}}

    per_uid = {}
    for strat in ("few_shot", "cot", "self_consistency"):
        for p in find_predictions(strat):
            s = score(p)
            if not s.get("n"):
                continue
            key = f"{strat}:{p.stem}"
            report["accuracies"][key] = {
                "n": s["n"], "accuracy": round(s["accuracy"], 4),
                "wilson95": [round(s["wilson95_lo"], 4), round(s["wilson95_hi"], 4)],
                "parse_rate": round(s["parse_rate"], 4)}
            per_uid[key] = s["_per_uid_correct"]

    # McNemar: few_shot vs self_consistency on shared datasets
    for stem in {p.stem for p in find_predictions("few_shot")}:
        a = per_uid.get(f"few_shot:{stem}")
        b = per_uid.get(f"self_consistency:{stem}")
        if not a or not b:
            continue
        shared = set(a) & set(b)
        bw = sum(1 for u in shared if not a[u] and not b[u])
        arb = sum(1 for u in shared if a[u] and not b[u])
        awb = sum(1 for u in shared if not a[u] and b[u])
        br = sum(1 for u in shared if a[u] and b[u])
        report["mcnemar_fewshot_vs_sc"][stem] = mcnemar(bw, arb, awb, br)

    # freeze tolerance bands (RA-17) already in configs/global.yaml -- echo them
    report["tolerances_RA17"] = io.read_yaml(paths.CONFIGS / "global.yaml")["tolerances"]

    (paths.RESULTS / "phase16_stats.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("scored %d prediction files; McNemar on %d datasets",
             len(report["accuracies"]), len(report["mcnemar_fewshot_vs_sc"]))
    log.info("PHASE 16 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
