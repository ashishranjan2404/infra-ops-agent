#!/usr/bin/env python3
"""D7 — Cascade-only "training" + simple↔cascade transfer eval (frozen-LLM regime).

WHAT THIS IS
------------
The policy in this repo is a FROZEN LLM steered by an in-context prompt. The only
lever that plays the role of "training data" is the EXEMPLAR POOL injected few-shot
into the proposer prompt. So "train on cascade incidents only" == build the exemplar
pool exclusively from the cascade family, then measure held-out pass@1 on BOTH the
cascade family (in-distribution) and the simple family (out-of-distribution) to see
transfer.

This is the cheap, reproducible analog of a real RFT run: same train/eval split
discipline, same metric (deterministic-judge binary pass@1 + Wilson 95% CI), no
gradient steps. If/when a real fine-tune is available, swap make_proposer() for a
checkpoint-backed call and the eval harness below is unchanged.

It edits NO shared core file. It imports core modules read-only and adds only the
exemplar-injection wrapper.

USAGE
-----
    set -a; source ~/.zshrc; set +a            # export HUD_API_KEY
    python3 experiments/ralph_outputs/D7/artifacts/d7_train_eval.py \
        --config experiments/ralph_outputs/D7/artifacts/d7_cascade_only.yaml \
        --out    experiments/ralph_outputs/D7/artifacts/d7_results.json

    # dry run (no network) — validates split/leakage/exemplar wiring deterministically:
    python3 .../d7_train_eval.py --config .../d7_cascade_only.yaml --dry-run

Output: a JSON object keyed by config in {cascade, mixed, none}, each holding per
eval-family {n, passes, pass@1, ci95, mean_reward, eval_incidents}, plus a
"transfer" block with the H1/H2 deltas.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics as st
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

# --- core imports (READ-ONLY; nothing here mutates shared modules) ----------
from compute_pass_at_k import wilson_ci, binary_pass            # noqa: E402
from rex.harness import load_scenario, run_plan, scenarios_by_family  # noqa: E402
from rex.loop import build_prompt, parse_plan                    # noqa: E402
from rex.scoring import score_plan                               # noqa: E402


# ---------------------------------------------------------------------------
# Exemplar pool = the "training set". An exemplar is a (symptom, gold action)
# pair we can show the frozen model in-context. We derive the gold action from
# the scenario's fix_tools (the deterministic judge's notion of a correct fix);
# when fix_tools is absent we fall back to the gold_root prose. This is exactly
# the signal a real fine-tune would distill — we just inject it at inference.
# ---------------------------------------------------------------------------
def _scenario_cfg(name: str) -> dict:
    """Read the merged registry entry without importing the private dict."""
    from rex.harness import _SCENARIOS  # noqa: PLC0415  (intentional read-only peek)
    return _SCENARIOS.get(name, {})


def make_exemplar(name: str) -> dict:
    cfg = _scenario_cfg(name)
    fix = cfg.get("fix_tools")
    if isinstance(fix, set):
        fix = sorted(fix)
    return {
        "name": name,
        "family": cfg.get("family", "unlabeled"),
        "symptom": cfg.get("symptom", ""),
        "gold_action": list(fix) if fix else [],
        "gold_root": cfg.get("gold_root", ""),
    }


def render_exemplars(exemplars: list[dict]) -> str:
    if not exemplars:
        return ""
    lines = [
        "Here are worked examples of past incidents and their CORRECT remediation.",
        "Use them to calibrate your diagnosis (note the failure pattern, not the names):",
        "",
    ]
    for i, ex in enumerate(exemplars, 1):
        act = ", ".join(ex["gold_action"]) if ex["gold_action"] else "(see root cause)"
        lines.append(f"Example {i} [{ex['family']}]:")
        lines.append(f"  Symptom: {ex['symptom']}")
        lines.append(f"  Root cause: {ex['gold_root']}")
        lines.append(f"  Correct remediation tool(s): {act}")
        lines.append("")
    lines.append("Now solve the NEW incident below.\n")
    return "\n".join(lines)


def make_proposer(model: str, exemplar_block: str, temp: float, max_tokens: int):
    """Frozen-LLM proposer with a fixed in-context exemplar prefix."""
    from agent.llm import call  # noqa: PLC0415  (lazy: dry-run needs no network)

    def _propose(scenario, prior_feedback=None):
        base = build_prompt(scenario, prior_feedback)
        prompt = (exemplar_block + base) if exemplar_block else base
        last = None
        for _ in range(2):
            try:
                txt = call(model, prompt, max_tokens=max_tokens, temperature=temp)
                return parse_plan(txt)
            except Exception as e:  # noqa: BLE001
                last = e
        raise last

    return _propose


# ---------------------------------------------------------------------------
# Train/eval split with a hard leakage guard.
# ---------------------------------------------------------------------------
def build_split(cfg: dict, rng: random.Random) -> dict:
    fam = scenarios_by_family()
    train_fam = cfg["train_family"]
    pool = sorted(fam.get(train_fam, []))
    rng.shuffle(pool)
    n_ex = min(cfg["n_exemplars"], max(0, len(pool) - 1))
    train_names = pool[:n_ex]

    eval_sets = {}
    for ef in cfg["eval_families"]:
        cands = sorted(set(fam.get(ef, [])) - set(train_names))  # leakage guard
        rng.shuffle(cands)
        eval_sets[ef] = cands[: cfg["n_eval_incidents"]]
    return {"train_names": train_names, "eval_sets": eval_sets}


def exemplar_block_for(config_name: str, train_names: list[str], eval_names: set,
                       cfg: dict, rng: random.Random) -> str:
    """cascade -> cascade-only pool; mixed -> all families; none -> empty.

    The mixed pool subtracts `eval_names` so the baseline is leakage-clean too
    (Ouroboros Eng A #1 fix): we never show the model an incident it is tested on.
    """
    if config_name == "none":
        return ""
    if config_name == "cascade":
        names = train_names                       # already leakage-clean
    elif config_name == "mixed":
        fam = scenarios_by_family()
        alln = sorted(n for ns in fam.values() for n in ns if n not in eval_names)
        rng.shuffle(alln)
        names = alln[: cfg["n_exemplars"]]
    else:
        raise ValueError(config_name)
    return render_exemplars([make_exemplar(n) for n in names])


# ---------------------------------------------------------------------------
# Eval loop.
# ---------------------------------------------------------------------------
def eval_family(propose, names: list[str], seeds: int, threshold: float,
                dry_run: bool) -> dict:
    rewards: list[float] = []
    for name in names:
        sc = load_scenario(name)
        for s in range(seeds):
            if dry_run:
                # Deterministic stand-in reward: no network. Proves wiring +
                # split + scoring path without spending tokens.
                rewards.append(round(0.5 + 0.4 * ((hash((name, s)) % 100) / 100.0), 3))
                continue
            plan = propose(sc, None)
            sim = run_plan(plan, sc)
            score, _ = score_plan(plan, sc, sim)
            rewards.append(float(score))
    n = len(rewards)
    passes = sum(binary_pass(r, threshold) for r in rewards)
    p1 = passes / n if n else 0.0
    lo, hi = wilson_ci(p1, n)
    return {
        "n": n, "passes": passes,
        "pass@1": round(p1, 4), "ci95": [round(lo, 4), round(hi, 4)],
        "mean_reward": round(st.mean(rewards), 4) if rewards else 0.0,
        "reward_std": round(st.pstdev(rewards), 4) if n > 1 else 0.0,
        "eval_incidents": names,
    }


def run(cfg: dict, dry_run: bool, model_override: str | None) -> dict:
    rng = random.Random(1337)
    split = build_split(cfg, rng)
    model = model_override or cfg.get("model", "glm-5p2")
    configs = ["cascade"] + list(cfg.get("baselines", []))
    out = {"_meta": {
        "model": model, "dry_run": dry_run,
        "train_family": cfg["train_family"], "n_exemplars": cfg["n_exemplars"],
        "train_names": split["train_names"], "configs": configs,
        "seeds": cfg["seeds"], "n_eval_incidents": cfg["n_eval_incidents"],
        "threshold": cfg["pass_threshold"],
    }}
    all_eval_names = {n for names in split["eval_sets"].values() for n in names}
    for cname in configs:
        block = exemplar_block_for(cname, split["train_names"], all_eval_names,
                                   cfg, random.Random(7))
        propose = None if dry_run else make_proposer(
            model, block, cfg.get("temperature", 0.7), cfg.get("max_tokens", 1400))
        out[cname] = {}
        for ef, names in split["eval_sets"].items():
            out[cname][ef] = eval_family(
                propose, names, cfg["seeds"], cfg["pass_threshold"], dry_run)

    # Transfer deltas (the headline numbers).
    def p1(c, f):
        return out.get(c, {}).get(f, {}).get("pass@1", 0.0)
    out["transfer"] = {
        "H1_helps_cascade_vs_none": round(p1("cascade", "cascade") - p1("none", "cascade"), 4),
        "H2_hurts_simple_vs_mixed": round(p1("cascade", "simple") - p1("mixed", "simple"), 4),
        "cascade_only": {"simple_p1": p1("cascade", "simple"), "cascade_p1": p1("cascade", "cascade")},
        "mixed":        {"simple_p1": p1("mixed", "simple"),    "cascade_p1": p1("mixed", "cascade")},
        "none":         {"simple_p1": p1("none", "simple"),     "cascade_p1": p1("none", "cascade")},
        "note": "Positive H1 => cascade-only training helps cascade. Negative H2 => it hurts simple.",
    }
    return out


def load_yaml(path: str) -> dict:
    try:
        import yaml  # noqa: PLC0415
        return yaml.safe_load(open(path))
    except ModuleNotFoundError:
        return _mini_yaml(open(path).read())


def _mini_yaml(text: str) -> dict:
    """Tiny fallback parser for this flat config (scalars + [a, b] lists)."""
    d: dict = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line or line.startswith(" ") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if not v:
            continue
        if v.startswith("[") and v.endswith("]"):
            d[k] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        elif v.lower() in ("true", "false"):
            d[k] = v.lower() == "true"
        else:
            try:
                d[k] = int(v)
            except ValueError:
                try:
                    d[k] = float(v)
                except ValueError:
                    d[k] = v
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    here = os.path.dirname(__file__)
    ap.add_argument("--config", default=os.path.join(here, "d7_cascade_only.yaml"))
    ap.add_argument("--out", default=os.path.join(here, "d7_results.json"))
    ap.add_argument("--model", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    res = run(cfg, args.dry_run, args.model)
    json.dump(res, open(args.out, "w"), indent=2)
    print(json.dumps(res["transfer"], indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
