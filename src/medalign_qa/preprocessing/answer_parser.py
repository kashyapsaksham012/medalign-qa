"""Extract the chosen option letter from a model generation.

NOT SPECIFIED IN PAPER: the exact parsing rule. The paper only says the model is
instructed to "Output a single option as the final answer" (Table A.18) and shows
outputs ending "Answer: (C)" / "Answer:(A)".

REPLICATION ASSUMPTION (RA-05):
  1. take the LAST "Answer:  (X)" / "Answer: X" match whose letter is valid;
  2. else the LAST standalone "(X)" whose letter is valid;
  3. else (only when `allow_bare=True`) the LAST bare valid letter token;
  4. else None  -> scored as incorrect.

`allow_bare` MUST be False for chain-of-thought / self-consistency generations
(step 3 would otherwise grab a stray "vitamin D" / "hepatitis B" / "grade A" token
from the reasoning text and score it as the answer). For greedy few-shot, where the
substitute model is instructed to emit only the letter (RA-24), `allow_bare=True`
is safe and necessary.
"""
from __future__ import annotations

import re

_ANSWER_RE = re.compile(r"answer\s*:?\s*\(?\s*([A-E])\s*\)?", re.IGNORECASE)
_PAREN_RE = re.compile(r"\(\s*([A-E])\s*\)")
_BARE_RE = re.compile(r"\b([A-E])\b")


def parse_choice(text: str, valid: str = "ABCDE", *, allow_bare: bool = True) -> str | None:
    if not text:
        return None
    valid = valid.upper()

    cands = [m.group(1).upper() for m in _ANSWER_RE.finditer(text)]
    cands = [c for c in cands if c in valid]
    if cands:
        return cands[-1]

    # a trailing "(X)" is only trusted near the END of the generation (last 2 non-empty
    # lines) -- mid-reasoning "(A) ..." option restatements must not win.
    tail = "\n".join([ln for ln in text.splitlines() if ln.strip()][-2:])
    cands = [m.group(1).upper() for m in _PAREN_RE.finditer(tail) if m.group(1).upper() in valid]
    if cands:
        return cands[-1]

    if allow_bare:
        cands = [m.group(1).upper() for m in _BARE_RE.finditer(text) if m.group(1).upper() in valid]
        if cands:
            return cands[-1]
    return None


def valid_letters(n_options: int) -> str:
    return "ABCDE"[:n_options]
