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

What IS tested: whether the paper's **qualitative findings** hold under the same
methodology (SC helps MedQA/MedMCQA, hurts PubMedQA; CoT does not beat few-shot on MC;
selective-prediction accuracy rises with deferral). See `results/comparison.md`.
