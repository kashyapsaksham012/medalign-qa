# Data Provenance

All inputs to the MultiMedQA replication. Raw data is **immutable**: originals are
never modified; `raw_data/` holds canonical copies/extracts; `processed_data/` and
`derived_data/` hold everything computed.

## 1. User-provided originals (present at repo root, NEVER modified)

| File | Size (bytes) | SHA-256 | Identified as | Verification |
|---|---|---|---|---|
| `project_healthcare_.pdf` | 1,438,481 | `e83a6fecf5820a49b2b1c716f4c1839a7301300a6e27aa53c3cb7212b7db9f4e` | arXiv:2212.13138v1, *Large Language Models Encode Clinical Knowledge* | full text + appendix read |
| `data.zip` | 55,285,460 | `16c1fbc6f47d548d2af7837b18e893aa45f45c0be9bda0a9adfff3c625bf9262` | **MedMCQA** official (train/dev/test JSONL) | 182,822 / 4,183 / 6,150; schema + 1-indexed `cop` verified |
| `data_clean.zip` | 131,741,885 | `1c2ca8130b3d86d9a99a432ab9bef14f3bb9807bef20facd9ac86ba36960f629` | **MedQA** (Jin et al. 2021) full data dir | US 4-opt 10,178 / 1,272 / 1,273; `answer_idx` present |
| `LiveQA_MedicalTask_TREC2017-master.zip` | 302,424 | `ea56456197b5714f7c2af67410c7fa881cab5b1b459f300abe5c92d1b72379ae` | **LiveQA TREC-2017 Medical** â€” TEST split + qrels only | 104 test questions verified; **training set absent** |
| `MedInfo2019-QA-Medications.xlsx` | 163,497 | `4f13d0e3b195bd6a5d72a1872f9118cb5f69fd02c370001695330cfc9e3b5832` | **MedicationQA** (Abacha et al. 2019) | sheet `DrugQA`, 690 rows, 6 columns verified |
| `41586_2023_6291_MOESM6_ESM.xlsx` | 72,573 | `a89f6639ee76717e2a1ea25bbe25c8c69cf396681be76fd8145da7e9c8917e1e` | **HealthSearchQA** â€” Nature (2023) Supplementary Data 6 | sheet1 = 3,173 questions; sheet2 = 140 human-eval subset |

Hashes recorded 2026-08-31 (session start).

## 2. Datasets still to acquire (Phase 2)

| Dataset | Official source | Exact target | Place in repo | Verify |
|---|---|---|---|---|
| **PubMedQA** `pqa_labeled` | `github.com/pubmedqa/pubmedqa` | `data/ori_pqal.json` (1,000) + `data/test_ground_truth.json` (500) | `raw_data/pubmedqa/` | `len==1000`; labels âŠ† {yes,no,maybe}; test split == 500 |
| **MMLU** (6 subjects) | `people.eecs.berkeley.edu/~hendrycks/data.tar` (fallback HF `cais/mmlu`) | `{subject}_dev.csv`, `{subject}_test.csv` for the 6 subjects | `raw_data/mmlu/{subject}/` | per-subject counts == `metadata/expected_counts.yaml` |
| **LiveQA training set** | `github.com/abachaa/LiveQA_MedicalTask_TREC2017` | `TrainingDatasets/TREC-2017-LiveQA-Medical-Train-1.xml`, `-Train-2.xml` | `raw_data/liveqa/TrainingDatasets/` | Train-1 = 200 `<NLM-QUESTION>`; pairs 388 + 246 = 634 |

Download URLs, retrieval timestamps, and SHA-256 of each downloaded file will be
appended here by `scripts/phase02_acquire.py`.

## 3. Unobtainable inputs (see docs/blockers.md)

| Input | Status | Blocker |
|---|---|---|
| PaLM / Flan-PaLM (8B/62B/540B) | never publicly released | B1 (CRITICAL) |
| Med-PaLM checkpoint | never released | B2 (CRITICAL) |
| 40 instruction-prompt-tuning exemplars | not in the Nature supplement | B3 (HIGH) |
| Human-eval raw ratings (Tables A.3â€“A.12) | not released | B4 (CRITICAL for Â§4.5) |
| 9 clinician + 5 lay raters | human study participants | B4 |

## 2b. Actually acquired (Phase 2, 2026-08-31T08:47:22Z)

| dest | method | source | bytes | sha256 (prefix) |
|---|---|---|---|---|
| `raw_data\pubmedqa\ori_pqal.json` | download | https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/ori_pqal.json | 2584787 | `8b3276be8942ebbd` |
| `raw_data\pubmedqa\test_ground_truth.json` | download | https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/test_ground_truth.json | 11414 | `939fe566f09017d1` |
| `raw_data\liveqa\TrainingDatasets\train.parquet` | download | https://huggingface.co/datasets/truehealth/liveqa/resolve/main/data/train-00000-of-00001-04a338ea541d09e8.parquet | 429730 | `615b1d30ed6d24fd` |
| `raw_data\liveqa\TrainingDatasets\train_pairs.jsonl` | parquet->jsonl | derived from train.parquet (truehealth/liveqa) | 945751 | `57d9433d4d9d15eb` |
| `raw_data\mmlu\anatomy\dev.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/anatomy/dev-00000-of-00001.parquet | 3503 | `1774b4af192a38e8` |
| `raw_data\mmlu\anatomy\dev.csv` | parquet->csv | cais/mmlu::anatomy/dev (parquet->csv) | 835 | `21efbd19218d8f97` |
| `raw_data\mmlu\anatomy\test.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/anatomy/test-00000-of-00001.parquet | 20078 | `cb88f5920b67ab29` |
| `raw_data\mmlu\anatomy\test.csv` | parquet->csv | cais/mmlu::anatomy/test (parquet->csv) | 29979 | `faabf8932ede8f63` |
| `raw_data\mmlu\clinical_knowledge\dev.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/clinical_knowledge/dev-00000-of-00001.parquet | 3669 | `105b492234b3de90` |
| `raw_data\mmlu\clinical_knowledge\dev.csv` | parquet->csv | cais/mmlu::clinical_knowledge/dev (parquet->csv) | 1080 | `4b04b73385e4dfd4` |
| `raw_data\mmlu\clinical_knowledge\test.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/clinical_knowledge/test-00000-of-00001.parquet | 40510 | `7bd3de302db35c6e` |
| `raw_data\mmlu\clinical_knowledge\test.csv` | parquet->csv | cais/mmlu::clinical_knowledge/test (parquet->csv) | 56564 | `1e63c7b42592555e` |
| `raw_data\mmlu\college_medicine\dev.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/college_medicine/dev-00000-of-00001.parquet | 4838 | `85bf7f27b795f63a` |
| `raw_data\mmlu\college_medicine\dev.csv` | parquet->csv | cais/mmlu::college_medicine/dev (parquet->csv) | 1550 | `0025d8b1c0eb1833` |
| `raw_data\mmlu\college_medicine\test.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/college_medicine/test-00000-of-00001.parquet | 42470 | `f21b3166975dbc14` |
| `raw_data\mmlu\college_medicine\test.csv` | parquet->csv | cais/mmlu::college_medicine/test (parquet->csv) | 78507 | `5b8999eb0f48627e` |
| `raw_data\mmlu\medical_genetics\dev.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/medical_genetics/dev-00000-of-00001.parquet | 3766 | `a3e66d3e161967c0` |
| `raw_data\mmlu\medical_genetics\dev.csv` | parquet->csv | cais/mmlu::medical_genetics/dev (parquet->csv) | 957 | `a3546a021f83d793` |
| `raw_data\mmlu\medical_genetics\test.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/medical_genetics/test-00000-of-00001.parquet | 16379 | `f5535475f3afc347` |
| `raw_data\mmlu\medical_genetics\test.csv` | parquet->csv | cais/mmlu::medical_genetics/test (parquet->csv) | 18522 | `eec6dcf8ad1a8c26` |
| `raw_data\mmlu\professional_medicine\dev.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/professional_medicine/dev-00000-of-00001.parquet | 8445 | `899036c8f5d8c035` |
| `raw_data\mmlu\professional_medicine\dev.csv` | parquet->csv | cais/mmlu::professional_medicine/dev (parquet->csv) | 3683 | `d34caf740e4a0ff1` |
| `raw_data\mmlu\professional_medicine\test.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/professional_medicine/test-00000-of-00001.parquet | 124933 | `8c1c18b16c9865bf` |
| `raw_data\mmlu\professional_medicine\test.csv` | parquet->csv | cais/mmlu::professional_medicine/test (parquet->csv) | 211587 | `9b5ea954574b00e4` |
| `raw_data\mmlu\college_biology\dev.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/college_biology/dev-00000-of-00001.parquet | 4273 | `0cf3cbb4fde72b09` |
| `raw_data\mmlu\college_biology\dev.csv` | parquet->csv | cais/mmlu::college_biology/dev (parquet->csv) | 1408 | `c205e641597cb024` |
| `raw_data\mmlu\college_biology\test.parquet` | download | https://huggingface.co/datasets/cais/mmlu/resolve/main/college_biology/test-00000-of-00001.parquet | 31845 | `5b6920ddbbb40ee6` |
| `raw_data\mmlu\college_biology\test.csv` | parquet->csv | cais/mmlu::college_biology/test (parquet->csv) | 45495 | `3c0eef8c13add72b` |
