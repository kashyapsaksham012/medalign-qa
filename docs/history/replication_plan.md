# Replication Plan — Med-PaLM / MultiMedQA

Paper: Singhal et al., *Large Language Models Encode Clinical Knowledge*,
arXiv:2212.13138v1 (2022) / *Nature* 620:172–180 (2023).

This is a **benchmark + prompting + light fine-tuning + human-evaluation** paper.
It has **no patient cohort, no EHR, no survival/regression modelling**. Sections of
the generic ML template that do not apply are marked NOT APPLICABLE below.

## What the paper does (faithful scope)
1. Assemble **MultiMedQA** = MedQA, MedMCQA, PubMedQA, MMLU(6 clinical subjects),
   LiveQA, MedicationQA + new **HealthSearchQA**.
2. Evaluate **PaLM** and **Flan-PaLM** (8B/62B/540B) on the MC subsets with
   **few-shot**, **chain-of-thought**, **self-consistency** prompting.
3. **Instruction prompt tuning** (soft prompt, len 100, 40 exemplars) → **Med-PaLM**.
4. **Human evaluation** (9 clinicians + 5 lay) of long-form answers to **140**
   consumer questions, 12 clinician + 2 lay axes, non-parametric bootstrap CIs.
5. **Selective prediction**: self-consistency vote count as an uncertainty proxy
   on MedQA.

## Feasibility
- PaLM / Flan-PaLM / Med-PaLM: **never released** → blockers B1, B2 (CRITICAL).
- Human raters: **not reproducible** → B4 (CRITICAL for §4.5).
- Faithfully replicable now: MultiMedQA assembly, the prompt harness, the IPT
  recipe (code), the human-eval instrument + bootstrap machinery.

## Phase list & feasibility

| Phase | Name | Feasible from public materials? | Paper section |
|---|---|---|---|
| 1 | Environment setup | YES | — |
| 2 | Dataset acquisition | YES (3 downloads) | §3.1 |
| 3 | Dataset verification | YES | §3.1, Table 1 |
| 4 | Data integration (unified schema, MultiMedQA, Table 1) | YES | §3.1.1 |
| 5 | Cohort construction (= 140-question set; IPT-exemplar slots) | YES (140); exemplars BLOCKED (B3) | §3.3.4, §4.5 |
| 6 | Preprocessing (prompt build, answer parse, SC plurality) | YES | §3.3.2 |
| 7 | Feature engineering (verbatim prompts; consumer prompts reconstructed) | YES / partial (B8) | §3.3.2, A.8–A.9 |
| 8 | Exploratory / data validation | YES | §3.1 |
| 9 | Baseline models (PaLM rows; Table 4 baseline column) | **BLOCKED B1** (cite-only for Table 4) | §4.1 |
| 10 | Primary models (Flan-PaLM) | **BLOCKED B1** | §4.1–4.4 |
| 11 | Hyperparameter / training replication (Med-PaLM IPT) | code YES; run **BLOCKED B1/B2/B3** | §3.3.3, A.1 |
| 12 | Evaluation (MC accuracy, variance, Tables 4–7, A.1) | harness YES; numbers BLOCKED | §4.1–4.4 |
| 13 | Calibration | **NOT APPLICABLE — not used by the paper** | — |
| 14 | Fairness / subgroup analysis (single binary bias axis + CI) | harness YES; run BLOCKED B4 | §4.5 |
| 15 | Uncertainty analysis (41-decode selective prediction, Fig 5) | logic YES; numbers BLOCKED B1 | §4.4 |
| 16 | Statistical analysis (bootstrap 100×, 95% percentile; MedQA variance) | YES (machinery) | §4.5, A.2 |
| 17 | Tables / figures | generators YES; content BLOCKED | §4 |
| 18 | Reproducibility validation | YES (for model-independent pipeline) | — |
| 19 | Paper-to-result comparison | partial (data counts only until a model exists) | §4 |
| 20 | Final documentation | YES | — |

## Data tiers
- `raw_data/`      immutable canonical copies / extracts / downloads
- `processed_data/` schema-unified parse of each dataset (one record schema)
- `derived_data/`  MultiMedQA assembly, prompts materialised, predictions, results

See `docs/blockers.md` and `docs/deviations.md` for the full registers.
