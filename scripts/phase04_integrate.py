#!/usr/bin/env python
"""Phase 4 — Data Integration."""
from __future__ import annotations

from medalign_qa.data import integrate
from medalign_qa.utils import paths
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    log = get_logger("phase04")
    rep = integrate.run(write_reports=True)

    log.info("--- processed_data/ row counts ---")
    for ds, n in sorted(rep["processed_counts"].items()):
        log.info("  %-30s %8d", ds, n)

    log.info("--- Table 1 (reproduced vs paper) ---")
    for t in rep["table1"]:
        log.info("  %-34s dev %-8s/%-8s  test %-6s/%-6s  %s",
                 t["dataset"], t["reproduced_dev"], t["paper_dev"],
                 t["reproduced_test"], t["paper_test"], t.get("note", ""))

    log.info("--- Leakage / integrity checks ---")
    bad = 0
    for c in rep["leakage_checks"]:
        lvl = log.info if c["status"] in ("PASS", "INFO") else log.warning
        if c["status"] == "FAIL":
            lvl = log.error; bad += 1
        lvl("  %-6s %-48s %s", c["status"], c["check"], c["detail"])

    log.info("Reports: tables/table1_reproduced.md , results/phase04_integration_report.json")
    log.info("PHASE 4 %s", "PASS" if bad == 0 else "FAIL")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
