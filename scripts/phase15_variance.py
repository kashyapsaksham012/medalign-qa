#!/usr/bin/env python
"""Phase 15 -- Variance of repeated MedQA evaluation (A.2: paper reports 0.078 over 4 runs)."""
from __future__ import annotations

import argparse
import json
import statistics

from medalign_qa.evaluation.mc_accuracy import score
from medalign_qa.inference.runner import run_mc_split
from medalign_qa.models import load_model
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--runs", type=int, default=4)          # PAPER-SPECIFIED (A.2)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml"))
    args = ap.parse_args()
    log = get_logger("phase15")

    sc = io.read_yaml(args.config)["decode"]["self_consistency"]
    model = load_model(args.config, mock=args.mock)
    dataset, split = "medqa_usmle_4opt", "test"

    accs = []
    for i in range(args.runs):
        run_mc_split(model, dataset, split, "self_consistency",
                     temperature=sc["temperature"], top_p=sc.get("top_p", 1.0),
                     max_tokens=sc["max_tokens"], n=sc["n"], seed=1000 + i,
                     limit=args.limit, max_workers=args.workers, resume=False,
                     out_subdir=f"variance/run{i}")
        s = score(paths.DERIVED / "predictions" / f"variance/run{i}" / f"{dataset}__{split}.jsonl")
        accs.append(round(100 * s["accuracy"], 2))
        log.info("  run %d: acc=%.2f", i, accs[-1])

    var = statistics.pvariance(accs) if len(accs) > 1 else 0.0
    res = {"runs": accs, "mean": round(statistics.mean(accs), 3),
           "variance": round(var, 4), "stdev": round(statistics.pstdev(accs), 3),
           "paper_variance_4runs": io.read_yaml(paths.METADATA / "paper_results.yaml")["variance_medqa_4runs"],
           "note": "Loose comparison only -- different model. Paper's 0.078 is for Flan-PaLM 540B."}
    (paths.RESULTS / "phase15_variance.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    log.info("variance=%.4f (paper: 0.078, Flan-PaLM 540B) | mean=%.2f", var, res["mean"])
    log.info("PHASE 15 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
