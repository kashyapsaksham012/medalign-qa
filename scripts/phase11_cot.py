#!/usr/bin/env python
"""Phase 11 -- Chain-of-thought multiple-choice inference (Table 6 + MMLU CoT for A.1)."""
from __future__ import annotations

import argparse
import json

from medalign_qa import config as run_config
from medalign_qa.evaluation.mc_accuracy import score
from medalign_qa.inference.runner import run_mc_split, split_is_complete
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
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "qwen25-7b-local.yaml"))
    args = ap.parse_args()
    log = get_logger("phase11")

    mcfg = io.read_yaml(args.config)
    dc = mcfg["decode"]["cot"]
    only = set(args.datasets.split(",")) if args.datasets else None
    targets = [(d, s) for (d, s) in TARGETS
               if (only is None or d in only) and (paths.PROCESSED / f"{d}.jsonl").exists()]

    need = [t for t in targets if not split_is_complete("cot", *t, limit=args.limit)]
    model = load_model(args.config, mock=args.mock) if need else None
    if model is None:
        log.info("all %d target(s) already complete -- re-scoring only", len(targets))

    summary = {}
    for dataset, split in targets:
        run_mc_split(model, dataset, split, "cot",
                     temperature=dc["temperature"], max_tokens=dc["max_tokens"],
                     limit=args.limit, max_workers=args.workers)
        s = score(run_config.prediction_file("cot", f"{dataset}__{split}"))
        s.pop("_per_uid_correct", None)
        summary[f"{dataset}/{split}"] = s
        log.info("  %-28s acc=%.3f parse=%.3f (n=%d)", f"{dataset}/{split}",
                 s.get("accuracy", 0), s.get("parse_rate", 0), s.get("n", 0))

    usage = model.usage_summary() if model is not None else {
        "model": f"{mcfg['model']}@{str(mcfg.get('revision', ''))[:12]}",
        "revision": mcfg.get("revision"), "n_calls": 0,
        "prompt_tokens": 0, "completion_tokens": 0, "est_cost_usd": 0.0}
    (paths.RESULTS / "phase11_cot_accuracy.json").write_text(
        json.dumps({"strategy": "cot", "model": usage["model"], "summary": summary, "usage": usage},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    min_parse = min((s.get("parse_rate", 0) for s in summary.values()), default=0)
    log.info("est cost $%.4f | min parse-rate %.1f%%", usage.get("est_cost_usd", 0), 100 * min_parse)
    log.info("PHASE 11 %s", "PASS" if min_parse >= 0.90 else "CHECK")
    return 0 if min_parse >= 0.90 else 1


if __name__ == "__main__":
    raise SystemExit(main())
