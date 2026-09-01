# Reproducibility

- Substitute model (RA-16): `Qwen/Qwen2.5-7B-Instruct` @ `a09a35458c702b33eeacc393d103063234e8bc28` via local vLLM (config `configs/model/qwen25-7b-local.yaml`)
- Prediction namespace: `derived_data/predictions/qwen25-7b-local/`
- Global seed: 0 (RA-19; paper reports none)
- Decode params: see the model config `decode:` block
- Data provenance + SHA-256: `metadata/data_provenance.md`
- Env: `requirements.txt` (pinned) + `requirements.lock.txt` (full freeze), CPython 3.14.7; GPU runtime `requirements-pathb.txt` (record what resolved)
- Deterministic: `python run.py phase01..phase08` reproduces `processed_data/` + `tables/table1_reproduced.*` byte-identically.
- Greedy decoding (few-shot / CoT) is deterministic per (revision, GPU arch, vLLM version). Sampled decoding (Phases 12/14/15) varies within the Phase-15 variance (RA-25).

- VERIFIED: original untouched: project_healthcare_.pdf
- VERIFIED: original untouched: data.zip
- VERIFIED: original untouched: data_clean.zip
- VERIFIED: original untouched: LiveQA_MedicalTask_TREC2017-master.zip
- VERIFIED: original untouched: MedInfo2019-QA-Medications.xlsx
- VERIFIED: original untouched: 41586_2023_6291_MOESM6_ESM.xlsx
- PASS: phase04 re-run is byte-identical (Table1 + 3 processed files)
- PASS: requirements.lock.txt present
- PASS: model config records model id + decode params
- PASS: substitute model frozen to an exact HF revision (RA-16)
- PASS: no unseeded RNG in src/ (excl. mock, seeding)
