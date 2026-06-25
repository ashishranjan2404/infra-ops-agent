#!/usr/bin/env python3
"""
B14 cost_model.py — token/cost model for the SRE-Degrees REx evaluation.

Computes an ESTIMATED USD cost per evaluation job (one incident x one seed) for
each evaluation condition, so a downstream script can compute pass@1-per-dollar.

================================  IMPORTANT  ================================
Tokens are NOT logged anywhere in the result JSONs (verified: no usage /
prompt_tokens / completion_tokens fields in the pass@k artifacts). So cost is
*modeled*, not measured. Two inputs drive the model:

  1. PRICES  — per-model $/1M input and $/1M output tokens.
       * Claude prices are REAL (Anthropic price sheet, cached 2026-06):
           Opus 4.8   $5 / $25      Sonnet 4.6 $3 / $15      Haiku 4.5  $1 / $5
       * The repo roster (agent/models.py) also has fictional slugs served via
         the HUD gateway / Fireworks (glm-5p2, deepseek-v4-pro, gpt-5.5,
         gemini-3.1-pro, grok-4.3, minimax-m3). Those are not real public models,
         so their prices here are DOCUMENTED ASSUMPTIONS (a frontier-mid tier),
         flagged with assumed=True. Override via PRICES if you have real numbers.

  2. CALL SHAPE — how many proposer LLM calls each condition issues per job, and
     the token budget per call. Grounded in the real code:
       * rex/eval_pass_at_k.py: proposer max_tokens=1400, temp 0.7; N=4 budget.
         - zero_shot      -> 1 proposer call
         - best_of_n      -> N (=4) proposer calls
         - retry_realistic-> 1..N calls, early-exit on a clean plan (modelled as
           an expected value RETRY_EXPECTED_CALLS, default 2.3)
         - rex            -> budget N (=4) proposer calls (tree expansions)
         - rex_no_oracle  -> budget N (=4) proposer calls
       * The plan SCORER (rex/scoring.py score_plan) is the P0 DETERMINISTIC
         judge — it runs the simulator, NOT an LLM. So judging adds $0. (An
         optional LLM judge in scoring.py uses max_tokens=8; we expose
         JUDGE_CALLS=0 by default to reflect the deterministic path actually used.)

  3. INPUT_TOKENS_PER_CALL — the prompt (scenario + prior feedback). Not logged;
     assumed 1200 input tokens/call (a compact incident spec + rubric). Override.

Everything assumed is a module-level constant you can override before calling
estimate_job_cost(); nothing here hides a number.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


# --------------------------------------------------------------------------- #
# 1. Price table.  $ per 1,000,000 tokens.  assumed=False => real Anthropic price.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Price:
    in_per_m: float           # USD per 1M input tokens
    out_per_m: float          # USD per 1M output tokens
    assumed: bool = False     # True => documented assumption, not a published price
    note: str = ""


PRICES: Dict[str, Price] = {
    # ---- REAL published Anthropic prices (cached 2026-06) ----
    "claude-opus-4-8":  Price(5.0, 25.0, assumed=False, note="Anthropic price sheet"),
    "claude-sonnet-4-6": Price(3.0, 15.0, assumed=False, note="Anthropic price sheet"),
    "claude-haiku-4-5": Price(1.0,  5.0, assumed=False, note="Anthropic price sheet"),
    # ---- DOCUMENTED ASSUMPTIONS for the repo's fictional gateway/fireworks slugs ----
    # Placed at a frontier-mid tier; adjust if real numbers become available.
    "glm-5p2":          Price(0.6,  2.2, assumed=True, note="ASSUMED frontier-mid (Fireworks-class)"),
    "minimax-m3":       Price(0.3,  1.2, assumed=True, note="ASSUMED mid tier (Fireworks-class)"),
    "deepseek-v4-pro":  Price(0.8,  2.4, assumed=True, note="ASSUMED frontier-mid (gateway)"),
    "gpt-5.5":          Price(5.0, 15.0, assumed=True, note="ASSUMED frontier (gateway)"),
    "gemini-3.1-pro":   Price(2.5, 10.0, assumed=True, note="ASSUMED frontier (gateway)"),
    "grok-4.3":         Price(3.0, 15.0, assumed=True, note="ASSUMED frontier (gateway)"),
}

# Fallback price for any model not in the table (clearly an assumption).
DEFAULT_PRICE = Price(1.0, 4.0, assumed=True, note="ASSUMED default (unknown model)")


# --------------------------------------------------------------------------- #
# 2. Call shape per condition (proposer LLM calls per job).  Grounded in code.
# --------------------------------------------------------------------------- #
N_BUDGET = 4                      # rex/eval_pass_at_k.py: N = 4
RETRY_EXPECTED_CALLS = 2.3        # ASSUMED expected calls for retry_realistic (early-exit)

PROPOSER_CALLS: Dict[str, float] = {
    "zero_shot":       1.0,
    "best_of_n":       float(N_BUDGET),
    "retry_realistic": RETRY_EXPECTED_CALLS,
    "rex":             float(N_BUDGET),
    "rex_no_oracle":   float(N_BUDGET),
}

# --------------------------------------------------------------------------- #
# 3. Token budgets per proposer call.
# --------------------------------------------------------------------------- #
OUTPUT_TOKENS_PER_CALL = 1400     # rex/eval_pass_at_k.py: proposer max_tokens=1400 (upper bound)
INPUT_TOKENS_PER_CALL = 1200      # ASSUMED prompt size (incident spec + rubric + feedback)

# Deterministic P0 judge -> no LLM call.  Set >0 only if modelling the LLM-judge path.
JUDGE_CALLS = 0
JUDGE_INPUT_TOKENS = 1200         # rex/scoring.py LLM-judge prompt (only if JUDGE_CALLS>0)
JUDGE_OUTPUT_TOKENS = 8           # rex/scoring.py: max_tokens=8 for the LLM judge


# --------------------------------------------------------------------------- #
# Core estimator.
# --------------------------------------------------------------------------- #
@dataclass
class JobCost:
    model: str
    condition: str
    proposer_calls: float
    input_tokens: int
    output_tokens: int
    usd: float
    price_assumed: bool
    output_token_utilization: float = 1.0   # fraction of max_tokens assumed actually emitted


def price_for(model: str) -> Price:
    return PRICES.get(model, DEFAULT_PRICE)


def _call_usd(price: Price, in_tok: float, out_tok: float) -> float:
    return (in_tok / 1_000_000.0) * price.in_per_m + (out_tok / 1_000_000.0) * price.out_per_m


def estimate_job_cost(
    model: str,
    condition: str,
    *,
    output_token_utilization: float = 0.6,
) -> JobCost:
    """Estimated USD to run ONE incident x ONE seed under `condition` with `model`.

    output_token_utilization: max_tokens is an upper bound; models rarely fill it.
        Default 0.6 => assume a plan uses ~60% of the 1400-token budget. Set 1.0 for
        the worst-case (max_tokens fully consumed) bound.
    """
    if condition not in PROPOSER_CALLS:
        raise KeyError(f"unknown condition {condition!r}; known: {sorted(PROPOSER_CALLS)}")
    price = price_for(model)
    n_prop = PROPOSER_CALLS[condition]
    out_per = OUTPUT_TOKENS_PER_CALL * output_token_utilization

    in_tok = n_prop * INPUT_TOKENS_PER_CALL + JUDGE_CALLS * JUDGE_INPUT_TOKENS
    out_tok = n_prop * out_per + JUDGE_CALLS * JUDGE_OUTPUT_TOKENS
    usd = _call_usd(price, in_tok, out_tok)

    return JobCost(
        model=model,
        condition=condition,
        proposer_calls=n_prop,
        input_tokens=int(round(in_tok)),
        output_tokens=int(round(out_tok)),
        usd=usd,
        price_assumed=price.assumed,
        output_token_utilization=output_token_utilization,
    )


if __name__ == "__main__":
    # quick self-demo
    for cond in PROPOSER_CALLS:
        jc = estimate_job_cost("claude-opus-4-8", cond)
        print(f"opus-4-8 {cond:16s} calls={jc.proposer_calls:>4}  "
              f"in={jc.input_tokens:>5} out={jc.output_tokens:>5}  ${jc.usd:.6f}/job")
