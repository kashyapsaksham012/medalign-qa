"""Phase 2 & 3 validation tests (run after `python run.py phase02 && phase03`)."""
from __future__ import annotations

import json

import pytest

from medalign_qa.utils import paths

RAW_EXPECTED = [
    paths.RAW_MEDQA / "US" / "4_options" / "phrases_no_exclude_test.jsonl",
    paths.RAW_MEDMCQA / "dev.json",
    paths.RAW_PUBMEDQA / "ori_pqal.json",
    paths.RAW_PUBMEDQA / "test_ground_truth.json",
    paths.RAW_LIVEQA / "TestDataset" / "TREC-2017-LiveQA-Medical-Test.xml",
    paths.RAW_LIVEQA / "TrainingDatasets" / "train_pairs.jsonl",
    paths.RAW_MEDICATIONQA / "MedInfo2019-QA-Medications.xlsx",
    paths.RAW_HEALTHSEARCHQA / "41586_2023_6291_MOESM6_ESM.xlsx",
]
RAW_EXPECTED += [paths.RAW_MMLU / s / f"{sp}.csv"
                 for s in paths.MMLU_SUBJECTS for sp in ("dev", "validation", "test")]


@pytest.mark.parametrize("p", RAW_EXPECTED, ids=lambda p: str(p.relative_to(paths.ROOT)))
def test_raw_file_present_nonempty(p):
    if not p.exists():
        pytest.skip(f"not acquired yet: {p} (run `python run.py phase02`)")
    assert p.stat().st_size > 0


def test_acquisition_manifest_has_no_errors():
    man = paths.RAW / "ACQUISITION_MANIFEST.json"
    if not man.exists():
        pytest.skip("run phase02 first")
    recs = json.loads(man.read_text())["records"]
    errs = [r for r in recs if "error" in r]
    assert not errs, errs


def test_originals_untouched():
    """SHA-256 of every original must match the value recorded at session start."""
    from medalign_qa.utils.io import sha256_file
    expected = {
        "project_healthcare_.pdf": "e83a6fecf5820a49b2b1c716f4c1839a7301300a6e27aa53c3cb7212b7db9f4e",
        "data.zip": "16c1fbc6f47d548d2af7837b18e893aa45f45c0be9bda0a9adfff3c625bf9262",
        "data_clean.zip": "1c2ca8130b3d86d9a99a432ab9bef14f3bb9807bef20facd9ac86ba36960f629",
        "LiveQA_MedicalTask_TREC2017-master.zip": "ea56456197b5714f7c2af67410c7fa881cab5b1b459f300abe5c92d1b72379ae",
        "MedInfo2019-QA-Medications.xlsx": "4f13d0e3b195bd6a5d72a1872f9118cb5f69fd02c370001695330cfc9e3b5832",
        "41586_2023_6291_MOESM6_ESM.xlsx": "a89f6639ee76717e2a1ea25bbe25c8c69cf396681be76fd8145da7e9c8917e1e",
    }
    for name, want in expected.items():
        assert sha256_file(paths.ROOT / name) == want, f"ORIGINAL MODIFIED: {name}"


def test_verification_report_no_failures():
    rep = paths.RESULTS / "phase03_verification_report.json"
    if not rep.exists():
        pytest.skip("run phase03 first")
    data = json.loads(rep.read_text())
    assert data["summary"].get("FAIL", 0) == 0, [
        c for c in data["checks"] if c["status"] == "FAIL"
    ]


def test_medmcqa_cop_one_based():
    rows = [json.loads(x) for x in
            (paths.RAW_MEDMCQA / "dev.json").read_text(encoding="utf-8").splitlines() if x.strip()]
    assert {r["cop"] for r in rows} == {1, 2, 3, 4}


def test_pubmedqa_labels():
    data = json.loads((paths.RAW_PUBMEDQA / "ori_pqal.json").read_text(encoding="utf-8"))
    assert len(data) == 1000
    assert {v["final_decision"] for v in data.values()} <= {"yes", "no", "maybe"}
