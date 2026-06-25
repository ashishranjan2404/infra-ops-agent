"""Tests for the noisy-metrics transform (A15).

Run from repo root:  python3 -m pytest experiments/ralph_outputs/A15/artifacts/test_noisy_metrics_transform.py -q
"""
import copy
import importlib.util
import os
import sys

import yaml

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import sim.spec as spec_mod  # noqa: E402

# Load the transform module by path (it lives outside any package).
_spec = importlib.util.spec_from_file_location(
    "noisy_metrics_transform", os.path.join(HERE, "noisy_metrics_transform.py"))
nmt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nmt)

BASE_WITH_GUN = os.path.join(
    ROOT, "scenarios/cidg/generated/55-github-network-partition.yaml")
BASE_NO_GUN = os.path.join(
    ROOT, "scenarios/cidg/generated/44-search-cpu-starve.yaml")


def _load(p):
    with open(p) as f:
        return yaml.safe_load(f)


def _valid(doc):
    return spec_mod.validate(spec_mod._spec_from_dict(doc))


def test_sets_noisy_observation():
    out = nmt.transform(_load(BASE_WITH_GUN))
    assert out["observation"]["alerting"] == "noisy"
    assert out["observation"]["monitoring_degrades"] is True
    assert out["assertions"]["monitoring_degrades"] is True


def test_buries_smoking_guns_deeper():
    base = _load(BASE_WITH_GUN)
    before = base["observation"]["smoking_guns"][0]["buried_under"]
    out = nmt.transform(base)
    after = out["observation"]["smoking_guns"][0]["buried_under"]
    assert after >= before and after >= nmt.BURIED_FLOOR
    assert after == max(before * nmt.BURIED_MULT, nmt.BURIED_FLOOR)


def test_injects_observes_edge_for_validity():
    out = nmt.transform(_load(BASE_WITH_GUN))
    assert any(e.get("type") == "observes" for e in out["topology"]["edges"])


def test_does_not_mutate_input():
    base = _load(BASE_WITH_GUN)
    snapshot = copy.deepcopy(base)
    nmt.transform(base)
    assert base == snapshot  # pure transform


def test_physics_unchanged():
    """Topology nodes/edges of the baseline, root cause, and fix are preserved
    (only a monitoring node + observes edge are ADDED)."""
    base = _load(BASE_WITH_GUN)
    out = nmt.transform(base)
    assert out["root_cause"] == base["root_cause"]
    assert out["canonical_fix"] == base["canonical_fix"]
    base_nodes = {n["name"] for n in base["topology"]["nodes"]}
    out_nodes = {n["name"] for n in out["topology"]["nodes"]}
    assert base_nodes.issubset(out_nodes)
    base_edges = base["topology"]["edges"]
    out_non_observe = [e for e in out["topology"]["edges"]
                       if e.get("type") != "observes"]
    assert out_non_observe == base_edges


def test_transformed_specs_validate():
    for p in (BASE_WITH_GUN, BASE_NO_GUN):
        out = nmt.transform(_load(p))
        assert _valid(out) == [], f"{p}: {_valid(out)}"


def test_idempotent_id():
    once = nmt.transform(_load(BASE_WITH_GUN))
    twice = nmt.transform(once)
    assert twice["meta"]["id"] == once["meta"]["id"]  # no double -noisy suffix
