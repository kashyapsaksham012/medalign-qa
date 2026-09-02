"""Assemble the paper's MC tables (4, 5, 6, 7, A.1) with PAPER | OURS | delta columns."""
from __future__ import annotations

import json

from .. import config as run_config
from ..utils import io, paths
from .mc_accuracy import score

PAPER = io.read_yaml(paths.METADATA / "paper_results.yaml")


def _model_label() -> str:
    """The substitute model is NOT frozen yet (see docs/STATUS.md). Best-effort label
    from whichever phase result was written last; never claim a specific model here."""
    for name in ("phase12_mc_results.json", "phase10_fewshot_accuracy.json"):
        p = paths.RESULTS / name
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                m = d.get("model")
                if m:
                    return f"{m}{' [MOCK]' if d.get('mock') else ''} — SUBSTITUTE (RA-16/RA-24)"
            except Exception:  # noqa: BLE001
                pass
    return "SUBSTITUTE MODEL (RA-16/RA-24) — not frozen, see docs/STATUS.md"


MODEL_LABEL = _model_label()

_BANNER = ("> Substitute-model numbers. NOT a reproduction of PaLM/Flan-PaLM/Med-PaLM. "
           "Absolute gaps vs the paper are expected; only the qualitative direction is tested "
           "(see results/comparison.md).")


def _acc(strategy: str, dataset: str, split: str) -> float | None:
    p = run_config.prediction_file(strategy, f"{dataset}__{split}")
    if not p.exists():
        return None
    s = score(p)
    return round(100 * s["accuracy"], 1) if s.get("n") else None


def _row(name, paper, ours):
    d = None if (paper is None or ours is None) else round(ours - paper, 1)
    return f"| {name} | {paper if paper is not None else '-'} | {ours if ours is not None else '-'} | {d if d is not None else '-'} |"


def table4() -> str:
    ours = _acc("self_consistency", "medqa_usmle_4opt", "test") or _acc("few_shot", "medqa_usmle_4opt", "test")
    L = ["# Table 4 -- MedQA (USMLE, 4-option) accuracy %",
         "", "| Model | Paper | Ours | Δ |", "|---|---|---|---|",
         _row(f"{MODEL_LABEL} (few-shot+SC) [SUBSTITUTE]", None, ours),
         _row("Flan-PaLM 540B [paper]", PAPER["table4_medqa_4opt"]["flan_palm_540b"], None)]
    for k in ("pubmedgpt_2_7b", "dragon_360m", "biolinkbert_340m", "galactica_120b",
              "pubmedbert_100m", "gpt_neo_2_7b"):
        L.append(_row(f"{k} [cited baseline, RA-15]", PAPER["table4_medqa_4opt"][k], None))
    return "\n".join(L) + "\n"


def table5() -> str:
    L = ["# Table 5 -- few-shot accuracy % (paper: PaLM/Flan-PaLM x 3 sizes; ours: substitute)",
         "", "| Dataset | Paper Flan-PaLM 8B | Paper Flan-PaLM 540B | Ours (8B substitute) | Δ vs paper 8B |",
         "|---|---|---|---|---|"]
    for ds, key, split in (("MedQA 4-opt", "medqa_usmle_4opt", "test"),
                           ("MedMCQA", "medmcqa", "validation"),
                           ("PubMedQA", "pubmedqa", "test")):
        ours = _acc("few_shot", key, split)
        p8 = PAPER["table5"][key]["flan_8b"]
        p540 = PAPER["table5"][key]["flan_540b"]
        d = None if ours is None else round(ours - p8, 1)
        L.append(f"| {ds} | {p8} | {p540} | {ours if ours is not None else '-'} | {d if d is not None else '-'} |")
    return "\n".join(L) + "\n"


def _fs_cot_sc(ds, key, split):
    return (_acc("few_shot", key, split), _acc("cot", key, split),
            _acc("self_consistency", key, split))


def table6() -> str:
    L = ["# Table 6 -- few-shot vs CoT",
         "", "| Dataset | Paper FS | Paper CoT | Ours FS | Ours CoT | Ours Δ(CoT-FS) |", "|---|---|---|---|---|---|"]
    for ds, key, split in (("MedQA 4-opt", "medqa_usmle_4opt", "test"),
                           ("MedMCQA", "medmcqa", "validation"), ("PubMedQA", "pubmedqa", "test")):
        fs, cot, _ = _fs_cot_sc(ds, key, split)
        d = None if (fs is None or cot is None) else round(cot - fs, 1)
        pp = PAPER["table6"][key]
        L.append(f"| {ds} | {pp['few_shot']} | {pp['cot']} | {fs or '-'} | {cot or '-'} | {d if d is not None else '-'} |")
    return "\n".join(L) + "\n"


def table7() -> str:
    L = ["# Table 7 -- few-shot vs self-consistency",
         "", "| Dataset | Paper FS | Paper SC | Ours FS | Ours SC | Ours Δ(SC-FS) |", "|---|---|---|---|---|---|"]
    for ds, key, split in (("MedQA 4-opt", "medqa_usmle_4opt", "test"),
                           ("MedMCQA", "medmcqa", "validation"), ("PubMedQA", "pubmedqa", "test")):
        fs, _, sc = _fs_cot_sc(ds, key, split)
        d = None if (fs is None or sc is None) else round(sc - fs, 1)
        pp = PAPER["table7"][key]
        L.append(f"| {ds} | {pp['few_shot']} | {pp['sc']} | {fs or '-'} | {sc or '-'} | {d if d is not None else '-'} |")
    return "\n".join(L) + "\n"


def tableA1() -> str:
    # PAPER["tableA1"][subj] = [PaLM-540B FS, Flan-PaLM-540B FS, Flan-PaLM-540B CoT,
    #                           Flan-PaLM-540B SC]  (all B1 -- unobtainable weights)
    L = ["# Table A.1 -- MMLU clinical topics",
         "",
         "Paper columns are Flan-PaLM / PaLM 540B (blocker B1 -- not reproducible). "
         "`Ours` is the substitute model.",
         "",
         "| Subject | Paper PaLM-540B FS | Paper FlanPaLM-540B FS | Paper FlanPaLM CoT | "
         "Paper FlanPaLM SC | Ours FS | Ours CoT | Ours SC |",
         "|---|---|---|---|---|---|---|---|"]
    for s in paths.MMLU_SUBJECTS:
        p = PAPER.get("tableA1", {}).get(s, ["-", "-", "-", "-"])
        fs = _acc("few_shot", f"mmlu_{s}", "test")
        cot = _acc("cot", f"mmlu_{s}", "test")
        sc = _acc("self_consistency", f"mmlu_{s}", "test")
        L.append(f"| {s} | {p[0]} | {p[1]} | {p[2]} | {p[3]} | {fs or '-'} | {cot or '-'} | {sc or '-'} |")
    return "\n".join(L) + "\n"


def write_all() -> list[str]:
    global MODEL_LABEL
    MODEL_LABEL = _model_label()
    out = []
    for name, fn in (("table4", table4), ("table5", table5), ("table6", table6),
                     ("table7", table7), ("tableA1", tableA1)):
        p = paths.TABLES / f"{name}.md"
        body = fn()
        # inject the substitute-model banner right after the H1
        lines = body.split("\n", 1)
        p.write_text(f"{lines[0]}\n\n{_BANNER}\n\n_Model: {MODEL_LABEL}_\n{lines[1] if len(lines) > 1 else ''}",
                     encoding="utf-8")
        out.append(str(p.relative_to(paths.ROOT)))
    return out
