"""Phase-1 GO/NO-GO probe: does a small frozen model's fix IMPROVE across
refinement iterations?

Runs haiku on oom_kill, ~6 iters x 3 seeds, and reports the per-iteration
best-score-so-far curve. CLIMB = feedback is informative and refinement works.
FLAT = the feedback text isn't informative enough (fix that before Phase 2).

    python3 -m rex.probe
"""
from __future__ import annotations

import statistics as st

from agent.llm import call
from rex.harness import load_scenario
from rex.loop import build_prompt, parse_plan, refine_loop

MODEL = "claude-haiku-4-5"
SEEDS = [1, 2, 3]
BUDGET = 6


def seeded_propose(seed: int, temperature: float = 0.6):
    """A proposer whose only difference across seeds is sampling temperature +
    a seed nonce, so the 3 runs are independent samples of the same policy."""
    def propose_fn(scenario, prior_feedback):
        prompt = build_prompt(scenario, prior_feedback) + f"\n\n(sampling variant: {seed})"
        text = call(MODEL, prompt, max_tokens=600, temperature=temperature)
        return parse_plan(text)
    return propose_fn


def _best_so_far(scores: list, n: int) -> list:
    """Monotone best-so-far, padded to length n with the last value (runs that
    resolve early hold their best)."""
    out, b = [], -1.0
    for s in scores:
        b = max(b, s)
        out.append(round(b, 3))
    while len(out) < n:
        out.append(out[-1] if out else 0.0)
    return out


def main() -> int:
    sc = load_scenario("oom_kill")
    print(f"=== REx Phase-1 probe: {MODEL} on '{sc.name}' "
          f"({len(SEEDS)} seeds x {BUDGET} iters) ===\n")

    curves = []
    for seed in SEEDS:
        res = refine_loop(sc, budget=BUDGET, propose_fn=seeded_propose(seed))
        scores = [it["score"] for it in res["iterations"]]
        best = _best_so_far(scores, BUDGET)
        curves.append(best)
        per_iter = "  ".join(f"i{it['iter']}={it['score']:.2f}"
                             f"{'*' if it['resolved'] else ''}" for it in res["iterations"])
        print(f"seed {seed}: {per_iter}")
        print(f"        raw     : {[round(s, 2) for s in scores]}")
        print(f"        best-so-far: {best}   resolved={res['resolved']} "
              f"@iter {res['best_iter']}")
        # show the failed checks per iter (what the loop is climbing on)
        for it in res["iterations"]:
            print(f"          iter {it['iter']}: score={it['score']:.2f} "
                  f"failed={it['failed_checks']}")
        print()

    agg = [round(st.mean(c[i] for c in curves), 3) for i in range(BUDGET)]
    delta = round(agg[-1] - agg[0], 3)
    print("=== aggregate best-so-far (mean over seeds) ===")
    print("  " + "  ".join(f"i{i}={agg[i]:.2f}" for i in range(BUDGET)))
    print(f"  delta(first->last) = {delta:+.3f}")
    verdict = "CLIMB ✅ (refinement works — proceed to gate)" if delta >= 0.15 else \
              "FLAT ⚠️  (feedback not informative enough — fix before Phase 2)"
    print(f"\nVERDICT: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
