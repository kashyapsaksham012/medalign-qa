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


def _findings_block() -> str:
    """Render the actual Phase-19 verdicts (never assert the paper's findings as ours)."""
    p = paths.RESULTS / "comparison.json"
    if not p.exists():
        return "See `results/comparison.md` for the per-finding verdict."
    try:
        fs = json.loads(p.read_text(encoding="utf-8")).get("qualitative_findings", [])
    except Exception:  # noqa: BLE001
        return "See `results/comparison.md` for the per-finding verdict."
    lines = []
    for f in fs:
        lines.append(f"- **{f.get('verdict')}** — {f.get('finding')}"
                     + (f" ({f['detail']})" if f.get("detail") else ""))
    return "\n".join(lines) if lines else "See `results/comparison.md`."


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

## Do the paper's qualitative findings hold on the substitute model?

{_findings_block()}

Full analysis: **`docs/REPLICATION_REPORT.md`**. Numbers + tolerances: `results/comparison.md`.
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

## Milestone 1 -- data harness (any machine, no GPU)

```
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\\Scripts\\activate
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
