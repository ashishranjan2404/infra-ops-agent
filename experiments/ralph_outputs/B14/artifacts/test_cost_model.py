#!/usr/bin/env python3
"""Unit tests for B14 cost_model.py. Run: python3 -m pytest test_cost_model.py -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cost_model as cm  # noqa: E402


def test_real_claude_prices_not_assumed():
    for m in ("claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5"):
        assert cm.PRICES[m].assumed is False, m
    # gateway/fireworks slugs are assumptions
    for m in ("glm-5p2", "deepseek-v4-pro", "gpt-5.5"):
        assert cm.PRICES[m].assumed is True, m


def test_opus_price_values():
    p = cm.PRICES["claude-opus-4-8"]
    assert (p.in_per_m, p.out_per_m) == (5.0, 25.0)


def test_zero_shot_is_one_call_rex_is_budget():
    assert cm.PROPOSER_CALLS["zero_shot"] == 1.0
    assert cm.PROPOSER_CALLS["best_of_n"] == float(cm.N_BUDGET)
    assert cm.PROPOSER_CALLS["rex"] == float(cm.N_BUDGET)
    assert cm.PROPOSER_CALLS["rex_no_oracle"] == float(cm.N_BUDGET)
    # retry_realistic between 1 and N
    assert 1.0 <= cm.PROPOSER_CALLS["retry_realistic"] <= cm.N_BUDGET


def test_rex_costs_more_than_zero_shot_same_model():
    z = cm.estimate_job_cost("glm-5p2", "zero_shot").usd
    r = cm.estimate_job_cost("glm-5p2", "rex").usd
    assert r > z
    # rex issues N calls vs 1 -> ~N x cost (within rounding; input+output both scale)
    assert abs(r / z - cm.N_BUDGET) < 0.01


def test_cost_scales_with_price():
    # opus output is 25/2.2 ~ 11x glm output price; cost should be strictly higher
    o = cm.estimate_job_cost("claude-opus-4-8", "zero_shot").usd
    g = cm.estimate_job_cost("glm-5p2", "zero_shot").usd
    assert o > g


def test_utilization_scales_output_cost_only():
    full = cm.estimate_job_cost("claude-opus-4-8", "zero_shot", output_token_utilization=1.0)
    half = cm.estimate_job_cost("claude-opus-4-8", "zero_shot", output_token_utilization=0.5)
    assert full.output_tokens > half.output_tokens
    assert full.input_tokens == half.input_tokens   # input unaffected
    assert full.usd > half.usd


def test_unknown_condition_raises():
    try:
        cm.estimate_job_cost("claude-opus-4-8", "bogus")
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown condition")


def test_unknown_model_uses_assumed_default():
    jc = cm.estimate_job_cost("totally-made-up-model", "zero_shot")
    assert jc.price_assumed is True
    assert jc.usd > 0


def test_judge_is_deterministic_zero_cost_by_default():
    assert cm.JUDGE_CALLS == 0  # deterministic P0 judge -> no LLM cost in the modelled path


if __name__ == "__main__":
    # allow running without pytest
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
