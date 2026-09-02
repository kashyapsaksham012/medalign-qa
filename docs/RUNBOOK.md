# Run-book

## Milestone 1 -- data harness (any machine, no GPU)

```
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
python run.py phase01   # ... through phase08   (env -> acquire -> verify -> integrate -> cohort -> preprocess -> prompts -> EDA)
```

## Milestone 2 -- Path B substitute-model evaluation (needs a GPU)

Model + decode params are frozen in `configs/model/qwen25-7b-local.yaml`
(`revision` is an exact HF commit SHA). Runbook for a free Kaggle/Colab T4:
`docs/pathb_runbook.md`.

```
python scripts/run_pathb_pipeline.py --all        # phases 9-20, all MC datasets
  # idempotent + resumable: completed splits are skipped (no model load), so this
  # is safe to kill and restart. --mock runs the whole thing offline, isolated
  # under */mock/ (never touches real outputs).

# or phase-by-phase (per-dataset is safest on a flaky free GPU):
python run.py phase09                       # smoke test (5 MedQA Q)
python run.py phase10 --all                 # few-shot
python run.py phase11 --datasets medmcqa    # CoT   (repeat per dataset)
python run.py phase12 --datasets medmcqa    # self-consistency 11x  (repeat per dataset)
python run.py phase13 14 15                 # scaling verdict / selective prediction 41x / variance 4x
python run.py phase16 17 18 19 20           # stats / render / repro / comparison / docs
```

After any GPU run, re-run `phase10 11 12 13 16 17 18 19 20` locally: a
`--datasets`-scoped run only infers that subset but every phase re-scores the
*whole* prediction tree, so the summaries stay complete.

Phases 12/16/17/19/20 hard-fail (exit 1, "NO DATA") when no model predictions
exist, so an empty run cannot masquerade as a completed replication.
