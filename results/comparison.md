# Phase 19 -- Paper vs Replication

Absolute-value gaps vs Flan-PaLM are EXPECTED -- a different (2024, 8B) model. The replication tests whether the paper's QUALITATIVE findings hold with the same methodology.

## Absolute comparisons (gaps expected -- different model)

| Metric | Paper | Ours | Δ | Tol (pp) | Verdict | Note |
|---|---|---|---|---|---|---|
| MedQA 4-opt few-shot | 35.4 | 59.4 | 24.0 | 1.0 | DIVERGENT (expected: different model) | vs paper Flan-PaLM 8B (same size) |
| MedQA 4-opt SC | 67.6 | 63.3 | -4.3 | 1.5 | DIVERGENT (expected: different model) | vs paper Flan-PaLM 540B |
| MedMCQA few-shot | 34.5 | None | None | 1.0 | NOT-ATTEMPTED | vs Flan-PaLM 8B |
| PubMedQA few-shot | 67.6 | None | None | 1.5 | NOT-ATTEMPTED | vs Flan-PaLM 8B |
| MMLU anatomy SC | 71.9 | None | None | 4.0 | NOT-ATTEMPTED | vs Flan-PaLM 540B (approx) |
| MMLU clinical_knowledge SC | 80.4 | None | None | 4.0 | NOT-ATTEMPTED | vs Flan-PaLM 540B (approx) |
| MMLU college_medicine SC | 76.3 | None | None | 4.0 | NOT-ATTEMPTED | vs Flan-PaLM 540B (approx) |
| MMLU medical_genetics SC | 74.0 | None | None | 4.0 | NOT-ATTEMPTED | vs Flan-PaLM 540B (approx) |
| MMLU professional_medicine SC | 83.5 | None | None | 4.0 | NOT-ATTEMPTED | vs Flan-PaLM 540B (approx) |
| MMLU college_biology SC | 88.9 | None | None | 4.0 | NOT-ATTEMPTED | vs Flan-PaLM 540B (approx) |

## Qualitative findings (the replication payoff)

| Finding | Verdict | Detail |
|---|---|---|
| SC beats few-shot on MedQA | **REPRODUCED-QUALITATIVELY** | ours: FS 59.4 -> SC 63.3; paper 60.3 -> 67.6 |
| SC beats few-shot on MedMCQA | **NOT-ATTEMPTED** | ours: FS None -> SC None; paper 56.5 -> 57.6 |
| SC hurts PubMedQA | **NOT-ATTEMPTED** | ours: FS None -> SC None; paper 79.0 -> 75.2 |
| CoT does not beat few-shot on MC (MedQA/MedMCQA/PubMedQA) | **NOT-ATTEMPTED** | ours FS/CoT -- MedQA 59.4/60.5, MedMCQA None/None, PubMedQA None/None |
| Selective-prediction accuracy rises with deferral | **REPRODUCED-QUALITATIVELY** | ours points: [(0.0, 0.636), (0.05, 0.6547), (0.1, 0.6644), (0.15, 0.6776), (0.2, 0.7), (0.25, 0.704), (0.3, 0.7343), (0.35, 0.7415), (0.4, 0.7567), (0.45, 0.7927)] |
| Instruction tuning helps (PaLM < Flan-PaLM) | **NOT-ATTEMPTED** | requires the model's non-instruct base -- not run (single model) |
| Scaling helps (~2x 8B->540B) | **NOT-ATTEMPTED** | requires >= 2 model sizes -- see Phase 13 |

## Not reproduced

- Med-PaLM / instruction prompt tuning (B1/B2)
- All human evaluation, Section 4.5 (B4)
- Scaling curves (single model)
