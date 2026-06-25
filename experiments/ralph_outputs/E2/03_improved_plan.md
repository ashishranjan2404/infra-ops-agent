# 03 — Improved Plan

## Changes from the grill (accepted)
1. **Keep full commands as the action** (`actions = commands_norm`), with
   `tools_used` only as a deduped verb convenience view. [AAAI/RLE — accepted]
2. **Skip empty action/target rows by default**, `--keep-empty` override.
   [PSRE/SMR — accepted; prevents blank training targets]
3. **Frame as a generic trajectory substrate**, not an SRE incident source —
   stated in schema + convert docstrings. [PSRE/SMR — accepted]
4. **Shard-limited fetch by default**, `--all` opt-in and loud; document that a
   real training run needs all 1475 shards. [DOL/RLE — accepted]
5. **Provenance + license + no-fabrication**: cite ACL 2023 / arXiv:2305.01528 /
   CC-BY-4.0; fixture rows are `SYNTH_*`. [AAAI — accepted]
6. **Note symlink/cache reproducibility caveat** in fetch docstring. [DOL — accepted]

## Rejected (with reason)
- **"Drop the dataset, it's not SRE" (PSRE R1):** rejected. FIREBALL's structure
  (NL + structured state + executed commands + deterministic results) is exactly
  our agent loop shape; it's a useful second substrate for the trajectory schema
  and converter. We just label it as such rather than pretending it's incidents.
- **"A couple shards is enough" implying full acquisition (DOL R1):** rejected as
  stated — we explicitly distinguish "converter validated on real data" from
  "full dataset acquired." One shard validates; `--all` acquires.

## Final deliverable shape
Same 5 artifacts as 01, with the above semantics baked in. Validation must run on
BOTH the synthetic fixture and at least one REAL downloaded shard.
