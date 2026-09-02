# MultiMedQA — Multiple-Choice Methodology Replication on a Substitute Model

**Paper.** Singhal et al., *Large Language Models Encode Clinical Knowledge*, arXiv:2212.13138v1 (26 Dec 2022) / *Nature* 620:172–180 (2023). "Med-PaLM / MultiMedQA".

**What this is.** A faithful re-implementation of the paper's **multiple-choice evaluation methodology** — the MultiMedQA benchmark assembly and the few-shot / chain-of-thought (CoT) / self-consistency (SC) / selective-prediction prompting pipeline — run end-to-end on one frozen open substitute model, `Qwen/Qwen2.5-7B-Instruct` @ `a09a3545…`.

**What this is not.** It is **not** a reproduction of PaLM / Flan-PaLM / Med-PaLM. Those weights were never released. Every absolute number below is from a different model (7B, 2024) and is not comparable point-for-point to the paper's (up to 540B, 2022). The replication target is the paper's **qualitative findings**: do the same prompting techniques produce the same *directional* effects on a different model?

---

## 1. Completeness against the paper — every table, figure, and section

Three states: **✅ done** (reproducible from public materials, and done) · **🔒 impossible** (needs Google's unreleased PaLM/Flan-PaLM/Med-PaLM weights or the paper's recruited clinician panel — no replication can do it) · **⚪ possible, not done** (needs a second open model — deliberately out of scope here).

| Paper item | State | Notes |
|---|---|---|
| §3.1 · **MultiMedQA benchmark** (7 datasets) · **Table 1** | ✅ | `phase03`: 56 PASS / 2 CAVEAT / 0 FAIL. Caveats (HealthSearchQA 3173 vs 3375, MedicationQA 690 vs 674, LiveQA-train mirror) are cases where the *public release* differs from the paper — unfixable by anyone. |
| §3.2 · **Human-evaluation framework** (Tables 2, 3) | ✅ spec / 🔒 ratings | 12 clinician + 2 lay axes captured; 140-question eval set materialised; bootstrap machinery (100 replicas, 95 %ile) implemented in `evaluation/stats.py`. The ratings themselves need 9 clinicians + 5 lay raters (**B4**). |
| §3.3.1 · **Models** (PaLM/Flan-PaLM 8B/62B/540B) | 🔒 | Never released (**B1**). Substitute: Qwen2.5-7B. |
| §3.3.2 · **Prompting** — few-shot / CoT / self-consistency (prompts A.13–A.21) | ✅ | Implemented; exemplar blocks transcribed verbatim. |
| §3.3.3–3.3.4 · **Instruction prompt tuning → Med-PaLM** (Fig 2, spec in `configs/global.yaml`) | 🔒 | Needs frozen Flan-PaLM 540B weights (**B2**) + the 40 unpublished clinician exemplars (**B3**). |
| §4.1 · **MedQA** — **Table 4** (leaderboard), **Fig 3** | ✅ | Methodology + all 6 cited baselines (RA-15) + substitute row. Paper's Flan-PaLM 67.6 = **B1**. |
| §4.2 · **MedMCQA / PubMedQA** — **Fig 3** | ✅ | Rendered with prior-SOTA + substitute numbers. |
| §4.3 · **MMLU clinical topics** — **Fig 4** | ✅ methodology / ⚠ partial | Ours-vs-Flan-PaLM-540B rendered. The OPT/BLOOM/Galactica/Gopher/Chinchilla context bars (paper's ref [79]) are not re-plotted — those values can't be read precisely from the paper's chart and ref [79] isn't in the provided materials. |
| §4.4 · **Table 5** (few-shot × PaLM/Flan-PaLM × 3 sizes) | ✅ substitute col / 🔒 grid | Full 6-model grid = **B1**. |
| §4.4 · **Table 6** (few-shot vs CoT) | ✅ | MedQA / MedMCQA / PubMedQA. |
| §4.4 · **Table 7** (few-shot vs self-consistency) | ✅ | MedQA / MedMCQA / PubMedQA. |
| §4.4 · **Scaling** finding + **Figs A.1, A.2** | ⚪ | Requires ≥ 2 model sizes. **The only paper component that is possible but not done.** |
| §4.4 · **Fig 5** (selective prediction, 41 decodes) | ✅ | Full 1,273-question MedQA test set. |
| §4.4 · **Table 8** (Flan-PaLM MedQA explanations) | 🔒 | Needs Flan-PaLM's actual generations (**B1**). |
| §4.5 / §A.7 · **Human-evaluation results** — **Tables A.3–A.12**, **Figs 6–11** | 🔒 | Rater panel (**B4**). |
| §A.1 · IPT hyperparameters | ✅ recorded | In `configs/global.yaml`; not runnable without B2. |
| §A.2 · **Variance** (0.078 over 4 runs) | ✅ | 4 runs, variance 0.035. |
| §A.3 · **Table A.1** (MMLU × 4 strategies) | ✅ | Ours FS/CoT/SC for all 6 subjects, beside all 4 paper columns (paper cols = B1). |
| §A.4 · **Figs A.1, A.2** (scaling plots) | ⚪ | Same as scaling above. |
| §A.5 · Med-PaLM model card | ✅ recorded | `docs/model_card.md` is the substitute-model analogue. |
| §A.6 · **Med-PaLM MC** (67.2 % MedQA) | 🔒 | Needs frozen Flan-PaLM 540B (**B2**). |
| §A.8 / §A.9 · Prompt exemplars (A.13–A.21) | ✅ | Transcribed into `prompts/`. |
| Tables 9, 10 · Med-PaLM long-form outputs | 🔒 | Needs Med-PaLM generations (**B2**). |

**Verdict.** Everything the paper does that is reproducible from public materials is done. **One** paper component — the scaling analysis — is reproducible only with a second open model and is deliberately excluded. Everything else that is undone (≈40 % of the paper by page count: Med-PaLM, instruction prompt tuning, and the entire human evaluation) is **permanently blocked** by the unavailability of Google's model weights and the paper's clinician panel — see `docs/blockers.md` (B1–B4).

**Datasets & scored splits.** MedQA-USMLE 4-opt (test, 1273) and 5-opt (test, 1273); MedMCQA (validation, 4183 — RA-01, test labels withheld); PubMedQA `pqa_labeled` (official test, 500 — RA-02); MMLU ×6 clinical subjects (test, 1089 total). Prompting is verbatim from the paper's exemplar blocks (Tables A.13–A.21); a chat-model system message is added for output formatting (RA-24); MMLU few-shot uses each subject's 5 `dev` rows (RA-06, the paper gives no MMLU few-shot prompt). Decoding: greedy for few-shot/CoT; temperature 0.7 for SC (RA-03, unspecified in the preprint). Runtime: local vLLM on a Kaggle T4×2, `float16` (Turing has no bf16 — RA-28). All 28 gap-filling assumptions are in `docs/deviations.md`.

---

## 2. Results — accuracy (%)

Wilson 95% intervals in brackets. `—` = not run for that strategy (paper runs CoT/SC on the four core MC sets only; 5-opt is few-shot only).

| Dataset | n | few-shot | CoT | self-consistency |
|---|--:|--:|--:|--:|
| MedQA 4-opt | 1273 | 59.4 [56.7, 62.1] | 60.5 [57.8, 63.1] | **63.3** [60.6, 65.9] |
| MedQA 5-opt | 1273 | 53.6 [50.8, 56.3] | — | — |
| MedMCQA (val) | 4183 | 56.6 [55.1, 58.1] | 56.4 [54.9, 57.9] | **58.5** [57.0, 60.0] |
| PubMedQA (test) | 500 | 72.8 [68.7, 76.5] | 74.8 [70.8, 78.4] | 73.6 [69.6, 77.3] |
| MMLU anatomy | 135 | 71.9 [63.7, 78.8] | 70.4 [62.2, 77.4] | 71.1 [63.0, 78.1] |
| MMLU clinical knowledge | 265 | 78.9 [73.6, 83.4] | 79.6 [74.4, 84.0] | 80.0 [74.8, 84.4] |
| MMLU college medicine | 173 | 65.9 [58.6, 72.5] | 75.1 [68.2, 81.0] | **76.9** [70.0, 82.5] |
| MMLU medical genetics | 100 | 81.0 [72.2, 87.5] | 86.0 [77.9, 91.5] | 84.0 [75.6, 89.9] |
| MMLU professional medicine | 272 | 76.1 [70.7, 80.8] | 76.1 [70.7, 80.8] | 78.3 [73.0, 82.8] |
| MMLU college biology | 144 | 82.6 [75.6, 88.0] | 84.7 [78.0, 89.7] | 86.1 [79.5, 90.8] |

Parse rate 0.998–1.000 on every split (one MedQA and eight MedMCQA CoT generations end without an extractable letter — genuine model non-answers, scored wrong).

**Run-to-run variance** (4× MedQA-4opt SC, different sampling seeds): accuracies {62.45, 62.37, 62.69, 62.84}, population variance **0.035**. The paper reports 0.078 for Flan-PaLM 540B (A.2) — same order of magnitude; not an apples-to-apples comparison.

---

## 3. Qualitative findings — 5 of 7 evaluated

McNemar test on paired few-shot vs SC predictions where relevant.

| # | Paper finding | Verdict | Detail |
|---|---|---|---|
| 1 | **Self-consistency beats few-shot on MedQA** | ✅ **REPRODUCED** | 59.4 → 63.3 (+3.9 pp, McNemar p = 3×10⁻⁴). Direction and significance hold; magnitude smaller than the paper's +7.3 (60.3 → 67.6). |
| 2 | **Self-consistency beats few-shot on MedMCQA** | ✅ **REPRODUCED** | 56.6 → 58.5 (+1.9 pp, p = 4×10⁻³). Larger gain than the paper's +1.1 (56.5 → 57.6). |
| 3 | **Selective-prediction accuracy rises with deferral** | ✅ **REPRODUCED** | Monotonic 62.9 % (defer 0) → 76.6 % (defer 0.45) on the full 1,273-question test set, 41 decodes. Paper endpoint 82.5 %. |
| 4 | **Self-consistency *hurts* PubMedQA** | ✗ **DIVERGENT** | Ours: 72.8 → 73.6 (+0.8 pp, McNemar p = 0.68 — no significant change). Paper: 79.0 → 75.2 (−3.8). The SC-hurts pattern did not appear on this model. |
| 5 | **CoT does not beat few-shot on MC** | ✗ **DIVERGENT** | Ours: CoT > few-shot on MedQA (+1.1) and PubMedQA (+2.0), ≈ on MedMCQA (−0.2). Paper: CoT flat-to-worse on all three. Note the per-dataset deltas sit inside the Wilson intervals — the honest reading is "CoT did not *underperform* few-shot here", contrary to the paper. |
| 6 | Instruction tuning helps (PaLM < Flan-PaLM) | ⚪ NOT-ATTEMPTED | Needs the non-instruct base of the same family. |
| 7 | Scaling helps (≈2× from 8B to 540B) | ⚪ NOT-ATTEMPTED | Needs ≥ 2 model sizes. |

**Reading.** The two techniques the paper leans on hardest — self-consistency for the headline MedQA number, and uncertainty-based deferral — reproduce cleanly, including statistical significance. The two that diverge are both cases where the paper reported a *negative* effect (SC or CoT making things worse) that simply does not occur on a modern 7B instruct model: here SC is neutral-to-helpful everywhere and CoT is neutral-to-helpful everywhere. That is itself a finding — the "SC/CoT can hurt on some MC datasets" caution is model-dependent, not universal.

---

## 4. Headline observation — a 7B 2024 model vs Flan-PaLM 540B on MMLU

MMLU clinical subjects, **self-consistency**, ours vs the paper's Flan-PaLM 540B (Table A.1, approximate):

| Subject | Ours (7B) | Flan-PaLM 540B | Δ |
|---|--:|--:|--:|
| anatomy | 71.1 | 71.9 | −0.8 |
| clinical knowledge | 80.0 | 80.4 | −0.4 |
| college medicine | 76.9 | 76.3 | **+0.6** |
| medical genetics | 84.0 | 74.0 | **+10.0** |
| professional medicine | 78.3 | 83.5 | −5.2 |
| college biology | 86.1 | 88.9 | −2.8 |

Four of six subjects land within ±4 pp of a model ~77× larger; one is a clear win. This is not a claim about the paper — it is what falls out of running the paper's own methodology on a 2024 model, and it quantifies how much two years of pre-training progress closes on brute scale for this task.

---

## 5. Limitations

- **Substitute model.** No absolute number here reproduces a paper number. Cross-model comparisons in §4 are illustrative, not the paper's experiment.
- **Preprint gaps.** SC temperature, top-p/top-k, tie-breaking, and the answer-extraction rule are unspecified in the arXiv v1 and were chosen (RA-03/04/05); the Nature version uses ~0.7 temperature.
- **MedMCQA split.** The paper's "dev set" is genuinely ambiguous (Table 1's "dev" = 187 K = train+val); we score the 4,183-row validation split, which is skewed (31.5 % Dental, 32 % gold-A) — RA-01.
- **MMLU few-shot prompt** is a reconstruction (RA-06); the paper specifies none.
- **`float16` not `bfloat16`** (T4 constraint, RA-28) — minor numeric effect, and greedy determinism holds only per (revision, GPU arch, vLLM version, dtype).
- Consumer long-form datasets (LiveQA, MedicationQA, HealthSearchQA) are acquired and schema-unified but **not evaluated** — they are only meaningful under the human-evaluation framework (B4), which is out of scope.

---

## 6. Reproducing this

```
# Milestone 1 — data harness (any machine, no GPU)
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && pip install -e .
python run.py phase01   # ... through phase08

# Milestone 2 — Path B evaluation (GPU; free Kaggle/Colab T4 works)
python scripts/run_pathb_pipeline.py --all      # phases 9–20, idempotent + resumable
```

Model and every decode parameter are frozen in `configs/model/qwen25-7b-local.yaml` (`revision` is an exact HF commit SHA). `python run.py phase18` verifies: originals untouched (SHA-256), the data pipeline is byte-reproducible, the model is pinned, no unseeded RNG. 96 automated tests. Per-phase outputs: `results/`; rendered tables/figures: `tables/`, `figures/`; the verdict: `results/comparison.md`.

**Not reproduced, and why:** `docs/blockers.md` (B1–B4). **Every deviation from a strict replication:** `docs/deviations.md` (RA-01 … RA-28).
