"""Checks from the Rules of ML that are worth running in code. Standard library only.

Copy into docs/ml-plans/<project>/analysis/ and change only the data loading.
Each check returns a list of findings: (severity, check, message).

    calibration_by_slice   rule 14: average prediction vs average label per slice
    model_delta            rule 24: position-weighted symmetric difference of two rankings
    skew_gaps              rule 37: training / holdout / next-day / live gaps
    serving_mismatch       rules 29, 32, 37: logged serving features vs features rebuilt by training
    feature_coverage       rules 10, 19, 22: share of examples where each feature is present

Run `python ml_checks.py` for the self-check.
"""
from __future__ import annotations

FATAL, SERIOUS, MINOR = "FATAL", "SERIOUS", "MINOR"
ORDER = {FATAL: 0, SERIOUS: 1, MINOR: 2}


def calibration_by_slice(preds, labels, slices, tol=0.02, min_n=100):
    """slices: {name: [bool per example]}. Flags slices where |mean pred - mean label| > tol."""
    out = []
    for name, mask in slices.items():
        idx = [i for i, m in enumerate(mask) if m]
        if len(idx) < min_n:
            out.append((MINOR, "calibration", f"{name}: {len(idx)} examples, below {min_n}, not checked"))
            continue
        p = sum(preds[i] for i in idx) / len(idx)
        y = sum(labels[i] for i in idx) / len(idx)
        if abs(p - y) > tol:
            out.append((SERIOUS, "calibration", f"{name}: mean prediction {p:.3f} vs mean label {y:.3f} (n={len(idx)})"))
    return out


def model_delta(ranked_a, ranked_b):
    """Position-weighted symmetric difference between two ranked lists, in [0, 1].

    An item at position k weighs 1/k. 0 means same set, 1 means disjoint.
    ponytail: set-based, ignores reordering inside the shared set; add a rank correlation if order matters.
    """
    wa = {x: 1 / (k + 1) for k, x in enumerate(ranked_a)}
    wb = {x: 1 / (k + 1) for k, x in enumerate(ranked_b)}
    total = sum(wa.values()) + sum(wb.values())
    if not total:
        return 0.0
    diff = sum(w for x, w in wa.items() if x not in wb) + sum(w for x, w in wb.items() if x not in wa)
    return diff / total


def skew_gaps(train, holdout, nextday, live=None, higher_is_better=True, nextday_drop=0.05, live_tol=1e-6):
    """One metric (say AUC) measured on the four data sets of rule 37."""
    sign = 1 if higher_is_better else -1
    out = []
    g1 = sign * (train - holdout)
    g2 = sign * (holdout - nextday)
    if g1 > 0.1 * abs(train):
        out.append((MINOR, "skew: train vs holdout", f"gap {g1:.4f}; expected to exist, check overfitting"))
    if g2 > nextday_drop * abs(holdout):
        out.append((SERIOUS, "skew: holdout vs next-day", f"gap {g2:.4f}; look for time-sensitive features"))
    if live is not None and abs(nextday - live) > live_tol:
        out.append((FATAL, "skew: next-day vs live", f"next-day {nextday} vs live {live}; same examples must score the same, this is an engineering bug"))
    return out


def serving_mismatch(served, rebuilt, tol=1e-9):
    """served, rebuilt: {example_id: {feature: value}}. Compares features logged at serving
    with the ones the training pipeline rebuilds for the same examples."""
    out, ids = [], served.keys() & rebuilt.keys()
    if not ids:
        return [(FATAL, "serving mismatch", "no example ids in common; cannot compare")]
    feats = {f for i in ids for f in served[i].keys() | rebuilt[i].keys()}
    for f in sorted(feats):
        bad = 0
        for i in ids:
            a, b = served[i].get(f), rebuilt[i].get(f)
            same = a == b or (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= tol)
            bad += not same
        if bad:
            out.append((FATAL, "serving mismatch", f"{f}: differs on {bad}/{len(ids)} examples"))
    return out


def feature_coverage(examples, baseline=None, drop=0.1):
    """examples: list of {feature: value}; a feature is present when its value is not None.
    baseline: {feature: coverage} from an earlier period; flags drops above `drop`."""
    n = len(examples)
    cov = {}
    for ex in examples:
        for f, v in ex.items():
            cov[f] = cov.get(f, 0) + (v is not None)
    cov = {f: c / n for f, c in cov.items()}
    out = []
    for f, c in (baseline or {}).items():
        now = cov.get(f, 0.0)
        if c - now > drop:
            out.append((SERIOUS, "coverage drop", f"{f}: {c:.0%} -> {now:.0%}; silent failure? (rule 10)"))
    return cov, out


def report(findings):
    for sev, check, msg in sorted(findings, key=lambda f: ORDER[f[0]]):
        print(f"{sev:8s} {check}: {msg}")
    if not findings:
        print("No findings.")


if __name__ == "__main__":
    # calibration: slice "new" overpredicts by 0.2
    preds = [0.5] * 200 + [0.4] * 200
    labels = [1, 0] * 100 + [0] * 160 + [1] * 40
    f = calibration_by_slice(preds, labels, {"old": [True] * 200 + [False] * 200, "new": [False] * 200 + [True] * 200})
    assert [x[1] for x in f] == ["calibration"] and "new" in f[0][2], f

    assert model_delta(list("abc"), list("abc")) == 0.0
    assert model_delta(list("abc"), list("xyz")) == 1.0
    assert 0 < model_delta(list("abc"), list("abz")) < model_delta(list("abc"), list("zbc"))

    f = skew_gaps(train=0.90, holdout=0.85, nextday=0.78, live=0.77)
    assert [x[0] for x in f] == [SERIOUS, FATAL], f

    f = serving_mismatch({1: {"a": 1.0, "b": "x"}, 2: {"a": 2.0, "b": "y"}}, {1: {"a": 1.0, "b": "x"}, 2: {"a": 2.5, "b": "y"}})
    assert f == [(FATAL, "serving mismatch", "a: differs on 1/2 examples")], f

    cov, f = feature_coverage([{"a": 1, "b": None}] * 6 + [{"a": None, "b": None}] * 4, baseline={"a": 0.9, "b": 0.0})
    assert cov == {"a": 0.6, "b": 0.0} and len(f) == 1, (cov, f)

    report(skew_gaps(0.90, 0.85, 0.78, 0.77))
    print("ml_checks self-check passed")
