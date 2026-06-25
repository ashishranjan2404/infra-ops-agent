"""D6 — DPO trainer scaffold for opensre incident preference pairs.

Reads dpo_config.yaml + dpo_pairs.jsonl (from build_dpo_pairs.py) and launches a
TRL DPOTrainer run. Mirrors train_rft.py (GRPO) but on STATIC preference data —
no env rollouts. Additive: does not touch env or rex core.

Usage:
  python build_dpo_pairs.py                 # regenerate dpo_pairs.jsonl
  python train_dpo.py --config dpo_config.yaml          # real run (needs GPU+TRL)
  python train_dpo.py --config dpo_config.yaml --dry-run  # validate data only, no backend

The --dry-run path is dependency-free and is what CI / this Ralph cycle exercises.
The real path requires trl/transformers/torch + a trainable (forked open) model and
will print a clear blocker if the backend is unavailable.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys


def load_yaml(path: str) -> dict:
    try:
        import yaml  # pyyaml is already a rex dep
        return yaml.safe_load(open(path))
    except ImportError:
        sys.exit("BLOCKER: pyyaml not installed; `pip install pyyaml`.")


def load_pairs(path: str) -> list[dict]:
    return [json.loads(l) for l in open(path) if l.strip()]


def split(pairs, val_split, seed):
    rng = random.Random(seed)
    idx = list(range(len(pairs)))
    rng.shuffle(idx)
    n_val = int(len(pairs) * val_split)
    val = {idx[i] for i in range(n_val)}
    train = [pairs[i] for i in idx if i not in val]
    valset = [pairs[i] for i in idx if i in val]
    return train, valset


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(os.path.dirname(__file__), "dpo_config.yaml"))
    ap.add_argument("--dry-run", action="store_true",
                    help="validate config+data and exit (no model/backend).")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    here = os.path.dirname(__file__)
    pairs_file = os.path.join(here, cfg["data"]["pairs_file"])
    if not os.path.exists(pairs_file):
        sys.exit(f"BLOCKER: {pairs_file} missing — run build_dpo_pairs.py first.")

    pairs = load_pairs(pairs_file)
    # enforce config-level filters (defense in depth vs. the constructor)
    mm = cfg["data"]["min_margin"]
    pairs = [p for p in pairs if p.get("margin", 1.0) >= mm]
    train, val = split(pairs, cfg["data"]["val_split"], cfg["data"]["shuffle_seed"])
    print(f"[dpo] pairs={len(pairs)} train={len(train)} val={len(val)} "
          f"beta={cfg['dpo']['beta']} base={cfg['model']['base_model']}")
    assert train, "no training pairs after filtering"
    for p in pairs:  # contract check
        assert {"prompt", "chosen", "rejected"} <= p.keys()
        assert p["chosen_reward"] > p["rejected_reward"]

    if args.dry_run:
        print("[dpo] DRY-RUN OK: config valid, data well-formed, orientation correct.")
        return 0

    # ---- real backend path ----
    try:
        import torch  # noqa: F401
        from datasets import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from trl import DPOConfig, DPOTrainer
    except ImportError as e:
        sys.exit(
            "BLOCKER: DPO backend unavailable — "
            f"missing {e.name}. Need torch+transformers+trl+datasets and a GPU. "
            "Closed models (Claude/GPT) are not trainable; fork an open base with "
            "`hud models fork Qwen/Qwen3-8B`. Re-run without --dry-run on a GPU host."
        )

    ds = Dataset.from_list([
        {"prompt": p["prompt"], "chosen": p["chosen"], "rejected": p["rejected"]}
        for p in train
    ])
    tok = AutoTokenizer.from_pretrained(cfg["model"]["base_model"])
    model = AutoModelForCausalLM.from_pretrained(cfg["model"]["base_model"])
    dpo_cfg = DPOConfig(
        beta=cfg["dpo"]["beta"],
        loss_type=cfg["dpo"]["loss_type"],
        learning_rate=float(cfg["train"]["learning_rate"]),
        num_train_epochs=cfg["train"]["num_train_epochs"],
        per_device_train_batch_size=cfg["train"]["per_device_train_batch_size"],
        gradient_accumulation_steps=cfg["train"]["gradient_accumulation_steps"],
        output_dir=cfg["train"]["output_dir"],
        max_prompt_length=cfg["model"]["max_prompt_length"],
        max_length=cfg["model"]["max_length"],
    )
    DPOTrainer(model=model, args=dpo_cfg, train_dataset=ds, processing_class=tok).train()
    print("[dpo] training complete ->", cfg["train"]["output_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
