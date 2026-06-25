"""C3 — Harness synthesis on ONLY novel incidents (generalization test).

This is a TASK-NAMESPACED runner. It imports the shared, unmodified machinery in
`rex/harness_synth.py` (labeled_examples, thompson_search, propose_ruleset,
train_score, confusion, hazard_coverage, the trusted rule interpreter, the
hand-written baseline) and re-runs synthesis over a DIFFERENT split: a TRAIN/HELDOUT
partition drawn ENTIRELY from the A8 strict-novel held-out set
(`experiments/ralph_outputs/A8/artifacts/heldout_manifest.json`).

Why this is the real generalization test:
  - A8 certified these 15 cidg incidents as having ZERO overlap with the training
    trajectories (exact-id + token-pair + company-axis novelty). So every example
    here is novel w.r.t. the policy's training corpus.
  - We further split the 15 novel incidents into TRAIN (10) / HELDOUT (5) so the
    spanning hazard `treats_forbidden_category` appears in BOTH splits — the genuine
    cross-incident test. Same-set synthesis would be a learned lookup; only held-out
    counts.

We NEVER exec LLM output. The LLM (mutation operator) only proposes edited rule-sets
(data); a trusted interpreter applies them over 6 known features. The hand-written
is_safe stays intact as the human baseline.

The mutation model is overridable via $C3_MODEL because the Anthropic credits used by
the default `claude-haiku-4-5` are exhausted in this env (HTTP 400); the HUD gateway
model `gpt-5.5` is the working frontier substitute. Synthesis is model-agnostic: any
model that emits a JSON rule list works.

    C3_MODEL=gpt-5.5 python3 experiments/ralph_outputs/C3/artifacts/run_novel_synth.py
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)

import rex.harness_synth as hs  # noqa: E402  (shared core, imported NOT edited)
from rex.tree import thompson_search  # noqa: E402

# ---- novel split (all 15 ids are A8-certified novel) -----------------------------
A8_MANIFEST = os.path.join(REPO, "experiments", "ralph_outputs", "A8",
                           "artifacts", "heldout_manifest.json")

# TRAIN/HELDOUT partition of the novel set. Chosen so the GENERALIZABLE hazard
# (treats_forbidden_category) spans both splits; leak_restart is single-incident
# (media_oom_leak) and lands in HELDOUT -> reported as out-of-scope for generalization.
TRAIN = ["auth_cert_expiry", "billing_disk_fill", "checkout_bad_rollout",
         "conntrack_exhaustion", "facebook_bgp_backbone", "gke_ip_exhaustion",
         "ingest_fd_exhaust", "kafka_poison_pill", "payments_dep_revoked",
         "search_cpu_starve"]
HELDOUT = ["azure_leapyear_cert", "firefox_addon_cert", "knight_capital_conflict",
           "media_oom_leak", "redis_cache_flush"]

MODEL = os.environ.get("C3_MODEL", "claude-haiku-4-5")
BUDGET = int(os.environ.get("C3_BUDGET", "8"))
OUT = os.path.join(os.path.dirname(__file__), "novel_synth_result.json")


def _load_novel_universe() -> list:
    """Read the A8 manifest and return its certified-novel cidg ids (the universe
    our TRAIN/HELDOUT must be drawn from). Falls back to the union of our split if
    the manifest is absent."""
    if os.path.exists(A8_MANIFEST):
        m = json.load(open(A8_MANIFEST))
        return sorted(m.get("held_out", []))
    return sorted(set(TRAIN) | set(HELDOUT))


def main() -> int:
    novel = _load_novel_universe()
    # provenance / safety asserts
    assert not (set(TRAIN) & set(HELDOUT)), "train/held-out overlap!"
    missing = (set(TRAIN) | set(HELDOUT)) - set(novel)
    assert not missing, f"split contains non-novel ids (not in A8 held-out): {missing}"

    train_ex = [e for n in TRAIN for e in hs.labeled_examples(n)]
    held_ex = [e for n in HELDOUT for e in hs.labeled_examples(n)]

    print(f"=== C3 novel-only harness synthesis: {MODEL}, budget {BUDGET} ===")
    print(f"A8 novel universe ({len(novel)}): {novel}")
    print(f"TRAIN novel ({len(TRAIN)}): {TRAIN}")
    print(f"HELDOUT novel ({len(HELDOUT)}): {HELDOUT}")
    print(f"labels: {len(train_ex)} train, {len(held_ex)} held-out\n")

    tr_cov, ho_cov = hs.hazard_coverage(TRAIN), hs.hazard_coverage(HELDOUT)
    print("HAZARD COVERAGE (which novel incidents exhibit each blockable hazard):")
    scope = {}
    for h in sorted(set(tr_cov) | set(ho_cov)):
        in_tr, in_ho = tr_cov.get(h, []), ho_cov.get(h, [])
        gen = "GENERALIZABLE" if (in_ho and in_tr) else \
              ("UNSEEN-in-train (out-of-scope)" if in_ho else "train-only")
        scope[h] = gen
        print(f"  {h:26} train={in_tr}  held_out={in_ho}  [{gen}]")
    print()

    # SYNTHESIS — train labels ONLY (no held-out leakage). Uses the shared operator.
    def _propose(parent):
        # temporarily point the shared operator at our chosen model
        prev = hs.MODEL
        hs.MODEL = MODEL
        try:
            return hs.propose_ruleset(parent, train_ex)
        finally:
            hs.MODEL = prev

    res = thompson_search(
        propose=_propose,
        evaluate=lambda rs: hs.train_score(rs, train_ex),
        budget=BUDGET, seed=0, stop_at=1.0)
    best = res["nodes"][res["best"]]["cand"]
    print(f"SYNTHESIS done: {len(res['nodes'])} tree nodes, "
          f"best TRAIN score={res['best_score']:.3f}")
    print(f"  node train-scores: {[round(n['score'], 3) for n in res['nodes']]}\n")

    print("SYNTHESIZED RULE-SET (best by TRAIN, learned on NOVEL incidents only):")
    for r in best:
        print(f"  - block if tool in {r['match_tools'] or 'ANY'} "
              f"and {r['conditions']}  | {r['reason'][:70]}")
    if not best:
        print("  (empty — synthesis found no improving rule)")
    print()

    harnesses = {
        "seed (empty)": lambda exs: hs.confusion([], exs),
        "synthesized (novel-train)": lambda exs: hs.confusion(best, exs),
        "hand-written is_safe": lambda exs: hs.confusion_pred(hs.handwritten_pred, exs),
    }
    print("=" * 80)
    print(f"{'harness':28}  {'TRAIN acc':>9} {'TRAIN FA%':>9}   "
          f"{'HELDOUT acc':>11} {'HELDOUT FA%':>11}")
    table = {}
    for label, fn in harnesses.items():
        tr, ho = fn(train_ex), fn(held_ex)
        table[label] = {
            "train": {k: tr[k] for k in ("accuracy", "false_allow", "false_allow_rate")},
            "heldout": {k: ho[k] for k in ("accuracy", "false_allow", "false_allow_rate")}}
        print(f"{label:28}  {tr['accuracy']:>9} {tr['false_allow_rate']:>9}   "
              f"{ho['accuracy']:>11} {ho['false_allow_rate']:>11}")
    print()

    hc = hs.confusion(best, held_ex)
    print(f"SYNTHESIZED held-out MISTAKES: {hc['false_allow']} false-allow, "
          f"{hc['false_block']} false-block")
    for e in hc["false_allow_ex"]:
        active = {k: v for k, v in e["features"].items() if v is True}
        print(f"  FALSE-ALLOW: {e['incident']} / {e['tool']}->{e['target']} "
              f"(hazard={e['hazard']}, active={active})")
    for e in hc["false_block_ex"]:
        print(f"  FALSE-BLOCK: {e['incident']} / {e['tool']}->{e['target']} "
              f"(was {e['hazard']})")
    print()
    print("LEAKAGE CHECK: synthesis used novel-TRAIN labels only; novel-HELDOUT "
          "labels never touched in propose()/evaluate(). disjoint:",
          not (set(TRAIN) & set(HELDOUT)))

    out = {
        "experiment": "C3_novel_only_synthesis",
        "model": MODEL, "budget": BUDGET,
        "a8_novel_universe": novel,
        "train": TRAIN, "heldout": HELDOUT,
        "rules": best,
        "hazard_scope": scope,
        "table": table,
        "node_scores": [n["score"] for n in res["nodes"]],
        "heldout_false_allow": [(e["incident"], e["tool"], e["target"], e["hazard"])
                                for e in hc["false_allow_ex"]],
        "heldout_false_block": [(e["incident"], e["tool"], e["target"], e["hazard"])
                                for e in hc["false_block_ex"]],
        "leakage_disjoint": not (set(TRAIN) & set(HELDOUT)),
    }
    json.dump(out, open(OUT, "w"), indent=2, default=list)
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
