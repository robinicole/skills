"""Ground-truth check: simulate series from known ETS and ARIMA models, fit the
matching model, and check that the median estimate of each parameter is within
10% of the truth (0.05 absolute when the true value is below 0.5).

Run: python evals/ground_truth.py [--n 1000] [--reps 200]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "templates"))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import simulate  # noqa: E402  (its preflight prints on import)
from statsforecast.models import ARIMA, AutoETS  # noqa: E402


def within(est, true):
    tol = 0.05 if abs(true) < 0.5 else 0.10 * abs(true)
    return abs(est - true) <= tol, tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--reps", type=int, default=200)
    a = ap.parse_args()
    checks = []
    for case in [dict(alpha=0.4, beta=0.1), dict(alpha=0.8, beta=0.05)]:
        est = []
        for s in range(a.reps):
            df, _ = simulate.ets_aan(n=a.n, seed=s, **case)
            par = AutoETS(model="AAN", damped=False).fit(df["y"].to_numpy()).model_["par"]
            est.append(par[:2])
        med = np.median(est, axis=0)
        for name, m in zip(["alpha", "beta"], med):
            ok, tol = within(m, case[name])
            checks.append({"model": f"ETS(A,A,N) {case}", "param": name, "true": case[name],
                           "median": round(float(m), 4), "tol": tol, "pass": bool(ok)})
    for case in [dict(ar=(0.6,), ma=(0.3,), d=1), dict(ar=(-0.5,), ma=(0.4,), d=1)]:
        est = []
        for s in range(a.reps):
            df, _ = simulate.arima(n=a.n, seed=s, **case)
            c = ARIMA(order=(1, case["d"], 1), include_mean=False).fit(df["y"].to_numpy()).model_["coef"]
            est.append([c["ar1"], c["ma1"]])
        med = np.median(est, axis=0)
        for name, true, m in [("ar1", case["ar"][0], med[0]), ("ma1", case["ma"][0], med[1])]:
            ok, tol = within(m, true)
            checks.append({"model": f"ARIMA(1,{case['d']},1) {case}", "param": name, "true": true,
                           "median": round(float(m), 4), "tol": tol, "pass": bool(ok)})
    for c in checks:
        print(f"{'PASS' if c['pass'] else 'FAIL'} {c['model']:45s} {c['param']:6s} true {c['true']:6.3f} median {c['median']:7.4f} tol {c['tol']:.3f}")
    out = Path(__file__).parent / "runs"
    out.mkdir(exist_ok=True)
    (out / "ground_truth.json").write_text(json.dumps(checks, indent=2))
    return 0 if all(c["pass"] for c in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
