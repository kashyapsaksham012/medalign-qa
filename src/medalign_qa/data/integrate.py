"""Phase 4 — parse every dataset to the unified schema, assemble MultiMedQA,
regenerate Table 1, and run leakage checks.
"""
from __future__ import annotations

import json
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
    # MedMCQA
    table.append({"dataset": "MedMCQA", "format": "Q+A, 4 choices",
                  "reproduced_dev": n("medmcqa", "train"),
                  "reproduced_test": n("medmcqa", "validation"),
                  "paper_dev": 187000, "paper_test": 6100,
                  "note": "paper 'test' 6.1K == withheld test; we evaluate the 4183 validation split (RA-01)"})
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
def leakage_checks() -> list[dict]:
    checks: list[dict] = []

    def rows(ds):
        return _rows(paths.PROCESSED / f"{ds}.jsonl")

    # 1. no duplicate uids anywhere
    allr = _rows(paths.PROCESSED / "_all.jsonl")
    uids = [r["uid"] for r in allr]
    checks.append({"check": "unique uids", "status": "PASS" if len(uids) == len(set(uids)) else "FAIL",
                   "detail": f"{len(uids)} records, {len(set(uids))} unique"})

    # 2. MC eval splits: exemplar/eval question overlap (would be contamination)
    for ds, ex_split, ev_split in (("medqa_usmle_4opt", "train", "test"),
                                   ("medqa_usmle_4opt", "dev", "test"),
                                   ("medmcqa", "train", "validation"),
                                   ("pubmedqa", "train", "test")):
        r = rows(ds)
        exq = {x["question"].strip() for x in r if x["split"] == ex_split}
        evq = {x["question"].strip() for x in r if x["split"] == ev_split}
        overlap = exq & evq
        checks.append({"check": f"{ds}: {ex_split} vs {ev_split} question overlap",
                       "status": "PASS" if not overlap else "WARN",
                       "detail": f"{len(overlap)} shared question strings"})

    # 3. duplicate questions within each eval split (informational)
    for ds, split in (("medqa_usmle_4opt", "test"), ("medmcqa", "validation"),
                      ("pubmedqa", "test")):
        r = [x for x in rows(ds) if x["split"] == split]
        c = Counter(x["question"].strip() for x in r)
        dups = {q: n for q, n in c.items() if n > 1}
        checks.append({"check": f"{ds}/{split} duplicate questions",
                       "status": "PASS" if not dups else "INFO",
                       "detail": f"{len(dups)} question strings appear >1x"})

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


def _write_table1_md(table1: list[dict]) -> None:
    lines = ["# Table 1 (reproduced) — MultiMedQA dataset sizes", "",
             "| Dataset | Format | Reproduced dev | Reproduced test | Paper dev | Paper test | Match | Note |",
             "|---|---|---|---|---|---|---|---|"]
    for t in table1:
        rd, rt = t["reproduced_dev"], t["reproduced_test"]
        pd_, pt = t["paper_dev"], t["paper_test"]
        match = "exact" if (rd == pd_ and rt == pt) else (
            "test exact" if rt == pt else "see note")
        lines.append(f"| {t['dataset']} | {t['format']} | {rd} | {rt} | {pd_} | {pt} | {match} | "
                     f"{t.get('note', '')} |")
    (paths.TABLES / "table1_reproduced.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
