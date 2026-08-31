#!/usr/bin/env python
"""Phase 20 -- Final documentation: model card, run-book, headline statement."""
from __future__ import annotations

import json

from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

HEADLINE = """\
# Replication outcome -- headline statement

This project **reproduces the MultiMedQA benchmark and the Flan-PaLM multiple-choice
evaluation methodology** (few-shot / chain-of-thought / self-consistency / selective
prediction) from *"Large Language Models Encode Clinical Knowledge"* (Singhal et al.,
arXiv:2212.13138v1), applied to a **substitute open model,
`meta-llama/llama-3.1-8b-instruct`**, via OpenRouter.

It **does NOT reproduce**:
- **Med-PaLM** or the instruction-prompt-tuning results (Sections 3.3.3-3.3.4, A.1, A.6)
  -- the frozen Flan-PaLM 540B weights are unavailable.
- **Any human-evaluation result** (Sections 3.2, 4.5; Tables A.3-A.12; Figures 6-11)
  -- these require a recruited panel of 9 clinicians + 5 lay raters.
- The **scaling curves** (Figures A.1, A.2) -- a single model size was run.

Every number produced by the substitute model is labelled
`REPLICATION ASSUMPTION -- SUBSTITUTE MODEL` and must not be read as a reproduction
of PaLM / Flan-PaLM / Med-PaLM. The **qualitative findings** the paper reports
(self-consistency helps MedQA/MedMCQA, hurts PubMedQA; CoT does not beat few-shot on
MC; selective-prediction accuracy rises with deferral) are tested in
`results/comparison.md`.
"""


def main() -> int:
    log = get_logger("phase20")

    (paths.DOCS / "OUTCOME.md").write_text(HEADLINE, encoding="utf-8")

    # model card (Table A.2 template, filled for the substitute)
    cfg = io.read_yaml(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml")
    card = f"""\
# Model card -- substitute model for the Path B replication

| Field | Value |
|---|---|
| Model | `{cfg.get('model')}` |
| Access | OpenRouter (OpenAI-compatible chat completions) |
| Role | substitute for PaLM/Flan-PaLM (RA-16) -- NOT Med-PaLM |
| Prompting | verbatim paper prompts (Tables A.13-A.21) + RA-24 system wrapper |
| Few-shot | 5-shot (MedQA/MedMCQA/MMLU), 3-shot (PubMedQA) -- PAPER-SPECIFIED |
| Self-consistency | 11 decodes, temperature 0.7 (RA-03), plurality -- n PAPER-SPECIFIED |
| Selective prediction | 41 decodes -- PAPER-SPECIFIED |
| Evaluation datasets | MedQA(4+5-opt) test, MedMCQA validation, PubMedQA test-500, MMLU x6 test |
| Not evaluated | long-form / human-eval datasets (out of scope, B4) |
| Intended use | methodology replication + contemporary benchmark; research only |
"""
    (paths.DOCS / "model_card.md").write_text(card, encoding="utf-8")

    # run-book
    runbook = """\
# Run-book

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pip install -e .
cp .env.example .env      # then fill MEDALIGN_API_KEY / MEDALIGN_API_BASE

python run.py phase01     # environment self-check
python run.py phase02     # acquire 7 datasets -> raw_data/
python run.py phase03     # verify vs paper Table 1
python run.py phase04     # unified schema -> processed_data/ ; reproduce Table 1
python run.py phase05     # 140-question human-eval set (materialise only)
python run.py phase06     # answer parser / prompt builder / self-consistency checks
python run.py phase07     # prompt files audit
python run.py phase08     # EDA
python run.py phase09     # model backend smoke test  (needs .env)
python run.py phase10 --all   # few-shot MC inference
python run.py phase11    # chain-of-thought
python run.py phase12    # self-consistency (11x) + Tables 4-7, A.1
python run.py phase13    # scaling (NOT REPRODUCED note -- single model)
python run.py phase14    # selective prediction (41x) -> Fig 5
python run.py phase15    # variance (4x MedQA SC)
python run.py phase16    # Wilson CIs / McNemar (beyond paper)
python run.py phase17    # render all in-scope tables + figures
python run.py phase18    # reproducibility validation
python run.py phase19    # paper-to-result comparison + findings verdict
python run.py phase20    # this file
python run.py test       # full pytest suite
```

Outputs: `tables/` `figures/` `results/comparison.md` `docs/OUTCOME.md`.
"""
    (paths.DOCS / "RUNBOOK.md").write_text(runbook, encoding="utf-8")

    manifest = {
        "phases_complete": list(range(1, 21)),
        "key_outputs": ["tables/table4.md", "tables/table5.md", "tables/table6.md",
                        "tables/table7.md", "tables/tableA1.md",
                        "figures/fig3_replication.png", "figures/fig4_replication.png",
                        "figures/fig5_replication.png",
                        "results/comparison.md", "docs/OUTCOME.md", "docs/model_card.md"],
        "registers": ["docs/deviations.md", "docs/blockers.md", "docs/reproducibility.md"],
    }
    (paths.RESULTS / "phase20_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    log.info("wrote docs/OUTCOME.md, docs/model_card.md, docs/RUNBOOK.md")
    log.info("PHASE 20 PASS -- replication complete (within scope)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
