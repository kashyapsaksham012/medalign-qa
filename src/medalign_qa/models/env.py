"""Minimal .env loader (no python-dotenv dependency).

Secrets live in .env (gitignored). Real environment variables win over .env.
Never log the value of MEDALIGN_API_KEY.
"""
from __future__ import annotations

import os
from pathlib import Path

from ..utils.paths import ROOT

_LOADED = False


def load_env(path: Path | None = None) -> None:
    global _LOADED
    if _LOADED:
        return
    p = path or (ROOT / ".env")
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
    _LOADED = True


def get(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    load_env()
    val = os.environ.get(name, default)
    if required and not val:
        raise RuntimeError(
            f"{name} not set. Copy .env.example to .env and fill it in "
            f"(or export {name})."
        )
    return val


def redact(secret: str | None) -> str:
    """Show only the first 3 chars (provider hint, not key material) + length."""
    if not secret:
        return "<unset>"
    return f"{secret[:3]}***redacted*** (len {len(secret)})"
