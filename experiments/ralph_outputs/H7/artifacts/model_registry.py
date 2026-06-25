#!/usr/bin/env python3
"""model_registry — list/query the SRE-Degrees model registry.

A tiny dependency-free CLI over model_registry.json. It tracks every model
referenced in the repo: frozen eval policies (the ROSTER in agent/models.py) and
forked/trainable open models (the GRPO/RFT runs in opensre-traj). For each model
it knows: slug, base, provider, role, training_status, eval pass@1 (if measured),
and the real frontier baseline/REx mean rewards.

Usage:
  python3 model_registry.py list
  python3 model_registry.py list --role trainable
  python3 model_registry.py list --status flat,aborted
  python3 model_registry.py list --json
  python3 model_registry.py show opensre-qwen3-8b
  python3 model_registry.py query --base Qwen/Qwen3-8B
  python3 model_registry.py query --provider gateway --role eval
  python3 model_registry.py stats

Exit codes: 0 ok, 2 not found / bad args.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(HERE, "model_registry.json")


def load(path):
    with open(path) as f:
        return json.load(f)


def _csv(s):
    return [x.strip() for x in s.split(",") if x.strip()] if s else None


def _match(m, role=None, status=None, provider=None, base=None):
    if role and m.get("role") != role:
        return False
    if provider and m.get("provider") != provider:
        return False
    if base and m.get("base") != base:
        return False
    if status and m.get("training_status") not in status:
        return False
    return True


def _fmt_num(v):
    return "-" if v is None else f"{v:.3f}" if isinstance(v, float) else str(v)


def cmd_list(reg, args):
    status = _csv(args.status)
    rows = [m for m in reg["models"]
            if _match(m, role=args.role, status=status, provider=args.provider, base=args.base)]
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("(no models match)")
        return 0
    hdr = f"{'ID':<22} {'BASE':<26} {'PROVIDER':<11} {'ROLE':<9} {'STATUS':<9} {'p@1':>5} {'base_mr':>7} {'rex_mr':>7}"
    print(hdr)
    print("-" * len(hdr))
    for m in rows:
        print(f"{m['id']:<22} {str(m['base']):<26} {m['provider']:<11} {m['role']:<9} "
              f"{str(m['training_status']):<9} {_fmt_num(m['eval_pass_at_1']):>5} "
              f"{_fmt_num(m['frontier_baseline_mean']):>7} {_fmt_num(m['frontier_rex_mean']):>7}")
    print(f"\n{len(rows)} model(s).  base_mr/rex_mr = frontier mean reward (baseline vs REx).")
    return 0


def cmd_show(reg, args):
    for m in reg["models"]:
        if m["id"] == args.id or m["slug"] == args.id:
            print(json.dumps(m, indent=2))
            return 0
    print(f"error: no model with id/slug '{args.id}'", file=sys.stderr)
    return 2


def cmd_query(reg, args):
    status = _csv(args.status)
    rows = [m for m in reg["models"]
            if _match(m, role=args.role, status=status, provider=args.provider, base=args.base)]
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for m in rows:
        print(f"{m['id']:<22} slug={m['slug']}  base={m['base']}  status={m['training_status']}")
    print(f"\n{len(rows)} match(es).")
    return 0 if rows else 2


def cmd_stats(reg, args):
    ms = reg["models"]
    by_role, by_status, by_provider = {}, {}, {}
    for m in ms:
        by_role[m["role"]] = by_role.get(m["role"], 0) + 1
        by_status[m["training_status"]] = by_status.get(m["training_status"], 0) + 1
        by_provider[m["provider"]] = by_provider.get(m["provider"], 0) + 1
    print(f"total models: {len(ms)}")
    print(f"by role:     {dict(sorted(by_role.items()))}")
    print(f"by status:   {dict(sorted(by_status.items()))}")
    print(f"by provider: {dict(sorted(by_provider.items()))}")
    trained = [m for m in ms if m["train_mean_reward_start"] is not None]
    if trained:
        print("\ntraining runs (mean reward start -> end):")
        for m in trained:
            d = m["train_mean_reward_end"] - m["train_mean_reward_start"]
            arrow = "up" if d > 0 else ("flat" if d == 0 else "down")
            print(f"  {m['id']:<22} {m['train_mean_reward_start']:.4f} -> "
                  f"{m['train_mean_reward_end']:.4f}  ({d:+.4f} {arrow})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="model_registry", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DEFAULT_DB, help="path to model_registry.json")
    sub = ap.add_subparsers(dest="cmd")

    pl = sub.add_parser("list", help="list models (filterable)")
    pl.add_argument("--role"); pl.add_argument("--status"); pl.add_argument("--provider")
    pl.add_argument("--base"); pl.add_argument("--json", action="store_true")

    ps = sub.add_parser("show", help="show one model by id or slug")
    ps.add_argument("id")

    pq = sub.add_parser("query", help="query by field")
    pq.add_argument("--role"); pq.add_argument("--status"); pq.add_argument("--provider")
    pq.add_argument("--base"); pq.add_argument("--json", action="store_true")

    sub.add_parser("stats", help="summary counts + training deltas")

    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 0
    reg = load(args.db)
    return {"list": cmd_list, "show": cmd_show, "query": cmd_query,
            "stats": cmd_stats}[args.cmd](reg, args)


if __name__ == "__main__":
    sys.exit(main())
