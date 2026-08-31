#!/usr/bin/env python
"""Phase 1 — Environment Setup: report and self-check.

Prints the environment report and verifies the project skeleton. Exits non-zero
if any required component is missing.
"""
from __future__ import annotations

import importlib
import platform
import sys

from medalign_qa.utils import paths
from medalign_qa.utils.logging_utils import get_logger
from medalign_qa.utils.seeding import set_seed

REQUIRED_LIBS = ["numpy", "pandas", "scipy", "openpyxl", "lxml", "requests",
                 "matplotlib", "yaml", "tqdm", "pytest"]

REQUIRED_DIRS = [
    paths.RAW, paths.PROCESSED, paths.DERIVED, paths.CONFIGS, paths.METADATA,
    paths.PROMPTS, paths.DOCS, paths.RESULTS, paths.FIGURES, paths.TABLES, paths.LOGS,
]

REQUIRED_FILES = [
    paths.ROOT / "requirements.txt",
    paths.ROOT / "requirements.lock.txt",
    paths.ROOT / "pyproject.toml",
    paths.CONFIGS / "global.yaml",
    paths.METADATA / "dataset_specs.yaml",
    paths.METADATA / "expected_counts.yaml",
    paths.METADATA / "data_provenance.md",
    paths.DOCS / "blockers.md",
    paths.DOCS / "deviations.md",
    paths.DOCS / "STATUS.md",
]

REQUIRED_ORIGINALS = list(paths.ORIGINALS.values())


def main() -> int:
    log = get_logger("phase01")
    ok = True

    log.info("Python %s  (%s)", platform.python_version(), sys.executable)
    if sys.version_info < (3, 11):
        log.error("Python >= 3.11 required"); ok = False

    log.info("--- Required libraries ---")
    for lib in REQUIRED_LIBS:
        try:
            m = importlib.import_module(lib)
            log.info("  OK   %-12s %s", lib, getattr(m, "__version__", "?"))
        except Exception as e:  # noqa: BLE001
            log.error("  MISS %-12s (%s)", lib, e); ok = False

    log.info("--- Project package ---")
    try:
        import medalign_qa
        log.info("  OK   medalign_qa %s", medalign_qa.__version__)
    except Exception as e:  # noqa: BLE001
        log.error("  MISS medalign_qa (%s)", e); ok = False

    log.info("--- Directory skeleton ---")
    paths.ensure_dirs()
    for d in REQUIRED_DIRS:
        (log.info if d.is_dir() else log.error)("  %s %s", "OK  " if d.is_dir() else "MISS", d.relative_to(paths.ROOT))
        ok &= d.is_dir()

    log.info("--- Phase-1 files ---")
    for f in REQUIRED_FILES:
        (log.info if f.is_file() else log.error)("  %s %s", "OK  " if f.is_file() else "MISS", f.relative_to(paths.ROOT))
        ok &= f.is_file()

    log.info("--- User-provided originals (read-only) ---")
    for f in REQUIRED_ORIGINALS:
        (log.info if f.is_file() else log.error)("  %s %s", "OK  " if f.is_file() else "MISS", f.name)
        ok &= f.is_file()

    log.info("--- Determinism check ---")
    set_seed(0)
    import numpy as np, random
    a = (random.random(), np.random.rand())
    set_seed(0)
    b = (random.random(), np.random.rand())
    if a == b:
        log.info("  OK   set_seed(0) reproducible")
    else:
        log.error("  FAIL seeding not reproducible"); ok = False

    log.info("PHASE 1 %s", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
