# Project Status — what is done, what is left

Paper: **"Large Language Models Encode Clinical Knowledge"** (Med-PaLM / MultiMedQA),
arXiv:2212.13138v1 / *Nature* 620:172–180 (2023).
Report generated 2026-08-31 after Phase 8.

---

## 1. One-line status

Phases **1–8 are COMPLETE and verified** (81 automated tests pass, all 6 input
datasets present + 3 downloaded, MultiMedQA rebuilt, Table 1 reproduced, 140-question
eval set materialised, verbatim prompt harness in place). Execution is **STOPPED at
Phase 9** on a CRITICAL blocker: the paper's models (PaLM / Flan-PaLM / Med-PaLM) were
never released. A **decision from you (Path A / B / C)** is required to continue.

---

## 2. What is DONE (Phases 1–8)

| Phase | Deliverable | Evidence |
|---|---|---|
| 1 Environment | `.venv` (CPython 3.14.7), pinned `requirements.txt` + lock, package skeleton, `configs/global.yaml` (every constant, evidence-labelled), `docs/{blockers,deviations,replication_plan}.md`, task runner `run.py` | `run.py phase01` PASS; 17 env tests |
| 2 Acquisition | `raw_data/` = 7 datasets. Local extracts (MedQA, MedMCQA, MedicationQA, HealthSearchQA, LiveQA-test) byte-faithful; downloads (PubMedQA `pqa_labeled`, MMLU ×6 subjects dev/val/test, LiveQA-train mirror). `ACQUISITION_MANIFEST.json` + SHA-256 in `data_provenance.md` | `run.py phase02` PASS (55 files, 0 errors) |
| 3 Verification | Every dataset checked vs paper Table 1 + public release | `results/phase03_verification_report.md` — 56 PASS / 2 CAVEAT / **0 FAIL** |
| 4 Integration | `processed_data/*.jsonl` (13 files, one unified `Record` schema, 212,722 records); `tables/table1_reproduced.md`; leakage checks | MedQA 11450/1273, PubMedQA 500/500, MMLU 123/1089 **EXACT**; uids unique; 0 exemplar↔eval overlap |
| 5 Cohort | `derived_data/human_eval_140.jsonl` (140 Q verbatim from xlsx sheet 2); `ipt_exemplars.PLACEHOLDER.jsonl` (40 empty slots) | test asserts exact set-equality with released sheet |
| 6 Preprocessing | `answer_parser.py` (RA-05), `prompt_builder.py`, `self_consistency.py` (11-vote plurality, first-seen tie-break) | 8/8 parser fixtures; plurality unit-tested |
| 7 Prompts | 9 prompt files. MC few-shot/CoT = **verbatim** from PDF Tables A.13–A.21; MMLU few-shot RA-06; consumer prompts RA-14 | `run.py phase07` PASS; PubMedQA = 3-shot asserted |
| 8 EDA | `results/phase08_eda_report.json`, `figures/phase08_gold_letter_balance.png` | 2 anomaly flags, both confirmed genuine dataset properties (PubMedQA yes-skew; MMLU prof-med position skew) |

### Datasets — final classification

| Dataset | Status | Note |
|---|---|---|
| MedQA (USMLE 4-opt) | `DATASET-VERIFIED` | 10178+1272=11450 dev / 1273 test — exact |
| MedMCQA | `DATASET-VERIFIED` | 182822 / 4183 valid / 6150 test; `cop` **1-indexed**; eval on valid (RA-01) |
| PubMedQA | `DATASET-VERIFIED` | `pqa_labeled` 1000; official 500-item test split (RA-02) |
| MMLU (6 subjects) | `DATASET-VERIFIED` | test 1089 exact; paper "dev" = **validation** split (123); 5-shot from `dev` (RA-06) |
| MedicationQA | `DATASET-VERIFIED` (caveat) | 690 rows; paper's 674 not reconstructable (RA-08) |
| HealthSearchQA | `DATASET-VERIFIED` (caveat) | 3173 released vs 3375 stated (RA-09) |
| LiveQA test | `DATASET-VERIFIED` | 104 questions |
| LiveQA train | `UNVERIFIED` | canonical XMLs unavailable; community mirror `truehealth/liveqa`, 635 pairs (RA-20) |

---

## 3. Codebase inventory

```
DONE / populated:
  src/medalign_qa/utils/         paths, seeding, io, logging_utils
  src/medalign_qa/data/          acquire, verify, schema, loaders, integrate, cohort, eda
  src/medalign_qa/preprocessing/ answer_parser, prompt_builder
  src/medalign_qa/inference/     self_consistency            (plurality + uncertainty score)
  scripts/                       phase01..phase08
  tests/                         5 files, 81 tests
  prompts/                       9 files
  configs/global.yaml, metadata/*, docs/*

STUB (only __init__.py — to be written in Phases 9-17):
  src/medalign_qa/inference/     few_shot.py, cot.py, selective_prediction.py runners, model backend
  src/medalign_qa/training/      instruction_prompt_tuning.py, soft_prompt.py, select_checkpoint.py
  src/medalign_qa/evaluation/    mc_accuracy.py, human_eval_harness.py, human_eval_stats.py, variance.py
  src/medalign_qa/fairness/      bias_axis.py
  src/medalign_qa/uncertainty/   selective_prediction.py
  src/medalign_qa/figures/       fig3..fig11, scaling
  src/medalign_qa/models/        (dir not yet created) base.py, mock_backend.py, <substitute>_backend.py
```

---

## 4. What is LEFT — phase by phase

Legend: 🟢 buildable now (no model) · 🟠 code now / run BLOCKED · 🔴 fully BLOCKED · ⚪ N/A

### Phase 9 — Baseline Models 🔴 (partly 🟢)
- 🟢 Table 4 **baseline column** = published numbers for DRAGON, PubMedGPT, BioLinkBERT,
  Galactica, PubMedBERT, GPT-Neo (RA-15 — this is what the authors did: cite, don't re-run).
- 🔴 PaLM 8B/62B/540B rows of Table 5 — need B1.

### Phase 10 — Primary Models (Flan-PaLM) 🔴
- 🟠 Write `models/base.py` (abstract `generate()`), `models/mock_backend.py`, `inference/few_shot.py`,
  `inference/cot.py`, `inference/run.py` — all unit-testable against the mock.
- 🔴 Any real accuracy number (Tables 4–7, Figs 3–4, A.1) — need B1.

### Phase 11 — Instruction Prompt Tuning → Med-PaLM 🔴
- 🟠 Write `training/soft_prompt.py` + `training/instruction_prompt_tuning.py` implementing A.1
  exactly (soft prompt len 100, U(−0.5,0.5), AdamW, grid LR{1e-3,3e-3,1e-2}×WD{1e-3,1e-5},
  batch 32, 200 steps) against the abstract backend.
- 🔴 Run — needs B1 (base model) + B2 + **B3 (the 40 exemplars — still PLACEHOLDER)** +
  B4 (clinician checkpoint ranking → RA-11 proxy).

### Phase 12 — Evaluation 🟠
- 🟢 `evaluation/mc_accuracy.py`, `evaluation/variance.py` (4× MedQA repeat, compare to A.2's 0.078),
  Table 4–7 / A.1 generators — buildable + testable on the mock now.
- 🔴 Populated tables — need B1.

### Phase 13 — Calibration ⚪
- `NOT APPLICABLE — NOT USED BY THE PAPER`. No reliability diagram / ECE / Brier / calibration
  slope anywhere in the paper. **Nothing to do.** (Do not add calibration metrics.)

### Phase 14 — Fairness / Subgroup Analysis 🔴
- 🟢 `fairness/bias_axis.py` — aggregate the **single binary "possibility of bias" clinician
  rating** + bootstrap CI → Table A.10 shape. Buildable now (empty ratings).
- 🔴 Real numbers — need B4 (raters) + B2 (Med-PaLM/Flan-PaLM answers).
- Note: the paper does **no** quantitative subgroup-performance / equalized-odds analysis;
  do not substitute one (that would change the methodology — §27 "optional improvements" only).

### Phase 15 — Uncertainty Analysis 🟠
- 🟢 `uncertainty/selective_prediction.py` — 41-decode self-consistency-count deferral curve on
  MedQA (Fig 5 logic). Testable on a stochastic mock (curve non-decreasing; d=0 == full accuracy).
- 🔴 The actual curve / 82.5%@0.45 endpoint — need B1.

### Phase 16 — Statistical Analysis 🟢 (machinery) / 🔴 (inputs)
- 🟢 `evaluation/human_eval_stats.py` — non-parametric bootstrap, 100 replicas, 95th-percentile
  interval (RA-13: resample the 140 questions). Testable against analytic normal approx.
- 🟢 `evaluation/variance.py` — MedQA repeated-eval variance.
- 🔴 Applied to real ratings / model outputs — B1, B4.

### Phase 17 — Tables / Figures 🟠
- 🟢 All generators (`figures/fig3..fig11`, `figures/scaling`, table writers) — buildable, will
  emit correctly-shaped, correctly-labelled outputs with cells **empty until a model/ratings exist**.
- 🔴 Filled figures/tables — B1, B2, B4.

### Phase 18 — Reproducibility Validation 🟢
- Not started. `make reproduce` equivalent: `run.py` full chain on a clean checkout must
  reproduce `processed_data/` + `tables/table1_reproduced.*` byte-identically (twice).
- Seed audit script; env-lock verification; provenance-hash re-check.
- **Fully doable now** for the model-independent pipeline (Phases 1–8).

### Phase 19 — Paper-to-Result Comparison 🟠
- 🟢 `results/comparison.md` for what IS comparable **today**: dataset counts, cohort composition,
  Table 1, PubMedQA label balance, prompt-shot counts — all against `configs/global.yaml`
  tolerances (RA-17).
- 🔴 Accuracy / human-eval / selective-prediction comparison — need B1/B2/B4.

### Phase 20 — Final Documentation 🟢
- Not started. README run-book, `docs/model_card.md` (Table A.2 template), consolidate
  `docs/deviations.md` (RA-01…RA-23) + `docs/blockers.md`, limitations, "what was and was not
  reproduced" statement.
- **Doable now.**

---

## 5. Blockers still open

| ID | Severity | State | Blocks | Needs from you |
|---|---|---|---|---|
| **B1** PaLM/Flan-PaLM | CRITICAL | OPEN | 9,10,12,15,17 (numbers) | Path A / B / C decision |
| **B2** Med-PaLM | CRITICAL | OPEN | 11,14 | same |
| **B3** 40 IPT exemplars | HIGH | OPEN (PLACEHOLDER) | 11 (faithful) | authorise RA-12 reconstruction, or supply |
| **B4** human raters + ratings | CRITICAL for §4.5 | OPEN | 14,16 (§4.5 parts) | recruit / authorise LLM-judge proxy / accept BLOCKED |
| **B8** consumer prompts incomplete | MEDIUM | OPEN | §4.5 long-form fidelity | authorise RA-14 (already partially done) |
| B5,B6,B7,B9,B10,B11,B12,B13,B14 | — | MITIGATED | — | none (documented RA-01..RA-23) |

## 6. Decision still pending (from end of Phase 8)

- **Path A** — stop at the model boundary; deliver benchmark + harness + recipe; report Phases
  9–17 numbers as `BLOCKED`; do Phases 18–20. *(recommended for a defensible academic replication)*
- **Path B** — add a substitute open model through the identical harness, every number tagged
  `REPLICATION ASSUMPTION — SUBSTITUTE MODEL`. Needs: model choice + local-GPU-or-API, plus
  B3 and B4 sub-decisions.
- **Path C** — you provide model/API access.

## 7. If you choose Path A, remaining work (all model-independent)

1. `models/{base,mock_backend}.py` + `inference/{few_shot,cot,run}.py` (harness, mock-tested)
2. `inference`/`uncertainty` selective-prediction runner (mock-tested)
3. `training/instruction_prompt_tuning.py` (recipe code, mock-tested, fails loudly on PLACEHOLDER exemplars)
4. `evaluation/{mc_accuracy,variance,human_eval_stats}.py` + `fairness/bias_axis.py` (mock/analytic-tested)
5. `figures/*` generators (emit shells)
6. Table 4 baseline column from citations
7. Phase 18 reproducibility harness + seed audit
8. Phase 19 `comparison.md` (counts/Table-1/prompt-shots only)
9. Phase 20 README run-book + model card + limitations + "not reproduced" statement
