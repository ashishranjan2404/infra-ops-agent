#!/usr/bin/env python3
"""
score_human_eval.py — Analysis + IAA for the J3 SRE human-evaluation study.

Consumes filled rating CSVs (one per rater) and produces:
  - per-item mean Likert scores per dimension (correctness / usefulness / safety)
  - per-rater means (to spot lenient/strict raters)
  - inter-annotator agreement (IAA):
        * Krippendorff's alpha (ordinal) per dimension   [primary]
        * mean pairwise Spearman rho per dimension       [secondary]
        * exact + adjacent (within-1) percent agreement   [descriptive]
  - correlation of human mean score vs the automated reward (validity check),
    by joining on blinding_key.json (Spearman + Pearson)

NO external deps (pure stdlib). Run:
    python3 score_human_eval.py --ratings ratings/*.csv \
        --key blinding_key.json --out results.json

Rating CSV schema (header required), one row per (rater,item):
    rater_id,item_id,correctness,usefulness,safety,confident_root_cause,free_text
  - correctness/usefulness/safety: integers 1..5 (Likert)
  - confident_root_cause: 0/1 (binary: would you trust this RC to act?)
  - free_text: optional notes (ignored by stats)

If --ratings is omitted, a built-in synthetic 5-rater self-test runs so the
script is validated end-to-end without human data (the documented blocker).
"""
import argparse, csv, glob, json, math, sys
from collections import defaultdict
from itertools import combinations

LIKERT = ["correctness", "usefulness", "safety"]
SCALE = (1, 5)


# ----------------------------- IO -----------------------------
def load_ratings(paths):
    """Return list of dict rows from one or more rating CSVs."""
    rows = []
    for p in paths:
        with open(p, newline="") as fh:
            for r in csv.DictReader(fh):
                rows.append(r)
    return rows


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


# ----------------------- basic statistics ---------------------
def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def _rank(xs):
    """Average-rank transform (handles ties) for Spearman."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 2:
        return float("nan")
    xs, ys = zip(*pairs)
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else float("nan")


def spearman(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 2:
        return float("nan")
    xs, ys = zip(*pairs)
    return _pearson(_rank(list(xs)), _rank(list(ys)))


# ---------------- Krippendorff's alpha (ordinal) --------------
def krippendorff_alpha_ordinal(matrix):
    """
    matrix: dict[item_id] -> list of ratings (one per rater, None if missing).
    Ordinal alpha with the standard ordinal difference function.
    Returns alpha in (-inf, 1]; 1 == perfect, 0 == chance.
    """
    # Build list of valid values & per-unit value lists
    units = {u: [v for v in vs if v is not None] for u, vs in matrix.items()}
    units = {u: vs for u, vs in units.items() if len(vs) >= 2}
    if not units:
        return float("nan")
    values = sorted({v for vs in units.values() for v in vs})
    if len(values) < 2:
        return 1.0  # all identical -> perfect agreement
    # coincidence matrix
    coinc = defaultdict(float)
    for vs in units.values():
        m = len(vs)
        for c in vs:
            for k in vs:
                if c is k:  # skip same element index handled below
                    pass
        # proper pairing: for each ordered pair of distinct positions
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                coinc[(vs[i], vs[j])] += 1.0 / (m - 1)
    n = sum(coinc.values())
    if n == 0:
        return float("nan")
    # marginal counts
    nv = defaultdict(float)
    for (c, k), w in coinc.items():
        nv[c] += w

    # ordinal metric: delta(c,k) = ( sum_{g=c..k} ng - (nc+nk)/2 )^2
    idx = {v: i for i, v in enumerate(values)}

    def delta(c, k):
        lo, hi = sorted((idx[c], idx[k]))
        s = sum(nv[values[g]] for g in range(lo, hi + 1))
        return (s - (nv[c] + nv[k]) / 2.0) ** 2

    Do = sum(coinc[(c, k)] * delta(c, k) for c in values for k in values)
    De = (1.0 / (n - 1)) * sum(
        nv[c] * nv[k] * delta(c, k) for c in values for k in values
    )
    if De == 0:
        return 1.0
    return 1.0 - Do / De


# --------------------- percent agreement ----------------------
def percent_agreement(matrix):
    exact = adj = tot = 0
    for vs in matrix.values():
        vs = [v for v in vs if v is not None]
        for a, b in combinations(vs, 2):
            tot += 1
            if a == b:
                exact += 1
            if abs(a - b) <= 1:
                adj += 1
    if tot == 0:
        return float("nan"), float("nan")
    return exact / tot, adj / tot


# --------------------- mean pairwise Spearman -----------------
def mean_pairwise_spearman(by_rater, item_ids, dim):
    raters = sorted(by_rater)
    rhos = []
    for r1, r2 in combinations(raters, 2):
        a = [by_rater[r1].get(i, {}).get(dim) for i in item_ids]
        b = [by_rater[r2].get(i, {}).get(dim) for i in item_ids]
        rho = spearman(a, b)
        if not math.isnan(rho):
            rhos.append(rho)
    return mean(rhos) if rhos else float("nan")


# --------------------------- analyze --------------------------
def analyze(rows, key_path=None):
    # index: by_rater[rater][item][dim] = int
    by_rater = defaultdict(lambda: defaultdict(dict))
    items = set()
    for r in rows:
        rid = r.get("rater_id")
        iid = r.get("item_id")
        if not rid or not iid:
            continue
        items.add(iid)
        for d in LIKERT + ["confident_root_cause"]:
            v = _to_int(r.get(d))
            if v is not None:
                by_rater[rid][iid][d] = v
    item_ids = sorted(items)
    raters = sorted(by_rater)

    out = {
        "n_raters": len(raters),
        "n_items": len(item_ids),
        "raters": raters,
        "per_item": {},
        "per_rater_mean": {},
        "dimension_summary": {},
        "iaa": {},
    }

    # per-item means
    for iid in item_ids:
        rec = {}
        for d in LIKERT + ["confident_root_cause"]:
            vals = [by_rater[r].get(iid, {}).get(d) for r in raters]
            rec[d + "_mean"] = round(mean(vals), 3)
            rec[d + "_n"] = len([v for v in vals if v is not None])
        out["per_item"][iid] = rec

    # per-rater means (leniency check)
    for r in raters:
        rec = {}
        for d in LIKERT:
            vals = [by_rater[r].get(i, {}).get(d) for i in item_ids]
            rec[d] = round(mean(vals), 3)
        out["per_rater_mean"][r] = rec

    # dimension-level IAA + summary
    for d in LIKERT:
        matrix = {
            iid: [by_rater[r].get(iid, {}).get(d) for r in raters] for iid in item_ids
        }
        alpha = krippendorff_alpha_ordinal(matrix)
        exact, adj = percent_agreement(matrix)
        rho = mean_pairwise_spearman(by_rater, item_ids, d)
        allvals = [v for vs in matrix.values() for v in vs if v is not None]
        out["dimension_summary"][d] = {
            "grand_mean": round(mean(allvals), 3),
            "n_ratings": len(allvals),
        }
        out["iaa"][d] = {
            "krippendorff_alpha_ordinal": _r(alpha),
            "mean_pairwise_spearman": _r(rho),
            "pct_exact_agreement": _r(exact),
            "pct_within1_agreement": _r(adj),
            "interpretation": _alpha_label(alpha),
        }

    # validity vs automated reward
    if key_path:
        out["validity_vs_auto_reward"] = _validity(by_rater, item_ids, raters, key_path)
    return out


def _r(x):
    return None if (x is None or (isinstance(x, float) and math.isnan(x))) else round(x, 4)


def _alpha_label(a):
    if a is None or math.isnan(a):
        return "n/a"
    if a >= 0.8:
        return "strong agreement"
    if a >= 0.667:
        return "acceptable (tentative conclusions only)"
    if a >= 0.4:
        return "moderate / weak"
    return "poor — do not draw conclusions"


def _validity(by_rater, item_ids, raters, key_path):
    key = json.load(open(key_path))
    auto = {k["item_id"]: k["auto_reward"] for k in key["items"]}
    res = {}
    for d in LIKERT:
        hmean = [mean([by_rater[r].get(i, {}).get(d) for r in raters]) for i in item_ids]
        a = [auto.get(i) for i in item_ids]
        res[d] = {
            "spearman_human_vs_auto": _r(spearman(hmean, a)),
            "pearson_human_vs_auto": _r(_pearson(hmean, a)),
        }
    return res


# ----------------------- synthetic self-test ------------------
def synthetic_rows(seed=0):
    """5 synthetic raters x 12 items with a true latent quality + rater noise/bias.
    Validates the whole pipeline without real human data."""
    import random

    rng = random.Random(seed)
    key = json.load(open(_default_key()))
    items = [k["item_id"] for k in key["items"]]
    truth = {k["item_id"]: 1 + 4 * k["auto_reward"] for k in key["items"]}  # map reward->1..5-ish
    raters = [f"sre{i+1}" for i in range(5)]
    bias = {r: rng.uniform(-0.4, 0.4) for r in raters}
    rows = []
    for r in raters:
        for iid in items:
            base = truth[iid] + bias[r]
            row = {"rater_id": r, "item_id": iid, "free_text": ""}
            for d in LIKERT:
                v = round(base + rng.gauss(0, 0.6))
                v = max(1, min(5, v))
                row[d] = v
            row["confident_root_cause"] = 1 if base >= 3 else 0
            rows.append(row)
    return rows


def _default_key():
    import os

    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "blinding_key.json")


# ------------------------------ main --------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratings", nargs="*", help="rating CSV files / globs")
    ap.add_argument("--key", default=_default_key(), help="blinding_key.json")
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--selftest", action="store_true", help="force synthetic run")
    args = ap.parse_args(argv)

    if args.ratings:
        paths = []
        for g in args.ratings:
            paths.extend(glob.glob(g))
        if not paths:
            print("no rating files matched", file=sys.stderr)
            return 2
        rows = load_ratings(paths)
        mode = "real"
    else:
        rows = synthetic_rows()
        mode = "synthetic-selftest"

    res = analyze(rows, key_path=args.key)
    res["_mode"] = mode
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"[{mode}] {res['n_raters']} raters x {res['n_items']} items -> {args.out}")
    for d in LIKERT:
        i = res["iaa"][d]
        print(
            f"  {d:12s} mean={res['dimension_summary'][d]['grand_mean']:.2f} "
            f"alpha={i['krippendorff_alpha_ordinal']} "
            f"within1={i['pct_within1_agreement']} ({i['interpretation']})"
        )
    if "validity_vs_auto_reward" in res:
        print("  validity (human vs auto reward), Spearman:")
        for d in LIKERT:
            print(f"    {d}: {res['validity_vs_auto_reward'][d]['spearman_human_vs_auto']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
