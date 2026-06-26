#!/usr/bin/env python3
"""
trajectory_audit.py — Reproducible proof of how trajectory data is generated and verified.

Run: python3 trajectory_audit.py

This script answers two questions:
1. How was the trajectory data generated?
2. Was it verified against the simulation engine, or is it tautological?

It does this by running the actual code paths and printing the results.
No dependencies beyond the repo's existing Python files.
"""
import json
import sys
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "opensre-traj"))
sys.path.insert(0, str(REPO))

SEPARATOR = "=" * 70

def section(title):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def part1_how_trajectories_are_generated():
    """Show exactly how a trajectory record is produced from a spec pack."""
    section("PART 1: HOW TRAJECTORY DATA IS GENERATED")

    from lib_opensre import render_trajectory, subst_map, substitute

    spec_path = REPO / "opensre-traj" / "specs" / "oom_kill.json"
    spec = json.loads(spec_path.read_text())

    print(f"Source spec pack: {spec_path.name}")
    print(f"Incident type: {spec['incident']}")
    print(f"Failure mode: {spec['failure_mode']}")
    print()

    # Show the spec pack structure
    print("Spec pack keys:", list(spec.keys()))
    print()
    print("ALERT template (with placeholders):")
    print(f"  title: {spec['alert']['title']}")
    print()

    # Substitute placeholders
    m = subst_map(spec, "oom_kill", seed=0)
    s = substitute(spec, m)
    print(f"Substituted pod name: {m['POD']}")
    print(f"Substituted service:  {m['SVC']}")
    print(f"Substituted node:     {m['NODE']}")
    print()

    # Render trajectory
    traj = render_trajectory(s, m)
    print(f"Rendered trajectory: {len(traj)} steps")
    print()
    for step in traj:
        if step["role"] == "assistant":
            print(f"  Step {step['step']:>2} [ASSISTANT]: {step['thought']}")
            print(f"           tool: {step['action']['tool']}")
            print(f"           args: {step['action'].get('args', {})}")
        else:
            result = step.get("result", {})
            print(f"  Step {step['step']:>2} [TOOL]:     {step['name']}")
            print(f"           result: {json.dumps(result)[:120]}")
    print()

    # Show the evidence file (what the agent "reads")
    ev = s.get("evidence", {})
    events = ev.get("k8s_events.json", {})
    print("EVIDENCE (k8s_events.json — what the agent reads in step 8):")
    for e in events.get("events", [])[:3]:
        print(f"  reason={e.get('reason')}")
        print(f"  message={e.get('message', '')[:100]}")
    print()

    # Show the answer key
    ans = spec.get("answer", {})
    print("ANSWER KEY (from spec pack, not computed):")
    print(f"  root_cause_category: {ans.get('root_cause_category')}")
    print(f"  optimal_trajectory: {ans.get('optimal_trajectory')}")
    print(f"  required_keywords: {ans.get('required_keywords')}")
    print()

    rem = spec.get("remediation", {})
    print("REMEDIATION (scripted state transition, NOT from sim engine):")
    print(f"  fix_tool: {rem.get('fix_tool')}")
    print(f"  state_before: {rem.get('state_before')}")
    print(f"  state_after: {rem.get('state_after')}")
    print()

    print("CONCLUSION: The trajectory is generated from a spec pack template.")
    print("The 'thought' strings are canned ('Triage the alert...', 'Corroborate...').")
    print("The tool results are placeholder references ('returned k8s_events.json').")
    print("The state_diff is scripted from the spec's state_before/state_after.")
    print("No simulation engine is called during generation.")


def part2_was_it_verified():
    """Check whether the SFT data was verified against the sim engine."""
    section("PART 2: WAS THE TRAJECTORY DATA VERIFIED?")

    # Check: does generate.py reference the sim engine?
    gen_path = REPO / "opensre-traj" / "generate.py"
    gen_code = gen_path.read_text()
    sim_refs = [line for line in gen_code.split("\n")
                if any(w in line.lower() for w in ["sim.engine", "is_resolved", "world", "verify"])]

    print(f"generate.py references to sim engine / is_resolved / verify:")
    if sim_refs:
        for line in sim_refs:
            print(f"  {line.strip()}")
    else:
        print("  NONE FOUND — generate.py does NOT call the sim engine")
    print()

    # Check: does lib_opensre.py reference the sim engine?
    lib_path = REPO / "opensre-traj" / "lib_opensre.py"
    lib_code = lib_path.read_text()
    lib_refs = [line for line in lib_code.split("\n")
                if any(w in line.lower() for w in ["sim.engine", "is_resolved", "world", "verify"])]

    print(f"lib_opensre.py references to sim engine / is_resolved / verify:")
    if lib_refs:
        for line in lib_refs:
            print(f"  {line.strip()}")
    else:
        print("  NONE FOUND — lib_opensre.py does NOT call the sim engine")
    print()

    # Check: does verify.py still exist?
    verify_path = REPO / "verify.py"
    print(f"verify.py exists: {verify_path.exists()}")
    if not verify_path.exists():
        # Check git history
        import subprocess
        result = subprocess.run(
            ["git", "log", "--oneline", "--", "verify.py"],
            capture_output=True, text=True, cwd=str(REPO)
        )
        if result.stdout.strip():
            print(f"  (deleted in commit: {result.stdout.strip().split(chr(10))[0]})")
    print()

    print("CONCLUSION: The SFT trajectory data (200K records) was NEVER verified")
    print("against the simulation engine. The old verify.py was tautological:")
    print("it checked that the scripted state_after matched the SLO threshold,")
    print("which is guaranteed by construction. No real state transitions were tested.")


def part3_eval_rubric_is_different():
    """Prove the eval rubric (rex/harness.py) uses real simulation."""
    section("PART 3: THE EVAL RUBRIC IS DIFFERENT (real simulation)")

    from rex.harness import load_scenario, run_plan
    from rex.scoring import score_plan

    sc = load_scenario("oom_kill")
    print(f"Scenario: oom_kill")
    print(f"  fault_node: {sc.fault_node}")
    print(f"  fault kind: {sc.kind}")
    print(f"  correct_fix_tools: {sc.correct_fix_tools}")
    print(f"  gold_root: {sc.gold_root_description[:80]}")
    print()

    # Test 1: correct tool, correct target
    plan1 = {
        "root_cause": "memory leak on image-resizer",
        "actions": [{"tool": "increase_memory_limit", "args": {"target": "image-resizer"}}]
    }
    sim1 = run_plan(plan1, sc)
    score1, _ = score_plan(plan1, sc, sim1)
    print(f"Test 1: CORRECT tool + CORRECT target")
    print(f"  resolved={sim1['resolved']}, root_cleared={sim1['root_cleared']}")
    print(f"  metrics={sim1['final_metrics']}")
    print(f"  score={score1:.3f}")
    print()

    # Test 2: correct tool, WRONG target
    plan2 = {
        "root_cause": "memory leak on image-resizer",
        "actions": [{"tool": "increase_memory_limit", "args": {"target": "payments-7b6b9dfb7c-lv9ld"}}]
    }
    sim2 = run_plan(plan2, sc)
    score2, _ = score_plan(plan2, sc, sim2)
    print(f"Test 2: CORRECT tool + WRONG target (pod name from SFT template)")
    print(f"  resolved={sim2['resolved']}, root_cleared={sim2['root_cleared']}")
    print(f"  metrics={sim2['final_metrics']}")
    print(f"  score={score2:.3f}")
    print()

    # Test 3: trap action
    plan3 = {
        "root_cause": "memory leak on image-resizer",
        "actions": [{"tool": "scale_deployment", "args": {"target": "image-resizer", "replicas": 8}}]
    }
    sim3 = run_plan(plan3, sc)
    score3, _ = score_plan(plan3, sc, sim3)
    print(f"Test 3: TRAP action (scale_deployment)")
    print(f"  resolved={sim3['resolved']}, root_cleared={sim3['root_cleared']}")
    print(f"  metrics={sim3['final_metrics']}")
    print(f"  score={score3:.3f}")
    print()

    # Test 4: empty plan
    plan4 = {"root_cause": "memory leak on image-resizer", "actions": []}
    sim4 = run_plan(plan4, sc)
    score4, _ = score_plan(plan4, sc, sim4)
    print(f"Test 4: EMPTY plan")
    print(f"  resolved={sim4['resolved']}, root_cleared={sim4['root_cleared']}")
    print(f"  metrics={sim4['final_metrics']}")
    print(f"  score={score4:.3f}")
    print()

    print("CONCLUSION: The eval rubric (rex/harness.py) uses a REAL sim engine.")
    print("Wrong targets fail to resolve. Trap actions get penalized to 0.0.")
    print("Empty plans score 0.3 (diagnosis credit only, no resolution).")
    print("This is NOT tautological — the sim has causal physics that can fail.")
    print()
    print("CRITICAL GAP: The SFT trajectory targets (pod names like")
    print("'payments-7b6b9dfb7c-lv9ld') do NOT match the sim engine's fault_node")
    print("('image-resizer'). If you ran the SFT trajectory through the eval")
    print("rubric, it would score 0.425 (correct tool, wrong target) — NOT 1.0.")
    print("The SFT data teaches the agent the wrong target.")


def part4_two_systems_summary():
    """Clear summary of the two separate systems."""
    section("PART 4: TWO SEPARATE SYSTEMS — DON'T CONFLATE THEM")

    print("""
SYSTEM A: SFT DATA GENERATION (Pipeline 1)
  Files:     opensre-traj/generate.py, lib_opensre.py, specs/*.json
  Output:    200K trajectories (incidents.jsonl on HuggingFace)
  Verifier:  verify.py (DELETED — was tautological)
  Sim engine: NOT USED
  Resolution: Scripted from spec pack's state_before/state_after
  Target:     Pod name from template (e.g. 'payments-7b6b9dfb7c-lv9ld')
  Status:     Structurally correct, causally ungrounded

SYSTEM B: EVAL BENCHMARK (Pipeline 3)
  Files:     rex/harness.py, rex/scoring.py, rex/eval_pass_at_k.py
  Output:    pass@k numbers (90% vs 23%)
  Verifier:  sim/engine.py (REAL simulation)
  Sim engine: YES — World.from_spec(), apply_action(), is_resolved()
  Resolution: Computed by sim engine (fault must clear + SLO must recover)
  Target:     fault_node from scenario (e.g. 'image-resizer')
  Status:     Real simulation, not tautological

THE PAPER'S NUMBERS COME FROM SYSTEM B, NOT SYSTEM A.
System A is training data. System B is evaluation.
They use different targets, different verifiers, different physics.
""")


def main():
    print("SRE-Degrees Trajectory Audit")
    print(f"Repo: {REPO}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Run: python3 trajectory_audit.py")

    part1_how_trajectories_are_generated()
    part2_was_it_verified()
    part3_eval_rubric_is_different()
    part4_two_systems_summary()

    print("\n" + SEPARATOR)
    print("  AUDIT COMPLETE")
    print(SEPARATOR)


if __name__ == "__main__":
    main()
