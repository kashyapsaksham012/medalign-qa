"""Phase 8 — exploratory / data-validation summaries.

Descriptive only. No target from the paper to match here (the paper tabulates no
feature distributions); the purpose is to catch anomalies before the harness runs.
"""
from __future__ import annotations

import json
import statistics
from collections import Counter

from ..utils import paths
from ..utils.io import read_jsonl, utcnow

MC_EVAL = {
    "medqa_usmle_4opt": "test",
    "medmcqa": "validation",
    "pubmedqa": "test",
    **{f"mmlu_{s}": "test" for s in paths.MMLU_SUBJECTS},
}
LONGFORM = {"liveqa": "test", "medicationqa": "all", "healthsearchqa": "all"}


def _wc(s: str) -> int:
    return len(s.split())


def summarise() -> dict:
    out: dict = {"generated": utcnow(), "mc": {}, "longform": {}}

    for ds, split in MC_EVAL.items():
        rows = [r for r in read_jsonl(paths.PROCESSED / f"{ds}.jsonl") if r["split"] == split]
        golds = [r.get("gold") for r in rows]
        qlens = [_wc(r["question"]) for r in rows]
        rec = {
            "eval_split": split,
            "n": len(rows),
            "gold_letter_balance": dict(Counter(golds)),
            "question_words": {"min": min(qlens), "median": statistics.median(qlens),
                               "mean": round(statistics.mean(qlens), 1), "max": max(qlens)},
            "n_options_distribution": dict(Counter(len(r["options"]) for r in rows)),
            "has_context": sum(1 for r in rows if r.get("context")),
        }
        if ds == "medmcqa":
            allrows = list(read_jsonl(paths.PROCESSED / "medmcqa.jsonl"))
            rec["choice_type_valid"] = dict(Counter(
                r["meta"].get("choice_type") for r in allrows if r["split"] == "validation"))
            rec["subject_top10_valid"] = dict(Counter(
                r["meta"].get("subject") for r in allrows if r["split"] == "validation").most_common(10))
        out["mc"][ds] = rec

    for ds, split in LONGFORM.items():
        rows = [r for r in read_jsonl(paths.PROCESSED / f"{ds}.jsonl") if r["split"] == split]
        qlens = [_wc(r["question"]) for r in rows]
        rec = {"eval_split": split, "n": len(rows),
               "question_words": {"min": min(qlens), "median": statistics.median(qlens),
                                  "mean": round(statistics.mean(qlens), 1), "max": max(qlens)},
               "with_reference_answer": sum(1 for r in rows if r.get("gold"))}
        if ds == "medicationqa":
            rec["question_type_counts"] = dict(Counter(
                r["meta"].get("question_type") for r in rows).most_common(15))
        out["longform"][ds] = rec

    # position-bias flag: MC eval golds should be roughly uniform across letters
    flags = []
    for ds, rec in out["mc"].items():
        bal = rec["gold_letter_balance"]
        bal = {k: v for k, v in bal.items() if k}
        if bal:
            frac = max(bal.values()) / sum(bal.values())
            if frac > 0.40:
                flags.append(f"{ds}: gold letter '{max(bal, key=bal.get)}' is {frac:.0%} of eval set")
    out["anomaly_flags"] = flags
    return out


def make_figures(summary: dict) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    made = []
    # gold-letter balance per MC eval set
    fig, ax = plt.subplots(figsize=(10, 4))
    datasets = list(summary["mc"])
    letters = ["A", "B", "C", "D", "E"]
    import numpy as np
    x = np.arange(len(datasets))
    for i, L in enumerate(letters):
        vals = [summary["mc"][d]["gold_letter_balance"].get(L, 0) / max(summary["mc"][d]["n"], 1)
                for d in datasets]
        ax.bar(x + i * 0.16, vals, width=0.16, label=L)
    ax.set_xticks(x + 0.32)
    ax.set_xticklabels([d.replace("mmlu_", "") for d in datasets], rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("fraction of eval set")
    ax.set_title("Gold-answer letter balance across MC evaluation splits (position-bias check)")
    ax.legend(title="gold letter", fontsize=8)
    fig.tight_layout()
    p = paths.FIGURES / "phase08_gold_letter_balance.png"
    fig.savefig(p, dpi=110)
    plt.close(fig)
    made.append(str(p.relative_to(paths.ROOT)))
    return made


def run() -> dict:
    s = summarise()
    figs = make_figures(s)
    s["figures"] = figs
    (paths.RESULTS / "phase08_eda_report.json").write_text(
        json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
    return s
