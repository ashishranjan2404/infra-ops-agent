#!/usr/bin/env python3
"""B9 self-contained tests for bootstrap_ci.py. Run: python3 test_bootstrap_ci.py"""
import importlib.util
import math
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("bootstrap_ci", HERE / "bootstrap_ci.py")
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

import random

failures = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)

# 1. percentile basics
xs = [0.0, 0.25, 0.5, 0.75, 1.0]
check("percentile median", abs(bc.percentile(xs, 0.5) - 0.5) < 1e-9)
check("percentile lo clamp", bc.percentile(xs, 0.0) == 0.0)
check("percentile hi clamp", bc.percentile(xs, 1.0) == 1.0)

# 2. all-pass -> degenerate CI at 1.0
lo, hi, pt, n, se = bc.bootstrap_ci([1, 1, 1, 1], 2000, random.Random(0))
check("all-pass point=1", pt == 1.0)
check("all-pass CI degenerate", lo == 1.0 and hi == 1.0 and se == 0.0)

# 3. all-fail -> degenerate CI at 0.0
lo, hi, pt, n, se = bc.bootstrap_ci([0, 0, 0], 2000, random.Random(0))
check("all-fail CI degenerate", lo == 0.0 and hi == 0.0)

# 4. bootstrap CI brackets the point estimate for a 50/50 sample
data = [0, 1] * 20
lo, hi, pt, n, se = bc.bootstrap_ci(data, 5000, random.Random(7))
check("50/50 point=0.5", abs(pt - 0.5) < 1e-9)
check("50/50 CI brackets point", lo <= pt <= hi)
check("50/50 SE ~ sqrt(pq/n)", abs(se - math.sqrt(0.25/40)) < 0.02)

# 5. determinism: same seed -> identical CI
a = bc.bootstrap_ci([0,1,1,0,1], 3000, random.Random(123))
b = bc.bootstrap_ci([0,1,1,0,1], 3000, random.Random(123))
check("deterministic given seed", a == b)

# 6. cluster bootstrap is >= plain bootstrap width on clustered data
#    (3 incidents, all-or-nothing within incident)
by_inc = {"a": [1,1,1], "b": [0,0,0], "c": [1,1,1]}
flat = [o for v in by_inc.values() for o in v]
pl_lo, pl_hi, *_ = bc.bootstrap_ci(flat, 5000, random.Random(1))
cl_lo, cl_hi, *_ = bc.cluster_bootstrap_ci(by_inc, 5000, random.Random(1))
check("cluster width >= plain width on clustered data",
      (cl_hi - cl_lo) >= (pl_hi - pl_lo) - 1e-9)

# 7. Wilson reference matches local fallback formula
def wilson_local(p, n, z=1.96):
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    spread = z*math.sqrt((p*(1-p) + z*z/(4*n))/n)/denom
    return (max(0.0, center-spread), min(1.0, center+spread))
wl = bc.WILSON_CI(0.4, 15)
loc = wilson_local(0.4, 15)
check("wilson matches formula", abs(wl[0]-loc[0]) < 1e-9 and abs(wl[1]-loc[1]) < 1e-9)

print()
if failures:
    print(f"{len(failures)} FAILED: {failures}")
    raise SystemExit(1)
print("ALL TESTS PASSED")
