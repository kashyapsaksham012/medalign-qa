# Model card -- substitute model for the Path B replication

| Field | Value |
|---|---|
| Model | `Qwen/Qwen2.5-7B-Instruct@a09a35458c70` |
| Role | substitute for PaLM/Flan-PaLM (RA-16) -- NOT Med-PaLM, NOT an exact reproduction |
| Prompting | verbatim paper exemplar blocks (Tables A.13-A.21) + RA-24 chat wrapper |
| Few-shot | 5-shot MedQA/MedMCQA (PAPER-SPECIFIED), 3-shot PubMedQA (PAPER-SPECIFIED), 5-shot MMLU (RA-06 assumption) |
| Self-consistency | 11 decodes (PAPER-SPECIFIED), temperature 0.7 (RA-03), plurality vote |
| Selective prediction | 41 decodes (PAPER-SPECIFIED), CoT+SC, MedQA only |
| Evaluation splits | MedQA 4+5-opt test, MedMCQA validation (RA-01), PubMedQA test-500 (RA-02), MMLU x6 test |
| Not evaluated | long-form / human-eval datasets (out of scope, B4) |
| Intended use | methodology replication + contemporary benchmark; research only |
