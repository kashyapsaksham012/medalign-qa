#!/usr/bin/env python
"""Phase 3 — Dataset Verification."""
from __future__ import annotations

import json

from medalign_qa.data import verify
from medalign_qa.utils import paths
from medalign_qa.utils.io import utcnow
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    log = get_logger("phase03")
    checks = verify.run_all()

    by_status: dict[str, int] = {}
    for c in checks:
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
        lvl = {"PASS": log.info, "CAVEAT": log.warning, "SKIP": log.info}.get(c["status"], log.error)
        lvl("  %-6s %-16s %-36s expected=%s observed=%s  [%s] %s",
            c["status"], c["dataset"], c["check"], c["expected"], c["observed"],
            c["label"], c["note"])

    report = {
        "generated": utcnow(),
        "summary": by_status,
        "checks": checks,
    }
    out = paths.RESULTS / "phase03_verification_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = paths.RESULTS / "phase03_verification_report.md"
    lines = ["# Phase 3 — Dataset Verification Report", "",
             f"_generated {report['generated']}_", "",
             "| status | dataset | check | expected | observed | evidence | note |",
             "|---|---|---|---|---|---|---|"]
    for c in checks:
        lines.append(f"| {c['status']} | {c['dataset']} | {c['check']} | `{c['expected']}` | "
                     f"`{c['observed']}` | {c['label']} | {c['note']} |")
    lines += ["", "## Summary", "", *[f"- **{k}**: {v}" for k, v in sorted(by_status.items())]]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    fails = by_status.get("FAIL", 0)
    log.info("Report: %s", out.relative_to(paths.ROOT))
    log.info("PHASE 3 %s  (%s)", "PASS" if fails == 0 else "FAIL", by_status)
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
