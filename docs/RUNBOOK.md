# Run-book

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pip install -e .
cp .env.example .env      # then fill MEDALIGN_API_KEY / MEDALIGN_API_BASE

python run.py phase01 .. phase08   # data harness (model-independent)
python run.py phase09              # model backend smoke test  (needs .env + a FROZEN model config)
python run.py phase10 --all        # few-shot MC inference
python run.py phase11              # chain-of-thought
python run.py phase12              # self-consistency (11x) + Tables 4-7, A.1
python run.py phase13              # scaling (NOT REPRODUCED -- single model)
python run.py phase14              # selective prediction (41x) -> Fig 5
python run.py phase15              # variance (4x MedQA SC)
python run.py phase16              # Wilson CIs / McNemar (beyond paper)
python run.py phase17              # render in-scope tables + figures  (hard-fails with NO DATA)
python run.py phase18              # reproducibility validation
python run.py phase19              # paper-to-result comparison  (hard-fails with NO DATA)
python run.py phase20              # this file  (hard-fails unless phase 19 produced comparison.md)
python run.py test
```

Phases 12/16/17/19/20 hard-fail (exit 1, "NO DATA") when no model predictions exist,
so an empty run cannot masquerade as a completed replication.
