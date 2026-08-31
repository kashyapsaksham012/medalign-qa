#!/usr/bin/env python
"""Phase 17 -- final render of all in-scope MC tables & figures."""
from __future__ import annotations

import json

from medalign_qa.evaluation import tables
from medalign_qa.evaluation.mc_accuracy import any_predictions
from medalign_qa.figures import mc_figures
from medalign_qa.utils import paths
from medalign_qa.utils.logging_utils import get_logger

BLOCKED = [
    "Table 8 (Flan-PaLM MedQA explanations) -- needs the actual model outputs",
    "Tables 9, 10 (Med-PaLM long-form answers) -- Med-PaLM unavailable (B2)",
    "Figures 6-11 (human evaluation) -- needs the clinician/lay rater panel (B4)",
    "Figures A.1, A.2 (scaling) -- single model; see Phase 13",
]


def main() -> int:
    log = get_logger("phase17")
    if not any_predictions():
        log.error("PHASE 17 NO DATA -- no model predictions under derived_data/predictions/. "
                  "Rendering empty PAPER-vs-OURS tables would misrepresent project state. "
                  "Run phases 10-15 first (real model, or --mock for a plumbing check).")
        return 1
    t = tables.write_all()
    f = mc_figures.write_all()
    (paths.TABLES / "_BLOCKED.md").write_text(
        "# Tables/figures NOT reproduced\n\n" + "\n".join(f"- {b}" for b in BLOCKED) + "\n",
        encoding="utf-8")
    (paths.RESULTS / "phase17_artifacts.json").write_text(
        json.dumps({"tables": t, "figures": f, "blocked": BLOCKED}, indent=2), encoding="utf-8")
    for x in t + f:
        log.info("  %s", x)
    log.info("PHASE 17 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
