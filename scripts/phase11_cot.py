#!/usr/bin/env python
"""Phase 11 -- Chain-of-thought multiple-choice inference (Table 6 + MMLU CoT for A.1)."""
from __future__ import annotations

import argparse
import json

from medalign_qa.evaluation.mc_accuracy import score
from medalign_qa.inference.runner import run_mc_split
from medalign_qa.models import load_model
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

# PAPER-SPECIFIED: Table 6 ablation datasets + MMLU (A.3 / Table A.1)
TARGETS = [("medqa_usmle_4opt", "test"), ("medmcqa", "validation"), ("pubmedqa", "test")]
TARGETS += [(f"mmlu_{s}", "test") for s in paths.MMLU_SUBJECTS]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--datasets", default=None, help="comma list to restrict targets")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml"))
    args = ap.parse_args()
    log = get_logger("phase11")

    dc = io.read_yaml(args.config)["decode"]["cot"]
    model = load_model(args.config, mock=args.mock)
    only = set(args.datasets.split(",")) if args.datasets else None

    summary = {}
    for dataset, split in TARGETS:
        if only and dataset not in only:
            continue
        if not (paths.PROCESSED / f"{dataset}.jsonl").exists():
            continue
        run_mc_split(model, dataset, split, "cot",
                     temperature=dc["temperature"], max_tokens=dc["max_tokens"],
                     limit=args.limit, max_workers=args.workers)
        s = score(paths.DERIVED / "predictions" / "cot" / f"{dataset}__{split}.jsonl")
        s.pop("_per_uid_correct", None)
        summary[f"{dataset}/{split}"] = s
        log.info("  %-28s acc=%.3f parse=%.3f (n=%d)", f"{dataset}/{split}",
                 s.get("accuracy", 0), s.get("parse_rate", 0), s.get("n", 0))

    usage = model.usage_summary()
    (paths.RESULTS / "phase11_cot_accuracy.json").write_text(
        json.dumps({"strategy": "cot", "model": model.name, "summary": summary, "usage": usage},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    min_parse = min((s.get("parse_rate", 0) for s in summary.values()), default=0)
    log.info("est cost $%.4f | min parse-rate %.1f%%", usage.get("est_cost_usd", 0), 100 * min_parse)
    log.info("PHASE 11 %s", "PASS" if min_parse >= 0.90 else "CHECK")
    return 0 if min_parse >= 0.90 else 1


if __name__ == "__main__":
    raise SystemExit(main())
