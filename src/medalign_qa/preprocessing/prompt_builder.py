"""Assemble the exact prompt text sent to a model.

The few-shot / CoT *exemplar blocks* are stored verbatim in prompts/ (transcribed
from the paper's Tables A.13-A.21). This module only appends the test question in
the same format and returns the full string.

PAPER-SPECIFIED (Section 3.3.2):
  - MedQA / MedMCQA / MMLU : 5-shot
  - PubMedQA               : 3-shot (context budget)
  - consumer datasets      : 5-shot (partial prompts, RA-14)
"""
from __future__ import annotations

from pathlib import Path

from ..utils import paths

PROMPT_DIR = paths.PROMPTS


def _load(kind: str, name: str) -> str:
    p = PROMPT_DIR / kind / f"{name}.txt"
    if not p.exists():
        raise FileNotFoundError(f"prompt file missing: {p}")
    return p.read_text(encoding="utf-8").rstrip() + "\n"


def _fmt_options(options: dict) -> str:
    return " ".join(f"({k}) {v}" for k, v in options.items())


# --------------------------------------------------------------------------- #
# Multiple choice
# --------------------------------------------------------------------------- #
def build_mc_fewshot(record: dict, dataset_key: str) -> str:
    """dataset_key in {medqa, medmcqa, pubmedqa, mmlu}."""
    header = _load("few_shot", dataset_key)
    q = record["question"]
    opts = _fmt_options(record["options"])
    if dataset_key == "pubmedqa":
        ctx = record.get("context", "")
        return (f"{header}\n"
                f"Answer the following question given the context (reply with one of the options): "
                f"Context: {ctx} Question: {q}\n{opts}\nAnswer:")
    return f"{header}\nQuestion: {q}\n{opts}\nAnswer:"


def build_mc_cot(record: dict, dataset_key: str) -> str:
    header = _load("cot", dataset_key)
    q = record["question"]
    opts = _fmt_options(record["options"])
    if dataset_key == "pubmedqa":
        ctx = record.get("context", "")
        return f"{header}\nContext: {ctx} Question: {q} {opts}\nExplanation:"
    return f"{header}\nQuestion: {q}\n{opts}\nExplanation:"


# --------------------------------------------------------------------------- #
# Long form (consumer) -- RA-14 (partial prompts)
# --------------------------------------------------------------------------- #
def build_longform_fewshot(record: dict, dataset_key: str) -> str:
    """dataset_key in {liveqa, medicationqa, healthsearchqa}."""
    header = _load("consumer", dataset_key)
    q = record["question"]
    return f"{header}\nQuestion: {q}\nComplete Answer:"


DATASET_KEY = {
    "medqa_usmle_4opt": "medqa",
    "medmcqa": "medmcqa",
    "pubmedqa": "pubmedqa",
    "liveqa": "liveqa",
    "medicationqa": "medicationqa",
    "healthsearchqa": "healthsearchqa",
    **{f"mmlu_{s}": "mmlu" for s in paths.MMLU_SUBJECTS},
}
