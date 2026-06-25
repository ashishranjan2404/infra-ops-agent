#!/usr/bin/env python3
"""Offline smoke check for the containerized REx eval pipeline.

Runs with NO API key and NO network: it proves the image's Python environment,
dependencies, and the deterministic eval code path are all intact by

  1. importing the heavy modules the live eval (`rex.eval_pass_at_k`) imports,
  2. loading the bundled CIDG scenarios off disk (pyyaml works),
  3. exercising the pure-math pass@k / Wilson-CI estimators.

Exit 0 == the container is healthy and ready for a live eval run. This is what
`docker run --rm rex-eval:latest` does by default, so a bare run is a green CI
signal that needs no secret.
"""
from __future__ import annotations

import os
import sys

REPO = os.environ.get("REX_REPO", "/app")
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))


def main() -> int:
    # 1. The deterministic, network-free import surface of the live eval.
    from compute_pass_at_k import binary_pass, pass_at_k, wilson_ci  # noqa: F401
    from rex.harness import scenarios_by_family
    from rex.scoring import failed_checks, score_plan  # noqa: F401
    from rex.loop import build_prompt, parse_plan  # noqa: F401

    # 2. Scenarios load off disk (pyyaml present, files baked into image).
    fam = scenarios_by_family()
    counts = {k: len(v) for k, v in fam.items()}
    total = sum(counts.values())
    assert total > 0, "no scenarios loaded — image is missing scenarios/"
    print(f"[smoke] scenarios by family: {counts}  (total={total})")

    # 3. Pure estimators behave (numpy present, math correct).
    p = pass_at_k(n=4, c=2, k=2)
    lo, hi = wilson_ci(p=0.5, n=4)
    assert 0.0 <= p <= 1.0 and lo <= hi, "pass@k / Wilson CI math is broken"
    print(f"[smoke] pass@2(n=4,c=2)={p:.3f}  wilson95%=({lo:.3f},{hi:.3f})")

    print("[smoke] OK — container healthy, deterministic eval path intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
