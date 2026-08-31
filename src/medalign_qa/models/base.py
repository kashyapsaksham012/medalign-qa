"""Abstract model interface + generation config/result types."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class GenConfig:
    n: int = 1                       # number of independent samples
    temperature: float = 0.0         # 0.0 == greedy (few-shot / CoT single decode)
    top_p: float = 1.0
    max_tokens: int = 16
    stop: list[str] | None = None
    seed: int | None = None          # forwarded when the provider supports it
    system: str | None = None        # RA-24: output-format instruction for chat-tuned
                                     # substitute models (the paper's completion-style
                                     # models did not need one; exemplar content is
                                     # unchanged). None -> single user message.


@dataclass
class GenResult:
    texts: list[str]                 # len == GenConfig.n
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    raw_meta: dict = field(default_factory=dict)


class LLM(Protocol):
    name: str

    def generate(self, prompt: str, cfg: GenConfig) -> GenResult:
        ...
