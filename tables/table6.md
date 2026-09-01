# Table 6 -- few-shot vs CoT

> Substitute-model numbers. NOT a reproduction of PaLM/Flan-PaLM/Med-PaLM. Absolute gaps vs the paper are expected; only the qualitative direction is tested (see results/comparison.md).

_Model: Qwen/Qwen2.5-7B-Instruct@a09a35458c70 — SUBSTITUTE (RA-16/RA-24)_

| Dataset | Paper FS | Paper CoT | Ours FS | Ours CoT | Ours Δ(CoT-FS) |
|---|---|---|---|---|---|
| MedQA 4-opt | 60.3 | 60.3 | 59.4 | 60.5 | 1.1 |
| MedMCQA | 56.5 | 53.6 | 56.6 | - | - |
| PubMedQA | 79.0 | 77.2 | 72.8 | - | - |
