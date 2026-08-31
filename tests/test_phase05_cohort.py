"""Phase 5 validation."""
from __future__ import annotations

import json

import pytest

from medalign_qa.utils import io, paths


def _need(p):
    if not p.exists():
        pytest.skip(f"run phase05 first ({p})")


def test_human_eval_set_is_140():
    _need(paths.DERIVED / "human_eval_140.jsonl")
    rows = list(io.read_jsonl(paths.DERIVED / "human_eval_140.jsonl"))
    assert len(rows) == 140
    assert all(r["question"].strip() for r in rows)


def test_human_eval_questions_are_verbatim_from_sheet2():
    _need(paths.DERIVED / "human_eval_140.jsonl")
    import openpyxl
    wb = openpyxl.load_workbook(
        paths.RAW_HEALTHSEARCHQA / "41586_2023_6291_MOESM6_ESM.xlsx", read_only=True)
    sheet2 = {r[0].strip() for r in wb.worksheets[1].iter_rows(values_only=True) if r and r[0]}
    ours = {r["question"].strip() for r in io.read_jsonl(paths.DERIVED / "human_eval_140.jsonl")}
    assert ours == sheet2


def test_ipt_placeholder_present_and_blocked():
    p = paths.DERIVED / "ipt_exemplars.PLACEHOLDER.jsonl"
    _need(p)
    rows = list(io.read_jsonl(p))
    assert len(rows) == 40
    assert all(r["question"] is None and "PLACEHOLDER" in r["_status"] for r in rows)


def test_cohort_report_composition_documented():
    p = paths.RESULTS / "phase05_cohort_report.json"
    _need(p)
    rep = json.loads(p.read_text())
    he = rep["human_eval_140"]
    assert he["n"] == 140
    assert sum(he["reconstructed_composition"].values()) == 140
    # paper composition recorded regardless of exact match
    assert he["paper_composition"] == {"healthsearchqa": 100, "liveqa": 20, "medicationqa": 20}
