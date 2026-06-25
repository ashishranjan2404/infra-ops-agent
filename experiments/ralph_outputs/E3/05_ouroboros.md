# E3 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the simulator-correctness skeptic"
**Problems found:**
- A1. The spec says zero-shot is a *single proposal*, but `make_proposer` loops twice. Ambiguity:
  is that a second *sample* (changing the policy) or only a transport retry? → It must be a retry
  ONLY on exception, not a best-of-2. Confirmed: the loop `return`s on first success and only
  re-enters on `except`. OK, but the spec wording should say "one retry on transient error" — fixed
  in 04.
- A2. `parse_plan` on a reasoning model emitting `<think>...</think>` may fail to find a plan and
  yield an empty plan → reward near 0, indistinguishable from "tried and failed." This is a real
  confound for *both* arms equally, so it doesn't bias the comparison, but it caps measurable lift.
  → Document as a caveat; it affects both arms symmetrically.
- A3. No floor/headroom assertion is enforced in code. → Accepted as report-only (per grill R3):
  per-incident means + std are emitted so a human can see headroom; not auto-asserted to avoid
  failing the run on a legitimate null.

## Engineer B — "the stats pedant"
**Problems found:**
- B1. `pass@2` with only `seeds=2` per incident is computed over the *pooled* 28 rewards, not
  per-incident — that's the same convention as `rex.eval_pass_at_k.summarize`, so it's consistent,
  but pass@2 here is weakly meaningful at this sample size. → Keep for parity but lead with pass@1.
- B2. Wilson CI on 28 trials is wide; a 3–4 point pass@1 gap will have heavily overlapping CIs. The
  harness must NOT print a winner without the CI. → Confirmed: the table prints the CI inline and
  03/08 explicitly state overlap. OK.
- B3. `reward_std` uses population stdev (`pstdev`) — correct for "spread within the group," matches
  the HUD trainability-spread convention. OK.

## Engineer C — "the parallel-safety / ops reviewer"
**Problems found:**
- C1. `ROSTER.setdefault` mutates the *imported* module dict at runtime. Although we don't write the
  file, another in-process consumer could see the extra keys. → In a Ralph worker this process is
  isolated and short-lived; the keys are namespaced (`qwen3-8b-base`, `opensre-qwen3-8b`) and don't
  collide with shipped roster keys. Acceptable; documented in 06. The *file* `agent/models.py` is
  never edited (the hard rule).
- C2. A 200 from the gateway doesn't prove the slug is the right OpenSRE *checkpoint*. → Mitigated by
  recording the exact `model` string in the result for audit (RLE's point). Can't verify checkpoint
  identity from here; noted in 09.
- C3. If the gateway rate-limits mid-sweep, errors are captured per-job (not fatal) and surfaced in
  `n_errors` / `errors`. Good — partial results still write. OK.

## Final filtered spec (deltas applied)
- Wording: "one retry on transient transport error" (not best-of-2) — clarified.
- Caveats added to 06/09: reasoning-model `<think>` parse cap (symmetric), gateway sampling parity,
  checkpoint-identity-by-trust, small-sample CI overlap.
- Headroom check stays **report-only** (emit per-incident means + std), not a hard assertion.
- Everything else from 04 stands.
