# MedAlign QA — replication of *Large Language Models Encode Clinical Knowledge*

Replication of the **MultiMedQA** multiple-choice methodology from
Singhal et al. (arXiv:2212.13138v1, 2022 · *Nature* 620:172–180, 2023), run on a
frozen open substitute model.

> **Status.** The paper's models (PaLM / Flan-PaLM / Med-PaLM) were never released,
> so its *numbers* cannot be reproduced. This repo reconstructs the benchmark and
> the full prompting harness (few-shot / CoT / self-consistency / selective
> prediction) and runs it end-to-end on **`Qwen/Qwen2.5-7B-Instruct`** (frozen HF
> revision, local vLLM). Of the paper's 7 qualitative MC findings, **5 are
> evaluated: 3 reproduce, 2 diverge**; the other 2 need a second model size.
> Instruction prompt tuning (Med-PaLM) and the human evaluation stay out of scope.
>
> **→ [`docs/REPLICATION_REPORT.md`](docs/REPLICATION_REPORT.md)** — results, verdicts, limitations.
> **→ [`docs/STATUS.md`](docs/STATUS.md)** — single source of truth. **[`docs/blockers.md`](docs/blockers.md)** — what's not reproducible and why.

## Layout

```
project_healthcare_.pdf         the paper (input, read-only)
data.zip / data_clean.zip / *.xlsx / LiveQA_*.zip   user-provided datasets (read-only)
raw_data/        immutable canonical copies / extracts / downloads
processed_data/  schema-unified parse of each dataset
derived_data/    MultiMedQA assembly, materialised prompts, predictions, results
prompts/         few-shot & CoT exemplar blocks (verbatim from paper Tables A.13-A.21
                 where given; MMLU few-shot = RA-06 assumption). The ASSEMBLED prompt
                 sent to a substitute model adds a chat output-format wrapper (RA-24).
configs/         global.yaml (every constant, evidence-labelled)
metadata/        dataset_specs.yaml, expected_counts.yaml, data_provenance.md
src/medalign_qa/ the package (utils, data, preprocessing, inference, training,
                 evaluation, fairness, uncertainty, figures)
scripts/         phaseNN_*.py entrypoints
tests/           pytest suite (per-phase validation)
docs/            REPLICATION_REPORT.md (results + verdicts), STATUS.md (source of
                 truth), OUTCOME.md, blockers.md, deviations.md, pathb_runbook.md,
                 reproducibility.md, history/ (superseded planning docs)
results/ figures/ tables/ logs/   generated artifacts
```

## Setup

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
```

Milestone-1 stack runs on CPython **3.14.7** (`docs/deviations.md` RA-18′). The GPU
runtime (vLLM) uses its own env — see `requirements-pathb.txt` / `docs/pathb_runbook.md`.

## Run

```bash
python run.py --list
python run.py phase01            # ... through phase08: data harness (no GPU)
python scripts/run_pathb_pipeline.py --all    # phases 9–20: substitute-model eval (GPU)
python run.py test              # full pytest suite (96 tests)
```

Phases execute sequentially (1 → 20); each `scripts/phaseNN_*.py` prints a plan,
does its work, and writes a status block. `docs/RUNBOOK.md` has the phase-by-phase
form. `--mock` runs the whole pipeline offline, isolated under `*/mock/`.

## Evidence labelling

Every non-obvious statement in code/docs carries one of:
`PAPER-SPECIFIED` · `DATASET-VERIFIED` · `DERIVED FROM PAPER` ·
`NOT SPECIFIED IN PAPER` · `REPLICATION ASSUMPTION` · `UNVERIFIED` ·
`NOT APPLICABLE` · `CANNOT BE DETERMINED FROM AVAILABLE MATERIALS`.

Assumptions are never silently promoted to facts. See `docs/deviations.md`.
