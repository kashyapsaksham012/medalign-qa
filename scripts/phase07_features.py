#!/usr/bin/env python
"""Phase 7 — Feature Engineering: materialise & audit the prompt files.

'Feature engineering' in this paper == prompt construction (Section 3.3.2, A.8-A.9).
The MC prompts (Tables A.13-A.21) are transcribed verbatim; consumer prompts
(A.16-A.17) are partial -> RA-14; MMLU few-shot text -> RA-06.
"""
from __future__ import annotations

import json
import re

from medalign_qa.utils import paths
from medalign_qa.utils.logging_utils import get_logger

EXPECTED = {
    "few_shot/medqa.txt":     {"verbatim": True,  "min_q": 5, "label": "PAPER-SPECIFIED (A.13)"},
    "few_shot/medmcqa.txt":   {"verbatim": True,  "min_q": 5, "label": "PAPER-SPECIFIED (A.14)"},
    "few_shot/pubmedqa.txt":  {"verbatim": True,  "min_q": 3, "label": "PAPER-SPECIFIED (A.15)"},
    "few_shot/mmlu.txt":      {"verbatim": False, "min_q": 5, "label": "RA-06 (few-shot text NOT SPECIFIED)"},
    "cot/medqa.txt":          {"verbatim": True,  "min_q": 5, "label": "PAPER-SPECIFIED (A.18)"},
    "cot/medmcqa.txt":        {"verbatim": True,  "min_q": 5, "label": "PAPER-SPECIFIED (A.19)"},
    "cot/pubmedqa.txt":       {"verbatim": True,  "min_q": 3, "label": "PAPER-SPECIFIED (A.20)"},
    "cot/mmlu.txt":           {"verbatim": True,  "min_q": 5, "label": "PAPER-SPECIFIED (A.21)"},
    "consumer/liveqa.txt":         {"verbatim": False, "min_q": 3, "label": "RA-14 (A.16 partial)"},
    "consumer/medicationqa.txt":   {"verbatim": False, "min_q": 3, "label": "RA-14 (A.17 partial)"},
    "consumer/healthsearchqa.txt": {"verbatim": False, "min_q": 1, "label": "RA-14 + NOT SPECIFIED (no table in paper)"},
}


def main() -> int:
    log = get_logger("phase07")
    report, ok = [], True
    for rel, spec in EXPECTED.items():
        p = paths.PROMPTS / rel
        if not p.exists():
            log.error("  MISSING %s", rel); ok = False
            report.append({"file": rel, "status": "MISSING"}); continue
        text = p.read_text(encoding="utf-8")
        n_q = len(re.findall(r"(?mi)^\s*(?:Question:|Answer the following question|Context:)", text))
        n_ans = len(re.findall(r"(?mi)Answer\s*:?\s*\(?[A-E]\)?", text))
        has_verbatim_marker = "VERBATIM" in text.split("\n")[0] or "VERBATIM" in text[:200]
        row = {"file": rel, "label": spec["label"], "n_question_markers": n_q,
               "n_answer_markers": n_ans, "chars": len(text),
               "verbatim_marker": has_verbatim_marker, "min_q": spec["min_q"]}
        status = "OK"
        if n_q < spec["min_q"]:
            status = "WARN"
        if spec["verbatim"] and not has_verbatim_marker:
            status = "WARN"
        row["status"] = status
        report.append(row)
        log.info("  %-6s %-26s q~%d ans~%d  [%s]", status, rel, n_q, n_ans, spec["label"])

    (paths.RESULTS / "phase07_prompts_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    warns = sum(1 for r in report if r.get("status") == "WARN")
    log.info("PHASE 7 %s  (%d warnings -- expected for RA-14 consumer prompts)",
             "PASS" if ok else "FAIL", warns)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
