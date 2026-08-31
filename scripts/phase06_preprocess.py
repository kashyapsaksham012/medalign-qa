#!/usr/bin/env python
"""Phase 6 — Preprocessing: answer parser, prompt assembly, self-consistency.

Validates the model-independent preprocessing logic on fixtures + real records.
No model is called.
"""
from __future__ import annotations

import json

from medalign_qa.inference.self_consistency import plurality, uncertainty_score
from medalign_qa.preprocessing import prompt_builder as pb
from medalign_qa.preprocessing.answer_parser import parse_choice, valid_letters
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

PARSER_FIXTURES = [
    ("... Therefore the answer is (C).", "ABCD", "C"),
    ("Answer: D", "ABCD", "D"),
    ("Answer:(A)", "ABCD", "A"),
    ("The correct choice is B.\nAnswer: (B)", "ABCD", "B"),
    ("Explanation: blah blah. Answer: (E)", "ABCDE", "E"),
    ("I think it is option A, but actually B. Answer: (B)", "ABCD", "B"),
    ("no letter here", "ABCD", None),
    ("Answer: (E)", "ABCD", None),           # E invalid for a 4-option question
]


def main() -> int:
    log = get_logger("phase06")
    report = {"parser": [], "prompt_builder": [], "self_consistency": []}
    ok = True

    log.info("--- answer_parser fixtures (RA-05) ---")
    for text, valid, exp in PARSER_FIXTURES:
        got = parse_choice(text, valid)
        good = got == exp
        ok &= good
        report["parser"].append({"input": text, "valid": valid, "expected": exp, "got": got, "pass": good})
        log.info("  %s  %-45r -> %s (exp %s)", "OK  " if good else "FAIL", text[:45], got, exp)

    log.info("--- prompt_builder: one prompt per dataset ---")
    for ds_key, dataset in (("medqa", "medqa_usmle_4opt"), ("medmcqa", "medmcqa"),
                            ("pubmedqa", "pubmedqa"), ("mmlu", "mmlu_anatomy")):
        rec = next(r for r in io.read_jsonl(paths.PROCESSED / f"{dataset}.jsonl")
                   if r["split"] in ("test", "validation") and r.get("options"))
        fs = pb.build_mc_fewshot(rec, ds_key)
        cot = pb.build_mc_cot(rec, ds_key)
        approx_tok = len(fs.split())
        report["prompt_builder"].append({"dataset": dataset, "fewshot_words": approx_tok,
                                         "fewshot_tail": fs[-120:], "cot_tail": cot[-80:]})
        log.info("  %-24s few-shot ~%d words; ends %r", dataset, approx_tok, fs[-40:])
        # PubMedQA 3-shot must fit a modest context (PAPER-SPECIFIED rationale)
        if ds_key == "pubmedqa" and approx_tok > 2200:
            log.warning("  PubMedQA 3-shot prompt is large (%d words) -- check context truncation", approx_tok)

    for ds_key, dataset in (("liveqa", "liveqa"), ("medicationqa", "medicationqa"),
                            ("healthsearchqa", "healthsearchqa")):
        rec = next(r for r in io.read_jsonl(paths.PROCESSED / f"{dataset}.jsonl"))
        lf = pb.build_longform_fewshot(rec, ds_key)
        log.info("  %-24s long-form prompt ends %r", dataset, lf[-40:])

    log.info("--- self-consistency plurality (PAPER-SPECIFIED: 11 decodes) ---")
    votes = ["A", "B", "A", "A", "C", "A", "B", "A", "A", "B", "A"]  # 11 votes, plurality A (7)
    win, meta = plurality(votes)
    _, frac = uncertainty_score(votes)
    ok &= (win == "A" and meta["top_count"] == 7)
    report["self_consistency"] = {"votes": votes, "winner": win, "meta": meta, "agreement_fraction": frac}
    log.info("  winner=%s counts=%s agreement=%.3f", win, meta["counts"], frac)

    (paths.RESULTS / "phase06_preprocess_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("PHASE 6 %s", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
