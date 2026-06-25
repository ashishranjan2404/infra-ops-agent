"""A14 — Time-pressure / budget-limited episode variants for realistic REx eval.

WHY
---
The core REx loops (`rex.loop.refine_loop`, `rex.tree.rex_tree`) treat the episode
budget as a flat *iteration count* (`budget=N`). That is unrealistic for an on-call
SRE: in a real incident the operator is bounded by WALL-CLOCK TIME (a deadline / SLA)
and by the number of REMEDIATION ACTIONS they can safely fire, NOT by a tidy count of
"refinement rounds". A model that takes 9 slow proposals to converge is worse, on-call,
than one that converges in 2 fast ones — even if both eventually clean-win.

This module imposes those realistic limits as a WRAPPER around the unchanged core loop.
It does NOT edit any shared core file. It works by:

  1. wrapping the proposer so every model call is timed and the per-call latency is
     accumulated into an episode budget;
  2. counting the remediation actions each proposed plan would fire (the "step" cost);
  3. cutting the loop off early (via a propose_fn that raises `BudgetExhausted` once a
     limit is crossed) so the loop terminates at the last in-budget iteration.

Two budget axes (either or both may be set):
  * time_budget_s  — wall-clock seconds across the whole episode (sum of proposer
                     latencies; the dominant real cost). 0/None = unlimited.
  * step_budget    — max cumulative remediation actions across all iterations.
                     0/None = unlimited.

DETERMINISM
-----------
For tests / reproducible demos you can pass a `clock` callable (defaults to
`time.monotonic`) and a `cost_fn` (defaults to real latency). With a fake clock the
whole thing is deterministic and needs no network.

USAGE
-----
    from budget_wrapper import BudgetConfig, run_budgeted_episode
    cfg = BudgetConfig(time_budget_s=30.0, step_budget=4)
    result = run_budgeted_episode(scenario, cfg, base_propose_fn=my_proposer)
    # result["budget"] -> {"time_spent_s", "steps_spent", "stopped_reason", ...}
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional


class BudgetExhausted(Exception):
    """Raised by the wrapped proposer when a budget axis is crossed; this terminates
    the underlying loop cleanly at the last in-budget iteration."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass
class BudgetConfig:
    """A realistic, time-pressured episode variant.

    time_budget_s : wall-clock seconds for the whole episode (None/0 = unlimited).
    step_budget   : max cumulative remediation actions (None/0 = unlimited).
    iter_cap      : hard ceiling on iterations passed to the loop (safety net; the
                    budget axes are what actually bite). Defaults to 8.
    label         : human name for the variant (e.g. "tight", "pager-storm").
    """
    time_budget_s: Optional[float] = None
    step_budget: Optional[int] = None
    iter_cap: int = 8
    label: str = "unbounded"

    def is_bounded(self) -> bool:
        return bool(self.time_budget_s) or bool(self.step_budget)


# A small library of named, realistic variants for eval sweeps. The time numbers are
# tuned for a ~few-second-per-call frozen small model; adjust per deployment.
PRESETS = {
    "unbounded":   BudgetConfig(label="unbounded", iter_cap=8),
    "relaxed":     BudgetConfig(time_budget_s=60.0, step_budget=8, iter_cap=8, label="relaxed"),
    "tight":       BudgetConfig(time_budget_s=20.0, step_budget=4, iter_cap=6, label="tight"),
    "pager-storm": BudgetConfig(time_budget_s=8.0,  step_budget=2, iter_cap=4, label="pager-storm"),
}


@dataclass
class BudgetMeter:
    """Mutable accounting carried across iterations of one episode."""
    cfg: BudgetConfig
    clock: Callable[[], float] = time.monotonic
    time_spent_s: float = 0.0
    steps_spent: int = 0
    iters_started: int = 0
    stopped_reason: Optional[str] = None
    per_iter: list = field(default_factory=list)

    def _over_budget(self) -> Optional[str]:
        if self.cfg.time_budget_s and self.time_spent_s >= self.cfg.time_budget_s:
            return (f"time_budget exceeded: {self.time_spent_s:.2f}s "
                    f">= {self.cfg.time_budget_s:.2f}s")
        if self.cfg.step_budget and self.steps_spent >= self.cfg.step_budget:
            return (f"step_budget exceeded: {self.steps_spent} "
                    f">= {self.cfg.step_budget}")
        return None

    def report(self) -> dict:
        return {
            "label": self.cfg.label,
            "time_budget_s": self.cfg.time_budget_s,
            "step_budget": self.cfg.step_budget,
            "time_spent_s": round(self.time_spent_s, 4),
            "steps_spent": self.steps_spent,
            "iters_started": self.iters_started,
            "stopped_reason": self.stopped_reason or "loop_converged_or_iter_cap",
            "per_iter": self.per_iter,
        }


def _action_cost(plan: dict) -> int:
    """Step cost of a plan = number of remediation actions it would fire. An empty
    plan still costs the *thinking* (handled by the time axis), but zero steps."""
    if not isinstance(plan, dict):
        return 0
    acts = plan.get("actions") or []
    return sum(1 for a in acts if isinstance(a, dict) and a.get("tool"))


def budgeted_proposer(
    base_propose_fn: Callable,
    meter: BudgetMeter,
    cost_fn: Optional[Callable[[float, float], float]] = None,
):
    """Wrap a proposer so each call (a) is checked against the budget BEFORE running,
    (b) is timed, and (c) feeds its latency + the plan's step cost into the meter.

    `cost_fn(t_before, t_after) -> seconds` lets tests inject a fake cost (default:
    real elapsed wall-clock from `meter.clock`).
    """
    def _propose(scenario, prior_feedback=None):
        # Pre-flight: if we are ALREADY out of budget, don't even start this iteration.
        reason = meter._over_budget()
        if reason:
            meter.stopped_reason = reason
            raise BudgetExhausted(reason)

        meter.iters_started += 1
        t0 = meter.clock()
        plan = base_propose_fn(scenario, prior_feedback)
        t1 = meter.clock()

        dt = cost_fn(t0, t1) if cost_fn else (t1 - t0)
        steps = _action_cost(plan)
        meter.time_spent_s += dt
        meter.steps_spent += steps
        meter.per_iter.append({
            "iter": meter.iters_started - 1,
            "latency_s": round(dt, 4),
            "steps": steps,
            "cum_time_s": round(meter.time_spent_s, 4),
            "cum_steps": meter.steps_spent,
        })

        # Post-flight: if THIS iteration tipped us over, record it. We still return the
        # plan (it ran within budget); the NEXT propose call will pre-flight-abort.
        post = meter._over_budget()
        if post:
            meter.stopped_reason = post
        return plan
    return _propose


def run_budgeted_episode(
    scenario,
    cfg: BudgetConfig,
    base_propose_fn: Callable,
    refine_loop_fn: Optional[Callable] = None,
    clock: Callable[[], float] = time.monotonic,
    cost_fn: Optional[Callable[[float, float], float]] = None,
    **loop_kwargs,
) -> dict:
    """Run one REx episode under a budget. Returns the loop's normal result dict with a
    "budget" key appended.

    Enforcement strategy (keeps every in-budget iteration — nothing is discarded):
    the wrapped proposer raises `BudgetExhausted` on its PRE-FLIGHT check, i.e. only
    when an iteration that has NOT yet started would exceed the budget. The unchanged
    core loop catches nothing, but `_run_with_budget` runs it via a generator-style
    re-entry: we let the loop run, and on `BudgetExhausted` we reconstruct the result
    from the iterations already logged through the wrapper's `meter.per_iter` and the
    loop's `log` callback. To stay simple AND lossless we capture each completed
    iteration via the loop's `log=` hook.
    """
    if refine_loop_fn is None:
        from rex.loop import refine_loop as refine_loop_fn

    meter = BudgetMeter(cfg=cfg, clock=clock)
    wrapped = budgeted_proposer(base_propose_fn, meter, cost_fn=cost_fn)

    captured: list = []
    user_log = loop_kwargs.pop("log", None)

    def _log(rec):
        captured.append(rec)
        if user_log:
            user_log(rec)

    truncated = False
    truncation_reason = None
    try:
        result = refine_loop_fn(scenario, budget=cfg.iter_cap, propose_fn=wrapped,
                                log=_log, **loop_kwargs)
    except BudgetExhausted as e:
        # Pre-flight abort: the iterations in `captured` all completed within budget.
        truncated = True
        truncation_reason = e.reason
        result = _result_from_iterations(scenario, captured)

    result["budget"] = meter.report()
    result["budget_truncated"] = truncated
    if truncated:
        result["truncation_reason"] = truncation_reason
    return result


def _result_from_iterations(scenario, iterations: list) -> dict:
    """Rebuild a refine_loop-shaped result from the iterations that fit in budget.
    Mirrors the aggregation in rex.loop.refine_loop so a truncated episode still
    reports best_score / resolved / clean_win / outcome consistently."""
    if not iterations:
        return {
            "scenario": getattr(scenario, "name", "?"),
            "iterations": [], "best_score": -1.0, "best_iter": -1,
            "resolved": False, "clean_win": False, "outcome": "escalated",
        }
    best_iter = max(range(len(iterations)), key=lambda i: iterations[i]["score"])
    clean_win = any(not it["failed_checks"] for it in iterations)
    result = {
        "scenario": getattr(scenario, "name", "?"),
        "iterations": iterations,
        "best_score": round(iterations[best_iter]["score"], 4),
        "best_iter": iterations[best_iter]["iter"],
        "resolved": any(it["resolved"] for it in iterations),
        "clean_win": clean_win,
        "outcome": "resolved" if clean_win else "escalated",
    }
    return result
