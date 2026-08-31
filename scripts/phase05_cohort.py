#!/usr/bin/env python
"""Phase 5 — Cohort Construction (140-question human-eval set + IPT exemplar slots)."""
from __future__ import annotations

from medalign_qa.data import cohort
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    log = get_logger("phase05")
    rep = cohort.run()
    he = rep["human_eval_140"]
    log.info("Human-eval set: %d questions (paper: 140)", he["n"])
    log.info("  paper composition:         %s", he["paper_composition"])
    log.info("  reconstructed composition: %s", he["reconstructed_composition"])
    log.info("  matches paper exactly:     %s  (%d source-attributions inferred)",
             he["composition_matches_paper"], he["n_inferred"])
    log.info("IPT exemplars: %s -> %s", rep["ipt_exemplars"]["status"], rep["ipt_exemplars"]["path"])

    status = "PASS" if he["n"] == 140 else "FAIL"
    log.info("PHASE 5 %s%s", status,
             "" if he["composition_matches_paper"]
             else "  (CAVEAT: source attribution is a reconstruction; see report)")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
