#!/usr/bin/env python
"""Phase 20 -- Final documentation: model card, run-book, headline statement.

HARD GUARD: this phase refuses to declare a replication "complete" unless Phase 19
actually produced results/comparison.md from real predictions. It used to emit
"replication complete (within scope)" and a headline naming a specific model even
when zero inference had been run.
"""
from __future__ import annotations

import json

from medalign_qa.evaluation.mc_accuracy import any_predictions
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger


def _substitute_model() -> tuple[str, bool]:
    """(model_id, is_mock) from the most recent phase result; ('<unfrozen>', False) if none."""
    for name in ("phase12_mc_results.json", "phase10_fewshot_accuracy.json", "phase09_smoke.json"):
        p = paths.RESULTS / name
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if d.get("model"):
                    return d["model"], bool(d.get("mock"))
            except Exception:  # noqa: BLE001
                pass
    return "<substitute model not yet frozen -- see docs/STATUS.md>", False


def _headline(model: str, is_mock: bool) -> str:
    mock_warn = ("\n> **These outputs are from MOCK data** -- a plumbing check only, "
                 "not a model run.\n") if is_mock else ""
    return f"""\
# Replication outcome -- headline statement
{mock_warn}
This project **reproduces the MultiMedQA benchmark and the multiple-choice evaluation
methodology** (few-shot / chain-of-thought / self-consistency / selective prediction)
of *"Large Language Models Encode Clinical Knowledge"* (Singhal et al.,
arXiv:2212.13138v1), applied to a **substitute open model: `{model}`**.

It is **NOT an exact replication**. The paper's models were never released.

It **does NOT reproduce**:
- **PaLM / Flan-PaLM** at any size -- unavailable. Every accuracy here is from `{model}`,
  a different model; absolute values are not comparable and are labelled
  `REPLICATION ASSUMPTION -- SUBSTITUTE MODEL`.
- **Med-PaLM** / instruction prompt tuning (Sections 3.3.3-3.3.4, A.1, A.6) -- needs the
  frozen Flan-PaLM 540B weights (blockers B1/B2).
- **Any human-evaluation result** (Sections 3.2, 4.5; Tables A.3-A.12; Figures 6-11) --
  needs a recruited panel of 9 clinicians + 5 lay raters (blocker B4).
- The **scaling curves** (Figures A.1, A.2) -- a single model size was run.

What IS tested: whether the paper's **qualitative findings** hold under the same
methodology (SC helps MedQA/MedMCQA, hurts PubMedQA; CoT does not beat few-shot on MC;
selective-prediction accuracy rises with deferral). See `results/comparison.md`.
"""


def main() -> int:
    log = get_logger("phase20")

    comparison = paths.RESULTS / "comparison.md"
    if not comparison.exists() or not any_predictions():
        log.error("PHASE 20 NO DATA -- results/comparison.md is missing or there are no "
                  "predictions. Phase 20 will NOT declare a replication complete. "
                  "Run phases 9-19 with a frozen substitute model first.")
        return 1

    model, is_mock = _substitute_model()

    (paths.DOCS / "OUTCOME.md").write_text(_headline(model, is_mock), encoding="utf-8")

    card = f"""\
# Model card -- substitute model for the Path B replication

| Field | Value |
|---|---|
| Model | `{model}`{'  (MOCK RUN)' if is_mock else ''} |
| Role | substitute for PaLM/Flan-PaLM (RA-16) -- NOT Med-PaLM, NOT an exact reproduction |
| Prompting | verbatim paper exemplar blocks (Tables A.13-A.21) + RA-24 chat wrapper |
| Few-shot | 5-shot MedQA/MedMCQA (PAPER-SPECIFIED), 3-shot PubMedQA (PAPER-SPECIFIED), 5-shot MMLU (RA-06 assumption) |
| Self-consistency | 11 decodes (PAPER-SPECIFIED), temperature 0.7 (RA-03), plurality vote |
| Selective prediction | 41 decodes (PAPER-SPECIFIED), CoT+SC, MedQA only |
| Evaluation splits | MedQA 4+5-opt test, MedMCQA validation (RA-01), PubMedQA test-500 (RA-02), MMLU x6 test |
| Not evaluated | long-form / human-eval datasets (out of scope, B4) |
| Intended use | methodology replication + contemporary benchmark; research only |
"""
    (paths.DOCS / "model_card.md").write_text(card, encoding="utf-8")

    runbook = """\
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
"""
    (paths.DOCS / "RUNBOOK.md").write_text(runbook, encoding="utf-8")

    manifest = {
        "model": model, "mock": is_mock,
        "data_phases_complete": list(range(1, 9)),
        "model_phases_have_data": any_predictions(),
        "comparison_present": comparison.exists(),
        "NOT_reproduced": [
            "PaLM / Flan-PaLM (any size) -- B1", "Med-PaLM / instruction prompt tuning -- B2",
            "All human evaluation, Section 4.5 -- B4", "Scaling curves -- single model",
        ],
    }
    (paths.RESULTS / "phase20_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    log.info("wrote docs/OUTCOME.md, docs/model_card.md, docs/RUNBOOK.md (model: %s%s)",
             model, " [MOCK]" if is_mock else "")
    log.info("PHASE 20 %s", "PASS (MOCK data -- not a real result)" if is_mock
             else "PASS -- documentation written for the in-scope substitute replication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
