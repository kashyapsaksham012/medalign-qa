# Deep analysis of `project_healthcare_.pdf` + exact remaining phases

Paper: **Singhal et al., "Large Language Models Encode Clinical Knowledge"**,
arXiv:2212.13138v1 (26 Dec 2022) / *Nature* 620:172–180 (2023). "Med-PaLM / MultiMedQA".

Scope chosen: **Path B, multiple-choice only** — reproduce the MultiMedQA benchmark
and the Flan-PaLM MC evaluation *methodology* on one (ideally 2–3) open model(s).
Instruction-prompt-tuning (Med-PaLM) and the human evaluation are permanently out
of scope (unreleased models / clinical rater panel).

---

# PART 1 — DEEP ANALYSIS OF THE PAPER

## 1.1 What the paper is

An **LLM benchmark + evaluation-methodology paper**. Not a clinical prediction model:
no patient cohort, no EHR, no regression/survival analysis, no train/test split of
patient data. Three contributions:

1. **MultiMedQA** — a medical-QA benchmark: 6 existing datasets + 1 new (HealthSearchQA).
2. **Evaluation of PaLM / Flan-PaLM** (8B, 62B, 540B) on the multiple-choice subsets,
   using **few-shot**, **chain-of-thought (CoT)**, **self-consistency (SC)** prompting,
   plus a **selective-prediction / uncertainty** probe.
3. **Med-PaLM** — Flan-PaLM 540B + **instruction prompt tuning** (a 100-token soft
   prompt, 40 clinician exemplars) — plus a **pilot human-evaluation framework**
   (9 clinicians + 5 lay raters, 12 + 2 rating axes, bootstrap CIs).

## 1.2 The complete replication-target list

### A. Multiple-choice results — **IN SCOPE for Path B** (values will differ; qualitative findings are the target)

| # | Claim / artifact | Exact value(s) | Paper location | Model in paper |
|---|---|---|---|---|
| T4 | **Table 4** — MedQA (USMLE, 4-opt) leaderboard | Flan-PaLM 540B **67.6** ; PubMedGPT 50.3 ; DRAGON 47.5 ; BioLinkBERT 45.1 ; Galactica 44.4 ; PubMedBERT 38.1 ; GPT-Neo 33.3 | §4.1 | Flan-PaLM 540B few-shot+SC |
| — | MedQA 5-option | **62.0** | §4.1 (text only) | Flan-PaLM 540B |
| F3 | **Figure 3** — bar chart vs prior SOTA | MedMCQA 52.9→57.6 ; MedQA 50.3→67.6 ; PubMedQA 78.2→79.0 | §4.2 | Flan-PaLM 540B |
| — | MedMCQA (validation) | **57.6** (SC) ; 56.5 (few-shot) | §4.2, Table 7 | Flan-PaLM 540B |
| — | PubMedQA (test 500) | **79.0** (few-shot) ; 75.2 (SC) | §4.2, Table 7 | Flan-PaLM 540B |
| — | MMLU professional medicine / clinical knowledge | **83.5 / 84.0** | §4.3 | Flan-PaLM 540B |
| F4 | **Figure 4** — MMLU 6 subjects vs OPT/BLOOM/Galactica/Gopher/Chinchilla | (per-subject bars) | §4.3 | Flan-PaLM 540B |
| T5 | **Table 5** — PaLM vs Flan-PaLM × {8B,62B,540B}, **few-shot** (3 rows) | MedQA 4-opt: 25.7 / 35.4 / 40.9 / 46.1 / 58.9 / **60.3**  ·  MedMCQA: 26.7 / 34.5 / 43.4 / 46.2 / 54.5 / **56.5**  ·  PubMedQA (3-shot): 34.0 / 67.6 / 57.8 / 77.2 / 55.0 / **79.0** | §4.4 | all 6 PaLM/Flan-PaLM |
| T6 | **Table 6** — few-shot vs CoT (Flan-PaLM 540B) | MedQA 60.3 / **60.3** ; MedMCQA 56.5 / **53.6** ; PubMedQA 79.0 / **77.2** | §4.4 | Flan-PaLM 540B |
| T7 | **Table 7** — few-shot vs SC (Flan-PaLM 540B) | MedQA 60.3 / **67.6** ; MedMCQA 56.5 / **57.6** ; PubMedQA 79.0 / **75.2** | §4.4 | Flan-PaLM 540B |
| A1 | **Table A.1** — MMLU 6 subjects × {PaLM 540B few-shot, Flan-PaLM 540B few-shot / CoT / SC} | (per-subject grid; e.g. clinical knowledge 80.4 SC ; prof. med. 83.5 SC) | §A.3 | 540B |
| F5 | **Figure 5** — selective-prediction curve on MedQA | accuracy rises to **82.5% at 0.45 deferral** | §4.4 | Flan-PaLM 540B, **41 decodes**, CoT+SC |
| A2 | **Table A.2 (variance)** — repeat MedQA eval 4× | **variance 0.078** | §A.2 | Flan-PaLM 540B |
| FA1/FA2 | **Figures A.1, A.2** — scaling vs FLOPs | monotone rise; steeper at larger scale | §A.4 | PaLM & Flan-PaLM few-shot ; Flan-PaLM few-shot vs few-shot+CoT+SC |

### B. Instruction-prompt-tuning results — **OUT OF SCOPE (blocked)**

| A6 | **Table A.1 / §A.6** — Med-PaLM (MC variant) preliminary | 67.2% MedQA with CoT+SC | §A.6 | needs frozen Flan-PaLM 540B weights |

### C. Human-evaluation results — **OUT OF SCOPE (blocked)**

Tables A.3–A.12, Figures 6–11, Tables 9–10. Headline: scientific consensus
Clinician 92.9 / Med-PaLM 92.6 / Flan-PaLM 61.9 ; potential harm 5.7 / 5.9 / 29.7 ;
bias 1.4 / 0.8 / 7.9 ; helpfulness 91.1 / 80.3 / 60.6. Needs **9 clinicians + 5 lay
raters** and the **Med-PaLM + Flan-PaLM answers to the 140 questions**.

### D. Qualitative tables — **OUT OF SCOPE (blocked)**

Table 8 (Flan-PaLM MedQA explanations), Tables 9–10 (Med-PaLM long-form answers).
Need the actual model outputs.

## 1.3 The method spec — exactly

### Datasets & splits (§3.1, Table 1) — **DONE (Phases 2–4)**

| Dataset | Split used for scoring | Split for few-shot exemplars | n (scoring) |
|---|---|---|---|
| MedQA USMLE 4-opt | test | train+dev (11,450) | 1,273 |
| MedQA USMLE 5-opt | test | train+dev | 1,273 |
| MedMCQA | **validation** (RA-01) | train (182,822) | 4,183 |
| PubMedQA `pqa_labeled` | official test (RA-02) | remaining 500 | 500 |
| MMLU ×6 subjects | test | `dev` split, 5 rows/subject (RA-06) | 1,089 |

### Prompting (§3.3.2, A.8–A.9)

- **Few-shot**: `fixed instruction line` + `N verbatim exemplars` + `test question`.
  N = **5** for MedQA / MedMCQA / MMLU ; N = **3** for PubMedQA (context budget).
  Exemplar text: verbatim Tables A.13–A.17 → already in `prompts/few_shot/`.
- **CoT**: exemplars carry a step-by-step `Explanation:` then `Answer: (X)`.
  Instruction: *"Solve them in a step-by-step fashion. Output a single option as the
  final answer."* Verbatim Tables A.18–A.21 → `prompts/cot/`.
- **Self-consistency**: **11** stochastic decodes with the CoT prompt; extract the
  answer letter from each; **plurality vote**. Applied to MedQA / MedMCQA / PubMedQA
  / MMLU. Sampling temperature **NOT SPECIFIED IN PAPER** (preprint) → **RA-03 = 0.7**,
  sweep {0.5, 0.7, 1.0}.
- **Selective prediction**: **41** decodes, CoT prompt, SC. Uncertainty score =
  (# decodes agreeing with the plurality answer) / 41. Sweep deferral fraction
  d ∈ [0, 0.45] ; report accuracy on the retained (1−d). MedQA only.

### Scoring (§4)

- MC accuracy. With SC: accuracy of the plurality answer.
- **No confidence intervals on MC accuracy anywhere in the paper.** The only
  variability statistic is A.2's single variance figure (0.078 over 4 MedQA runs).
- No significance tests between models/strategies.

### Instruction prompt tuning (§3.3.3, A.1) — **OUT OF SCOPE**, spec recorded for completeness

Base **Flan-PaLM 540B, frozen** · soft prompt **length 100**, embedding dim **18,432**
→ **1.84M** params · init **U(−0.5, 0.5)** · **AdamW** · grid **LR {0.001, 0.003, 0.01}
× weight-decay {0.001, 0.00001}** · batch **32** · **200 steps** · **40 clinician
exemplars** from HealthSearchQA/MedicationQA/LiveQA · checkpoint chosen by **clinician
ranking** (chosen: LR 0.003, WD 0.00001).

### Human evaluation (§3.2, §4.5) — **OUT OF SCOPE**, spec recorded

140 questions (100 HealthSearchQA + 20 LiveQA + 20 MedicationQA), disjoint from the
40 IPT exemplars · 3 blinded answer sources (clinician / Flan-PaLM / Med-PaLM) ·
9 clinicians rate 12 axes (Table 2), 5 lay raters rate 2 axes (Table 3), 1 rating per
answer · non-parametric bootstrap, **100 replicas, 95% percentile interval**.

## 1.4 What the paper does NOT contain — do not add these

| Absent | Note |
|---|---|
| Calibration (ECE, Brier, reliability diagrams, calibration slope/intercept) | never mentioned → **NOT APPLICABLE** |
| Quantitative fairness / subgroup-performance analysis (equalized odds, subgroup AUROC) | "bias" = one subjective clinician yes/no rating only |
| AUROC, AUPRC, F1, sensitivity, specificity, PPV, NPV | MC accuracy only |
| Any model training except the Med-PaLM soft prompt | — |
| Retrieval / RAG | MedQA textbooks in `data_clean.zip` belong to *other* papers' baselines |
| BLEU / ROUGE on long-form answers | deliberately rejected (§3.1) in favour of human eval |

---

# PART 2 — WHERE YOU ARE (Phases 1–8, DONE)

| Phase | Result |
|---|---|
| 1 Environment | `.venv` 3.14.7, pinned deps, package skeleton, configs, docs, `run.py` |
| 2 Acquisition | 7 datasets in `raw_data/` (4 local extracts + PubMedQA + MMLU×6 + LiveQA-train mirror), SHA-256 provenance |
| 3 Verification | 56 PASS / 2 CAVEAT / **0 FAIL** vs paper Table 1 |
| 4 Integration | `processed_data/` 13 files, unified schema, 212,722 records ; **Table 1 reproduced** (MedQA 11450/1273, PubMedQA 500/500, MMLU 123/1089 exact) ; leakage checks clean |
| 5 Cohort | 140-question human-eval set materialised (verbatim) ; 40-slot IPT placeholder (blocked) |
| 6 Preprocessing | answer parser (RA-05), prompt builder, self-consistency plurality — unit-tested |
| 7 Prompts | 9 files ; MC few-shot/CoT verbatim from A.13–A.21 ; PubMedQA 3-shot asserted |
| 8 EDA | distributions computed ; 2 anomaly flags, both confirmed genuine dataset properties |

**81 automated tests pass. All 6 original input files byte-intact (SHA-256 checked).**

---

# PART 3 — THE REMAINING PHASES (9 → 20)

Continues the numbering of `scripts/phaseNN_*.py`. Effort assumes an **8B model**;
divide by ~10–50 for a fast API. Compute-heavy phases have a labelled subsample fallback.

---

## Phase 9 — Model access & backend
**Objective:** a working `generate(prompt, n, temperature, max_tokens)` against a real model, plus the Table 4 baseline column from citations.
**Reproduces:** enabling step ; §4.1 Table 4 non-Flan-PaLM rows (RA-15 — cite, don't re-run).
**Tasks:** (1) decide runtime — local GPU (model + VRAM) **or** API + budget ; (2) pick model(s) — for the scaling + instruction-tuning story pick a family with ≥2 sizes and a base+instruct pair, else one instruct model ; (3) create `src/medalign_qa/models/{base,mock,<backend>}.py` ; (4) 5-question MedQA smoke test ; (5) fill Table 4 baseline rows (PubMedGPT 50.3, DRAGON 47.5, BioLinkBERT 45.1, Galactica 44.4, PubMedBERT 38.1, GPT-Neo 33.3) with citations.
**Inputs:** your hardware/API decision.
**Outputs:** `configs/model/<name>.yaml`, `results/phase09_smoke.json`, `tables/table4_baselines.md`.
**Validation:** 5 MedQA questions answered end-to-end; parser extracts a letter from each.
**Done when:** smoke test green; model version/revision pinned in the config.
**Compute:** minutes.
**Blocker:** **B1 — needs your decision. Nothing else proceeds without it.**

## Phase 10 — Few-shot multiple-choice inference
**Objective:** run the core few-shot evaluation.
**Reproduces:** §4.4 few-shot columns of Table 5; the few-shot baseline of Tables 6 & 7; §4.1–4.3 few-shot numbers.
**Tasks:** for each of MedQA-4opt (1273), MedQA-5opt (1273), MedMCQA-valid (4183), PubMedQA-test (500), MMLU ×6 (1089) — build the verbatim few-shot prompt (`prompt_builder`), greedy-decode, parse the answer, save per-question predictions with the raw generation.
**Inputs:** `processed_data/`, `prompts/few_shot/`, model.
**Outputs:** `derived_data/predictions/fewshot/<dataset>.jsonl`, `results/phase10_fewshot_accuracy.json`.
**Validation:** parse-rate ≥ 98% per dataset (log the unparseable ones); accuracy within a plausible band; hand-check 10 predictions per dataset.
**Done when:** every in-scope split has a few-shot accuracy + a per-question prediction file.
**Compute:** MedQA ~1 h ; full set ~4–8 h (8B). API: <1 h.

## Phase 11 — Chain-of-thought inference
**Objective:** run the CoT evaluation.
**Reproduces:** §4.4 Table 6 (few-shot vs CoT).
**Tasks:** same splits, verbatim CoT prompts (A.18–A.21), `max_tokens` large enough for reasoning, parse the trailing `Answer: (X)`. Save reasoning text.
**Outputs:** `derived_data/predictions/cot/<dataset>.jsonl`, `results/phase11_cot_accuracy.json`, `tables/table6.md`.
**Validation:** reasoning present in ≥ 95% of outputs; parse-rate ≥ 96%; report CoT−few-shot delta per dataset. **Test the paper's finding:** CoT ≈ or < few-shot on MC.
**Done when:** Table 6 (your model) rendered next to the paper's.
**Compute:** ~2× Phase 10.

## Phase 12 — Self-consistency + MC evaluation (the headline phase)
**Objective:** the SC results and all MC tables.
**Reproduces:** §4.1–4.4 — Tables 4, 5, 6, 7, A.1; Figures 3, 4.
**Tasks:** (1) SC: **11 decodes** per question, CoT prompt, temperature 0.7 (RA-03), on MedQA / MedMCQA / PubMedQA / MMLU; plurality vote (`self_consistency.plurality`). (2) Compute accuracy for every (dataset × strategy) cell. (3) Assemble Table 4 (your MedQA best + cited baselines), Table 5 (few-shot; full 6-model grid only if you ran base+instruct × ≥2 sizes — else the cells you have), Table 6, Table 7, Table A.1 (MMLU per-subject × 4 strategies). (4) Render Fig 3 & Fig 4 with your numbers beside the paper's.
**Outputs:** `derived_data/predictions/sc/<dataset>.jsonl`, `tables/table{4,5,6,7,A1}.md`, `figures/fig{3,4}.png`, `results/phase12_mc_results.json`.
**Validation:** SC ≥ few-shot on MedQA & MedMCQA (paper's finding); SC ≤ few-shot on PubMedQA (paper's finding); every accuracy carries n and a Wilson 95% CI (your addition, labelled "beyond paper").
**Done when:** all in-scope MC tables/figures rendered with paper-vs-yours columns.
**Compute:** SC = 11× few-shot. MedQA SC ~11 h (8B) / ~1 h (API). **Fallback:** SC on MedQA + MedMCQA first; add PubMedQA/MMLU later.

## Phase 13 — Scaling analysis
**Objective:** the scale-vs-accuracy story.
**Reproduces:** §4.4 scaling narrative; Figures A.1, A.2; Table 5's scaling reading.
**Tasks:** only if you ran ≥ 2 model sizes — plot accuracy vs approx params (or FLOPs) for (a) few-shot and (b) few-shot+CoT+SC, on MedQA & MedMCQA.
**Outputs:** `figures/figA1.png`, `figures/figA2.png`, `results/phase13_scaling.json`.
**Validation:** monotone (or near-monotone) rise with size; report the 8B→largest delta against the paper's "~2×".
**Done when:** plots rendered, or — if single model — a one-line **NOT REPRODUCED (requires multiple model sizes)** with rationale.
**Compute:** = Phases 10+12 repeated per extra size.

## Phase 14 — Selective prediction / uncertainty
**Objective:** the deferral curve.
**Reproduces:** §4.4 "Uncertainty and Selective Prediction"; Figure 5.
**Tasks:** **41** CoT decodes per MedQA-test question; uncertainty = agree_count/41; sweep d ∈ {0, 0.05, …, 0.45}; accuracy on the retained (1−d); plot.
**Outputs:** `figures/fig5_selective_prediction.png`, `results/phase14_selective_prediction.json`.
**Validation:** curve monotonically non-decreasing (paper's qualitative claim); at d=0 the accuracy equals your Phase 12 MedQA CoT+SC accuracy; report your endpoint vs the paper's 82.5%.
**Done when:** Fig 5 rendered with your curve.
**Compute:** 41 × 1,273 ≈ 52k generations — **the most expensive phase**. 8B: 1–2 days. API: a few hours + \$. **Fallback:** a fixed 300-question random subsample, clearly labelled.

## Phase 15 — Variance analysis
**Objective:** run-to-run stability.
**Reproduces:** §A.2 (variance 0.078 over 4 MedQA runs).
**Tasks:** repeat the MedQA CoT+SC evaluation **4×** with different sampling seeds; report the variance of the 4 accuracies.
**Outputs:** `results/phase15_variance.json`.
**Validation:** loose comparison of your variance's magnitude to 0.078 (different model — not expected to match, only to be "small").
**Done when:** 4 accuracies + variance recorded.
**Compute:** 4 × a MedQA SC run.

## Phase 16 — Statistical analysis
**Objective:** the (deliberately minimal) statistics + the Phase-19 tolerance bands.
**Reproduces:** the paper's MC statistics (almost none) + `configs/global.yaml` tolerances (RA-17).
**Tasks:** Wilson 95% CI on every accuracy; bootstrap CI on the SC accuracies; McNemar test few-shot vs SC per dataset (labelled "beyond paper"). Build the 100-replica / 95-percentile bootstrap helper (it's the §4.5 machinery — unused here but needed for a complete implementation and cheap to write).
**Outputs:** `results/phase16_stats.json`.
**Validation:** CI half-widths ≈ normal approximation on synthetic data; bootstrap deterministic under the fixed seed.
**Done when:** every accuracy in the results has an interval.
**Compute:** seconds.

## Phase 17 — Tables & figures (final render)
**Objective:** publication-quality outputs.
**Reproduces:** every in-scope table/figure — Tables 4, 5, 6, 7, A.1, A.2; Figures 3, 4, 5, A.1, A.2.
**Tasks:** consistent styling; every table has **PAPER | YOUR MODEL | Δ** columns; figures overlay/adjoin the paper's values.
**Outputs:** `tables/*.md`, `figures/*.png`.
**Explicitly SKIP:** Table 8 (Flan-PaLM explanations), Tables 9–10, Figures 6–11 — mark **BLOCKED**.
**Done when:** `tables/` and `figures/` hold every in-scope artifact.

## Phase 18 — Reproducibility validation
**Objective:** another researcher can reproduce your run.
**Tasks:** (1) full `run.py` chain on a clean checkout reproduces `processed_data/` + `tables/table1_reproduced.*` **byte-identically twice**; (2) seed-audit script (grep for un-seeded RNG); (3) `requirements.lock.txt` re-install check; (4) re-hash all `raw_data/` files against the manifest; (5) pin the model revision + record every decode parameter used.
**Outputs:** `results/phase18_repro.json`, `docs/reproducibility.md`.
**Done when:** two clean model-independent runs match byte-for-byte; model runs are re-runnable from saved configs + seeds (accepting sampling noise).

## Phase 19 — Paper-to-result comparison (the verdict)
**Objective:** the actual replication assessment.
**Tasks:** `results/comparison.md` — one row per claim in Part 1.2.A: **PAPER RESULT | YOUR RESULT (model X) | Δ | within tolerance? | explanation**. Then a **qualitative-findings verdict** for each of:
- instruction tuning helps (PaLM < Flan-PaLM) — testable only with a base+instruct pair
- scale helps — testable only with ≥2 sizes
- **SC beats few-shot on MedQA & MedMCQA**
- **SC hurts PubMedQA**
- **CoT does not beat few-shot on MC**
- **selective-prediction accuracy rises with deferral**
Each verdict ∈ {REPRODUCED-QUALITATIVELY, DIVERGENT, NOT-ATTEMPTED, BLOCKED}.
**Framing:** absolute-value gaps are **expected** (different model). The science is *which findings hold*.
**Done when:** every claim row + every qualitative finding has a verdict.

## Phase 20 — Final documentation
**Objective:** ship a clean, honest, reproducible repo.
**Tasks:** README run-book (exact commands per phase); `docs/model_card.md` (Table A.2 template for your model); consolidate `docs/deviations.md` (RA-01…RA-23+) and `docs/blockers.md`; a **limitations** section; and the **headline statement**:

> *"This project reproduces the MultiMedQA benchmark and the Flan-PaLM multiple-choice
> evaluation methodology (few-shot / CoT / self-consistency / selective prediction),
> applied to [model X]. It does NOT reproduce Med-PaLM, the instruction-prompt-tuning
> results (§3.3.3–3.3.4, §A.1, §A.6), or any human-evaluation result (§3.2, §4.5,
> Tables A.3–A.12, Figures 6–11) — those require the unreleased PaLM/Flan-PaLM weights
> and a panel of clinician raters."*

**Done when:** a new user can `pip install -r`, `pip install -e .`, and run phases 1→19 from the README, and understands exactly what was and was not reproduced.

---

# PART 4 — PERMANENTLY OUT OF SCOPE (and why that is correct)

| Paper section | Artifact | Why not done | Label |
|---|---|---|---|
| §3.3.3–3.3.4, §A.1, §A.6 | Med-PaLM (instruction prompt tuning) | needs the **frozen Flan-PaLM 540B weights**; a soft prompt on a substitute base is a different experiment | **BLOCKED (B1/B2)** |
| §3.2, §4.5 | Human evaluation — Tables A.3–A.12, Figs 6–11 | needs **9 clinicians + 5 lay raters**; an LLM-judge stand-in is not defensible | **BLOCKED (B4)** |
| §4.5 | Long-form generation on LiveQA / MedicationQA / HealthSearchQA | only meaningful when scored by the human framework | **BLOCKED (B4)** |
| §4.4, §4.5 | Tables 8, 9, 10 (qualitative model outputs) | need the actual Flan-PaLM / Med-PaLM generations | **BLOCKED (B1/B2)** |
| — | Calibration (ECE / Brier / reliability curves) | **not in the paper** | **NOT APPLICABLE** |
| — | Quantitative fairness / subgroup analysis | **not in the paper** (bias = 1 subjective rating) | **NOT APPLICABLE** |

These are ~40% of the paper by page count but a smaller share of its scientific weight
for a methodology replication: the MC benchmark + prompting story is fully in scope.

---

# PART 5 — HOW TO PROCEED RIGHT NOW

1. **Answer two questions:**
   - **Runtime:** local NVIDIA GPU (which model / how much VRAM) **or** an API (which, and rough budget)?
   - **Model(s):** one current open instruct model for the main run; **plus**, if you
     want the scaling + instruction-tuning findings, its non-instruct base and one
     larger size. (Tell me if you want me to pick, or name one.)
2. I build **Phase 9** (backend + smoke test + Table 4 baselines). You confirm 5 MedQA questions get answered.
3. **Phase 10, MedQA-only first** → your first real number to sit next to 60.3 / 67.6.
4. Then Phases 11 → 20 in order, with the compute fallbacks above for Phases 12 & 14.

**Rough total compute:** an 8B local model ≈ 3–5 days wall-clock (dominated by Phases
12 & 14). A fast API ≈ several hours + \$30–80. Everything else (Phases 16, 18, 19, 20)
is minutes.
