#!/usr/bin/env python
"""Phase 10 -- Few-shot multiple-choice inference.

Default: run MedQA-4opt only (the 10.checkpoint gate). Pass --all for the full sweep
(MedQA 4-opt & 5-opt, MedMCQA validation, PubMedQA test, MMLU x6 test).
"""
from __future__ import annotations

import argparse
import json

from medalign_qa.inference.runner import run_mc_split, score_file
from medalign_qa.models import load_model
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

# (dataset, split) in scope for few-shot  --  PAPER-SPECIFIED splits (RA-01/RA-02/RA-06)
GATE = [("medqa_usmle_4opt", "test")]
FULL = GATE + [
    ("medqa_usmle_5opt", "test"),        # loader emits this only if 5-opt processed; see note
    ("medmcqa", "validation"),
    ("pubmedqa", "test"),
    *[(f"mmlu_{s}", "test") for s in paths.MMLU_SUBJECTS],
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml"))
    args = ap.parse_args()
    log = get_logger("phase10")

    cfg = io.read_yaml(args.config)["decode"]["few_shot"]
    model = load_model(args.config, mock=args.mock)
    targets = FULL if args.all else GATE
    targets = [(d, s) for (d, s) in targets
               if (paths.PROCESSED / f"{d}.jsonl").exists()]

    summary = {}
    for dataset, split in targets:
        res = run_mc_split(model, dataset, split, "few_shot",
                           temperature=cfg["temperature"], max_tokens=cfg["max_tokens"],
                           limit=args.limit, max_workers=args.workers)
        summary[f"{dataset}/{split}"] = res
        log.info("  %-28s acc=%.3f  parse=%.3f  (n=%d)",
                 f"{dataset}/{split}", res.get("accuracy", 0), res.get("parse_rate", 0), res.get("n", 0))

    usage = model.usage_summary()
    report = {"strategy": "few_shot", "model": model.name, "summary": summary, "usage": usage}
    (paths.RESULTS / "phase10_fewshot_accuracy.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    min_parse = min((r.get("parse_rate", 0) for r in summary.values()), default=0)
    log.info("est cost $%.4f  |  min parse-rate %.1f%%", usage.get("est_cost_usd", 0), 100 * min_parse)
    ok = min_parse >= 0.95
    log.info("PHASE 10 %s%s", "PASS" if ok else "CHECK",
             "" if ok else "  (parse-rate < 95% on some split -- inspect predictions)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
