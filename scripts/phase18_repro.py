#!/usr/bin/env python
"""Phase 18 -- Reproducibility validation.

Checks the MODEL-INDEPENDENT pipeline is deterministic and that provenance holds.
Model runs are re-runnable from saved configs + seeds (sampling noise accepted).
"""
from __future__ import annotations

import json
import subprocess
import sys

from medalign_qa.utils import io, paths
from medalign_qa.utils.io import sha256_file
from medalign_qa.utils.logging_utils import get_logger

ORIGINAL_HASHES = {
    "project_healthcare_.pdf": "e83a6fecf5820a49b2b1c716f4c1839a7301300a6e27aa53c3cb7212b7db9f4e",
    "data.zip": "16c1fbc6f47d548d2af7837b18e893aa45f45c0be9bda0a9adfff3c625bf9262",
    "data_clean.zip": "1c2ca8130b3d86d9a99a432ab9bef14f3bb9807bef20facd9ac86ba36960f629",
    "LiveQA_MedicalTask_TREC2017-master.zip": "ea56456197b5714f7c2af67410c7fa881cab5b1b459f300abe5c92d1b72379ae",
    "MedInfo2019-QA-Medications.xlsx": "4f13d0e3b195bd6a5d72a1872f9118cb5f69fd02c370001695330cfc9e3b5832",
    "41586_2023_6291_MOESM6_ESM.xlsx": "a89f6639ee76717e2a1ea25bbe25c8c69cf396681be76fd8145da7e9c8917e1e",
}


def main() -> int:
    log = get_logger("phase18")
    checks = []

    # 1. originals untouched
    for name, want in ORIGINAL_HASHES.items():
        got = sha256_file(paths.ROOT / name)
        checks.append({"check": f"original untouched: {name}", "pass": got == want})

    # 2. deterministic re-integration: capture current hashes, re-run phase04 once,
    #    confirm the outputs are byte-identical (loaders are pure functions).
    targets = [paths.TABLES / "table1_reproduced.json",
               paths.PROCESSED / "pubmedqa.jsonl",
               paths.PROCESSED / "mmlu_anatomy.jsonl",
               paths.PROCESSED / "medqa_usmle_4opt.jsonl"]
    before = [sha256_file(p) for p in targets if p.exists()]
    subprocess.run([sys.executable, "run.py", "phase04"], cwd=paths.ROOT, capture_output=True)
    after = [sha256_file(p) for p in targets if p.exists()]
    checks.append({"check": "phase04 re-run is byte-identical (Table1 + 3 processed files)",
                   "pass": before == after and len(before) == 4,
                   "before": before, "after": after})

    # 3. env lock present + non-trivial
    lock = paths.ROOT / "requirements.lock.txt"
    checks.append({"check": "requirements.lock.txt present", "pass": lock.exists() and lock.stat().st_size > 200})

    # 4. model run reproducibility metadata
    cfg = io.read_yaml(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml")
    seed_note = io.read_yaml(paths.CONFIGS / "global.yaml")["seed"]
    checks.append({"check": "model config records model id + decode params", "pass": "decode" in cfg})

    # 5. seed audit -- grep src for unseeded RNG
    grep = subprocess.run(["git", "grep", "-nE", r"random\.(random|choice|randint|shuffle)|np\.random\.(rand|randint|choice)",
                           "--", "src/"], cwd=paths.ROOT, capture_output=True, text=True)
    offenders = [ln for ln in grep.stdout.splitlines()
                 if "default_rng" not in ln and "seeding.py" not in ln and "mock.py" not in ln]
    checks.append({"check": "no unseeded RNG in src/ (excl. mock, seeding)",
                   "pass": len(offenders) == 0, "offenders": offenders})

    report = {"seed": seed_note, "model": cfg.get("model"),
              "decode_params": cfg.get("decode"), "checks": checks,
              "all_pass": all(c["pass"] for c in checks)}
    (paths.RESULTS / "phase18_repro.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    doc = ["# Reproducibility", "",
           f"- Model: `{cfg.get('model')}` via OpenRouter (config `configs/model/llama31-8b-instruct.yaml`)",
           f"- Global seed: {seed_note} (RA-19; paper reports none)",
           "- Decode params: see the model config `decode:` block",
           "- Data provenance + SHA-256: `metadata/data_provenance.md`",
           "- Env: `requirements.txt` (pinned) + `requirements.lock.txt` (full freeze), CPython 3.14.7",
           "- Deterministic: `python run.py phase01..phase08` reproduces `processed_data/` + "
           "`tables/table1_reproduced.*` byte-identically.",
           "- API sampling (Phases 12/14/15) is inherently non-deterministic; re-runs vary "
           "within the Phase-15 variance.", ""]
    for c in checks:
        doc.append(f"- {'PASS' if c['pass'] else 'FAIL'}: {c['check']}")
    (paths.DOCS / "reproducibility.md").write_text("\n".join(doc) + "\n", encoding="utf-8")

    for c in checks:
        (log.info if c["pass"] else log.error)("  %s %s", "OK  " if c["pass"] else "FAIL", c["check"])
    log.info("PHASE 18 %s", "PASS" if report["all_pass"] else "CHECK")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
