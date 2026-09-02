# Replication outcome -- headline statement

This project **reproduces the MultiMedQA benchmark and the multiple-choice evaluation
methodology** (few-shot / chain-of-thought / self-consistency / selective prediction)
of *"Large Language Models Encode Clinical Knowledge"* (Singhal et al.,
arXiv:2212.13138v1), applied to a **substitute open model: `Qwen/Qwen2.5-7B-Instruct@a09a35458c70`**.

It is **NOT an exact replication**. The paper's models were never released.

It **does NOT reproduce**:
- **PaLM / Flan-PaLM** at any size -- unavailable. Every accuracy here is from `Qwen/Qwen2.5-7B-Instruct@a09a35458c70`,
  a different model; absolute values are not comparable and are labelled
  `REPLICATION ASSUMPTION -- SUBSTITUTE MODEL`.
- **Med-PaLM** / instruction prompt tuning (Sections 3.3.3-3.3.4, A.1, A.6) -- needs the
  frozen Flan-PaLM 540B weights (blockers B1/B2).
- **Any human-evaluation result** (Sections 3.2, 4.5; Tables A.3-A.12; Figures 6-11) --
  needs a recruited panel of 9 clinicians + 5 lay raters (blocker B4).
- The **scaling curves** (Figures A.1, A.2) -- a single model size was run.

## Do the paper's qualitative findings hold on the substitute model?

- **REPRODUCED-QUALITATIVELY** — SC beats few-shot on MedQA (ours: FS 59.4 -> SC 63.3; paper 60.3 -> 67.6)
- **REPRODUCED-QUALITATIVELY** — SC beats few-shot on MedMCQA (ours: FS 56.6 -> SC 58.5; paper 56.5 -> 57.6)
- **DIVERGENT** — SC hurts PubMedQA (ours: FS 72.8 -> SC 73.6; paper 79.0 -> 75.2)
- **DIVERGENT** — CoT does not beat few-shot on MC (MedQA/MedMCQA/PubMedQA) (ours FS/CoT -- MedQA 59.4/60.5, MedMCQA 56.6/56.4, PubMedQA 72.8/74.8)
- **REPRODUCED-QUALITATIVELY** — Selective-prediction accuracy rises with deferral (ours points: [(0.0, 0.6292), (0.05, 0.6452), (0.1, 0.6632), (0.15, 0.671), (0.2, 0.6945), (0.25, 0.7047), (0.3, 0.7273), (0.35, 0.7388), (0.4, 0.7513), (0.45, 0.7657)])
- **NOT-ATTEMPTED** — Instruction tuning helps (PaLM < Flan-PaLM) (requires the model's non-instruct base -- not run (single model))
- **NOT-ATTEMPTED** — Scaling helps (~2x 8B->540B) (requires >= 2 model sizes -- see Phase 13)

Full analysis: **`docs/REPLICATION_REPORT.md`**. Numbers + tolerances: `results/comparison.md`.
