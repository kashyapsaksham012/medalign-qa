# Phase 3 — Dataset Verification Report

_generated 2026-09-01T08:58:20Z_

| status | dataset | check | expected | observed | evidence | note |
|---|---|---|---|---|---|---|
| PASS | medqa_usmle_4opt | train row count | `10178` | `10178` | DATASET-VERIFIED |  |
| PASS | medqa_usmle_4opt | dev row count | `1272` | `1272` | DATASET-VERIFIED |  |
| PASS | medqa_usmle_4opt | test row count | `1273` | `1273` | DATASET-VERIFIED |  |
| PASS | medqa_usmle_4opt | dev(=train+dev) == paper 11450 | `11450` | `11450` | PAPER-SPECIFIED |  |
| PASS | medqa_usmle_4opt | n options | `4` | `4` | PAPER-SPECIFIED |  |
| PASS | medqa_usmle_4opt | gold present (answer_idx) all rows | `True` | `True` | DATASET-VERIFIED |  |
| PASS | medmcqa | train row count | `182822` | `182822` | DATASET-VERIFIED |  |
| PASS | medmcqa | dev row count | `4183` | `4183` | DATASET-VERIFIED |  |
| PASS | medmcqa | test row count | `6150` | `6150` | DATASET-VERIFIED |  |
| PASS | medmcqa | cop indexing | `one_based (1..4)` | `[1, 2, 3, 4]` | DATASET-VERIFIED |  |
| PASS | medmcqa | test labels withheld | `0` | `0` | DATASET-VERIFIED | test split unusable for scoring -> eval on valid (RA-01) |
| PASS | pubmedqa | labeled total | `1000` | `1000` | UNVERIFIED |  |
| PASS | pubmedqa | label set | `{'no', 'yes', 'maybe'}` | `{'yes', 'no', 'maybe'}` | PAPER-SPECIFIED |  |
| PASS | pubmedqa | official test split size | `500` | `500` | PAPER-SPECIFIED | paper Table 1: 500 test (RA-02) |
| PASS | mmlu | anatomy/dev 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | anatomy/validation 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | anatomy/test 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | anatomy/test row count | `135` | `135` | PAPER-SPECIFIED |  |
| PASS | mmlu | anatomy/validation == paper 'dev' | `14` | `14` | DATASET-VERIFIED | paper Table 1 'dev' column == MMLU validation split size |
| PASS | mmlu | anatomy/dev == 5-shot source | `5` | `5` | REPLICATION ASSUMPTION | RA-06: few-shot exemplars from the 5-row dev split |
| PASS | mmlu | clinical_knowledge/dev 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | clinical_knowledge/validation 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | clinical_knowledge/test 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | clinical_knowledge/test row count | `265` | `265` | PAPER-SPECIFIED |  |
| PASS | mmlu | clinical_knowledge/validation == paper 'dev' | `29` | `29` | DATASET-VERIFIED | paper Table 1 'dev' column == MMLU validation split size |
| PASS | mmlu | clinical_knowledge/dev == 5-shot source | `5` | `5` | REPLICATION ASSUMPTION | RA-06: few-shot exemplars from the 5-row dev split |
| PASS | mmlu | college_medicine/dev 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | college_medicine/validation 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | college_medicine/test 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | college_medicine/test row count | `173` | `173` | PAPER-SPECIFIED |  |
| PASS | mmlu | college_medicine/validation == paper 'dev' | `22` | `22` | DATASET-VERIFIED | paper Table 1 'dev' column == MMLU validation split size |
| PASS | mmlu | college_medicine/dev == 5-shot source | `5` | `5` | REPLICATION ASSUMPTION | RA-06: few-shot exemplars from the 5-row dev split |
| PASS | mmlu | medical_genetics/dev 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | medical_genetics/validation 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | medical_genetics/test 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | medical_genetics/test row count | `100` | `100` | PAPER-SPECIFIED |  |
| PASS | mmlu | medical_genetics/validation == paper 'dev' | `11` | `11` | DATASET-VERIFIED | paper Table 1 'dev' column == MMLU validation split size |
| PASS | mmlu | medical_genetics/dev == 5-shot source | `5` | `5` | REPLICATION ASSUMPTION | RA-06: few-shot exemplars from the 5-row dev split |
| PASS | mmlu | professional_medicine/dev 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | professional_medicine/validation 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | professional_medicine/test 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | professional_medicine/test row count | `272` | `272` | PAPER-SPECIFIED |  |
| PASS | mmlu | professional_medicine/validation == paper 'dev' | `31` | `31` | DATASET-VERIFIED | paper Table 1 'dev' column == MMLU validation split size |
| PASS | mmlu | professional_medicine/dev == 5-shot source | `5` | `5` | REPLICATION ASSUMPTION | RA-06: few-shot exemplars from the 5-row dev split |
| PASS | mmlu | college_biology/dev 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | college_biology/validation 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | college_biology/test 6 cols | `True` | `True` | DERIVED FROM PAPER |  |
| PASS | mmlu | college_biology/test row count | `144` | `144` | PAPER-SPECIFIED |  |
| PASS | mmlu | college_biology/validation == paper 'dev' | `16` | `16` | DATASET-VERIFIED | paper Table 1 'dev' column == MMLU validation split size |
| PASS | mmlu | college_biology/dev == 5-shot source | `5` | `5` | REPLICATION ASSUMPTION | RA-06: few-shot exemplars from the 5-row dev split |
| PASS | liveqa | test questions | `104` | `104` | DATASET-VERIFIED |  |
| CAVEAT | liveqa | train QA pairs (truehealth mirror, RA-20) | `~634 (paper Table 1)` | `635` | UNVERIFIED | third-party mirror; paper 'dev'=634 (388+246); mirror flattens to QA pairs |
| PASS | medicationqa | raw row count | `690` | `690` | DATASET-VERIFIED |  |
| PASS | medicationqa | columns | `['Question', 'Focus (Drug)', 'Question Type', 'Answer', 'Section Title', 'URL']` | `['Question', 'Focus (Drug)', 'Question Type', 'Answer', 'Section Title', 'URL']` | DATASET-VERIFIED |  |
| PASS | medicationqa | non-empty Q&A rows | `690` | `690` | DATASET-VERIFIED | all 690 rows have Q and A; 651 distinct questions |
| CAVEAT | medicationqa | paper's 674 reconstructable? | `674` | `no` | CANNOT BE DETERMINED FROM AVAILABLE MATERIALS | RA-08: released file has 690 rows; 674 cannot be derived; use all 690 |
| PASS | healthsearchqa | sheet1 non-empty questions | `3173` | `3173` | DATASET-VERIFIED | paper states 3375 (CANNOT BE DETERMINED why 3173) |
| PASS | healthsearchqa | sheet2 human-eval subset | `140` | `140` | PAPER-SPECIFIED |  |

## Summary

- **CAVEAT**: 2
- **PASS**: 56
