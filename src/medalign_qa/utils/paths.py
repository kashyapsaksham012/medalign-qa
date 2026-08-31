"""Canonical project paths. Single source of truth for every phase.

Layout (see README.md / docs/replication_plan.md):
    raw_data/        immutable canonical copies of every input dataset
    processed_data/  parsed, schema-unified copies (one record schema)
    derived_data/    benchmark assembly, eval sets, predictions, computed results
    results/ figures/ tables/ logs/   generated artifacts
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# --- User-provided originals (NEVER modified; referenced read-only) -------------
ORIGINALS = {
    "paper_pdf": ROOT / "project_healthcare_.pdf",
    "medmcqa_zip": ROOT / "data.zip",
    "medqa_zip": ROOT / "data_clean.zip",
    "liveqa_zip": ROOT / "LiveQA_MedicalTask_TREC2017-master.zip",
    "medicationqa_xlsx": ROOT / "MedInfo2019-QA-Medications.xlsx",
    "healthsearchqa_xlsx": ROOT / "41586_2023_6291_MOESM6_ESM.xlsx",
}

# --- Data trees ---------------------------------------------------------------
RAW = ROOT / "raw_data"
PROCESSED = ROOT / "processed_data"
DERIVED = ROOT / "derived_data"

RAW_MEDQA = RAW / "medqa"
RAW_MEDMCQA = RAW / "medmcqa"
RAW_PUBMEDQA = RAW / "pubmedqa"
RAW_MMLU = RAW / "mmlu"
RAW_LIVEQA = RAW / "liveqa"
RAW_MEDICATIONQA = RAW / "medicationqa"
RAW_HEALTHSEARCHQA = RAW / "healthsearchqa"

# --- Config / metadata / docs ------------------------------------------------
CONFIGS = ROOT / "configs"
METADATA = ROOT / "metadata"
PROMPTS = ROOT / "prompts"
DOCS = ROOT / "docs"

# --- Outputs ----------------------------------------------------------------
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
LOGS = ROOT / "logs"

# MMLU clinical subjects  ---  PAPER-SPECIFIED (Section 3.1, line ~340)
MMLU_SUBJECTS = (
    "anatomy",
    "clinical_knowledge",
    "college_medicine",
    "medical_genetics",
    "professional_medicine",
    "college_biology",
)


def ensure_dirs() -> None:
    """Create the data/output trees if missing (idempotent)."""
    for p in (
        RAW, PROCESSED, DERIVED, RESULTS, FIGURES, TABLES, LOGS,
        RAW_MEDQA, RAW_MEDMCQA, RAW_PUBMEDQA, RAW_MMLU, RAW_LIVEQA,
        RAW_MEDICATIONQA, RAW_HEALTHSEARCHQA,
    ):
        p.mkdir(parents=True, exist_ok=True)
