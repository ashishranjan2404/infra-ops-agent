# F11 — 08 Verification

## Against the success criteria (from 01, as revised in 03)

1. **APPENDIX.md has all AE-required sections.** ✔ Sections A.1–A.9 present (verified by structural
   check, T4): Abstract, check-list meta-info, Description (access/HW/SW/data), Installation,
   two-tier Experiment workflow, Expected results + reproduction tolerance, Customization, Threats,
   Badge mapping. All commands grounded in real repo files/flags (`rex/eval_pass_at_k.py` argparse,
   `scenarios_by_family`, `REX_JUDGE_MODE`, `floor_check`, output JSON keys).

2. **badge_claim_map.json validates against its schema test.** ✔ `test_badge_map.py` — 6 passed
   (T2). Exactly the three ACM badges; every evidence file resolves; offline badge credential-free;
   online badge command references `rex.eval_pass_at_k` + `--conditions`.

3. **smoke_ae.sh runs offline and exits 0.** ✔ RC=0 (T1); registry loads, `floor_ok=True` over the
   full registry, deterministic-judge tests green — all without credentials.

4. **No shared core file edited.** ✔ `git status` shows `experiments/ralph_outputs/F11/` as the only
   untracked addition from this session; mtimes confirm `rex/*.py`, `sim/*.py` were last touched
   before this session. The pre-existing branch `M` flags predate my work.

## Are the outputs real (not placeholder)?
- **APPENDIX.md** — real, copy-pasteable commands; every flag/key verified against source. Where a
  numeric result would require a paid LLM run, the appendix references the camera-ready table rather
  than inventing a figure (deliberate, per ouroboros P1.1).
- **badge_claim_map.json** — real JSON, schema-validated, file references resolve on disk.
- **smoke_ae.sh** — really executed; produced real output (T1).
- **test_badge_map.py** — really executed; 6 real assertions pass (T2).

## Honest scope note
The appendix's **Reproduced** tier (Tier B) was intentionally NOT executed — it needs live LLM
credentials and real spend. This is a documented blocker (07/09), not a gap in the deliverable: the
deliverable is the *appendix + self-checking artifacts*, and the offline Functional path is fully
demonstrated end-to-end on this machine.

**Verdict: success criteria 1–4 met. Deliverable complete; downstream Tier-B run blocked on
credentials (documented).**
