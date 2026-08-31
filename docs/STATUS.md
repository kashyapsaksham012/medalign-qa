# Project Status — single source of truth

Paper: Singhal et al., *Large Language Models Encode Clinical Knowledge*,
arXiv:2212.13138v1 (26 Dec 2022) / *Nature* 620:172–180 (2023). "Med-PaLM / MultiMedQA".

Last updated: 2026-08-31, after an external replication audit + first round of fixes.
This file supersedes `docs/history/{replication_plan,REMAINING_PLAN,PROJECT_STATUS}.md`
(kept for history only — do not treat them as current).

---

## 1. One-line status

**Milestone 1 (dataset acquisition + validation): substantively complete, pending final
documentation sign-off.** The multiple-choice datasets needed for Milestone 2 — MedQA
(4- and 5-option), PubMedQA, MMLU ×6 — are verified **exact** against the paper; MedMCQA
data is correct with a documented eval-split assumption (RA-01). Leakage checks are clean.

**Milestone 2 (model evaluation): Path B chosen (§4); code ready, no real run yet.**
No valid model results exist. Earlier attempts — a full `llama-3.1-8b-instruct` MedQA run,
a partial `qwen3.8-27b`/Groq run ("B1", 95/1273 few-shot), mock-data artifacts that logged
"replication complete" — are quarantined in `attic/` (unfrozen / incomplete / mock).
The Path B harness (local vLLM, `Qwen2.5-7B-Instruct`, frozen by HF revision) is built and
passes end-to-end in `--mock`; the real run is pending a Kaggle GPU session (§7 steps 5–8).

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

89 pytest tests pass.

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
| Any substitute-model MC number | model not frozen; no run completed | see §4 |

---

## 4. Decision (made 2026-08-31): **Path B**

**Path B — one frozen substitute open model through the identical harness.**
- Model: `Qwen/Qwen2.5-7B-Instruct` @ `a09a35458c702b33eeacc393d103063234e8bc28`
  (pinned 2026-08-31 in `configs/model/qwen25-7b-local.yaml`; ungated, no HF token needed).
- Runner: **local vLLM** on a free Kaggle/Colab T4 (no paid API). See `docs/pathb_runbook.md`.
- First pass: **MedQA only** (4-opt + 5-opt), all strategies (RA-27). Second pass = `--all`.
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
| B5–B14 | — | MITIGATED | documented RA-01…RA-24 |

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

## 7. Remaining before Phase 10 can officially begin

Path B code is in place (2026-08-31, second commit): `configs/model/qwen25-7b-local.yaml`,
`src/…/models/vllm_backend.py`, `src/…/config.py` (run_tag namespacing), `scripts/pin_model.py`,
`scripts/kaggle_pathb.py`, `requirements-pathb.txt`, `docs/pathb_runbook.md`. The full pipeline
passes end-to-end in `--mock`. What is left is operational, not code:

| # | Item | State |
|---|---|---|
| 1 | Path A/B/C decision | ✅ Path B (§4) |
| 2 | **Rotate the leaked API keys** (OpenRouter + Groq) — they were pasted in chat. `.env` still holds the old Groq key. | ❌ user action |
| 3 | Re-transcribe Table A.1 → `metadata/paper_results.yaml` | ✅ done (`tableA1` + `tableA1_flan_palm_540b_sc`) |
| 4 | `requirements-portable.txt` + `.gitattributes` + `PYTHONUTF8` in `run.py` | ✅ done |
| 5 | **Pin the model** — `revision: a09a35458c702b33eeacc393d103063234e8bc28` (resolved 2026-08-31) | ✅ done |
| 6 | **Kaggle/Colab GPU env**: create the notebook, `python scripts/kaggle_pathb.py --setup`, attach `processed_data/` (or run `phase04` from `raw_data/`) | ❌ |
| 7 | **Phase 9 smoke on the real model** (`run.py phase09`) — 5 MedQA Qs, parser pulls a letter from each | ❌ blocked on 5+6 |
| 8 | Then `python scripts/run_pathb_pipeline.py` (MedQA-only) | ❌ |

Nothing here needs money. Steps 5–8 are one Kaggle session.
