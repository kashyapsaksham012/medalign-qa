# MedAlign QA — replication of *Large Language Models Encode Clinical Knowledge*

Faithful-replication scaffold for **Med-PaLM / MultiMedQA**
(Singhal et al., arXiv:2212.13138v1, 2022 · *Nature* 620:172–180, 2023).

> **Replication status:** the paper's models (**PaLM / Flan-PaLM / Med-PaLM**) were
> never publicly released, and the human evaluation used a recruited clinician
> panel. A strict reproduction of the paper's numbers is therefore **not possible**
> from public materials. This repo faithfully reconstructs everything that *is*
> reproducible — the MultiMedQA benchmark, the prompting/self-consistency/selective-
> prediction harness, the instruction-prompt-tuning recipe, and the human-evaluation
> statistics machinery — and stops at the model boundary. See `docs/blockers.md`.

## Layout

```
project_healthcare_.pdf         the paper (input, read-only)
data.zip / data_clean.zip / *.xlsx / LiveQA_*.zip   user-provided datasets (read-only)
raw_data/        immutable canonical copies / extracts / downloads
processed_data/  schema-unified parse of each dataset
derived_data/    MultiMedQA assembly, materialised prompts, predictions, results
prompts/         few-shot & CoT prompts (verbatim from the paper where given)
configs/         global.yaml (every constant, evidence-labelled)
metadata/        dataset_specs.yaml, expected_counts.yaml, data_provenance.md
src/medalign_qa/ the package (utils, data, preprocessing, inference, training,
                 evaluation, fairness, uncertainty, figures)
scripts/         phaseNN_*.py entrypoints
tests/           pytest suite (per-phase validation)
docs/            replication_plan.md, blockers.md, deviations.md
results/ figures/ tables/ logs/   generated artifacts
```

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pip install -e .
```

Environment: CPython **3.14.7** (the only interpreter on the build machine — the
model-independent stack works on it; see `docs/deviations.md` RA-18′).

## Run

```bash
.venv/Scripts/python run.py --list
.venv/Scripts/python run.py phase01     # environment self-check
.venv/Scripts/python run.py test        # full pytest suite
```

Phases execute sequentially (1 → 20). Each `scripts/phaseNN_*.py` prints an
execution plan, does its work, and writes a status block.

## Evidence labelling

Every non-obvious statement in code/docs carries one of:
`PAPER-SPECIFIED` · `DATASET-VERIFIED` · `DERIVED FROM PAPER` ·
`NOT SPECIFIED IN PAPER` · `REPLICATION ASSUMPTION` · `UNVERIFIED` ·
`NOT APPLICABLE` · `CANNOT BE DETERMINED FROM AVAILABLE MATERIALS`.

Assumptions are never silently promoted to facts. See `docs/deviations.md`.
