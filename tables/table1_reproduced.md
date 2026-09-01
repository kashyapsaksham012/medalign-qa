# Table 1 (reproduced) — MultiMedQA dataset sizes

Match = `exact` (identical) · `~rounding` (paper rounds this figure; within its rounding step) · `test exact` · `see note` (documented deviation — RA-xx).

| Dataset | Format | Reproduced dev | Reproduced test | Paper dev | Paper test | Match | Note |
|---|---|---|---|---|---|---|---|
| MedQA (USMLE, 4-opt) | Q+A, 4 choices | 11450 | 1273 | 11450 | 1273 | exact |  |
| MedMCQA | Q+A, 4 choices | 187005 | 6150 | 187000 | 6100 | ~rounding | scored split: validation (n=4183, RA-01 (test labels withheld; paper 'dev set' ambiguous)). dev = train+validation = 187005 ~= 187000 (paper rounds 'over 187k'); test = 6150 ~= 6100. Scoring is on the 4183 validation split (RA-01). |
| PubMedQA | Q+context+A (yes/no/maybe) | 500 | 500 | 500 | 500 | exact |  |
| MMLU (6 clinical subjects, sum) | Q+A, 4 choices | 123 | 1089 | 123 | 1089 | exact |  |
| LiveQA TREC-2017 | Q + long answer | 635 | 104 | 634 | 104 | test exact | train from community mirror (RA-20) |
| MedicationQA | Q + long answer | 0 | 690 | None | 674 | see note | released file has 690 rows; paper's 674 not reconstructable (RA-08) |
| HealthSearchQA | Q only + long answer | None | 3173 | None | 3375 | see note | released file has 3173 questions (RA-09) |
