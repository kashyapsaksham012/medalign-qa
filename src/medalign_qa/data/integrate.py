"""Phase 4 — parse every dataset to the unified schema, assemble MultiMedQA,
regenerate Table 1, and run leakage checks.
"""
from __future__ import annotations

import json
import re
from collections import Counter

from ..utils import paths
from ..utils.io import read_jsonl, utcnow, write_jsonl
from .loaders import LOADERS
from .schema import Record


def _rows(path) -> list[dict]:
    return list(read_jsonl(path))


def build_processed() -> dict[str, int]:
    """Write processed_data/<dataset>.jsonl for each loader. Returns row counts."""
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    all_recs: list[Record] = []
    for name, fn in LOADERS.items():
        recs = fn()
        all_recs.extend(recs)
        # a single loader ("mmlu") emits 6 datasets -> split the files by record.dataset
        by_ds: dict[str, list[Record]] = {}
        for r in recs:
            by_ds.setdefault(r.dataset, []).append(r)
        for ds, rs in by_ds.items():
            n = write_jsonl(paths.PROCESSED / f"{ds}.jsonl", (r.to_dict() for r in rs))
            counts[ds] = n
    # combined
    write_jsonl(paths.PROCESSED / "_all.jsonl", (r.to_dict() for r in all_recs))
    return counts


# --------------------------------------------------------------------------- #
# Table 1 (paper Section 3.1)
# --------------------------------------------------------------------------- #
def regenerate_table1(counts: dict[str, int]) -> list[dict]:
    def n(ds, split):
        return sum(1 for r in _rows(paths.PROCESSED / f"{ds}.jsonl") if r["split"] == split)

    table = []
    # MedQA
    table.append({"dataset": "MedQA (USMLE, 4-opt)", "format": "Q+A, 4 choices",
                  "reproduced_dev": n("medqa_usmle_4opt", "train") + n("medqa_usmle_4opt", "dev"),
                  "reproduced_test": n("medqa_usmle_4opt", "test"),
                  "paper_dev": 11450, "paper_test": 1273})
    # MedMCQA -- paper Table 1 'dev'(187K) == train+validation (exactly as MedQA's
    # dev == train+dev); 'test'(6.1K) == the withheld 6150-row test split. Paper
    # rounds both. The split we actually SCORE is the 4183 validation split (RA-01).
    table.append({"dataset": "MedMCQA", "format": "Q+A, 4 choices",
                  "reproduced_dev": n("medmcqa", "train") + n("medmcqa", "validation"),
                  "reproduced_test": n("medmcqa", "test"),
                  "paper_dev": 187000, "paper_test": 6100,
                  "paper_rounds": True,
                  "scored_split": {"split": "validation", "n": n("medmcqa", "validation"),
                                   "basis": "RA-01 (test labels withheld; paper 'dev set' ambiguous)"},
                  "note": "dev = train+validation = 187005 ~= 187000 (paper rounds 'over 187k'); "
                          "test = 6150 ~= 6100. Scoring is on the 4183 validation split (RA-01)."})
    # PubMedQA
    table.append({"dataset": "PubMedQA", "format": "Q+context+A (yes/no/maybe)",
                  "reproduced_dev": n("pubmedqa", "train"),
                  "reproduced_test": n("pubmedqa", "test"),
                  "paper_dev": 500, "paper_test": 500})
    # MMLU (sum of 6 subjects; report validation as 'dev' per paper)
    mmlu_val = sum(n(f"mmlu_{s}", "validation") for s in paths.MMLU_SUBJECTS)
    mmlu_test = sum(n(f"mmlu_{s}", "test") for s in paths.MMLU_SUBJECTS)
    table.append({"dataset": "MMLU (6 clinical subjects, sum)", "format": "Q+A, 4 choices",
                  "reproduced_dev": mmlu_val, "reproduced_test": mmlu_test,
                  "paper_dev": 14 + 29 + 22 + 11 + 31 + 16, "paper_test": 135 + 265 + 173 + 100 + 272 + 144})
    # LiveQA
    table.append({"dataset": "LiveQA TREC-2017", "format": "Q + long answer",
                  "reproduced_dev": n("liveqa", "train"),
                  "reproduced_test": n("liveqa", "test"),
                  "paper_dev": 634, "paper_test": 104,
                  "note": "train from community mirror (RA-20)"})
    # MedicationQA
    table.append({"dataset": "MedicationQA", "format": "Q + long answer",
                  "reproduced_dev": 0, "reproduced_test": n("medicationqa", "all"),
                  "paper_dev": None, "paper_test": 674,
                  "note": "released file has 690 rows; paper's 674 not reconstructable (RA-08)"})
    # HealthSearchQA
    table.append({"dataset": "HealthSearchQA", "format": "Q only + long answer",
                  "reproduced_dev": None, "reproduced_test": n("healthsearchqa", "all"),
                  "paper_dev": None, "paper_test": 3375,
                  "note": "released file has 3173 questions (RA-09)"})
    return table


# --------------------------------------------------------------------------- #
# Leakage / integrity checks (task 11 of the plan)
# --------------------------------------------------------------------------- #
def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def leakage_checks() -> list[dict]:
    checks: list[dict] = []

    def rows(ds):
        return _rows(paths.PROCESSED / f"{ds}.jsonl")

    # 1. no duplicate uids anywhere
    allr = _rows(paths.PROCESSED / "_all.jsonl")
    uids = [r["uid"] for r in allr]
    checks.append({"check": "unique uids", "status": "PASS" if len(uids) == len(set(uids)) else "FAIL",
                   "detail": f"{len(uids)} records, {len(set(uids))} unique"})

    # 2. MC exemplar-pool vs scored-split question overlap (train/test contamination).
    #    Uses NORMALISED text (whitespace + case) -- exact .strip() misses variant leakage.
    for ds, ex_split, ev_split in (("medqa_usmle_4opt", "train", "test"),
                                   ("medqa_usmle_4opt", "dev", "test"),
                                   ("medqa_usmle_5opt", "train", "test"),
                                   ("medqa_usmle_5opt", "dev", "test"),
                                   ("medmcqa", "train", "validation"),
                                   ("pubmedqa", "train", "test")):
        r = rows(ds)
        exq = {_norm(x["question"]) for x in r if x["split"] == ex_split}
        evq = {_norm(x["question"]) for x in r if x["split"] == ev_split}
        overlap = exq & evq
        checks.append({"check": f"{ds}: {ex_split} vs {ev_split} normalized question overlap",
                       "status": "PASS" if not overlap else "WARN",
                       "detail": f"{len(overlap)} shared normalized questions"})

    # 3. duplicate questions within each scored split (informational)
    for ds, split in (("medqa_usmle_4opt", "test"), ("medqa_usmle_5opt", "test"),
                      ("medmcqa", "validation"), ("pubmedqa", "test")):
        r = [x for x in rows(ds) if x["split"] == split]
        c = Counter(_norm(x["question"]) for x in r)
        dups = {q: k for q, k in c.items() if k > 1}
        checks.append({"check": f"{ds}/{split} duplicate questions",
                       "status": "PASS" if not dups else "INFO",
                       "detail": f"{len(dups)} normalized question strings appear >1x "
                                 f"(of {len(r)} rows)"})

    # 4. MMLU: gold letter always in A-D
    bad = 0
    for s in paths.MMLU_SUBJECTS:
        for x in rows(f"mmlu_{s}"):
            if x.get("gold") not in ("A", "B", "C", "D"):
                bad += 1
    checks.append({"check": "MMLU gold in A-D", "status": "PASS" if bad == 0 else "FAIL",
                   "detail": f"{bad} bad gold values"})

    # 5. PubMedQA: gold present for all test rows
    r = [x for x in rows("pubmedqa") if x["split"] == "test"]
    missing = sum(1 for x in r if x.get("gold") not in ("A", "B", "C"))
    checks.append({"check": "PubMedQA test gold present", "status": "PASS" if missing == 0 else "FAIL",
                   "detail": f"{missing}/{len(r)} missing"})

    # 6. MMLU: few-shot exemplar splits vs the scored test split (contamination)
    for s in paths.MMLU_SUBJECTS:
        r = rows(f"mmlu_{s}")
        test_q = {_norm(x["question"]) for x in r if x["split"] == "test"}
        for src in ("dev", "validation"):
            src_q = {_norm(x["question"]) for x in r if x["split"] == src}
            ov = src_q & test_q
            checks.append({"check": f"mmlu_{s}: {src} vs test question overlap",
                           "status": "PASS" if not ov else "WARN",
                           "detail": f"{len(ov)} shared normalized questions"})

    # 7. intra-dataset duplicate questions (Part 4 of the audit brief -- every dataset)
    for ds in ("healthsearchqa", "medicationqa", "liveqa", "medqa_usmle_4opt",
               "medqa_usmle_5opt", "medmcqa", "pubmedqa"):
        r = rows(ds)
        norms = [_norm(x["question"]) for x in r]
        n_dup = len(norms) - len(set(norms))
        checks.append({"check": f"{ds}: intra-dataset duplicate questions",
                       "status": "PASS" if n_dup == 0 else "INFO",
                       "detail": f"{n_dup} duplicate normalized question strings "
                                 f"across {len(norms)} records ({len(set(norms))} distinct)"})

    # 8. 140-question human-eval set disjoint from the 40 IPT exemplars (paper §4.5).
    #    Exemplars are the null PLACEHOLDER (B3) -> vacuously disjoint until RA-12 fills them;
    #    this check exists so it FAILS LOUDLY once real exemplars are added and overlap.
    he_p = paths.DERIVED / "human_eval_140.jsonl"
    ipt_p = paths.DERIVED / "ipt_exemplars.PLACEHOLDER.jsonl"
    if he_p.exists() and ipt_p.exists():
        he_q = {_norm(x["question"]) for x in _rows(he_p)}
        ipt_q = {_norm(x.get("question") or "") for x in _rows(ipt_p)} - {""}
        ov = he_q & ipt_q
        checks.append({"check": "human_eval_140 vs IPT exemplars disjoint (§4.5)",
                       "status": "PASS" if not ov else "FAIL",
                       "detail": f"{len(ov)} shared questions "
                                 f"({len(ipt_q)} non-null exemplars — 0 == placeholder, B3)"})

    return checks


def run(write_reports: bool = True) -> dict:
    counts = build_processed()
    table1 = regenerate_table1(counts)
    leak = leakage_checks()
    report = {"generated": utcnow(), "processed_counts": counts,
              "table1": table1, "leakage_checks": leak}
    if write_reports:
        (paths.DERIVED / "multimedqa").mkdir(parents=True, exist_ok=True)
        (paths.TABLES / "table1_reproduced.json").write_text(
            json.dumps(table1, indent=2), encoding="utf-8")
        _write_table1_md(table1)
        (paths.RESULTS / "phase04_integration_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def _matches(reproduced, paper, *, rounds: bool) -> bool:
    """Exact match, or -- when the paper explicitly rounds this figure -- within the
    rounding step implied by the paper's own precision (nearest 100 for 187K/6.1K)."""
    if reproduced is None or paper is None:
        return reproduced == paper
    if reproduced == paper:
        return True
    if not rounds:
        return False
    step = 10 ** (len(str(paper)) - len(str(paper).rstrip("0")))  # 187000 -> 1000, 6100 -> 100
    return abs(reproduced - paper) < max(step, 1)


def _write_table1_md(table1: list[dict]) -> None:
    lines = ["# Table 1 (reproduced) — MultiMedQA dataset sizes", "",
             "Match = `exact` (identical) · `~rounding` (paper rounds this figure; within its "
             "rounding step) · `test exact` · `see note` (documented deviation — RA-xx).", "",
             "| Dataset | Format | Reproduced dev | Reproduced test | Paper dev | Paper test | Match | Note |",
             "|---|---|---|---|---|---|---|---|"]
    for t in table1:
        rd, rt = t["reproduced_dev"], t["reproduced_test"]
        pd_, pt = t["paper_dev"], t["paper_test"]
        rounds = t.get("paper_rounds", False)
        dev_ok = _matches(rd, pd_, rounds=rounds)
        test_ok = _matches(rt, pt, rounds=rounds)
        if dev_ok and test_ok:
            match = "~rounding" if rounds else "exact"
        elif test_ok:
            match = "test exact"
        else:
            match = "see note"
        scored = t.get("scored_split")
        note = t.get("note", "")
        if scored:
            note = f"scored split: {scored['split']} (n={scored['n']}, {scored['basis']}). " + note
        lines.append(f"| {t['dataset']} | {t['format']} | {rd} | {rt} | {pd_} | {pt} | {match} | {note} |")
    (paths.TABLES / "table1_reproduced.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
