# Table 5 -- few-shot accuracy % (paper: PaLM/Flan-PaLM x 3 sizes; ours: substitute)

> Substitute-model numbers. NOT a reproduction of PaLM/Flan-PaLM/Med-PaLM. Absolute gaps vs the paper are expected; only the qualitative direction is tested (see results/comparison.md).

_Model: Qwen/Qwen2.5-7B-Instruct@a09a35458c70 — SUBSTITUTE (RA-16/RA-24)_

| Dataset | Paper Flan-PaLM 8B | Paper Flan-PaLM 540B | Ours (8B substitute) | Δ vs paper 8B |
|---|---|---|---|---|
| MedQA 4-opt | 35.4 | 60.3 | 59.4 | 24.0 |
| MedMCQA | 34.5 | 56.5 | 56.6 | 22.1 |
| PubMedQA | 67.6 | 79.0 | 72.8 | 5.2 |
