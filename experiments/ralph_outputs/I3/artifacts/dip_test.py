"""
Hartigan's dip test of unimodality for the SRE-Degrees reward distributions.

PRIMARY engine: the vetted `diptest` package (v0.11), a Python binding around the
canonical Hartigan & Hartigan (1985) AS 217 C routine `diptst`, with the analytic
p-value interpolation table from the original paper. This is the implementation
recommended by the brief ("or use a vetted implementation").

We expose `dip_test(samples)` -> (D, p_value). A pure-NumPy fallback dip
*statistic* is also provided (`_dip_statistic_fallback`) for environments without
the package, but the package is preferred because a correct dip statistic for
non-uniform unimodal shapes (e.g. Gaussian) requires the exact AS 217 modal-
interval recursion, which is fiddly to reproduce by hand.

Reference: Hartigan, J. A. and Hartigan, P. M. (1985), "The Dip Test of
Unimodality", The Annals of Statistics 13(1): 70-84.
"""
from __future__ import annotations
import numpy as np

try:
    import diptest as _diptest_pkg
    _HAVE_PKG = True
except Exception:  # pragma: no cover
    _HAVE_PKG = False


def dip_test(samples, n_boot=10000, seed=0):
    """Return (D, p_value) for the dip test of unimodality.

    Uses the vetted `diptest` package: D is the AS 217 dip statistic, p is the
    probability under the least-favourable unimodal (Uniform) null of a dip at
    least as large, computed from the package's bootstrap/interpolation table.
    """
    x = np.asarray(samples, dtype=float)
    if x.size < 4:
        return 0.0, 1.0
    if _HAVE_PKG:
        D, p = _diptest_pkg.diptest(x, boot_pval=False)
        return float(D), float(p)
    # Fallback: statistic only, with a Uniform Monte-Carlo p-value.
    D = _dip_statistic_fallback(x)
    rng = np.random.default_rng(seed)
    n = x.size
    ge = sum(_dip_statistic_fallback(rng.random(n)) >= D for _ in range(n_boot))
    return float(D), (ge + 1) / (n_boot + 1)


def dip_statistic(samples):
    """Dip statistic D only."""
    return dip_test(samples)[0]


# --------------------------------------------------------------------------- #
# Pure-NumPy fallback (statistic only). Correct for the uniform/bimodal regimes
# exercised here; the packaged AS 217 routine is preferred when available.
# --------------------------------------------------------------------------- #
def _gcm(x, y):
    idx = [0]
    for i in range(1, len(x)):
        while len(idx) >= 2:
            a, b = idx[-2], idx[-1]
            if (y[b] - y[a]) * (x[i] - x[b]) >= (y[i] - y[b]) * (x[b] - x[a]):
                idx.pop()
            else:
                break
        idx.append(i)
    return idx


def _dip_statistic_fallback(samples):
    x = np.sort(np.asarray(samples, dtype=float))
    n = len(x)
    if n < 4:
        return 0.0
    ecdf_lo = np.arange(0, n) / n
    ecdf_hi = np.arange(1, n + 1) / n
    g = _gcm(x, ecdf_lo)
    gi = np.interp(x, x[g], ecdf_lo[g])
    li_idx = _gcm(x[::-1], -ecdf_hi[::-1])
    lx = x[::-1][li_idx]
    ly = ecdf_hi[::-1][li_idx]
    o = np.argsort(lx)
    li = np.interp(x, lx[o], ly[o])
    d = 0.5 * max(np.max(np.abs(ecdf_hi - gi)), np.max(np.abs(ecdf_lo - li)))
    return float(min(max(d, 0.0), 0.25))


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    print("have diptest pkg:", _HAVE_PKG)
    print("uniform   :", dip_test(rng.random(300)))
    print("normal    :", dip_test(rng.normal(0, 1, 300)))
    bi = np.concatenate([rng.normal(0, 0.05, 150), rng.normal(1, 0.05, 150)])
    print("bimodal   :", dip_test(bi))
