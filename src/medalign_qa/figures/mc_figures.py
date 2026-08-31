"""Figures 3, 4, 5 with substitute-model numbers beside the paper's."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from ..evaluation.mc_accuracy import score  # noqa: E402
from ..utils import io, paths  # noqa: E402

PAPER = io.read_yaml(paths.METADATA / "paper_results.yaml")


def _acc(strategy, stem):
    p = paths.DERIVED / "predictions" / strategy / f"{stem}.jsonl"
    return round(100 * score(p)["accuracy"], 1) if p.exists() and score(p).get("n") else None


def fig3() -> str:
    dsets = [("MedMCQA", "medmcqa__validation", "medmcqa"),
             ("MedQA", "medqa_usmle_4opt__test", "medqa"),
             ("PubMedQA", "pubmedqa__test", "pubmedqa")]
    labels, prior, flan, ours = [], [], [], []
    for disp, stem, key in dsets:
        labels.append(disp)
        prior.append(PAPER["fig3"][key]["prior_sota"])
        flan.append(PAPER["fig3"][key]["flan_palm_540b"])
        ours.append(_acc("self_consistency", stem) or _acc("few_shot", stem) or 0)
    x = np.arange(len(labels))
    w = 0.27
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w, prior, w, label="Prior SOTA (paper)")
    ax.bar(x, flan, w, label="Flan-PaLM 540B (paper)")
    ax.bar(x + w, ours, w, label="Llama-3.1-8B-Instruct (this repl.)")
    for i, v in enumerate(ours):
        ax.text(x[i] + w, v + 1, f"{v}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Accuracy (%)"); ax.set_ylim(0, 100)
    ax.set_title("Figure 3 (replication) -- MC accuracy vs paper")
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = paths.FIGURES / "fig3_replication.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    return str(p.relative_to(paths.ROOT))


def fig4() -> str:
    subs = list(paths.MMLU_SUBJECTS)
    ours_sc = [_acc("self_consistency", f"mmlu_{s}__test") or 0 for s in subs]
    ours_fs = [_acc("few_shot", f"mmlu_{s}__test") or 0 for s in subs]
    paper = [PAPER["tableA1_flan_palm_540b_sc"].get(s, 0) for s in subs]
    x = np.arange(len(subs)); w = 0.27
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(x - w, paper, w, label="Flan-PaLM 540B SC (paper, approx)")
    ax.bar(x, ours_fs, w, label="Ours few-shot")
    ax.bar(x + w, ours_sc, w, label="Ours SC")
    ax.set_xticks(x); ax.set_xticklabels([s.replace("_", "\n") for s in subs], fontsize=8)
    ax.set_ylabel("Accuracy (%)"); ax.set_ylim(0, 100)
    ax.set_title("Figure 4 (replication) -- MMLU clinical topics")
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = paths.FIGURES / "fig4_replication.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    return str(p.relative_to(paths.ROOT))


def fig5() -> str:
    src = paths.RESULTS / "phase14_selective_prediction.json"
    if not src.exists():
        return "SKIPPED (run phase14 first)"
    data = json.loads(src.read_text())
    pts = [p for p in data["points"] if p["accuracy"] is not None]
    xs = [p["deferral"] for p in pts]
    ys = [100 * p["accuracy"] for p in pts]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(xs, ys, marker="o", label="Llama-3.1-8B-Instruct (this repl.)")
    ax.scatter([0.45], [82.5], color="red", zorder=5, label="Flan-PaLM 540B (paper): 82.5% @ 0.45")
    ax.set_xlabel("Deferral fraction"); ax.set_ylabel("Accuracy on retained (%)")
    ax.set_title("Figure 5 (replication) -- selective prediction on MedQA")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout()
    p = paths.FIGURES / "fig5_replication.png"
    fig.savefig(p, dpi=120); plt.close(fig)
    return str(p.relative_to(paths.ROOT))


def write_all() -> list[str]:
    return [fig3(), fig4(), fig5()]
