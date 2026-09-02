# Phase 19 -- Paper vs Replication

Absolute-value gaps vs Flan-PaLM are EXPECTED -- a different (2024, 8B) model. The replication tests whether the paper's QUALITATIVE findings hold with the same methodology.

## Absolute comparisons (gaps expected -- different model)

| Metric | Paper | Ours | Δ | Tol (pp) | Verdict | Note |
|---|---|---|---|---|---|---|
| MedQA 4-opt few-shot | 35.4 | 59.4 | 24.0 | 1.0 | DIVERGENT (expected: different model) | vs paper Flan-PaLM 8B (same size) |
| MedQA 4-opt SC | 67.6 | 63.3 | -4.3 | 1.5 | DIVERGENT (expected: different model) | vs paper Flan-PaLM 540B |
| MedMCQA few-shot | 34.5 | 56.6 | 22.1 | 1.0 | DIVERGENT (expected: different model) | vs Flan-PaLM 8B |
| PubMedQA few-shot | 67.6 | 72.8 | 5.2 | 1.5 | DIVERGENT (expected: different model) | vs Flan-PaLM 8B |
| MMLU anatomy SC | 71.9 | 71.1 | -0.8 | 4.0 | WITHIN-TOLERANCE | vs Flan-PaLM 540B (approx) |
| MMLU clinical_knowledge SC | 80.4 | 80.0 | -0.4 | 4.0 | WITHIN-TOLERANCE | vs Flan-PaLM 540B (approx) |
| MMLU college_medicine SC | 76.3 | 76.9 | 0.6 | 4.0 | WITHIN-TOLERANCE | vs Flan-PaLM 540B (approx) |
| MMLU medical_genetics SC | 74.0 | 84.0 | 10.0 | 4.0 | DIVERGENT (expected: different model) | vs Flan-PaLM 540B (approx) |
| MMLU professional_medicine SC | 83.5 | 78.3 | -5.2 | 4.0 | DIVERGENT (expected: different model) | vs Flan-PaLM 540B (approx) |
| MMLU college_biology SC | 88.9 | 86.1 | -2.8 | 4.0 | WITHIN-TOLERANCE | vs Flan-PaLM 540B (approx) |

## Qualitative findings (the replication payoff)

| Finding | Verdict | Detail |
|---|---|---|
| SC beats few-shot on MedQA | **REPRODUCED-QUALITATIVELY** | ours: FS 59.4 -> SC 63.3; paper 60.3 -> 67.6 |
| SC beats few-shot on MedMCQA | **REPRODUCED-QUALITATIVELY** | ours: FS 56.6 -> SC 58.5; paper 56.5 -> 57.6 |
| SC hurts PubMedQA | **DIVERGENT** | ours: FS 72.8 -> SC 73.6; paper 79.0 -> 75.2 |
| CoT does not beat few-shot on MC (MedQA/MedMCQA/PubMedQA) | **DIVERGENT** | ours FS/CoT -- MedQA 59.4/60.5, MedMCQA 56.6/56.4, PubMedQA 72.8/74.8 |
| Selective-prediction accuracy rises with deferral | **REPRODUCED-QUALITATIVELY** | ours points: [(0.0, 0.6292), (0.05, 0.6452), (0.1, 0.6632), (0.15, 0.671), (0.2, 0.6945), (0.25, 0.7047), (0.3, 0.7273), (0.35, 0.7388), (0.4, 0.7513), (0.45, 0.7657)] |
| Instruction tuning helps (PaLM < Flan-PaLM) | **NOT-ATTEMPTED** | requires the model's non-instruct base -- not run (single model) |
| Scaling helps (~2x 8B->540B) | **NOT-ATTEMPTED** | requires >= 2 model sizes -- see Phase 13 |

## Repeated-run variance (Phase 15)

Four MedQA 4-option self-consistency runs (n=11 decodes, 1,273 examples each):

| Run | Accuracy % |
|---|---:|
| Run 0 | 62.45 |
| Run 1 | 62.37 |
| Run 2 | 62.69 |
| Run 3 | 62.84 |
| **Mean** | **62.587** |
| **Population variance** | **0.0351** |
| **Population stdev** | **0.187** |

Paper reports variance **0.078** over four runs for Flan-PaLM 540B (A.2). Different model -> loose methodological comparison only.

## Not reproduced

- Med-PaLM / instruction prompt tuning (B1/B2)
- All human evaluation, Section 4.5 (B4)
- Scaling curves (single model)
