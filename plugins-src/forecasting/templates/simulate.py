"""Simulate series with known structure, for exercises and for checking that a
method recovers what it should. Every generator returns a long frame
(unique_id, ds, y) and the true parameters.

Not from the book: the generators are written for this plugin. The models they
simulate are the book's (ETS state space form, ARIMA, hierarchies).
Run: python simulate.py   (needs fc_checks.py in the same folder)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "statsforecast": "statsforecast",
                     "statsmodels": "statsmodels", "matplotlib": "matplotlib"})
if missing:
    raise SystemExit("Install the missing packages, then run again.")

import numpy as np
import pandas as pd


def _frame(y, uid, freq="MS", start="2000-01-01"):
    return pd.DataFrame({"unique_id": uid, "ds": pd.date_range(start, periods=len(y), freq=freq), "y": y})


def ets_aan(n=200, alpha=0.4, beta=0.1, level=100.0, slope=1.0, sigma=2.0, seed=0, uid="ETS_AAN"):
    """ETS(A,A,N), error-correction form: l = l + b + alpha*e, b = b + beta*e."""
    rng = np.random.default_rng(seed)
    y = np.empty(n)
    for t in range(n):
        e = rng.normal(0, sigma)
        y[t] = level + slope + e
        level, slope = level + slope + alpha * e, slope + beta * e
    return _frame(y, uid), {"alpha": alpha, "beta": beta, "sigma": sigma}


def ets_ana(n=240, m=12, alpha=0.3, gamma=0.1, level=50.0, amplitude=10.0, sigma=1.5, seed=0, uid="ETS_ANA"):
    """ETS(A,N,A): level plus a seasonal pattern that evolves at rate gamma."""
    rng = np.random.default_rng(seed)
    season = list(amplitude * np.sin(2 * np.pi * np.arange(m) / m))
    y = np.empty(n)
    for t in range(n):
        e = rng.normal(0, sigma)
        s = season[t % m]
        y[t] = level + s + e
        level += alpha * e
        season[t % m] = s + gamma * e
    return _frame(y, uid), {"alpha": alpha, "gamma": gamma, "m": m, "sigma": sigma}


def arima(n=300, ar=(0.6,), ma=(0.3,), d=1, sigma=1.0, seed=0, uid="ARIMA"):
    """ARIMA(p,d,q) with no constant. ar and ma follow the book's sign convention:
    y_t = ar1*y_{t-1} + ... + e_t + ma1*e_{t-1} + ..."""
    from statsmodels.tsa.arima_process import arma_generate_sample
    rng = np.random.default_rng(seed)
    x = arma_generate_sample(ar=np.r_[1, -np.asarray(ar)], ma=np.r_[1, np.asarray(ma)],
                             nsample=n + 100, scale=sigma, burnin=100,
                             distrvs=lambda size: rng.standard_normal(size))[-n:]
    for _ in range(d):
        x = np.cumsum(x)
    return _frame(x, uid), {"ar": tuple(ar), "ma": tuple(ma), "d": d, "sigma": sigma}


def intermittent(n=120, p_demand=0.3, size_mean=4.0, seed=0, uid="intermittent"):
    """Zero most periods; a Poisson size (at least 1) with probability p_demand."""
    rng = np.random.default_rng(seed)
    y = np.where(rng.random(n) < p_demand, 1 + rng.poisson(size_mean - 1, n), 0).astype(float)
    return _frame(y, uid), {"rate": p_demand * size_mean}


def hierarchy(n=80, m=4, seed=0):
    """Total = A + B, A = A1 + A2, B = B1 + B2. Bottom series are seasonal random walks
    with drift. Returns the bottom series only (aggregate them with hierarchicalforecast)."""
    rng = np.random.default_rng(seed)
    rows = []
    for g, k in [("A", "A1"), ("A", "A2"), ("B", "B1"), ("B", "B2")]:
        base = 50 + 20 * rng.random()
        seas = rng.normal(0, 5, m)
        walk = np.cumsum(rng.normal(0.2, 1.0, n))
        y = base + walk + np.tile(seas, n // m + 1)[:n] + rng.normal(0, 1, n)
        f = _frame(y, k, freq="QS")
        rows.append(f.assign(group=g, item=k))
    return pd.concat(rows, ignore_index=True), {"structure": "Total > {A, B} > {A1, A2, B1, B2}"}


def regression_arima_errors(n=200, beta=2.0, phi=0.7, sigma=1.0, seed=0, uid="DynReg"):
    """y = 10 + beta*x + eta, eta AR(1) with coefficient phi; x is a stationary AR(1)."""
    rng = np.random.default_rng(seed)
    x, eta = np.zeros(n), np.zeros(n)
    for t in range(1, n):
        x[t] = 0.5 * x[t - 1] + rng.normal()
        eta[t] = phi * eta[t - 1] + rng.normal(0, sigma)
    f = _frame(10 + beta * x + eta, uid).assign(x=x)
    return f, {"beta": beta, "phi": phi, "sigma": sigma}


if __name__ == "__main__":
    # %% 1 Data
    s_ets, true_ets = ets_aan(n=1000, seed=1)
    s_ar, true_ar = arima(n=1000, seed=1)
    # %% 2 Exploration needed for this method
    print("Simulated", len(s_ets), "points of ETS(A,A,N) and", len(s_ar), "of ARIMA(1,1,1)")
    # %% 3 Baselines
    # Not needed: the truth is known, so recovery is checked directly.
    # %% 4 Model fit
    from statsforecast.models import ARIMA, AutoETS
    ets = AutoETS(model="AAN", damped=False).fit(s_ets["y"].to_numpy())
    ar = ARIMA(order=(1, 1, 1), include_mean=False).fit(s_ar["y"].to_numpy())
    # %% 5 Diagnostics
    est_ets = dict(zip(["alpha", "beta"], ets.model_["par"][:2]))
    est_ar = {k: float(v) for k, v in ar.model_["coef"].items()}
    print("ETS truth", true_ets, "estimate", {k: round(float(v), 3) for k, v in est_ets.items()})
    print("ARIMA truth", true_ar, "estimate", {k: round(v, 3) for k, v in est_ar.items()})
    # %% 6 Evaluation with time series cross-validation
    # See evals/ground_truth.py for recovery over many simulated series.
    # %% 7 Forecast with prediction intervals and a plot
    # Exercises use these series with the method templates.
    # %% 8 What to report
    # - The generating model and its parameters; the estimates and their gap to the truth.
    print("Done.")
