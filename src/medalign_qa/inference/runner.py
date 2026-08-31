"""Multiple-choice inference runner (few-shot / CoT), resumable.

One JSONL row per question:
  {uid, dataset, split, strategy, gold, n_options, parsed, correct,
   raw_generation, prompt_tokens, completion_tokens}
Re-running with resume=True skips uids already in the output file, so a crashed
9000-call job continues where it stopped.
"""
from __future__ import annotations

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..models.base import GenConfig
from ..preprocessing import prompt_builder as pb
from ..preprocessing.answer_parser import parse_choice, valid_letters
from ..utils import io, paths
from ..utils.logging_utils import get_logger

log = get_logger("inference.runner")

_MC_DATASET_KEY = pb.DATASET_KEY  # dataset -> prompt-file key


def _done_uids(out_path: Path) -> set[str]:
    if not out_path.exists():
        return set()
    return {r["uid"] for r in io.read_jsonl(out_path)}


def run_mc_split(model, dataset: str, split: str, strategy: str,
                 *, temperature: float, max_tokens: int, n: int = 1,
                 top_p: float = 1.0, limit: int | None = None,
                 resume: bool = True, log_every: int = 200,
                 seed: int | None = None, max_workers: int = 12,
                 out_subdir: str | None = None) -> dict:
    """strategy in {'few_shot','cot','self_consistency'}. n>1 -> SC decodes/question.
    out_subdir overrides the predictions/<...> folder (used by Phase 14)."""
    assert strategy in ("few_shot", "cot", "self_consistency")
    key = _MC_DATASET_KEY[dataset]
    out_path = paths.DERIVED / "predictions" / (out_subdir or strategy) / f"{dataset}__{split}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # self_consistency reuses the CoT prompt but samples n decodes
    prompt_strategy = "cot" if strategy == "self_consistency" else strategy

    rows = [r for r in io.read_jsonl(paths.PROCESSED / f"{dataset}.jsonl") if r["split"] == split]
    if limit:
        rows = rows[:limit]
    done = _done_uids(out_path) if resume else set()
    todo = [r for r in rows if r["uid"] not in done]
    log.info("%s/%s [%s] n=%d: %d rows, %d done, %d to run (workers=%d)",
             dataset, split, strategy, n, len(rows), len(done), len(todo), max_workers)
    out_path.touch(exist_ok=True)
    if not todo:
        return score_file(out_path)

    sys_msg = pb.system_for(prompt_strategy)
    build = pb.build_mc_fewshot if prompt_strategy == "few_shot" else pb.build_mc_cot
    write_lock = threading.Lock()
    t0 = time.time()
    counter = {"done": 0}

    # RA-05: bare-letter fallback is only safe for greedy few-shot (letter-only output).
    # CoT / self-consistency generations are long reasoning text -> require an explicit
    # "Answer:" / trailing "(X)" anchor, else count the decode as unparsed.
    allow_bare = prompt_strategy == "few_shot"

    def work(r: dict) -> dict:
        letters = valid_letters(len(r["options"]))
        prompt = build(r, key)
        cfg = GenConfig(n=n, temperature=temperature, top_p=top_p,
                        max_tokens=max_tokens, system=sys_msg, seed=seed,
                        stop=["\nQuestion:", "\n\nQuestion"])
        res = model.generate(prompt, cfg)
        preds = [parse_choice(t, letters, allow_bare=allow_bare) for t in res.texts]
        row = {"uid": r["uid"], "dataset": dataset, "split": split, "strategy": strategy,
               "gold": r["gold"], "n_options": len(r["options"]),
               "generations": res.texts, "parsed": preds,
               "prompt_tokens": res.prompt_tokens, "completion_tokens": res.completion_tokens}
        if n == 1:
            row["parsed_single"] = preds[0]
            row["correct"] = (preds[0] == r["gold"]) if r["gold"] else None
        return row

    with open(out_path, "a", encoding="utf-8") as fh, \
            ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(work, r): r["uid"] for r in todo}
        for fut in as_completed(futs):
            try:
                row = fut.result()
            except Exception as e:  # noqa: BLE001
                log.error("  question %s failed: %s", futs[fut], e)
                continue
            with write_lock:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                counter["done"] += 1
                d = counter["done"]
            if d % log_every == 0:
                rate = d / (time.time() - t0)
                log.info("  %d/%d  (%.1f/s)  cost so far $%.4f",
                         d, len(todo), rate, model.usage_summary().get("est_cost_usd", 0))

    return score_file(out_path)


def score_file(out_path: Path) -> dict:
    rows = list(io.read_jsonl(out_path))
    scored = [r for r in rows if r.get("gold")]
    n = len(scored)
    if n == 0:
        return {"path": str(out_path), "n": 0}
    if all("parsed_single" in r for r in scored):        # single-decode
        n_parsed = sum(1 for r in scored if r["parsed_single"] is not None)
        n_correct = sum(1 for r in scored if r.get("correct"))
        return {"path": str(out_path.relative_to(paths.ROOT)), "n": n,
                "accuracy": n_correct / n, "n_correct": n_correct,
                "parse_rate": n_parsed / n, "n_parsed": n_parsed}
    # multi-decode -> plurality
    from .self_consistency import plurality
    n_parsed = n_correct = 0
    for r in scored:
        win, meta = plurality(r["parsed"])
        if win is not None:
            n_parsed += 1
        if win == r["gold"]:
            n_correct += 1
    return {"path": str(out_path.relative_to(paths.ROOT)), "n": n,
            "accuracy": n_correct / n, "n_correct": n_correct,
            "parse_rate": n_parsed / n, "n_parsed": n_parsed, "mode": "self_consistency"}
