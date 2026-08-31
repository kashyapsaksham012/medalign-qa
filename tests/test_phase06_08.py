"""Phases 6-8 validation."""
from __future__ import annotations

import json

import pytest

from medalign_qa.inference.self_consistency import plurality, uncertainty_score
from medalign_qa.preprocessing.answer_parser import parse_choice
from medalign_qa.utils import io, paths


# ---- Phase 6: parser ----
@pytest.mark.parametrize("text,valid,exp", [
    ("Answer: (C)", "ABCD", "C"),
    ("blah Answer:(A) blah", "ABCD", "A"),
    ("first (B) then Answer: (D)", "ABCD", "D"),
    ("Answer: (E)", "ABCD", None),
    ("", "ABCD", None),
])
def test_parse_choice(text, valid, exp):
    assert parse_choice(text, valid) == exp


def test_self_consistency_plurality_11():
    votes = ["A", "B", "A", "A", "C", "A", "B", "A", "A", "B", "A"]  # 11, plurality A=7
    win, meta = plurality(votes)
    assert win == "A" and meta["top_count"] == 7 and meta["n_total"] == 11
    _, frac = uncertainty_score(votes)
    assert abs(frac - 7 / 11) < 1e-9


def test_self_consistency_tiebreak_first_seen():
    assert plurality(["B", "A", "A", "B"])[0] == "B"  # tie 2-2, B seen first


# ---- Phase 7: prompts ----
REQUIRED_PROMPTS = [
    "few_shot/medqa.txt", "few_shot/medmcqa.txt", "few_shot/pubmedqa.txt", "few_shot/mmlu.txt",
    "cot/medqa.txt", "cot/medmcqa.txt", "cot/pubmedqa.txt", "cot/mmlu.txt",
    "consumer/liveqa.txt", "consumer/medicationqa.txt", "consumer/healthsearchqa.txt",
]


@pytest.mark.parametrize("rel", REQUIRED_PROMPTS)
def test_prompt_file_present_nonempty(rel):
    p = paths.PROMPTS / rel
    assert p.exists() and p.stat().st_size > 100


def test_verbatim_prompts_have_marker():
    for rel in ("few_shot/medqa.txt", "few_shot/pubmedqa.txt", "cot/medqa.txt", "cot/mmlu.txt"):
        head = (paths.PROMPTS / rel).read_text(encoding="utf-8")[:200]
        assert "VERBATIM" in head


def test_pubmedqa_fewshot_is_3_shot():
    txt = (paths.PROMPTS / "few_shot/pubmedqa.txt").read_text(encoding="utf-8")
    assert txt.count("Answer:(") == 3  # PAPER-SPECIFIED: 3-shot for PubMedQA


def test_prompt_builder_appends_question():
    from medalign_qa.preprocessing import prompt_builder as pb
    rec = next(r for r in io.read_jsonl(paths.PROCESSED / "medqa_usmle_4opt.jsonl")
               if r["split"] == "test")
    fs = pb.build_mc_fewshot(rec, "medqa")
    assert rec["question"][:40] in fs and fs.rstrip().endswith("Answer:")


# ---- Phase 8: EDA anomaly flags are the two KNOWN dataset properties ----
def test_eda_anomalies_are_expected_only():
    p = paths.RESULTS / "phase08_eda_report.json"
    if not p.exists():
        pytest.skip("run phase08")
    flags = json.loads(p.read_text())["anomaly_flags"]
    # Both are documented, real properties of the public datasets (not integration bugs).
    assert all(("pubmedqa" in f) or ("professional_medicine" in f) for f in flags), flags
