# G1 — Ouroboros (3 engineers critique the spec, in sequence)

## Engineer A — "the integration realist"
Real problems found:
1. **The `SREGymClient` Protocol is invented.** The public SREGym excerpt does not
   publish the submission API's Python names. The spec hand-waves "bound at install
   time." That's a genuine gap: an integrator can't wire this without reading
   SREGym's actual `BaseAgent`. FIX: make the Protocol minimal and explicit, and in
   the run plan point at the exact integration seam (`--agent <name>` registers a
   class implementing SREGym's agent base — our adapter is the body of its
   `solve(problem)` method). Mark the seam as "TODO: bind to SREGym API" in code.
2. **`build_diagnosis` just echoing `root_cause` will underperform O_d.** O_d scores
   9 questions across localization/characterization/scope. A one-sentence root cause
   may miss "concrete details (port values, env vars)" and "failure scope." FIX:
   `build_diagnosis` should ALSO append the topology/affected-services context from
   the observation bundle, not just the bare sentence — give the judge more to check.
3. **No timeout / step budget.** SREGym measures Time-To-Diagnose/Mitigate and token
   usage. The spec ignores cost. Acknowledge it's unmeasured offline; note it.

## Engineer B — "the correctness skeptic" (reacts to A)
1. **Disagree with A's fix #2 being free.** Padding the diagnosis with topology can
   *lower* the localization sub-score if it names cascade victims as if they were
   roots. Our cascade prompts specifically warn against that. FIX: append affected
   services LABELED as downstream/victims, and keep the originating component first
   and explicit. Otherwise A's fix backfires.
2. **`translate_action` assumes args.target exists.** Some of our plans have actions
   with no `target` (or a target our resolver can't find). The spec doesn't define
   the failure path. FIX: if resolve() raises / returns empty, mark the action
   `expressible:false, reason="unresolved target"` — don't emit a malformed kubectl.
3. **`out_of_action_space` true only if ALL actions inexpressible — too lenient.**
   A plan with one expressible + one inexpressible action will be partially applied
   on the live cluster, which can leave the system in a worse state and fail O_m.
   FIX: record `partial_action_space=true` distinctly; the run plan must count these
   as a separate bucket, not a clean mitigation.

## Engineer C — "the scope auditor" (reacts to A and B)
1. **Over-engineering: the REx `budget=4` refinement is dead offline.** Our refine
   loop needs live feedback (run_plan against a sim, or the cluster). The adapter has
   neither in dry-run. So `budget` is a no-op knob that implies capability we don't
   have. FIX: drop refinement from the offline scaffold; do ONE propose. Document
   that on a live cluster the loop would re-observe between O_d and O_m — but that's
   future work, not in this scaffold. (Accept B's and A's points; cut this one.)
2. **Under-specified: where does `Scenario` come from?** Our `propose_fn` signature
   takes a `Scenario`, but SREGym gives an observation bundle, not our `Scenario`
   dataclass. FIX: the adapter must build the prompt DIRECTLY from the observation
   bundle (a thin `_prompt_from_observation`), bypassing `rex.harness.load_scenario`
   entirely — we have no spec for a SREGym problem. This also keeps us from touching
   shared core. Good: confirms no shared-core dependency at run time.
3. **Test T7 over-asserts exact namespace.** Brittle. FIX: assert the resolved name
   appears in argv, not the entire command equals a golden string.

## Final filtered spec (deltas applied)
- `SREGymClient` Protocol kept MINIMAL + flagged `# TODO bind to SREGym BaseAgent`;
  run plan names the `--agent` registration seam.
- `build_diagnosis(plan, observation)` = originating component first, then affected
  downstream services LABELED as victims (B1), from the observation bundle (A2).
- `translate_action`: unresolved/absent target -> `expressible:false,
  reason="unresolved target"` (B2). Static-inexpressible tools unchanged.
- `translate_plan` returns BOTH `out_of_action_space` (all inexpressible) AND
  `partial_action_space` (some inexpressible) (B3).
- Offline scaffold does ONE propose, no refinement loop; `budget` removed (C1).
- Prompt built directly from the observation bundle via `_prompt_from_observation`;
  no `rex.harness.load_scenario` at run time (C2) -> zero shared-core runtime dep.
- T7 asserts resolved name is a substring of argv (C3).
- Cost/time/token usage explicitly noted as unmeasured offline (A3).
