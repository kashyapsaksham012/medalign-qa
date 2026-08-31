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


# RA-24: system-message output-format instructions for chat-tuned substitute models.
# The paper's models continued a completion-style prompt directly; a chat model needs
# to be told to emit only the answer. The verbatim exemplar blocks are unchanged.
SYSTEM_MC_FEWSHOT = (
    "You are answering multiple-choice medical exam questions. "
    "Reply with ONLY the letter of the correct option, in the exact format: Answer: (X)"
)
SYSTEM_MC_COT = (
    "You are answering multiple-choice medical exam questions. Solve each in a "
    "step-by-step fashion, then end your response with the final answer on its own "
    "line in the exact format: Answer: (X)"
)
SYSTEM_LONGFORM = (
    "You are a helpful medical knowledge assistant. Provide a useful, complete, and "
    "scientifically grounded answer to the question."
)


def system_for(strategy: str) -> str:
    return {"few_shot": SYSTEM_MC_FEWSHOT, "cot": SYSTEM_MC_COT,
            "longform": SYSTEM_LONGFORM}[strategy]


def _load(kind: str, name: str) -> str:
    p = PROMPT_DIR / kind / f"{name}.txt"
    if not p.exists():
        raise FileNotFoundError(f"prompt file missing: {p}")
    raw = p.read_text(encoding="utf-8").splitlines()
    # strip the provenance header: leading '#' lines up to and including a '# ---'
    # sentinel (or just the leading run of '#' lines if no sentinel).
    body_start = 0
    for i, line in enumerate(raw):
        if line.strip() == "# ---":
            body_start = i + 1
            break
        if not line.lstrip().startswith("#") and line.strip():
            body_start = i
            break
    return "\n".join(raw[body_start:]).strip() + "\n"


def _fmt_options(options: dict) -> str:
    return " ".join(f"({k}) {v}" for k, v in options.items())


# --------------------------------------------------------------------------- #
# Multiple choice
# --------------------------------------------------------------------------- #
def _mmlu_fewshot_header(subject: str) -> str:
    """RA-06: 5-shot MMLU prompt = that subject's own 5 `dev` rows, standard format."""
    import csv as _csv
    import io as _sio
    p = paths.RAW_MMLU / subject / "dev.csv"
    rows = [r for r in _csv.reader(_sio.StringIO(p.read_text(encoding="utf-8"))) if r]
    body = ["The following are multiple choice questions (with answers) about "
            f"{subject.replace('_', ' ')}."]
    for q, a, b, c, d, ans in rows:
        body.append(f"\nQuestion: {q}\n(A) {a} (B) {b} (C) {c} (D) {d}\nAnswer:({ans.strip()})")
    return "".join(body[:1]) + "".join(body[1:]) + "\n"


def build_mc_fewshot(record: dict, dataset_key: str) -> str:
    """dataset_key in {medqa, medmcqa, pubmedqa, mmlu}."""
    if dataset_key == "mmlu":
        subject = record.get("meta", {}).get("mmlu_subject") or record["dataset"].removeprefix("mmlu_")
        header = _mmlu_fewshot_header(subject)
    else:
        header = _load("few_shot", dataset_key)
    q = record["question"]
    opts = _fmt_options(record["options"])
    tail = "\nRespond with only the letter of the correct answer.\nAnswer:"
    if dataset_key == "pubmedqa":
        ctx = record.get("context", "")
        return (f"{header}\n"
                f"Answer the following question given the context (reply with one of the options): "
                f"Context: {ctx} Question: {q}\n{opts}{tail}")
    return f"{header}\nQuestion: {q}\n{opts}{tail}"


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
    "medqa_usmle_5opt": "medqa",
    "medmcqa": "medmcqa",
    "pubmedqa": "pubmedqa",
    "liveqa": "liveqa",
    "medicationqa": "medicationqa",
    "healthsearchqa": "healthsearchqa",
    **{f"mmlu_{s}": "mmlu" for s in paths.MMLU_SUBJECTS},
}
