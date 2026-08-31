#!/usr/bin/env python
"""Phase 19 -- Paper-to-result comparison + qualitative-findings verdict."""
from __future__ import annotations

import json

from medalign_qa.evaluation.mc_accuracy import score
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

PAPER = io.read_yaml(paths.METADATA / "paper_results.yaml")
TOL = io.read_yaml(paths.CONFIGS / "global.yaml")["tolerances"]


def _acc(strategy, stem):
    p = paths.DERIVED / "predictions" / strategy / f"{stem}.jsonl"
    if not p.exists():
        return None
    s = score(p)
    return round(100 * s["accuracy"], 1) if s.get("n") else None


def main() -> int:
    log = get_logger("phase19")
    rows = []

    def cmp(name, paper, ours, tol, note=""):
        if ours is None:
            verdict = "NOT-ATTEMPTED"
            d = None
        else:
            d = round(ours - paper, 1)
            verdict = "WITHIN-TOLERANCE" if abs(d) <= tol else "DIVERGENT (expected: different model)"
        rows.append({"metric": name, "paper": paper, "ours": ours, "delta": d,
                     "tolerance_pp": tol, "verdict": verdict, "note": note})

    # absolute-value comparisons (gaps EXPECTED -- different model)
    cmp("MedQA 4-opt few-shot", PAPER["table5"]["medqa_usmle_4opt"]["flan_8b"],
        _acc("few_shot", "medqa_usmle_4opt__test"), TOL["mc_accuracy_large_n_pp"],
        "vs paper Flan-PaLM 8B (same size)")
    cmp("MedQA 4-opt SC", PAPER["table7"]["medqa_usmle_4opt"]["sc"],
        _acc("self_consistency", "medqa_usmle_4opt__test"), TOL["mc_accuracy_self_consistency_pp"],
        "vs paper Flan-PaLM 540B")
    cmp("MedMCQA few-shot", PAPER["table5"]["medmcqa"]["flan_8b"],
        _acc("few_shot", "medmcqa__validation"), TOL["mc_accuracy_large_n_pp"], "vs Flan-PaLM 8B")
    cmp("PubMedQA few-shot", PAPER["table5"]["pubmedqa"]["flan_8b"],
        _acc("few_shot", "pubmedqa__test"), TOL["mc_accuracy_self_consistency_pp"], "vs Flan-PaLM 8B")
    for s in paths.MMLU_SUBJECTS:
        cmp(f"MMLU {s} SC", PAPER["tableA1_flan_palm_540b_sc"].get(s),
            _acc("self_consistency", f"mmlu_{s}__test"), TOL["mc_accuracy_small_n_pp"],
            "vs Flan-PaLM 540B (approx)")

    # qualitative findings -- the actual replication payoff
    def _f(a, b):  # return (val_a, val_b) or None
        return (a, b) if (a is not None and b is not None) else None

    findings = []

    fs_mq = _acc("few_shot", "medqa_usmle_4opt__test"); sc_mq = _acc("self_consistency", "medqa_usmle_4opt__test")
    fs_mm = _acc("few_shot", "medmcqa__validation"); sc_mm = _acc("self_consistency", "medmcqa__validation")
    fs_pm = _acc("few_shot", "pubmedqa__test"); sc_pm = _acc("self_consistency", "pubmedqa__test")
    cot_mq = _acc("cot", "medqa_usmle_4opt__test"); cot_mm = _acc("cot", "medmcqa__validation"); cot_pm = _acc("cot", "pubmedqa__test")

    def finding(name, ok, detail):
        v = "NOT-ATTEMPTED" if ok is None else ("REPRODUCED-QUALITATIVELY" if ok else "DIVERGENT")
        findings.append({"finding": name, "verdict": v, "detail": detail})

    finding("SC beats few-shot on MedQA",
            None if _f(fs_mq, sc_mq) is None else sc_mq > fs_mq,
            f"ours: FS {fs_mq} -> SC {sc_mq}; paper 60.3 -> 67.6")
    finding("SC beats few-shot on MedMCQA",
            None if _f(fs_mm, sc_mm) is None else sc_mm > fs_mm,
            f"ours: FS {fs_mm} -> SC {sc_mm}; paper 56.5 -> 57.6")
    finding("SC hurts PubMedQA",
            None if _f(fs_pm, sc_pm) is None else sc_pm < fs_pm,
            f"ours: FS {fs_pm} -> SC {sc_pm}; paper 79.0 -> 75.2")
    finding("CoT does not beat few-shot on MC (MedQA/MedMCQA/PubMedQA)",
            None if None in (fs_mq, cot_mq, fs_mm, cot_mm, fs_pm, cot_pm)
            else (cot_mq <= fs_mq + 1 and cot_mm <= fs_mm + 1 and cot_pm <= fs_pm + 1),
            f"ours FS/CoT -- MedQA {fs_mq}/{cot_mq}, MedMCQA {fs_mm}/{cot_mm}, PubMedQA {fs_pm}/{cot_pm}")
    sp = paths.RESULTS / "phase14_selective_prediction.json"
    if sp.exists():
        d = json.loads(sp.read_text())
        finding("Selective-prediction accuracy rises with deferral",
                d.get("monotonic_non_decreasing"),
                f"ours points: {[(p['deferral'], p['accuracy']) for p in d['points'] if p['accuracy'] is not None]}")
    else:
        finding("Selective-prediction accuracy rises with deferral", None, "phase14 not run")
    finding("Instruction tuning helps (PaLM < Flan-PaLM)", None,
            "requires the model's non-instruct base -- not run (single model)")
    finding("Scaling helps (~2x 8B->540B)", None,
            "requires >= 2 model sizes -- see Phase 13")

    out = {"absolute_comparisons": rows, "qualitative_findings": findings,
           "framing": "Absolute-value gaps vs Flan-PaLM are EXPECTED -- a different "
                      "(2024, 8B) model. The replication tests whether the paper's "
                      "QUALITATIVE findings hold with the same methodology.",
           "not_reproduced": ["Med-PaLM / instruction prompt tuning (B1/B2)",
                              "All human evaluation, Section 4.5 (B4)",
                              "Scaling curves (single model)"]}
    (paths.RESULTS / "comparison.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 19 -- Paper vs Replication", "", out["framing"], "",
          "## Absolute comparisons (gaps expected -- different model)", "",
          "| Metric | Paper | Ours | Δ | Tol (pp) | Verdict | Note |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['metric']} | {r['paper']} | {r['ours']} | {r['delta']} | "
                  f"{r['tolerance_pp']} | {r['verdict']} | {r['note']} |")
    md += ["", "## Qualitative findings (the replication payoff)", "",
           "| Finding | Verdict | Detail |", "|---|---|---|"]
    for f in findings:
        md.append(f"| {f['finding']} | **{f['verdict']}** | {f['detail']} |")
    md += ["", "## Not reproduced", ""] + [f"- {x}" for x in out["not_reproduced"]]
    (paths.RESULTS / "comparison.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    for f in findings:
        log.info("  %-52s %s", f["finding"], f["verdict"])
    log.info("PHASE 19 PASS -- results/comparison.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
