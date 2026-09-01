# Table 7 -- few-shot vs self-consistency

> Substitute-model numbers. NOT a reproduction of PaLM/Flan-PaLM/Med-PaLM. Absolute gaps vs the paper are expected; only the qualitative direction is tested (see results/comparison.md).

_Model: Qwen/Qwen2.5-7B-Instruct@a09a35458c70 — SUBSTITUTE (RA-16/RA-24)_

| Dataset | Paper FS | Paper SC | Ours FS | Ours SC | Ours Δ(SC-FS) |
|---|---|---|---|---|---|
| MedQA 4-opt | 60.3 | 67.6 | 59.4 | 63.3 | 3.9 |
| MedMCQA | 56.5 | 57.6 | 56.6 | - | - |
| PubMedQA | 79.0 | 75.2 | 72.8 | - | - |
