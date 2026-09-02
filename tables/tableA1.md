# Table A.1 -- MMLU clinical topics

> Substitute-model numbers. NOT a reproduction of PaLM/Flan-PaLM/Med-PaLM. Absolute gaps vs the paper are expected; only the qualitative direction is tested (see results/comparison.md).

_Model: Qwen/Qwen2.5-7B-Instruct@a09a35458c70 — SUBSTITUTE (RA-16/RA-24)_

Paper columns are Flan-PaLM / PaLM 540B (blocker B1 -- not reproducible). `Ours` is the substitute model.

| Subject | Paper PaLM-540B FS | Paper FlanPaLM-540B FS | Paper FlanPaLM CoT | Paper FlanPaLM SC | Ours FS | Ours CoT | Ours SC |
|---|---|---|---|---|---|---|---|
| anatomy | 63.7 | 65.2 | 66.7 | 71.9 | 71.9 | 70.4 | 71.1 |
| clinical_knowledge | 76.2 | 77.0 | 77.0 | 80.4 | 78.9 | 79.6 | 80.0 |
| college_medicine | 68.2 | 69.9 | 71.1 | 76.3 | 65.9 | 75.1 | 76.9 |
| medical_genetics | 68.0 | 70.0 | 75.0 | 74.0 | 81.0 | 86.0 | 84.0 |
| professional_medicine | 75.0 | 83.8 | 76.5 | 83.5 | 76.1 | 76.1 | 78.3 |
| college_biology | 87.5 | 87.5 | 83.3 | 88.9 | 82.6 | 84.7 | 86.1 |
