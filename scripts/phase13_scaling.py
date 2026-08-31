#!/usr/bin/env python
"""Phase 13 -- Scaling analysis (Figs A.1, A.2).

Requires >= 2 model sizes. With a single substitute model this is NOT REPRODUCED;
we record that verdict + the paper's qualitative claim and what would be needed.
"""
from __future__ import annotations

import json

from medalign_qa.evaluation.mc_accuracy import find_predictions, score
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    log = get_logger("phase13")
    models_run = sorted({p.name for strat in ("few_shot", "self_consistency")
                         for p in find_predictions(strat)})
    # single model -> cannot draw a scaling curve
    g = io.read_yaml(paths.CONFIGS / "global.yaml")
    mcfg = io.read_yaml(paths.CONFIGS / "model" / "qwen25-7b-local.yaml")
    verdict = {
        "status": "NOT REPRODUCED",
        "reason": "Scaling (Figs A.1/A.2, Table 5 scaling reading) requires >= 2 model "
                  f"sizes. This run used a single substitute model ({mcfg.get('model')}).",
        "paper_claim": io.read_yaml(paths.METADATA / "paper_results.yaml")["findings"]["scaling_helps"],
        "to_reproduce": "Add a second `configs/model/*.yaml` at a larger size (e.g. "
                        "Qwen2.5-14B-Instruct), set `run_tag` in configs/global.yaml to a "
                        "new value, and re-run Phases 10 & 12; ideally also the non-instruct "
                        "base for the 'instruction tuning helps' finding.",
        "run_tag": g.get("run_tag"),
        "single_model_reference_points": {},
    }
    for strat in ("few_shot", "self_consistency"):
        for p in find_predictions(strat):
            s = score(p)
            if s.get("n"):
                verdict["single_model_reference_points"][f"{strat}:{p.stem}"] = round(100 * s["accuracy"], 1)

    (paths.RESULTS / "phase13_scaling.json").write_text(
        json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("PHASE 13: %s -- %s", verdict["status"], verdict["reason"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
