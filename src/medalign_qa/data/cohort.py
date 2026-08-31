"""Phase 5 — 'cohort' construction.

NOT APPLICABLE: there is no clinical patient cohort in this paper. The analogues are
  (a) the 140-question long-form human-evaluation set  (Section 4.5)
  (b) the 40 instruction-prompt-tuning exemplars       (Section 3.3.4)  [BLOCKED B3]
"""
from __future__ import annotations

import json
import re

import openpyxl

from ..utils import paths
from ..utils.io import read_jsonl, utcnow, write_jsonl


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower()).strip(" ?.")


# --------------------------------------------------------------------------- #
# (a) 140-question human-evaluation set   PAPER-SPECIFIED (line ~878)
#     100 HealthSearchQA + 20 LiveQA + 20 MedicationQA, disjoint from the 40 IPT
#     exemplars. The 140 questions themselves are released (xlsx sheet 2) and are
#     treated as authoritative. Source attribution is reconstructed by matching.
# --------------------------------------------------------------------------- #
def build_human_eval_140() -> dict:
    wb = openpyxl.load_workbook(
        paths.RAW_HEALTHSEARCHQA / "41586_2023_6291_MOESM6_ESM.xlsx", read_only=True)
    questions = [r[0].strip() for r in wb.worksheets[1].iter_rows(values_only=True)
                 if r and r[0] and r[0].strip()]

    hsqa = {_norm(r["question"]): r["question"]
            for r in read_jsonl(paths.PROCESSED / "healthsearchqa.jsonl")}
    medq = {_norm(r["question"]): r["question"]
            for r in read_jsonl(paths.PROCESSED / "medicationqa.jsonl")}
    live = [r for r in read_jsonl(paths.PROCESSED / "liveqa.jsonl") if r["split"] == "test"]
    live_norms = {_norm(r["question"]) for r in live} | {_norm(r["meta"].get("message")) for r in live}

    records, comp = [], {"healthsearchqa": 0, "liveqa": 0, "medicationqa": 0}
    for i, q in enumerate(questions):
        n = _norm(q)
        if n in hsqa:
            src = "healthsearchqa"
        elif n in medq:
            src = "medicationqa"
        elif n in live_norms or any(n in x or x in n for x in live_norms if x):
            src = "liveqa"
        else:
            # remaining unmatched are LiveQA-style (paraphrased consumer questions
            # whose released text differs from the raw NIST MESSAGE). RA-13-adjacent.
            src = "liveqa"
        comp[src] += 1
        records.append({"uid": f"human_eval_140/{i}", "question": q,
                        "source_dataset": src,
                        "source_match": "exact" if (n in hsqa or n in medq or n in live_norms) else "inferred_liveqa"})

    write_jsonl(paths.DERIVED / "human_eval_140.jsonl", records)
    return {
        "n": len(records),
        "paper_composition": {"healthsearchqa": 100, "liveqa": 20, "medicationqa": 20},
        "reconstructed_composition": comp,
        "composition_matches_paper": comp == {"healthsearchqa": 100, "liveqa": 20, "medicationqa": 20},
        "n_inferred": sum(1 for r in records if r["source_match"] != "exact"),
    }


# --------------------------------------------------------------------------- #
# (b) 40 instruction-prompt-tuning exemplars   PAPER-SPECIFIED count; content BLOCKED
# --------------------------------------------------------------------------- #
def build_ipt_exemplar_placeholder() -> dict:
    """B3: the 40 (question, ideal-answer) pairs are NOT published.

    We emit a *schema-only placeholder* so Phase 11 code is runnable and fails
    loudly. RA-12 would fill this by authoring clinician-style answers.
    """
    out = paths.DERIVED / "ipt_exemplars.PLACEHOLDER.jsonl"
    rows = [{"uid": f"ipt_exemplar/{i}", "question": None, "ideal_answer": None,
             "source_dataset": None,
             "_status": "PLACEHOLDER — content unavailable (blocker B3). "
                        "Fill via RA-12 or supply the authors' 40 exemplars."}
            for i in range(40)]
    write_jsonl(out, rows)
    return {"path": str(out.relative_to(paths.ROOT)), "n_slots": 40,
            "status": "BLOCKED (B3)"}


def run() -> dict:
    he = build_human_eval_140()
    ipt = build_ipt_exemplar_placeholder()
    report = {"generated": utcnow(), "human_eval_140": he, "ipt_exemplars": ipt}
    (paths.RESULTS / "phase05_cohort_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
