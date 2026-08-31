"""Phase 2 helpers — acquire raw datasets into an immutable raw_data/ tree.

Design rules:
  * Originals at repo root are opened READ-ONLY and never modified.
  * Everything written goes under raw_data/<dataset>/.
  * Every acquired file is hashed; provenance is appended to
    metadata/data_provenance.md and raw_data/ACQUISITION_MANIFEST.json.
"""
from __future__ import annotations

import csv
import json
import shutil
import time
import zipfile
from pathlib import Path

import requests

from ..utils import paths
from ..utils.io import sha256_file, utcnow

UA = {"User-Agent": "medalign-qa-replication/0.1 (academic replication)"}

# --------------------------------------------------------------------------- #
# Remote sources
# --------------------------------------------------------------------------- #
PUBMEDQA_FILES = {
    "ori_pqal.json":
        "https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/ori_pqal.json",
    "test_ground_truth.json":
        "https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/test_ground_truth.json",
}

# LiveQA training set.
# CANNOT BE DETERMINED FROM AVAILABLE MATERIALS at the canonical source: the repo
# github.com/abachaa/LiveQA_MedicalTask_TREC2017 contains ONLY the TestDataset
# (verified via the GitHub trees API 2026-08-31). The two training XMLs referenced
# in its Readme.txt are not hosted anywhere by the original authors.
# REPLICATION ASSUMPTION (RA-20): use the community mirror `truehealth/liveqa`
# (flattened QA-pair parquet). Provenance is third-party -> label UNVERIFIED.
LIVEQA_TRAIN_PARQUET = (
    "https://huggingface.co/datasets/truehealth/liveqa/resolve/main/"
    "data/train-00000-of-00001-04a338ea541d09e8.parquet"
)

# MMLU: canonical HF dataset `cais/mmlu`, per-subject parquet (dev + test).
MMLU_PARQUET = (
    "https://huggingface.co/datasets/cais/mmlu/resolve/main/"
    "{subject}/{split}-00000-of-00001.parquet"
)


# --------------------------------------------------------------------------- #
# Local extraction (faithful copies out of the user's archives)
# --------------------------------------------------------------------------- #
MEDQA_MEMBERS = [
    "data_clean/questions/US/4_options/phrases_no_exclude_train.jsonl",
    "data_clean/questions/US/4_options/phrases_no_exclude_dev.jsonl",
    "data_clean/questions/US/4_options/phrases_no_exclude_test.jsonl",
    "data_clean/questions/US/train.jsonl",
    "data_clean/questions/US/dev.jsonl",
    "data_clean/questions/US/test.jsonl",
]
MEDMCQA_MEMBERS = ["train.json", "dev.json", "test.json"]
LIVEQA_TEST_MEMBERS = [
    "LiveQA_MedicalTask_TREC2017-master/Readme.txt",
    "LiveQA_MedicalTask_TREC2017-master/TestDataset/TREC-2017-LiveQA-Medical-Test.xml",
    "LiveQA_MedicalTask_TREC2017-master/TestDataset/TREC-2017-LiveQA-Medical-Test-Questions-w-summaries.xml",
    "LiveQA_MedicalTask_TREC2017-master/TestDataset/TREC-2017-LiveQA-Medical-qrels-NIST-692.txt",
]


def _extract(zip_path: Path, member: str, dest: Path) -> dict:
    with zipfile.ZipFile(zip_path) as z:
        data = z.read(member)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"dest": str(dest.relative_to(paths.ROOT)), "bytes": len(dest.read_bytes()),
            "sha256": sha256_file(dest), "source": f"{zip_path.name}::{member}",
            "acquired": utcnow(), "method": "zip-extract"}


def _copy(src: Path, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return {"dest": str(dest.relative_to(paths.ROOT)), "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest), "source": src.name,
            "acquired": utcnow(), "method": "copy"}


def _download(url: str, dest: Path, timeout: int = 120) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            r.raise_for_status()
            dest.write_bytes(r.content)
            return {"dest": str(dest.relative_to(paths.ROOT)), "bytes": len(r.content),
                    "sha256": sha256_file(dest), "source": url,
                    "acquired": utcnow(), "method": "download",
                    "http_status": r.status_code}
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                return {"dest": str(dest.relative_to(paths.ROOT)), "source": url,
                        "acquired": utcnow(), "method": "download", "error": repr(e)}
            time.sleep(2 * (attempt + 1))
    return {}


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def acquire_local() -> list[dict]:
    man: list[dict] = []
    for m in MEDQA_MEMBERS:
        man.append(_extract(paths.ORIGINALS["medqa_zip"], m,
                            paths.RAW_MEDQA / Path(m).relative_to("data_clean/questions")))
    for m in MEDMCQA_MEMBERS:
        man.append(_extract(paths.ORIGINALS["medmcqa_zip"], m, paths.RAW_MEDMCQA / m))
    for m in LIVEQA_TEST_MEMBERS:
        man.append(_extract(paths.ORIGINALS["liveqa_zip"], m,
                            paths.RAW_LIVEQA / Path(m).name
                            if m.endswith("Readme.txt")
                            else paths.RAW_LIVEQA / "TestDataset" / Path(m).name))
    man.append(_copy(paths.ORIGINALS["medicationqa_xlsx"],
                     paths.RAW_MEDICATIONQA / "MedInfo2019-QA-Medications.xlsx"))
    man.append(_copy(paths.ORIGINALS["healthsearchqa_xlsx"],
                     paths.RAW_HEALTHSEARCHQA / "41586_2023_6291_MOESM6_ESM.xlsx"))
    return man


def acquire_pubmedqa() -> list[dict]:
    return [_download(url, paths.RAW_PUBMEDQA / name)
            for name, url in PUBMEDQA_FILES.items()]


def acquire_liveqa_train() -> list[dict]:
    """RA-20: community mirror (truehealth/liveqa) -> also written as original-style XML."""
    import pyarrow.parquet as pq

    dest_pq = paths.RAW_LIVEQA / "TrainingDatasets" / "train.parquet"
    rec = _download(LIVEQA_TRAIN_PARQUET, dest_pq, timeout=180)
    recs = [rec]
    if dest_pq.exists() and dest_pq.stat().st_size:
        rows = pq.read_table(dest_pq).to_pylist()
        # also emit a jsonl copy for convenience (raw-faithful: same values)
        dest_jsonl = paths.RAW_LIVEQA / "TrainingDatasets" / "train_pairs.jsonl"
        dest_jsonl.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
            encoding="utf-8")
        recs.append({"dest": str(dest_jsonl.relative_to(paths.ROOT)),
                     "bytes": dest_jsonl.stat().st_size, "sha256": sha256_file(dest_jsonl),
                     "source": "derived from train.parquet (truehealth/liveqa)",
                     "acquired": utcnow(), "method": "parquet->jsonl",
                     "n_rows": len(rows), "label": "UNVERIFIED (third-party mirror)"})
    return recs


def acquire_mmlu() -> list[dict]:
    """Canonical HF `cais/mmlu`, per-subject parquet -> headerless CSV (original MMLU shape)."""
    import pyarrow.parquet as pq

    # dev  = 5-shot exemplar source (RA-06)
    # test = scored split (Section 4.3)
    # validation = the split whose size the paper reports as "dev" in Table 1
    man: list[dict] = []
    for subject in paths.MMLU_SUBJECTS:
        for split in ("dev", "validation", "test"):
            pq_dest = paths.RAW_MMLU / subject / f"{split}.parquet"
            rec = _download(MMLU_PARQUET.format(subject=subject, split=split), pq_dest, timeout=120)
            man.append(rec)
            if not (pq_dest.exists() and pq_dest.stat().st_size):
                continue
            rows = pq.read_table(pq_dest).to_pylist()
            # original MMLU csv shape: question, A, B, C, D, answer_letter (headerless)
            csv_dest = paths.RAW_MMLU / subject / f"{split}.csv"
            with open(csv_dest, "w", encoding="utf-8", newline="") as fh:
                w = csv.writer(fh)
                for r in rows:
                    ch = r["choices"]
                    w.writerow([r["question"], ch[0], ch[1], ch[2], ch[3],
                                "ABCD"[int(r["answer"])]])
            man.append({"dest": str(csv_dest.relative_to(paths.ROOT)),
                        "bytes": csv_dest.stat().st_size, "sha256": sha256_file(csv_dest),
                        "source": f"cais/mmlu::{subject}/{split} (parquet->csv)",
                        "acquired": utcnow(), "method": "parquet->csv", "n_rows": len(rows),
                        "label": "DATASET-VERIFIED (canonical MMLU)"})
    return man


def write_manifest(records: list[dict]) -> Path:
    out = paths.RAW / "ACQUISITION_MANIFEST.json"
    out.write_text(json.dumps({"generated": utcnow(), "records": records},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    return out
