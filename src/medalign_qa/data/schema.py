"""Unified record schema for every MultiMedQA dataset.

One dataclass covers both multiple-choice and long-form items. Fields that do not
apply to a given dataset are left as None / empty — never invented.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Record:
    uid: str                       # "<dataset>/<split>/<local_id>"
    dataset: str                   # medqa_usmle_4opt | medmcqa | pubmedqa | mmlu_<subj> | liveqa | medicationqa | healthsearchqa
    split: str                     # train | dev | validation | test | all
    task: str                      # "mc" | "longform"
    question: str
    options: Optional[dict] = None      # {"A": "...", ...}  (mc only)
    context: Optional[str] = None       # PubMedQA abstract (closed-domain)
    gold: Optional[str] = None          # mc: option letter ; longform: reference answer text (if any)
    gold_source: Optional[str] = None   # provenance of `gold`
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None or k in ("options", "context", "gold")}


MC_DATASETS = ("medqa_usmle_4opt", "medqa_usmle_5opt", "medmcqa", "pubmedqa",
               "mmlu_anatomy", "mmlu_clinical_knowledge", "mmlu_college_medicine",
               "mmlu_medical_genetics", "mmlu_professional_medicine", "mmlu_college_biology")
LONGFORM_DATASETS = ("liveqa", "medicationqa", "healthsearchqa")
