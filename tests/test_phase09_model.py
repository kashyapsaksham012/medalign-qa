"""Phase 9 -- model backend (offline, mock only; no network, no cost)."""
from __future__ import annotations

from medalign_qa.models import load_model
from medalign_qa.models.base import GenConfig
from medalign_qa.models.env import redact
from medalign_qa.preprocessing import prompt_builder as pb
from medalign_qa.utils import io, paths


def test_mock_generate_shapes():
    m = load_model(mock=True)
    r = m.generate("hi", GenConfig(n=3, temperature=0.7))
    assert len(r.texts) == 3
    assert all("Answer:" in t for t in r.texts)


def test_mock_greedy_is_deterministic():
    m = load_model(mock=True)
    a = m.generate("some prompt", GenConfig(n=1, temperature=0.0)).texts[0]
    b = m.generate("some prompt", GenConfig(n=1, temperature=0.0)).texts[0]
    assert a == b


def test_redact_never_leaks_key():
    out = redact("sk-or-v1-abcdefghijklmnop")
    assert out.startswith("sk-or-") and out.endswith("mnop (len 25)")
    assert "abcdefghij" not in out
    assert redact(None) == "<unset>"


def test_prompt_builder_strips_provenance_header():
    # the '# VERBATIM ...' header must not reach the model
    p = pb.build_mc_fewshot(
        next(r for r in io.read_jsonl(paths.PROCESSED / "medqa_usmle_4opt.jsonl")
             if r["split"] == "test"), "medqa")
    assert "VERBATIM" not in p
    assert p.lstrip().startswith("The following are multiple choice questions")
    assert p.rstrip().endswith("Answer:")


def test_system_prompts_defined():
    for s in ("few_shot", "cot", "longform"):
        assert len(pb.system_for(s)) > 20


def test_config_file_present():
    cfg = io.read_yaml(paths.CONFIGS / "model" / "llama31-8b-instruct.yaml")
    assert cfg["decode"]["self_consistency"]["n"] == 11        # PAPER-SPECIFIED
    assert cfg["decode"]["selective_prediction"]["n"] == 41    # PAPER-SPECIFIED


def test_env_file_is_gitignored():
    import subprocess
    r = subprocess.run(["git", "check-ignore", ".env"], cwd=paths.ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0 and ".env" in r.stdout


def test_no_secret_in_tracked_files():
    """The API key must not appear in any git-tracked file."""
    import subprocess
    key_frag = "sk-or-v1-"
    tracked = subprocess.run(["git", "ls-files"], cwd=paths.ROOT,
                             capture_output=True, text=True).stdout.split()
    for f in tracked:
        fp = paths.ROOT / f
        try:
            if key_frag in fp.read_text(encoding="utf-8", errors="ignore"):
                raise AssertionError(f"possible secret in tracked file: {f}")
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            pass
