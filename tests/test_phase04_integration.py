"""Phase 4 validation (run after `python run.py phase04`)."""
from __future__ import annotations

import json

import pytest

from medalign_qa.utils import io, paths

PROC = paths.PROCESSED


def _need(p):
    if not p.exists():
        pytest.skip(f"run phase04 first ({p})")


def test_processed_files_exist():
    for ds in ("medqa_usmle_4opt", "medmcqa", "pubmedqa", "liveqa",
               "medicationqa", "healthsearchqa"):
        _need(PROC / f"{ds}.jsonl")
    for s in paths.MMLU_SUBJECTS:
        _need(PROC / f"mmlu_{s}.jsonl")


def test_uids_globally_unique():
    _need(PROC / "_all.jsonl")
    uids = [r["uid"] for r in io.read_jsonl(PROC / "_all.jsonl")]
    assert len(uids) == len(set(uids))


def test_table1_medqa_exact():
    _need(paths.TABLES / "table1_reproduced.json")
    t1 = {r["dataset"]: r for r in json.loads((paths.TABLES / "table1_reproduced.json").read_text())}
    m = t1["MedQA (USMLE, 4-opt)"]
    assert m["reproduced_dev"] == m["paper_dev"] == 11450
    assert m["reproduced_test"] == m["paper_test"] == 1273


def test_table1_pubmedqa_and_mmlu_exact():
    _need(paths.TABLES / "table1_reproduced.json")
    t1 = {r["dataset"]: r for r in json.loads((paths.TABLES / "table1_reproduced.json").read_text())}
    assert t1["PubMedQA"]["reproduced_dev"] == 500
    assert t1["PubMedQA"]["reproduced_test"] == 500
    mmlu = t1["MMLU (6 clinical subjects, sum)"]
    assert mmlu["reproduced_dev"] == mmlu["paper_dev"] == 123
    assert mmlu["reproduced_test"] == mmlu["paper_test"] == 1089


def test_medmcqa_gold_mapping_matches_raw_cop():
    _need(PROC / "medmcqa.jsonl")
    raw = {r["id"]: r for r in io.read_jsonl(paths.RAW_MEDMCQA / "dev.json")}
    proc = [r for r in io.read_jsonl(PROC / "medmcqa.jsonl") if r["split"] == "validation"]
    letters = "ABCD"
    checked = 0
    for r in proc[:500]:
        rid = r["meta"]["medmcqa_id"]
        cop = raw[rid]["cop"]
        assert r["gold"] == letters[cop - 1]   # 1-indexed cop -> letter
        checked += 1
    assert checked > 0


def test_pubmedqa_test_split_is_official_500():
    _need(PROC / "pubmedqa.jsonl")
    gt = json.loads((paths.RAW_PUBMEDQA / "test_ground_truth.json").read_text())
    proc = [r for r in io.read_jsonl(PROC / "pubmedqa.jsonl") if r["split"] == "test"]
    assert len(proc) == 500
    letter = {"yes": "A", "no": "B", "maybe": "C"}
    for r in proc:
        assert r["gold"] == letter[gt[r["meta"]["pmid"]]]


def test_no_exemplar_eval_contamination():
    _need(paths.RESULTS / "phase04_integration_report.json")
    rep = json.loads((paths.RESULTS / "phase04_integration_report.json").read_text())
    for c in rep["leakage_checks"]:
        if "overlap" in c["check"]:
            assert c["status"] == "PASS", c
