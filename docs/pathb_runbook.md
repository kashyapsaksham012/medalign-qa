# Path B run-book — substitute model on free GPU

Path B (RA-16): run `Qwen/Qwen2.5-7B-Instruct` (frozen HF revision) through the
MedAlign-QA harness on a **free** Kaggle or Colab GPU. No paid API. Every number
is `REPLICATION ASSUMPTION — SUBSTITUTE MODEL` — not a reproduction of Flan-PaLM.

Estimated GPU time (Kaggle T4, MedQA-only first pass, RA-27):
few-shot ~2 min · CoT ~15 min · self-consistency n=11 ~2 h · selective prediction
n=41 on 500 Q ~1 h · variance 4×SC ~2 h. Well inside Kaggle's 30 GPU-h/week.

---

## 0. One-time, on your normal machine (has internet, no GPU needed)

```bash
python scripts/pin_model.py              # resolves Qwen2.5-7B-Instruct @ main -> commit SHA
git add configs/model/qwen25-7b-local.yaml
git commit -m "chore(pathb): freeze substitute model to <sha>"
git push                                  # so Kaggle can clone the pinned config
```

`scripts/pin_model.py` needs `huggingface-hub` (`pip install huggingface-hub`).
Until `revision:` is a real SHA, every phase refuses to load the model and Phase 18
reports CHECK — that is the guard working.

Also: **rotate the leaked keys** (OpenRouter + Groq) and clear `.env` — Path B does
not use them. `HF_TOKEN` is only needed for a gated model; Qwen2.5 is ungated.

---

## 1. Make the data dataset (once)

Only MedQA is needed for the first pass. On your machine, upload these two files as a
**private Kaggle Dataset** (kaggle.com/datasets → New Dataset → drag the files):

    processed_data/medqa_usmle_4opt.jsonl
    processed_data/medqa_usmle_5opt.jsonl

Name it e.g. `medalign-medqa`. `scripts/kaggle_pathb.py --run` scans `/kaggle/input/**`
for `medqa_usmle_*.jsonl` and stages them automatically — no path wiring needed.

## 2. Private-repo access (once)

The repo is private, so Kaggle needs a GitHub token:
1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained →
   new token, **read-only Contents** on `medalign-qa`, 30-day expiry.
2. Kaggle notebook → Add-ons → Secrets → add `GH_TOKEN` = that token.

---

## 3. Kaggle notebook

1. New Notebook → Settings → **Accelerator: GPU T4 x2**, **Internet: On**,
   **Add data → your `medalign-medqa` dataset**.
2. Cells:

```python
from kaggle_secrets import UserSecretsClient
tok = UserSecretsClient().get_secret("GH_TOKEN")
!git clone https://{tok}@github.com/kashyapsaksham012/medalign-qa.git mq && cd mq && git log -1 --oneline
%cd mq

!python scripts/kaggle_pathb.py --setup     # vllm install (~10 min) + GPU/pin check
!python scripts/kaggle_pathb.py --run       # stages data, phases 9-20 (MedQA-only), packages
```

3. `--run` writes `pathb_artifacts.zip` (results/, tables/, figures/, logs/,
   `derived_data/predictions/qwen25-7b-local/`, `requirements-pathb.lock.txt`).
   Download it from the notebook's Output tab.

For a dry run first: `!python scripts/run_pathb_pipeline.py --mock` (no GPU, ~4 min,
confirms every phase is wired).

Full MC sweep later (adds MedMCQA / PubMedQA / MMLU): `--run --all`.

---

## 3. Back on your machine

```bash
unzip pathb_artifacts.zip -d .
python run.py phase19        # regenerate results/comparison.md locally from the predictions
git add results/ tables/ figures/ derived_data/predictions/qwen25-7b-local/
git commit -m "feat(pathb): MedQA substitute-model results (Qwen2.5-7B @ <sha>)"
```

Check `results/comparison.md`: absolute gaps vs Flan-PaLM are **expected** (7B, 2024,
general model). What the replication tests is whether the paper's *qualitative* findings
hold — SC > few-shot on MedQA, selective-prediction accuracy rising with deferral, etc.

---

## Notes / gotchas

- **1× vs 2× T4**: 7B bf16 @ 4k ctx fits one T4. If vLLM OOMs, set
  `tensor_parallel_size: 2` in the config or lower `gpu_memory_utilization`.
- **Session timeout**: Kaggle interactive sessions stop after ~9 h idle / 12 h total.
  The pipeline is resumable — prediction JSONLs are append-and-skip, so re-running
  `--run` continues where it stopped. Self-consistency and variance are the long poles;
  run them in their own session if needed (`run.py phase12 --datasets medqa_usmle_4opt`).
- **Determinism** (RA-25): greedy phases are reproducible per (revision, GPU arch, vLLM
  version). Sampled phases vary within the Phase-15 variance — that is expected and measured.
- **Colab** works too (free T4, shorter sessions) — same commands, data via Google Drive mount.
