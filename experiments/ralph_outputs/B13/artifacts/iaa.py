"""Inter-annotator agreement (IAA) metrics — pure-Python, zero-dependency.

Task B13. The deterministic judge in `rex/scoring.py:deterministic_judge` is a pure
function: given (stated_cause, gold_root, red_herrings) it always returns the same
boolean. So machine-vs-itself agreement is trivially kappa=1.0 — that is exactly the
"sanity baseline" we want to assert. The interesting IAA question (does a HUMAN agree
with the judge, and do humans agree with EACH OTHER) requires human labels we do not
have; that is the documented blocker (see 07/09).

This module implements the three standard nominal-label agreement statistics so that,
the moment a relabeling CSV comes back from humans, agreement can be computed with one
command. It is deliberately self-contained (no numpy/sklearn) so it runs anywhere the
repo's Python 3.13 runs.

Definitions implemented:
  - percent_agreement(a, b)        raw observed agreement (P_o)
  - cohen_kappa(a, b)              2-rater chance-corrected agreement
  - fleiss_kappa(table)            >=2 raters, fixed categories, per-item rating counts
  - krippendorff_alpha(matrix)     any number of raters, missing data OK, nominal metric

All functions raise ValueError on malformed input rather than silently returning a
misleading number.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Sequence


# ---- two-rater statistics -------------------------------------------------
def percent_agreement(a: Sequence, b: Sequence) -> float:
    """Raw observed agreement P_o in [0,1]. a[i], b[i] are the two raters' labels."""
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    if not a:
        raise ValueError("no items to compare")
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


def cohen_kappa(a: Sequence, b: Sequence) -> float:
    """Cohen's kappa for two raters over nominal labels.

    kappa = (P_o - P_e) / (1 - P_e), where P_e is the agreement expected by chance
    given each rater's marginal label distribution. Returns 1.0 for perfect agreement,
    0.0 for chance-level, negative for worse-than-chance. When both raters use a SINGLE
    constant label (P_e == 1, the degenerate all-same case) we return 1.0 if they always
    agree else 0.0 — a defensible convention (sklearn returns nan here).
    """
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    n = len(a)
    if n == 0:
        raise ValueError("no items to compare")
    p_o = percent_agreement(a, b)
    ca, cb = Counter(a), Counter(b)
    cats = set(ca) | set(cb)
    p_e = sum((ca.get(c, 0) / n) * (cb.get(c, 0) / n) for c in cats)
    if p_e >= 1.0:                       # degenerate: both raters constant
        return 1.0 if p_o >= 1.0 else 0.0
    return (p_o - p_e) / (1.0 - p_e)


# ---- multi-rater: Fleiss' kappa -------------------------------------------
def fleiss_kappa(table: Sequence[Sequence[int]]) -> float:
    """Fleiss' kappa. `table[i][j]` = number of raters who assigned category j to item i.

    Every item must have been rated by the same number of raters n (rows sum equal).
    Suitable when each item is labelled by a fixed-size panel.
    """
    if not table:
        raise ValueError("empty table")
    N = len(table)
    k = len(table[0])
    row_sums = [sum(row) for row in table]
    n = row_sums[0]
    if n <= 1:
        raise ValueError("need >=2 raters per item")
    if any(rs != n for rs in row_sums):
        raise ValueError("every item must have the same number of ratings")
    # P_i: extent of agreement on item i
    P = [(sum(c * c for c in row) - n) / (n * (n - 1)) for row in table]
    P_bar = sum(P) / N
    # p_j: proportion of all assignments to category j
    total = N * n
    p_j = [sum(table[i][j] for i in range(N)) / total for j in range(k)]
    P_e = sum(pj * pj for pj in p_j)
    if P_e >= 1.0:
        return 1.0 if P_bar >= 1.0 else 0.0
    return (P_bar - P_e) / (1.0 - P_e)


# ---- Krippendorff's alpha (nominal) ---------------------------------------
def krippendorff_alpha(matrix: Sequence[Sequence]) -> float:
    """Krippendorff's alpha for nominal data, robust to missing values.

    `matrix[r][i]` is rater r's label for item i, or None if that rater did not label
    item i. Any number of raters; items rated by <2 raters contribute nothing (and are
    excluded from the unit count, per Krippendorff). Uses the nominal difference metric
    (0 if equal, 1 otherwise), computed from the coincidence matrix.
    """
    if not matrix:
        raise ValueError("empty matrix")
    n_items = len(matrix[0])
    if any(len(row) != n_items for row in matrix):
        raise ValueError("all rater rows must have equal length")

    # values present per item (excluding None)
    per_item = []
    for i in range(n_items):
        vals = [row[i] for row in matrix if row[i] is not None]
        if len(vals) >= 2:
            per_item.append(vals)
    if not per_item:
        raise ValueError("no item has >=2 ratings; alpha undefined")

    # coincidence matrix over the value set
    values = sorted({v for vals in per_item for v in vals}, key=str)
    idx = {v: j for j, v in enumerate(values)}
    V = len(values)
    coinc = [[0.0] * V for _ in range(V)]
    for vals in per_item:
        m_u = len(vals)
        cnt = Counter(vals)
        # each ordered pair (c, c') within the unit contributes 1/(m_u - 1)
        for c in cnt:
            for cp in cnt:
                if c == cp:
                    pairs = cnt[c] * (cnt[c] - 1)
                else:
                    pairs = cnt[c] * cnt[cp]
                if pairs:
                    coinc[idx[c]][idx[cp]] += pairs / (m_u - 1)

    n_total = sum(sum(row) for row in coinc)
    if n_total == 0:
        raise ValueError("degenerate coincidence matrix")
    n_c = [sum(coinc[j]) for j in range(V)]

    # nominal metric: disagreement = 1 for off-diagonal
    D_o = sum(coinc[j][k] for j in range(V) for k in range(V) if j != k)
    D_e = sum(n_c[j] * n_c[k] for j in range(V) for k in range(V) if j != k) / (n_total - 1)
    if D_e == 0:
        return 1.0
    return 1.0 - (D_o / D_e)


# ---- convenience: pairwise mean kappa over a labels-by-rater dict ----------
def mean_pairwise_cohen(labels_by_rater: dict) -> float:
    """Mean Cohen's kappa across every rater pair. `labels_by_rater[name] = [labels...]`.
    All raters must label the same item set in the same order. Requires >=2 raters."""
    raters = list(labels_by_rater)
    if len(raters) < 2:
        raise ValueError("need >=2 raters")
    ks = [cohen_kappa(labels_by_rater[x], labels_by_rater[y])
          for x, y in combinations(raters, 2)]
    return sum(ks) / len(ks)
