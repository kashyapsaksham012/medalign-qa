# Critical Blockers Register

Severity: CRITICAL (cannot proceed) · HIGH (substantially affects fidelity) ·
MEDIUM (affects fidelity, work continues) · LOW (cosmetic/minor).

Status: OPEN · MITIGATED (documented REPLICATION ASSUMPTION in place) · RESOLVED.

---

## B1 — PaLM / Flan-PaLM models unavailable  ·  CRITICAL  ·  OPEN (Path B substitute in place)

**2026-08-31: Path B chosen.** Substitute = `Qwen/Qwen2.5-7B-Instruct` (frozen HF revision),
run locally via vLLM through the same harness (RA-16 / RA-24 / RA-25). This does **not**
resolve B1 — the paper's own models are still unobtainable and no substitute number is a
reproduction of PaLM/Flan-PaLM. It unblocks *execution* of Phases 9–10, 12, 14, 15 with
clearly-tagged substitute results. Scaling (Phase 13) stays NOT REPRODUCED (one model size).

1. **Missing:** weights or inference API for PaLM and Flan-PaLM at 8B, 62B, 540B.
2. **Required for:** every quantitative MC result — Tables 4, 5, 6, 7, 8, A.1;
   Figs 3, 4, 5, A.1, A.2; all scaling / instruction-tuning / CoT / SC ablations.
3. **Determined from:** §3.3.1 (model definitions), §4.1–4.4, A.1; §3.3.1 line ~541
   ("6144 TPUv4 chips for pretraining").
4. **Resolvable from project files?** No. Never released by Google in any form.
5. **Needs from user:** a decision — Path A (stop at model boundary) or Path B
   (authorise a SUBSTITUTE open model, RA-16, results quarantined).
6. **Blocks next phase?** Blocks *execution* of Phase 9 (baselines) and Phase 10
   (primary models). Does NOT block writing/testing the harness code.

## B2 — Med-PaLM checkpoint unavailable  ·  CRITICAL  ·  OPEN
1. **Missing:** the instruction-prompt-tuned Flan-PaLM 540B checkpoint.
2. **Required for:** all of §4.5 — Tables A.3–A.12; Figs 6–11; Tables 9, 10.
3. **Determined from:** §3.3.4, §4.5, A.5.
4. **Resolvable?** No. Never released.
5. **Needs from user:** same decision as B1; if Path B, also B3.
6. **Blocks next phase?** Blocks execution of Phases 11 and 14.

## B3 — 40 instruction-prompt-tuning exemplars not published  ·  HIGH  ·  OPEN
1. **Missing:** the 40 (question, ideal-answer) pairs; per-dataset split; the pool
   they were sampled and filtered from.
2. **Required for:** reproducing Med-PaLM training data (Phase 11).
3. **Determined from:** §3.3.4 lines ~688–694.
4. **Resolvable?** No — the Nature supplement released HealthSearchQA + the 140
   eval questions only, not the exemplars.
5. **Needs from user:** authorise reconstruction of 40 clinician-style exemplars
   (RA-12) OR supply exemplars.
6. **Blocks next phase?** Blocks *faithful* execution of Phase 11 (not the code).

## B4 — Human rater panels + raw ratings unavailable  ·  CRITICAL (for §4.5)  ·  OPEN
1. **Missing:** 9 qualified clinicians + 5 lay raters; the raw per-answer ratings.
2. **Required for:** §4.5 results — Tables A.3–A.12; Figs 6–11; the fairness/bias
   axis (Phase 14); lay-user axes (Phase 14).
3. **Determined from:** §3.2, §4.5 lines ~918–923.
4. **Resolvable?** No.
5. **Needs from user:** recruit raters, OR authorise an LLM-as-judge proxy
   (explicit deviation, must be validated against a small human sample), OR accept
   §4.5 as BLOCKED / not reproduced.
6. **Blocks next phase?** Blocks execution of Phases 14 and 16 (human-eval stats).

## B5 — Self-consistency sampling temperature unspecified  ·  HIGH  ·  MITIGATED
1. **Missing:** decoding temperature / top-k / top-p for the 11- and 41-decode SC.
2. **Required for:** Tables 7, A.1; Fig 5 (numbers depend on it).
3. **Determined from:** §4.4 — SC described, sampling params absent (preprint).
4. **Resolvable?** No (preprint). Nature version uses ~0.7.
5. **Mitigation:** RA-03 — temperature 0.7, sweep {0.5, 0.7, 1.0}. Documented.
6. **Blocks next phase?** No.

## B6 — PubMedQA 500/500 partition undefined  ·  MEDIUM  ·  MITIGATED
Mitigation: RA-02 — use the official `pqa_labeled` test split (500) for scoring.

## B7 — MedMCQA "dev set" ambiguity  ·  MEDIUM  ·  MITIGATED
Mitigation: RA-01 — evaluate the 4,183-row validation split; exemplars from train.

## B8 — Consumer-dataset few-shot / CoT prompts incomplete  ·  MEDIUM  ·  OPEN
1. **Missing:** full prompt sets for LiveQA / MedicationQA / HealthSearchQA
   (A.16–A.17 show only some exemplars; no consumer CoT prompts anywhere).
2. **Required for:** long-form generation (Phase 7 / Phase 10 / §4.5).
3. **Determined from:** §3.3.2, A.8–A.9.
4. **Resolvable?** Partially — reconstruct from the shown exemplars.
5. **Needs from user:** authorise reconstruction (RA-14).
6. **Blocks next phase?** No (blocks faithful §4.5 only).

## B9 — MMLU few-shot exemplar source unspecified  ·  LOW–MEDIUM  ·  MITIGATED
Mitigation: RA-06 — use the 5 official `dev` exemplars per subject.

## B10 — No random seeds anywhere in the paper  ·  MEDIUM  ·  MITIGATED
Mitigation: RA-19 — fixed project seed (0); documented that exact-draw reproduction
is impossible even with the real models.

## B11 — IPT training schedule details missing  ·  MEDIUM  ·  MITIGATED
Missing: LR schedule, warmup, max-seq-len, checkpoint cadence, explicit loss.
Mitigation: RA-10 (constant LR, no warmup, seq-len 2048) + DERIVED (token CE loss).

## B12 — MedicationQA 690→674 and HealthSearchQA 3,375→3,173  ·  LOW  ·  MITIGATED
Mitigation: RA-08 / RA-09 — documented filtering rule; released artifacts treated
as authoritative.

## B14 — LiveQA training set not at the canonical source  ·  MEDIUM  ·  MITIGATED
1. **Missing:** `TREC-2017-LiveQA-Medical-Train-{1,2}.xml` (634 QA pairs).
2. **Required for:** Table 1 "dev=634"; LiveQA few-shot exemplars; IPT exemplar pool.
3. **Determined from:** §3.1 "LiveQA", Table 1.
4. **Resolvable?** Not from the canonical repo — `github.com/abachaa/LiveQA_MedicalTask_TREC2017`
   contains ONLY `TestDataset/` (confirmed via GitHub trees API, 2026-08-31).
5. **Mitigation:** RA-20 — community mirror `truehealth/liveqa` (635 flattened QA
   pairs) acquired to `raw_data/liveqa/TrainingDatasets/train_pairs.jsonl`.
   Provenance third-party -> `UNVERIFIED`. If you have the original NIST XMLs,
   drop them in `raw_data/liveqa/TrainingDatasets/` and re-run Phase 3.
6. **Blocks next phase?** No.

## B13 — Local Python is 3.14; ML ecosystem lag  ·  LOW  ·  MITIGATED
Mitigation: RA-18′ — the model-independent stack installs and imports cleanly on
3.14.7. A substitute-model runtime (Path B) may need a separate 3.11 env.
