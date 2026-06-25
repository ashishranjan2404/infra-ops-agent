# F8 · 09 Critique (honest)

## What a reviewer would attack
1. **The checklist audits the repo, but doesn't audit the *paper's claims*.** It proves
   "a deterministic judge exists," not "the headline table in the paper was produced by
   the deterministic judge with these seeds." Without a results→(judge,seed,data) map,
   a skeptic can't trace any specific number to a reproducible recipe. The judge-pinning
   row *prescribes* this but the linkage doesn't yet exist in the repo.
2. **`verify_repro.py` checks presence, not correctness.** `seed.tree` passes if the
   string `random.Random(seed)` appears — it doesn't prove the seed actually controls
   output. Only `replay_double_grade` is a true behavioral check; the rest are
   existence/grep proxies. An adversary could keep the string and break the behavior.
3. **Manifest vs script count mismatch** (4/3 SEEDED/PARTIAL in manifest vs 3/2 in
   script) is explained but is a smell — two sources of truth that can drift. A single
   generator should emit both.
4. **`>=` pins, no lockfile/container.** I marked deps AVAILABLE, but a future
   `pyyaml`/`numpy` major could break a fresh install. True reproducibility wants
   `==` pins or a lockfile; this is a soft AVAILABLE.
5. **I corrected DATA.md's numbers but didn't fix DATA.md** (shared file, correctly
   off-limits) — so the repo still ships a stale doc; my checklist is the only place
   the truth is recorded, which a reviewer reading top-down won't see first.

## What's weak / missing
- No **environment hash** (pip freeze snapshot) committed — "Python 3.13.7" alone is
  thin. A `pip freeze > F8/artifacts/env.lock` would harden the code axis.
- No **end-to-end replay demo** — I assert the committed `.jsonl` re-grades exactly but
  only spot-check one record; a full re-grade script would be stronger evidence.
- The **closed-model drift** limitation is correct but unactionable — I name it without
  offering mitigation beyond "trust the committed transcripts."
- Compute/cost axis is the thinnest (PARTIAL, no ledger) — genuinely not available.

## Blocked / negative results (stated plainly)
- **Trained checkpoint: BLOCKED** — no weights in repo; reproducing the open-model RFT
  needs HUD_API_KEY + GPU, neither available here. Honestly out of scope for this task.
- **53 generated scenarios: not reproducible on a fresh clone** — untracked, and no
  committed generator+seed for those specific files (unlike the SIMPLE tier). Real gap.

## Net
The deliverable is a *truthful map of the reproducibility surface* with a runnable
self-audit — strong on honesty and grounding. Its weakness is that it documents and
mechanically spot-checks reproducibility rather than fully *demonstrating* end-to-end
replay of a paper number, and the existence-grep checks are proxies, not proofs.
