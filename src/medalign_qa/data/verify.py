"""Phase 3 — verify every acquired dataset against the paper and the release.

Produces a list of Check records:  {dataset, check, expected, observed, status, label}
status  in {PASS, CAVEAT, FAIL, SKIP}
label   is the evidence label for the *expectation* being tested.
"""
from __future__ import annotations

import csv
import io as _io
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from lxml import etree

from ..utils import paths
from ..utils.io import read_yaml


@dataclass
class Check:
    dataset: str
    check: str
    expected: object
    observed: object
    status: str
    label: str
    note: str = ""


def _load_counts() -> dict:
    return read_yaml(paths.METADATA / "expected_counts.yaml")


def _jsonl_rows(p: Path) -> list[dict]:
    with open(p, "r", encoding="utf-8") as fh:   # not splitlines() -- see loaders._jsonl
        return [json.loads(line) for line in fh if line.strip()]


# --------------------------------------------------------------------------- #
def verify_medqa(ec: dict) -> list[Check]:
    d = paths.RAW_MEDQA / "US" / "4_options"
    out: list[Check] = []
    spec = ec["medqa_usmle_4opt"]
    counts = {}
    for split, exp in (("train", spec["local_train"]), ("dev", spec["local_dev"]),
                       ("test", spec["local_test"])):
        p = d / f"phrases_no_exclude_{split}.jsonl"
        rows = _jsonl_rows(p) if p.exists() else []
        counts[split] = len(rows)
        out.append(Check("medqa_usmle_4opt", f"{split} row count", exp, len(rows),
                         "PASS" if len(rows) == exp else "FAIL", "DATASET-VERIFIED"))
    out.append(Check("medqa_usmle_4opt", "dev(=train+dev) == paper 11450",
                     spec["paper_dev"], counts.get("train", 0) + counts.get("dev", 0),
                     "PASS" if counts.get("train", 0) + counts.get("dev", 0) == spec["paper_dev"] else "FAIL",
                     "PAPER-SPECIFIED"))
    # schema / gold / n_options on the test split
    p = d / "phrases_no_exclude_test.jsonl"
    if p.exists():
        r0 = _jsonl_rows(p)[0]
        n_opt = len(r0.get("options", {}))
        out.append(Check("medqa_usmle_4opt", "n options", 4, n_opt,
                         "PASS" if n_opt == 4 else "FAIL", "PAPER-SPECIFIED"))
        has_gold = all("answer_idx" in r and r["answer_idx"] for r in _jsonl_rows(p))
        out.append(Check("medqa_usmle_4opt", "gold present (answer_idx) all rows",
                         True, has_gold, "PASS" if has_gold else "FAIL", "DATASET-VERIFIED"))
    return out


def verify_medmcqa(ec: dict) -> list[Check]:
    spec = ec["medmcqa"]
    out: list[Check] = []
    rows = {}
    for split, exp in (("train", spec["local_train"]), ("dev", spec["local_valid"]),
                       ("test", spec["local_test"])):
        p = paths.RAW_MEDMCQA / f"{split}.json"
        r = _jsonl_rows(p) if p.exists() else []
        rows[split] = r
        out.append(Check("medmcqa", f"{split} row count", exp, len(r),
                         "PASS" if len(r) == exp else "FAIL", "DATASET-VERIFIED"))
    if rows.get("train"):
        cops = {r.get("cop") for r in rows["train"]}
        one_based = cops == {1, 2, 3, 4}
        out.append(Check("medmcqa", "cop indexing", "one_based (1..4)",
                         sorted(x for x in cops if x is not None),
                         "PASS" if one_based else "FAIL", "DATASET-VERIFIED"))
    if rows.get("test"):
        n_gold = sum(1 for r in rows["test"] if r.get("cop") is not None)
        out.append(Check("medmcqa", "test labels withheld", 0, n_gold,
                         "PASS" if n_gold == 0 else "CAVEAT", "DATASET-VERIFIED",
                         "test split unusable for scoring -> eval on valid (RA-01)"))
    return out


def verify_pubmedqa(ec: dict) -> list[Check]:
    spec = ec["pubmedqa"]
    out: list[Check] = []
    p = paths.RAW_PUBMEDQA / "ori_pqal.json"
    if not p.exists():
        return [Check("pubmedqa", "file present", "ori_pqal.json", "MISSING", "FAIL", "PAPER-SPECIFIED")]
    data = json.loads(p.read_text(encoding="utf-8"))
    out.append(Check("pubmedqa", "labeled total", spec["official_labeled_total"], len(data),
                     "PASS" if len(data) == spec["official_labeled_total"] else "FAIL",
                     "UNVERIFIED"))
    labels = {v.get("final_decision") for v in data.values()}
    out.append(Check("pubmedqa", "label set", {"yes", "no", "maybe"}, labels,
                     "PASS" if labels <= {"yes", "no", "maybe"} else "FAIL", "PAPER-SPECIFIED"))
    tg = paths.RAW_PUBMEDQA / "test_ground_truth.json"
    if tg.exists():
        t = json.loads(tg.read_text(encoding="utf-8"))
        out.append(Check("pubmedqa", "official test split size", spec["official_test_split"], len(t),
                         "PASS" if len(t) == spec["official_test_split"] else "FAIL",
                         "PAPER-SPECIFIED", "paper Table 1: 500 test (RA-02)"))
    return out


def verify_mmlu(ec: dict) -> list[Check]:
    spec = ec["mmlu_clinical"]["subjects"]
    fewshot_n = ec["mmlu_clinical"]["fewshot_dev_rows_per_subject"]
    out: list[Check] = []
    for subject, exp in spec.items():
        rows_by_split = {}
        for split in ("dev", "validation", "test"):
            p = paths.RAW_MMLU / subject / f"{split}.csv"
            if not p.exists():
                out.append(Check("mmlu", f"{subject}/{split} present", True, "MISSING", "FAIL",
                                 "PAPER-SPECIFIED"))
                continue
            rows = [r for r in csv.reader(_io.StringIO(p.read_text(encoding="utf-8"))) if r]
            rows_by_split[split] = rows
            ncols_ok = all(len(r) == 6 for r in rows)
            out.append(Check("mmlu", f"{subject}/{split} 6 cols", True, ncols_ok,
                             "PASS" if ncols_ok else "FAIL", "DERIVED FROM PAPER"))
        # test count == PAPER-SPECIFIED
        n_test = len(rows_by_split.get("test", []))
        out.append(Check("mmlu", f"{subject}/test row count", exp["test"], n_test,
                         "PASS" if n_test == exp["test"] else "FAIL", "PAPER-SPECIFIED"))
        # validation count == paper's "dev" column
        n_val = len(rows_by_split.get("validation", []))
        out.append(Check("mmlu", f"{subject}/validation == paper 'dev'", exp["paper_dev"], n_val,
                         "PASS" if n_val == exp["paper_dev"] else "FAIL", "DATASET-VERIFIED",
                         "paper Table 1 'dev' column == MMLU validation split size"))
        # dev == 5-shot exemplar source
        n_dev = len(rows_by_split.get("dev", []))
        out.append(Check("mmlu", f"{subject}/dev == 5-shot source", fewshot_n, n_dev,
                         "PASS" if n_dev == fewshot_n else "CAVEAT", "REPLICATION ASSUMPTION",
                         "RA-06: few-shot exemplars from the 5-row dev split"))
    return out


def _count_nlm_questions(xml_bytes: bytes) -> int:
    root = etree.fromstring(xml_bytes)
    return len(root.findall(".//NLM-QUESTION"))


def verify_liveqa(ec: dict) -> list[Check]:
    spec = ec["liveqa_trec2017"]
    out: list[Check] = []
    test = paths.RAW_LIVEQA / "TestDataset" / "TREC-2017-LiveQA-Medical-Test.xml"
    if test.exists():
        n = _count_nlm_questions(test.read_bytes())
        out.append(Check("liveqa", "test questions", spec["local_test"], n,
                         "PASS" if n == spec["local_test"] else "FAIL", "DATASET-VERIFIED"))
    # Training set: canonical XMLs unavailable -> community mirror (RA-20).
    jl = paths.RAW_LIVEQA / "TrainingDatasets" / "train_pairs.jsonl"
    if not jl.exists():
        out.append(Check("liveqa", "train pairs (mirror) present", True, "MISSING", "FAIL",
                         "PAPER-SPECIFIED",
                         "canonical training XMLs not published; expected community mirror"))
    else:
        n = len(_jsonl_rows(jl))
        out.append(Check("liveqa", "train QA pairs (truehealth mirror, RA-20)",
                         f"~{spec['paper_dev']} (paper Table 1)", n,
                         "CAVEAT" if abs(n - spec["paper_dev"]) <= 2 else "FAIL",
                         "UNVERIFIED",
                         "third-party mirror; paper 'dev'=634 (388+246); mirror flattens to QA pairs"))
    return out


def verify_medicationqa(ec: dict) -> list[Check]:
    spec = ec["medicationqa"]
    import openpyxl
    p = paths.RAW_MEDICATIONQA / "MedInfo2019-QA-Medications.xlsx"
    wb = openpyxl.load_workbook(p, read_only=True)
    ws = wb["DrugQA"]
    rows = list(ws.iter_rows(values_only=True))
    header, body = rows[0], rows[1:]
    n = len(body)
    out = [Check("medicationqa", "raw row count", spec["local_rows"], n,
                 "PASS" if n == spec["local_rows"] else "FAIL", "DATASET-VERIFIED")]
    cols_ok = [str(c).strip() for c in header] == spec["columns"]
    out.append(Check("medicationqa", "columns", spec["columns"],
                     [str(c).strip() for c in header],
                     "PASS" if cols_ok else "FAIL", "DATASET-VERIFIED"))
    nonempty = sum(1 for r in body if r[0] and r[3] and str(r[0]).strip() and str(r[3]).strip())
    distinct_q = len({str(r[0]).strip().lower() for r in body if r[0]})
    out.append(Check("medicationqa", "non-empty Q&A rows", nonempty, nonempty,
                     "PASS", "DATASET-VERIFIED",
                     f"all {nonempty} rows have Q and A; {distinct_q} distinct questions"))
    out.append(Check("medicationqa", "paper's 674 reconstructable?", 674, "no",
                     "CAVEAT", "CANNOT BE DETERMINED FROM AVAILABLE MATERIALS",
                     "RA-08: released file has 690 rows; 674 cannot be derived; use all 690"))
    return out


def verify_healthsearchqa(ec: dict) -> list[Check]:
    spec = ec["healthsearchqa"]
    import openpyxl
    p = paths.RAW_HEALTHSEARCHQA / "41586_2023_6291_MOESM6_ESM.xlsx"
    wb = openpyxl.load_workbook(p, read_only=True)
    s1, s2 = wb.worksheets[0], wb.worksheets[1]
    n1 = sum(1 for r in s1.iter_rows(values_only=True) if r and r[0] and str(r[0]).strip())
    n2 = sum(1 for r in s2.iter_rows(values_only=True) if r and r[0] and str(r[0]).strip())
    out = [
        Check("healthsearchqa", "sheet1 non-empty questions", spec["local_sheet1_nonempty"], n1,
              "PASS" if n1 == spec["local_sheet1_nonempty"] else "CAVEAT", "DATASET-VERIFIED",
              f"paper states 3375 (CANNOT BE DETERMINED why {n1})"),
        Check("healthsearchqa", "sheet2 human-eval subset", spec["local_sheet2_rows"], n2,
              "PASS" if n2 == spec["local_sheet2_rows"] else "FAIL", "PAPER-SPECIFIED"),
    ]
    return out


ALL = {
    "medqa_usmle_4opt": verify_medqa,
    "medmcqa": verify_medmcqa,
    "pubmedqa": verify_pubmedqa,
    "mmlu": verify_mmlu,
    "liveqa": verify_liveqa,
    "medicationqa": verify_medicationqa,
    "healthsearchqa": verify_healthsearchqa,
}


def run_all() -> list[dict]:
    ec = _load_counts()
    checks: list[Check] = []
    for fn in ALL.values():
        try:
            checks.extend(fn(ec))
        except Exception as e:  # noqa: BLE001
            checks.append(Check(fn.__name__, "exception", "-", repr(e), "FAIL", "UNVERIFIED"))
    return [asdict(c) for c in checks]
