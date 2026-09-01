# Project Status — single source of truth

Paper: Singhal et al., *Large Language Models Encode Clinical Knowledge*,
arXiv:2212.13138v1 (26 Dec 2022) / *Nature* 620:172–180 (2023). "Med-PaLM / MultiMedQA".

Last updated: 2026-09-01, after the first real Path B run (MedQA, Qwen2.5-7B on Kaggle T4).
This file supersedes `docs/history/{replication_plan,REMAINING_PLAN,PROJECT_STATUS}.md`
(kept for history only — do not treat them as current).

---

## 1. One-line status

**Milestone 1 (dataset acquisition + validation): substantively complete, pending final
documentation sign-off.** The multiple-choice datasets needed for Milestone 2 — MedQA
(4- and 5-option), PubMedQA, MMLU ×6 — are verified **exact** against the paper; MedMCQA
data is correct with a documented eval-split assumption (RA-01). Leakage checks are clean.

**Milestone 2 (model evaluation): Path B first pass DONE — MedQA only.**
`Qwen/Qwen2.5-7B-Instruct` @ `a09a3545…` was run through the full harness on a Kaggle
T4 x2 (2026-09-01, `dtype: float16` — RA-28). Real results (`mock: false`), all
strategies, MedQA 4-opt + 5-opt. Predictions + tables + figures are committed under
`derived_data/predictions/qwen25-7b-local/`, `results/`, `tables/`, `figures/`.
Earlier attempts (`llama-3.1-8b-instruct`, partial Groq "B1", mock artifacts) stay
quarantined in `attic/`.

**Results (MedQA 4-opt, Qwen2.5-7B — SUBSTITUTE, not Flan-PaLM):**
few-shot 59.4 · CoT 60.5 · self-consistency(11) 63.3 · MedQA 5-opt few-shot 53.6.
Selective prediction (n=41, 500-Q subset RA-26): 63.6 → 79.3 % across 0–0.45 deferral,
monotonic. Variance over 4 SC runs: 0.035. Parse rate ≈ 100 % (1 genuine CoT non-answer).

**Phase 19 verdict: 2 / 7 qualitative findings evaluated, both REPRODUCED-QUALITATIVELY**
(SC > few-shot on MedQA; selective-prediction accuracy rises with deferral). The other
5 are NOT-ATTEMPTED pending the second pass (MedMCQA / PubMedQA / MMLU — needs `--all`)
and a second model size (scaling / instruction-tuning findings).

---

## 2. What is verified (Phases 1–8)

| Phase | State | Evidence |
|---|---|---|
| 1 Environment | ✅ | `run.py phase01` PASS; CPython 3.14.7 (RA-18′), deps pinned + `requirements.lock.txt` |
| 2 Acquisition | ✅ | 7 datasets in `raw_data/`; 4 local extracts byte-faithful; PubMedQA / MMLU×6 / LiveQA-train downloaded; SHA-256 in `metadata/data_provenance.md` |
| 3 Verification | ✅ | `run.py phase03`: **56 PASS / 2 CAVEAT / 0 FAIL** vs paper Table 1 |
| 4 Integration | ✅ | `processed_data/` 13 files, unified schema; `tables/table1_reproduced.md`; leakage checks (now incl. MMLU dev/val→test, intra-dataset dups, exemplar↔eval) all clean; re-runs byte-identical |
| 5 Cohort | ✅ | `derived_data/human_eval_140.jsonl` (140 Q verbatim from xlsx sheet 2); `ipt_exemplars.PLACEHOLDER.jsonl` (40 null slots — BLOCKED B3) |
| 6 Preprocessing | ✅ | answer parser (RA-05, now CoT-safe), prompt builder, self-consistency plurality — unit-tested |
| 7 Prompts | ✅ | MC few-shot/CoT exemplar blocks **verbatim** from Tables A.13–A.21; MMLU few-shot = RA-06 assumption; assembled prompt adds RA-24 wrapper |
| 8 EDA | ✅ | `results/phase08_eda_report.json`; 2 anomaly flags, both genuine dataset properties |

91 pytest tests collected: **86 pass / 5 skip / 0 fail** (datasets staged + `project_healthcare_.pdf` present).

### Dataset classification (final)

| Dataset | Scoring split | Counts (actual vs paper) | Status |
|---|---|---|---|
| MedQA USMLE 4-opt | test 1273 | dev 11450 / test 1273 — **exact** | DATASET-VERIFIED |
| MedQA USMLE 5-opt | test 1273 | same questions; 5 options; gold incl. E | DATASET-VERIFIED |
| MedMCQA | **validation 4183 (RA-01)** | dev = train+val = **187005 ≈ 187000**; test 6150 ≈ 6100 (paper rounds). Scoring split is an assumption; it is 31.5% Dental / 32% gold-A (comparability caveat, RA-01) | DATASET-VERIFIED (data) / REPRODUCTION ASSUMPTION (eval split) |
| PubMedQA `pqa_labeled` | official test 500 (RA-02) | 1000 total; test 500; labels verified; 0 label mismatch | DATASET-VERIFIED |
| MMLU ×6 | test (sum 1089) | validation 123 (= paper "dev"), test 1089 — **exact, subject-by-subject** | DATASET-VERIFIED (counts) / few-shot source RA-06 |
| LiveQA test | — | 104 — exact | DATASET-VERIFIED |
| LiveQA train | — | 635 (community mirror) vs 634 — canonical XMLs unpublished | UNVERIFIED (RA-20) |
| MedicationQA | — | 690 rows (651 distinct); paper's 674 **unreconstructable** (RA-08) | DATASET-VERIFIED (caveat) |
| HealthSearchQA | — | 3173 released (3156 distinct) vs 3375 preprint — CANNOT BE DETERMINED (RA-09) | DATASET-VERIFIED (caveat) |

---

## 3. What is NOT done / NOT reproducible

| Item | Why | Blocker |
|---|---|---|
| PaLM / Flan-PaLM (8B/62B/540B) results | never released | B1 |
| Med-PaLM / instruction prompt tuning (§3.3.3–3.3.4, A.1, A.6) | frozen Flan-PaLM 540B weights unavailable; spec captured in `configs/global.yaml`, no training code | B2, B3 |
| All human evaluation (§3.2, §4.5; Tables A.3–A.12; Figs 6–11) | needs 9 clinicians + 5 lay raters | B4 |
| Scaling curves (Figs A.1, A.2) | needs ≥2 model sizes | — |
| Substitute MC numbers for MedMCQA / PubMedQA / MMLU | first pass was MedQA-only (RA-27); second pass `--all` not yet run | — |

---

## 4. Decision (made 2026-08-31): **Path B**

**Path B — one frozen substitute open model through the identical harness.**
- Model: `Qwen/Qwen2.5-7B-Instruct` @ `a09a35458c702b33eeacc393d103063234e8bc28`
  (pinned 2026-08-31 in `configs/model/qwen25-7b-local.yaml`; ungated, no HF token needed).
- Runner: **local vLLM** on a free Kaggle/Colab T4 (no paid API). See `docs/pathb_runbook.md`.
- First pass: **MedQA only** (4-opt + 5-opt), all strategies (RA-27) — ✅ DONE 2026-09-01. Second pass = `--all` (MedMCQA / PubMedQA / MMLU) — pending.
- Every number tagged `REPLICATION ASSUMPTION — SUBSTITUTE MODEL`; never compared 1:1 to Flan-PaLM.
- B3 (40 IPT exemplars) and B4 (human eval) remain **BLOCKED** — Phase 11/14 not attempted.
- The two un-chosen candidate configs moved to `attic/configs_superseded/`; the legacy
  hosted-API `.env` keys are **deprecated** and must be rotated (they leaked in chat).

Predictions are namespaced `derived_data/predictions/<run_tag>/` (`run_tag: qwen25-7b-local`)
so a fresh run never mixes with the quarantined B1 Groq run at the flat `predictions/` path.

(Path A — stop at the model boundary — and Path C — you supply PaLM access — were not taken.)

---

## 5. Blockers (see `docs/blockers.md` for detail)

| ID | Severity | State | Blocks |
|---|---|---|---|
| B1 PaLM/Flan-PaLM | CRITICAL | OPEN | 9,10,12,15,17 (numbers) |
| B2 Med-PaLM | CRITICAL | OPEN | 11,14 |
| B3 40 IPT exemplars | HIGH | OPEN (PLACEHOLDER) | 11 (faithful) |
| B4 human raters | CRITICAL for §4.5 | OPEN | 14,16 (§4.5 parts) |
| B5–B14 | — | MITIGATED | documented RA-01…RA-28 |

---

## 6. Audit fixes applied (2026-08-31)

- Quarantined premature Path-B artifacts + stale "replication complete" logs → `attic/`.
- `configs/global.yaml`: MMLU / consumer few-shot counts relabelled `REPLICATION ASSUMPTION`
  (paper specifies no MMLU few-shot prompt); MedQA/MedMCQA citation corrected to Table 5/6/7 headers.
- `docs/deviations.md`: RA-01 confidence → Medium + Dental/gold-A caveat; RA-08 corrected
  (674 unreconstructable, not a working filter); RA-09 + 17 intra-dataset dups noted.
- `metadata/expected_counts.yaml`: MedMCQA "dev" = train+validation (187005 ≈ 187000).
- `src/…/data/integrate.py`: Table-1 reproduction now reports MedMCQA as `~rounding` match +
  names the scored split; leakage suite gained MMLU dev/val→test, intra-dataset dup, and
  human-eval↔IPT-exemplar disjointness checks.
- `src/…/preprocessing/answer_parser.py`: bare-letter fallback disabled for CoT/SC
  (`allow_bare=False`) so reasoning text can't be mis-parsed as the answer.
- `src/…/models/openai_compat.py`: self-consistency decodes get a per-decode seed offset
  (fixed-seed → 11 identical decodes bug).
- Phases 12/14/15/16/17/19/20: hard-fail with **NO DATA** (exit 1) when no predictions exist;
  mock runs are stamped "MOCK — not a real result"; Phase 20 no longer hard-codes a model
  name or logs "replication complete" unconditionally.

## 7. Progress log

| # | Item | State |
|---|---|---|
| 1 | Path A/B/C decision | ✅ Path B (§4) |
| 2 | **Rotate the leaked API keys** (OpenRouter + Groq) — they were pasted in chat. Local `.env` has been deleted; rotation on the provider side is still prudent. | ⚠ user action (Path B doesn't use them) |
| 3 | Re-transcribe Table A.1 → `metadata/paper_results.yaml` | ✅ done |
| 4 | `requirements-portable.txt` + `.gitattributes` + `PYTHONUTF8` in `run.py` | ✅ done |
| 5 | **Pin the model** — `revision: a09a35458c702b33eeacc393d103063234e8bc28` | ✅ done |
| 6 | Kaggle GPU env + data staging | ✅ done (T4 x2, `medalign-medqa` dataset) |
| 7 | Phase 9 smoke on the real model | ✅ done (`results/phase09_smoke.json`, parse rate 1.0) |
| 8 | `run_pathb_pipeline.py` (MedQA-only), phases 9–20 | ✅ done 2026-09-01; artifacts committed |
| 9 | Extract artifacts locally, re-run phase 16–20, hand-check predictions | ✅ done 2026-09-01 (results consistent) |
| 10 | `project_healthcare_.pdf` supplied; SHA-256 matches provenance; **Phase 18 reproducibility validation PASS** (`results/phase18_repro.json`, `docs/reproducibility.md`); 86/0/5 tests | ✅ done 2026-09-01 |
| 11 | **Second pass — `run_pathb_pipeline.py --all`** (MedMCQA / PubMedQA / MMLU×6) | ❌ next Kaggle session (~4–6 T4-h) |
| 12 | Optional: a second model size for scaling / instruction-tuning findings | ❌ optional stretch |
| 13 | Phase 20 final write-up polish once the full MC sweep is in | ❌ after step 11 |

### For the second pass (step 10)
- Upload `processed_data/{medmcqa,pubmedqa,mmlu_*}.jsonl` to the Kaggle dataset (or
  re-run `phase04` in-notebook from `raw_data/`).
- `python scripts/run_pathb_pipeline.py --all` — append-and-skip, so MedQA is not re-run.
- Back on this machine: `unzip -o pathb_artifacts.zip -d . && python run.py phase19`,
  then commit the new predictions.
