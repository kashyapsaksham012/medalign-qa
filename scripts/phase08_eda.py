#!/usr/bin/env python
"""Phase 8 — Exploratory / Data Validation."""
from __future__ import annotations

from medalign_qa.data import eda
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    log = get_logger("phase08")
    s = eda.run()

    log.info("--- MC evaluation splits ---")
    for ds, rec in s["mc"].items():
        log.info("  %-26s n=%-5d golds=%s  q_words(med=%s,max=%s)  ctx=%d",
                 ds, rec["n"], rec["gold_letter_balance"],
                 rec["question_words"]["median"], rec["question_words"]["max"], rec["has_context"])
    log.info("--- Long-form splits ---")
    for ds, rec in s["longform"].items():
        log.info("  %-26s n=%-5d q_words(med=%s,max=%s) with_ref_answer=%d",
                 ds, rec["n"], rec["question_words"]["median"], rec["question_words"]["max"],
                 rec["with_reference_answer"])

    if s["anomaly_flags"]:
        for f in s["anomaly_flags"]:
            log.warning("  ANOMALY: %s", f)
    else:
        log.info("  no anomaly flags")
    log.info("Figures: %s", s["figures"])
    log.info("PHASE 8 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
