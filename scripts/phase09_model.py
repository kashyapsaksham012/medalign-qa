#!/usr/bin/env python
"""Phase 9 -- Model backend smoke test + Table 4 baseline column.

Runs 5 MedQA-4opt test questions end-to-end through the frozen Path B backend
(local vLLM): build prompt -> generate (greedy) -> parse answer -> score.
"""
from __future__ import annotations

import argparse
import json

from medalign_qa.models import load_model
from medalign_qa.models.base import GenConfig
from medalign_qa.preprocessing import prompt_builder as pb
from medalign_qa.preprocessing.answer_parser import parse_choice
from medalign_qa.utils import io, paths
from medalign_qa.utils.logging_utils import get_logger

BASELINE_TABLE4 = [  # RA-15: published numbers, cited -- NOT re-run
    ("Flan-PaLM (540B) [paper]", "67.6", "Singhal et al. 2022 (this paper), Table 4"),
    ("PubMedGPT / BioMedLM (2.7B)", "50.3", "Bolton et al. 2022 [9]"),
    ("DRAGON (360M)", "47.5", "Yasunaga et al. 2022 [94]"),
    ("BioLinkBERT (340M)", "45.1", "Yasunaga et al. 2022 [95]"),
    ("Galactica (120B)", "44.4", "Taylor et al. 2022 [79]"),
    ("PubMedBERT (100M)", "38.1", "Gu et al. 2021 [25]"),
    ("GPT-Neo (2.7B)", "33.3", "Black et al. 2021 [7]"),
]


def write_table4_baselines() -> None:
    lines = ["# Table 4 baseline column (RA-15 -- cited, not re-run)", "",
             "MedQA (USMLE, 4 options) accuracy %. These rows are copied verbatim from the",
             "cited papers, exactly as the authors of project_healthcare_.pdf did.", "",
             "| Model | MedQA 4-opt % | Source |", "|---|---|---|"]
    for m, a, s in BASELINE_TABLE4:
        lines.append(f"| {m} | {a} | {s} |")
    lines += ["", "The substitute-model row(s) are added by Phase 12."]
    (paths.TABLES / "table4_baselines.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(paths.CONFIGS / "model" / "qwen25-7b-local.yaml"))
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--mock", action="store_true", help="offline dry-run")
    args = ap.parse_args()
    log = get_logger("phase09")

    write_table4_baselines()
    log.info("Wrote tables/table4_baselines.md")

    mcfg = io.read_yaml(args.config)
    log.info("Backend  : %s", mcfg.get("provider", "vllm"))
    log.info("Config   : %s  (revision %s)", mcfg.get("model"), str(mcfg.get("revision"))[:12])
    model = load_model(args.config, mock=args.mock)
    log.info("Model    : %s", model.name)

    rows = [r for r in io.read_jsonl(paths.PROCESSED / "medqa_usmle_4opt.jsonl")
            if r["split"] == "test"][:args.n]
    cfg = GenConfig(n=1, temperature=0.0, max_tokens=24,
                    system=pb.system_for("few_shot"))  # RA-24

    results, correct, parsed_ok = [], 0, 0
    for r in rows:
        prompt = pb.build_mc_fewshot(r, "medqa")
        out = model.generate(prompt, cfg)
        gen = out.texts[0]
        pred = parse_choice(gen, "ABCD")
        ok = pred == r["gold"]
        correct += ok
        parsed_ok += pred is not None
        results.append({"uid": r["uid"], "gold": r["gold"], "parsed": pred,
                        "correct": ok, "raw_generation": gen[:400]})
        log.info("  %s  gold=%s pred=%s  gen=%r", "OK " if ok else "XX ", r["gold"], pred, gen[:60])

    usage = model.usage_summary()
    report = {"model": model.name, "n": len(rows), "n_correct": correct,
              "n_parsed": parsed_ok, "accuracy": correct / len(rows),
              "parse_rate": parsed_ok / len(rows), "usage": usage, "results": results}
    (paths.RESULTS / "phase09_smoke.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    log.info("smoke: %d/%d correct, parse-rate %.0f%%, est cost $%.4f",
             correct, len(rows), 100 * parsed_ok / len(rows), usage.get("est_cost_usd", 0))
    ok_gate = parsed_ok == len(rows)
    log.info("PHASE 9 %s%s", "PASS" if ok_gate else "CHECK",
             "" if ok_gate else "  (some generations did not parse -- inspect phase09_smoke.json)")
    return 0 if ok_gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
