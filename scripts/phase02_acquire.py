#!/usr/bin/env python
"""Phase 2 — Dataset Acquisition."""
from __future__ import annotations

from medalign_qa.data import acquire
from medalign_qa.utils import paths
from medalign_qa.utils.logging_utils import get_logger


def main() -> int:
    log = get_logger("phase02")
    paths.ensure_dirs()
    records: list[dict] = []

    log.info("[1/4] Extracting local datasets (originals untouched)...")
    records += acquire.acquire_local()

    log.info("[2/4] Downloading PubMedQA (pqa_labeled)...")
    records += acquire.acquire_pubmedqa()

    log.info("[3/4] Downloading LiveQA training XMLs...")
    records += acquire.acquire_liveqa_train()

    log.info("[4/4] Downloading MMLU 6 clinical subjects...")
    records += acquire.acquire_mmlu()

    man = acquire.write_manifest(records)
    ok = sum(1 for r in records if "error" not in r and r.get("bytes", 0) > 0)
    err = [r for r in records if "error" in r or r.get("bytes", 0) == 0]
    for r in records:
        tag = "OK  " if ("error" not in r and r.get("bytes", 0) > 0) else "FAIL"
        log.info("  %s %-55s %s", tag, r.get("dest", "?"),
                 r.get("error", f"{r.get('bytes', 0):,} B"))
    log.info("Manifest: %s", man.relative_to(paths.ROOT))
    log.info("PHASE 2 %s  (%d ok, %d failed)", "PASS" if not err else "PARTIAL", ok, len(err))
    return 0 if not err else 1


if __name__ == "__main__":
    raise SystemExit(main())
