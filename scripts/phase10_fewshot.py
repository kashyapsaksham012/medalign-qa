#!/usr/bin/env python
"""Phase 10 -- Few-shot multiple-choice inference.

Default (MedQA-only first pass, RA-27): MedQA 4-opt + 5-opt test.
Pass --all for the full sweep (adds MedMCQA validation, PubMedQA test, MMLU x6 test).
Pass --datasets a,b to restrict to a comma list.
"""
from __future__ import annotations

import argparse
import json

from medalign_qa import config as run_config
from medalign_qa.inference.runner import run_mc_split, score_file, split_is_complete
from medalign_qa.models import load_model
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

# (dataset, split) in scope for few-shot  --  PAPER-SPECIFIED splits (RA-01/RA-02/RA-06)
GATE = [("medqa_usmle_4opt", "test"), ("medqa_usmle_5opt", "test")]   # RA-27: MedQA first
FULL = GATE + [
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
    ap.add_argument("--datasets", default=None, help="comma list to restrict targets")
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "qwen25-7b-local.yaml"))
    args = ap.parse_args()
    log = get_logger("phase10")

    mcfg = io.read_yaml(args.config)
    cfg = mcfg["decode"]["few_shot"]
    only = set(args.datasets.split(",")) if args.datasets else None
    targets = FULL if args.all else GATE
    targets = [(d, s) for (d, s) in targets
               if (paths.PROCESSED / f"{d}.jsonl").exists()
               and (only is None or d in only)]

    # Skip loading the (GPU) model entirely when every target is already complete —
    # a re-score-only pass, safe on a no-GPU machine / an incremental sweep.
    need = [t for t in targets
            if not split_is_complete("few_shot", *t, limit=args.limit)]
    model = load_model(args.config, mock=args.mock) if need else None
    if model is None:
        log.info("all %d target(s) already complete -- re-scoring only", len(targets))

    summary = {}
    for dataset, split in targets:
        res = run_mc_split(model, dataset, split, "few_shot",
                           temperature=cfg["temperature"], max_tokens=cfg["max_tokens"],
                           limit=args.limit, max_workers=args.workers)
        summary[f"{dataset}/{split}"] = res
        log.info("  %-28s acc=%.3f  parse=%.3f  (n=%d)",
                 f"{dataset}/{split}", res.get("accuracy", 0), res.get("parse_rate", 0), res.get("n", 0))

    usage = model.usage_summary() if model is not None else {
        "model": f"{mcfg['model']}@{str(mcfg.get('revision', ''))[:12]}",
        "revision": mcfg.get("revision"), "n_calls": 0,
        "prompt_tokens": 0, "completion_tokens": 0, "est_cost_usd": 0.0}
    report = {"strategy": "few_shot", "model": usage["model"], "mock": args.mock,
              "run_tag": run_config.run_tag(), "summary": summary, "usage": usage}
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
