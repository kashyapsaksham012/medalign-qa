# MedAlign QA

A personal engineering project: a completed **benchmark reconstruction**, a from-scratch
**re-implementation of a multiple-choice evaluation pipeline**, an **experimental run** of
that pipeline on an open model, and a **reproducibility-validation** pass over the whole
thing.

I rebuilt a seven-dataset medical question-answering benchmark from its public sources,
implemented the evaluation methodology (few-shot, chain-of-thought, self-consistency, and
selective-prediction prompting) against a common inference runner, executed it end-to-end
on a frozen open model, and verified that the pipeline and its results are reproducible.

## What was built and run

**Benchmark reconstruction**
- Seven public datasets acquired, parsed to one unified record schema, and integrated:
  MedQA (USMLE, 4- and 5-option), MedMCQA, PubMedQA, MMLU (6 clinical subjects), LiveQA,
  MedicationQA, and a consumer health-question set.
- Dataset sizes and splits checked against reference counts: **56 checks pass, 2 caveats,
  0 failures**.
- Leakage checks (train/test overlap, exemplar/eval overlap, intra-dataset duplicates) — clean.

**Evaluation pipeline**
- Few-shot, chain-of-thought, self-consistency (11 sampled decodes + plurality vote), and
  selective prediction (41 decodes, uncertainty-based deferral), implemented against a
  single resumable inference runner.
- Prompt exemplar blocks transcribed verbatim from the reference tables; the MMLU few-shot
  source is one documented assumption.

**Experimental run**
- Executed end-to-end on **`Qwen/Qwen2.5-7B-Instruct`**, pinned to an exact Hugging Face
  commit revision, served locally with vLLM on a 2×T4 GPU.
- All multiple-choice datasets covered. Answer parse rate 99.8–100%.
- Run-to-run variance measured over 4 independent self-consistency runs: **0.035**.
- Selective-prediction deferral curve computed on the full 1,273-question MedQA test set.

**Reproducibility validation**
- All source input files SHA-256-verified against a recorded manifest.
- The data-assembly pipeline (phases 1–8) is byte-reproducible — re-running produces
  identical output hashes.
- Model frozen to an exact revision; global seed fixed; no unseeded RNG anywhere in the package.
- **96 automated tests pass.**

**Independent cross-check**
- A separate fresh inference run on the same pinned model reproduces the MedQA results:
  few-shot **byte-identical**, chain-of-thought within 0.2 pp (99.6% per-question
  agreement), self-consistency within 0.1 pp (99.1% majority-vote agreement) — consistent
  with the measured stochastic variance.
- Details: `docs/VALIDATION_REPORT.md`.

## Results snapshot

Open substitute model — every number is model-specific and is never compared 1:1 against
any other model.

| Dataset | n | few-shot | CoT | self-consistency |
|---|--:|--:|--:|--:|
| MedQA 4-opt | 1273 | 59.4 | 60.5 | 63.3 |
| MedQA 5-opt | 1273 | 53.6 | — | — |
| MedMCQA (val) | 4183 | 56.6 | 56.4 | 58.5 |
| PubMedQA (test) | 500 | 72.8 | 74.8 | 73.6 |
| MMLU ×6 (test) | 1089 | 65.9–82.6 | 70.4–86.0 | 71.1–86.1 |

Selective prediction (MedQA, 41 decodes): accuracy rises monotonically from 62.9% to 76.6%
as the 45% least-confident answers are deferred.

Full numbers, per-question confidence intervals, and an item-by-item completeness matrix:
`docs/REPLICATION_REPORT.md`.

## Scope boundaries

Parts of the reference methodology depend on assets that are not publicly available. These
are documented as explicit boundaries and are not attempted:

| Component | Boundary |
|---|---|
| Original large proprietary models | Never publicly released. A frozen open model is substituted; results are model-specific and never compared 1:1 against the originals. |
| Prompt-tuning / domain-alignment stage | Requires the unreleased frozen base weights and an unpublished exemplar set. |
| Human-rater evaluation of long-form answers | Requires a recruited panel of clinician and lay raters. The rating framework and bootstrap statistics are implemented; the ratings are not collected. |
| Model-scaling analysis | Requires ≥ 2 model sizes (single model run). |

Full list: `docs/blockers.md`.

## Layout

```
raw_data/        immutable canonical copies / extracts / downloads of every input dataset
processed_data/  schema-unified parse of each dataset (one record schema)
derived_data/    benchmark assembly, materialised prompts, model predictions
prompts/         few-shot & CoT exemplar blocks (verbatim from the reference tables;
                 MMLU few-shot is a documented assumption). The assembled prompt adds a
                 chat output-format wrapper for instruction-tuned models.
configs/         global.yaml — every constant, evidence-labelled
metadata/        dataset specs, expected counts, data provenance + SHA-256 manifest
src/medalign_qa/ the package (utils, data, preprocessing, inference, evaluation,
                 uncertainty, figures)
scripts/         phaseNN_*.py entrypoints + the pipeline driver
tests/           pytest suite (96 tests)
docs/            REPLICATION_REPORT.md (results + completeness), STATUS.md,
                 VALIDATION_REPORT.md, blockers.md (scope boundaries),
                 deviations.md (documented assumptions), reproducibility.md, RUNBOOK.md
results/ figures/ tables/ logs/   generated artifacts
```

## Setup

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
```

The data-harness stack runs on CPython 3.14.7. The GPU runtime (vLLM) uses its own
environment — see `requirements-pathb.txt` / `docs/pathb_runbook.md`.

## Run

```bash
python run.py --list
python run.py phase01                          # ... through phase08: benchmark reconstruction (no GPU)
python scripts/run_pathb_pipeline.py --all      # phases 9–20: model evaluation (GPU)
python run.py test                             # 96 tests
```

Phases run sequentially (1 → 20); each prints a plan, does its work, and writes a status
block. The pipeline is idempotent and resumable — completed splits are skipped, so it is
safe to kill and restart. `--mock` runs everything offline, isolated under `*/mock/`,
without touching real outputs.

## Evidence labelling

Every non-obvious statement in code and docs is tagged by its evidence class — specified
by the source, verified from the dataset, derived, an explicit assumption, unverified,
not applicable, or undeterminable — so an assumption is never silently treated as a fact.
See `docs/deviations.md`.
