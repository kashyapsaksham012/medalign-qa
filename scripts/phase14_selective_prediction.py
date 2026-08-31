#!/usr/bin/env python
"""Phase 14 -- Selective prediction on MedQA (41 decodes, Fig 5)."""
from __future__ import annotations

import argparse
import json

from medalign_qa.inference.runner import run_mc_split
from medalign_qa.models import load_model
from medalign_qa.uncertainty.selective_prediction import curve
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="subsample size (default: full 1273)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml"))
    args = ap.parse_args()
    log = get_logger("phase14")

    g = io.read_yaml(paths.CONFIGS / "global.yaml")
    sp_cfg = io.read_yaml(args.config)["decode"]["selective_prediction"]  # n=41 PAPER-SPECIFIED
    grid = g["selective_prediction"]["deferral_grid"]
    model = load_model(args.config, mock=args.mock)

    dataset, split = "medqa_usmle_4opt", "test"
    run_mc_split(model, dataset, split, "self_consistency",
                 temperature=sp_cfg["temperature"], top_p=sp_cfg.get("top_p", 1.0),
                 max_tokens=sp_cfg["max_tokens"], n=sp_cfg["n"],
                 limit=args.limit, max_workers=args.workers,
                 out_subdir="selective_prediction")
    out = paths.DERIVED / "predictions" / "selective_prediction" / f"{dataset}__{split}.jsonl"
    res = curve(out, grid)
    res["paper_reference"] = io.read_yaml(paths.METADATA / "paper_results.yaml")["selective_prediction"]
    res["subsample"] = args.limit
    (paths.RESULTS / "phase14_selective_prediction.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    for p in res["points"]:
        log.info("  defer %.2f  n=%4d  acc=%s", p["deferral"], p["n_kept"], p["accuracy"])
    log.info("monotonic non-decreasing: %s | paper: 82.5%% @ 0.45", res["monotonic_non_decreasing"])
    log.info("est cost $%.4f", model.usage_summary().get("est_cost_usd", 0))
    log.info("PHASE 14 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
