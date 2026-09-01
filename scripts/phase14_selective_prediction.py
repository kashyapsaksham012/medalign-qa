#!/usr/bin/env python
"""Phase 14 -- Selective prediction on MedQA (41 decodes, Fig 5)."""
from __future__ import annotations

import argparse
import json

from medalign_qa import config as run_config
from medalign_qa.inference.runner import run_mc_split, split_is_complete
from medalign_qa.models import load_model
from medalign_qa.uncertainty.selective_prediction import curve
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="subsample size (default: full 1273)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "qwen25-7b-local.yaml"))
    args = ap.parse_args()
    log = get_logger("phase14")

    g = io.read_yaml(paths.CONFIGS / "global.yaml")
    sp_cfg = io.read_yaml(args.config)["decode"]["selective_prediction"]  # n=41 PAPER-SPECIFIED
    grid = g["selective_prediction"]["deferral_grid"]
    dataset, split = "medqa_usmle_4opt", "test"

    complete = split_is_complete("self_consistency", dataset, split,
                                 limit=args.limit, out_subdir="selective_prediction")
    model = None if complete else load_model(args.config, mock=args.mock)
    if model is None:
        log.info("selective-prediction decodes already complete -- scoring the curve only")

    run_mc_split(model, dataset, split, "self_consistency",
                 temperature=sp_cfg["temperature"], top_p=sp_cfg.get("top_p", 1.0),
                 max_tokens=sp_cfg["max_tokens"], n=sp_cfg["n"],
                 limit=args.limit, max_workers=args.workers, seed=g["seed"],
                 out_subdir="selective_prediction")
    out = run_config.prediction_file("selective_prediction", f"{dataset}__{split}")
    if not out.exists() or not any(True for _ in io.read_jsonl(out)):
        log.error("PHASE 14 NO DATA -- no decodes were produced for %s/%s.", dataset, split)
        return 1
    res = curve(out, grid)
    res["mock"] = args.mock
    res["paper_reference"] = io.read_yaml(paths.METADATA / "paper_results.yaml")["selective_prediction"]
    res["subsample"] = args.limit
    (paths.RESULTS / "phase14_selective_prediction.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    for p in res["points"]:
        log.info("  defer %.2f  n=%4d  acc=%s", p["deferral"], p["n_kept"], p["accuracy"])
    log.info("monotonic non-decreasing: %s | paper: 82.5%% @ 0.45", res["monotonic_non_decreasing"])
    log.info("est cost $%.4f", model.usage_summary().get("est_cost_usd", 0) if model is not None else 0.0)
    log.info("PHASE 14 %s", "PASS (MOCK -- not a real result)" if args.mock else "PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
