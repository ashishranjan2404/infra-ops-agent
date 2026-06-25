# D5 — 08_verification

## Success criteria from 01_plan
1. **Runnable SFT data builder producing valid JSONL pairs from the shared pool.** ✅ MET.
   `build_sft_data.py` ran on the real 197-trajectory pool → 21 valid SFT pairs + frozen split +
   manifest. Each line is valid JSON, every pair ≥ min_reward and from the train split (T1-T2).
2. **Matched RFT/SFT configs referencing one frozen split + same base + same grader.** ✅ MET.
   `configs/{rft,sft}.yaml` share base_model/split_path/grader/eval_metric verbatim (T5), both point
   at the single `split.json`.
3. **Comparison harness that runs offline and prints a real per-split table.** ✅ MET.
   `compare_harness.py --offline` produced a real 10-row eval table + `comparison.json`, no network.
4. **Hypothesis stated with a fair pre-registered metric; compute blocker honestly documented.**
   ✅ MET. H1/H2/H0 pre-registered in 03; metric = mean v2 reward on held-out eval; blocker (compute
   + SFT SDK surface) documented in 07/09; no fabricated trained numbers.

## Are the outputs REAL (not placeholder)?
- `split.json`, `sft_pairs.jsonl`, `sft_manifest.json`, `comparison.json` — all generated from the
  actual trajectory pool, reproducible by re-running the scripts. ✅
- Proxy-ceiling number (0.6787) is a real computation over real demos, explicitly labeled as an
  upper bound and NOT presented as a trained SFT/RFT result. ✅
- The one unavoidable gap (trained eval rewards) is left BLANK with the blocker named, per the brief's
  "a correct scaffold + honest blocker beats fabricated numbers." ✅

## Independent re-run evidence
All four scripts were executed in this session (build, harness, dry-train, tests) and their real
stdout is captured in 06/07. The introspection guard in train_sft.py was exercised to the SDK
boundary, confirming the SFT-SDK blocker is real, not assumed.
