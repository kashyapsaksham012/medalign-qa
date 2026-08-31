"""Console + JSONL run logging. Every phase script gets one run log under logs/."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from .paths import LOGS


def get_logger(name: str, run_tag: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
                            "%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    LOGS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = run_tag or name.replace(".", "_")
    fh = logging.FileHandler(LOGS / f"{stamp}_{tag}.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


class RunRecord:
    """Accumulates structured events, flushed to logs/<stamp>_<tag>.jsonl."""

    def __init__(self, tag: str):
        self.tag = tag
        self.events: list[dict] = []
        LOGS.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.path = LOGS / f"{stamp}_{tag}.jsonl"

    def add(self, **kv) -> None:
        kv["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.events.append(kv)

    def flush(self) -> Path:
        with open(self.path, "w", encoding="utf-8") as fh:
            for e in self.events:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
        return self.path
