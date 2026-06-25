# A18 — 03 Improved Plan

## What changed after the grill

1. **Belt-and-suspenders config resolution (accepted, SMR+RLE).** Keep the typed loading script AND
   give the card a fully self-sufficient `configs:` + `dataset_info:` block, so the dataset resolves
   even if the Hub ignores the script. Mitigates RLE's "scripts can break on the Hub sandbox" concern
   without losing SMR's typed-schema guarantee.

2. **Build-not-copy push (accepted, DVO).** `push_to_hub.py` *assembles* the package: writes the root
   `hud_trajectories.jsonl` (the `all` config) plus `synthetic/synthetic.jsonl` and `real/real.jsonl`
   shards so the multi-config card has real files to point at.

3. **Provenance distinction (accepted, PSRE+AAAI).** Card states `source_url` grounds the *incident's
   ground truth*; the `answer` + `reward` are frozen-LLM output scored by an automatic proxy — not gold
   human labels. Validator asserts every real record keeps its `source_url`.

4. **Leaderboard + subscores surfaced (accepted, RLE).** Card includes the per-model leaderboard and
   documents the 4 `subscores` so consumers can re-weight reward.

5. **Limitations & Ethics section (accepted, AAAI).** Explicit: reconstructed simulation, small frozen
   model set, automatic proxy reward.

6. **Credential-safe push (accepted, DVO).** Token from `HF_TOKEN` env / `huggingface-cli login`,
   `create_repo(exist_ok=True)`, `--dry-run` needs no network, no hardcoded secrets.

## Rejected / deferred

- **RLE: drop the loading script entirely.** REJECTED — heterogeneous real-only fields make inferred
  typing fragile; the script is the stable contract. Compromise: card is also self-sufficient.
- **Trap-fix penalty grader.** DEFERRED — out of scope for an *upload* task; `trap_actions` are shipped
  in the data so a future grader can use them. Noted in the card.

## Final deliverables (unchanged set, hardened)
`opensre_trajectories.py`, `README.md` (rich YAML + provenance + ethics + leaderboard),
`push_to_hub.py` (build+shard+upload+dry-run), `validate_package.py` (offline checks),
bundled `hud_trajectories.jsonl`.
