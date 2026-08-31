#!/usr/bin/env python
"""Phase 12 -- Self-consistency (11 decodes) + assemble MC tables 4-7, A.1.

PAPER-SPECIFIED: 11 CoT decodes, temperature sampling, plurality vote
(Section 4.4). Temperature -> RA-03 (0.7).
"""
from __future__ import annotations

import argparse
import json

from medalign_qa.evaluation import tables
from medalign_qa.evaluation.mc_accuracy import score
from medalign_qa.inference.runner import run_mc_split
from medalign_qa.models import load_model
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

TARGETS = [("medqa_usmle_4opt", "test"), ("medmcqa", "validation"), ("pubmedqa", "test")]
TARGETS += [(f"mmlu_{s}", "test") for s in paths.MMLU_SUBJECTS]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--datasets", default=None, help="comma list to restrict targets")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml"))
    args = ap.parse_args()
    log = get_logger("phase12")

    sc = io.read_yaml(args.config)["decode"]["self_consistency"]  # n=11 PAPER-SPECIFIED
    model = load_model(args.config, mock=args.mock)
    only = set(args.datasets.split(",")) if args.datasets else None

    summary = {}
    for dataset, split in TARGETS:
        if only and dataset not in only:
            continue
        if not (paths.PROCESSED / f"{dataset}.jsonl").exists():
            continue
        run_mc_split(model, dataset, split, "self_consistency",
                     temperature=sc["temperature"], top_p=sc.get("top_p", 1.0),
                     max_tokens=sc["max_tokens"], n=sc["n"], limit=args.limit,
                     max_workers=args.workers)
        s = score(paths.DERIVED / "predictions" / "self_consistency" / f"{dataset}__{split}.jsonl")
        s.pop("_per_uid_correct", None)
        summary[f"{dataset}/{split}"] = s
        log.info("  %-28s SC acc=%.3f parse=%.3f (n=%d)", f"{dataset}/{split}",
                 s.get("accuracy", 0), s.get("parse_rate", 0), s.get("n", 0))

    written = tables.write_all()
    usage = model.usage_summary()
    (paths.RESULTS / "phase12_mc_results.json").write_text(
        json.dumps({"strategy": "self_consistency", "n_decodes": sc["n"],
                    "model": model.name, "summary": summary, "tables": written,
                    "usage": usage}, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("tables: %s", written)
    log.info("est cost $%.4f", usage.get("est_cost_usd", 0))
    log.info("PHASE 12 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
