"""Shared checks used by every template: preflight, residual diagnostics, scoring.

Copy this file next to the template you run, together with fpp_data.py.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import numpy as np
import pandas as pd


# --- Preflight: detect missing packages (does NOT install) -------------------
def preflight(required: dict[str, str], label: str = "required") -> list[str]:
    """required maps import name -> pip name. Prints and returns the missing pip names."""
    missing = [pip for mod, pip in required.items() if importlib.util.find_spec(mod) is None]
    if missing:
        print(f"Missing {label} Python packages:", ", ".join(missing))
        print("Install with: pip install " + " ".join(missing))
    else:
        print(f"All {label} Python packages are installed.")
    return missing


def out_dir() -> Path:
    """Folder for plots and tables. Set FC_OUT to change it."""
    d = Path(os.environ.get("FC_OUT", "forecast_out"))
    d.mkdir(parents=True, exist_ok=True)
    return d


# --- Residual diagnostics ------------------------------------------------------
def ljung_box_lag(m: int, n: int) -> int:
    """Lag rule: 10 for non-seasonal data, 2m for seasonal data, at most n/5."""
    lag = 2 * m if m > 1 else 10
    return max(1, min(lag, n // 5))


def residual_check(resid, m: int, dof: int = 0, name: str = "model",
                   plot: bool = True) -> dict:
    """Ljung-Box, mean test and three diagnostic plots for one residual series.

    resid: innovation residuals (on the transformed scale if a transform was used).
    dof: number of estimated ARMA or regression coefficients (0 for ETS and benchmarks).
    """
    from statsmodels.stats.diagnostic import acorr_ljungbox

    r = pd.Series(np.asarray(resid, dtype=float)).dropna()
    lag = ljung_box_lag(m, len(r))
    lb = acorr_ljungbox(r, lags=[lag], model_df=dof if dof < lag else 0, return_df=True)
    se = r.std(ddof=1) / np.sqrt(len(r))
    out = {
        "model": name,
        "lb_lag": lag,
        "lb_dof": dof,
        "lb_stat": float(lb["lb_stat"].iloc[0]),
        "lb_pvalue": float(lb["lb_pvalue"].iloc[0]),
        "mean": float(r.mean()),
        "mean_within_2se": bool(abs(r.mean()) <= 2 * se),
    }
    out["white_noise"] = out["lb_pvalue"] > 0.05
    if plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from statsmodels.graphics.tsaplots import plot_acf

        fig, ax = plt.subplots(3, 1, figsize=(8, 8))
        ax[0].plot(r.values)
        ax[0].axhline(0, color="grey", lw=0.8)
        ax[0].set_title(f"{name}: residuals over time (variance should look constant)")
        plot_acf(r, ax=ax[1], lags=min(3 * max(m, 4), len(r) // 2 - 1), zero=False)
        ax[1].set_title("ACF of residuals (spikes should stay inside the band)")
        ax[2].hist(r, bins=25)
        ax[2].set_title("Histogram (normality matters only for the interval formula)")
        fig.tight_layout()
        fig.savefig(out_dir() / f"residuals_{name}.png", dpi=120)
        plt.close(fig)
    return out


# --- Time series cross-validation scoring ------------------------------------
def add_horizon(cv: pd.DataFrame) -> pd.DataFrame:
    """Add h = 1..H within each (series, cutoff)."""
    cv = cv.sort_values(["unique_id", "cutoff", "ds"]).copy()
    cv["h"] = cv.groupby(["unique_id", "cutoff"]).cumcount() + 1
    return cv


def model_names(cv: pd.DataFrame) -> list[str]:
    skip = {"unique_id", "ds", "cutoff", "y", "h"}
    return [c for c in cv.columns if c not in skip and "-lo-" not in c and "-hi-" not in c]


def crps_from_intervals(cv: pd.DataFrame, model: str, levels: list[int]) -> pd.Series:
    """Approximate CRPS per row from symmetric interval bounds.

    Not from the book: the book computes CRPS from the full forecast distribution.
    Here CRPS is approximated by twice the mean quantile (pinball) loss over the
    quantiles implied by the interval levels plus the median (the point forecast).
    Use many levels (for example 10, 20, ..., 90) for a close approximation.
    """
    y = cv["y"].to_numpy()
    losses = []
    qs = [(0.5, cv[model].to_numpy())]
    for lv in levels:
        a = (100 - lv) / 200
        qs.append((a, cv[f"{model}-lo-{lv}"].to_numpy()))
        qs.append((1 - a, cv[f"{model}-hi-{lv}"].to_numpy()))
    for p, q in qs:
        losses.append(np.where(y >= q, p * (y - q), (1 - p) * (q - y)))
    return pd.Series(2 * np.mean(losses, axis=0), index=cv.index)


def score_cv(cv: pd.DataFrame, train_df: pd.DataFrame, m: int,
             levels: list[int], crps_levels: list[int] | None = None,
             by_h: bool = True) -> pd.DataFrame:
    """Score a cross_validation frame per forecast horizon (or overall).

    Metrics: MAE, RMSE, MASE, RMSSE, coverage and Winkler score at each level in
    `levels`, and approximate CRPS when `crps_levels` is given (the cv frame must
    hold those interval columns). Squared-error metrics are averaged over series
    and forecast origins before the square root. MASE and RMSSE are scaled with
    the training data before each cutoff only.
    Returns a long table: (h,) metric, one column per model.
    """
    from functools import partial
    from utilsforecast.evaluation import evaluate
    from utilsforecast.losses import coverage, mae, mase, mse, msse, winkler_score

    cv = add_horizon(cv)
    models = model_names(cv)
    metrics = [mae, mse, partial(mase, seasonality=m), partial(msse, seasonality=m),
               coverage, winkler_score]
    groups = cv.groupby("h") if by_h else [(None, cv)]
    rows = []
    for h, g in groups:
        g = g.drop(columns="h")
        s = evaluate(g, metrics=metrics, models=models, train_df=train_df, level=levels)
        s = s.groupby("metric")[models].mean()
        s.loc["rmse"] = np.sqrt(s.loc["mse"])
        s.loc["rmsse"] = np.sqrt(s.loc["msse"])
        s = s.drop(index=["mse", "msse"])
        if crps_levels:
            s.loc["crps_approx"] = pd.Series(
                {mdl: crps_from_intervals(g, mdl, crps_levels).mean() for mdl in models})
        if h is not None:
            s["h"] = h
        rows.append(s.reset_index())
    return pd.concat(rows, ignore_index=True)


def skill(scores: pd.DataFrame, metric: str, benchmark: str) -> pd.DataFrame:
    """Skill score against a benchmark: 1 - score / benchmark score. Positive is better."""
    t = scores[scores["metric"] == metric].copy()
    models = [c for c in t.columns if c not in ("metric", "h")]
    base = t[benchmark].copy()
    for mdl in models:
        t[mdl] = 1 - t[mdl] / base
    return t


def rolling_origin(df: pd.DataFrame, h: int, n_windows: int, step_size: int,
                   fit_forecast) -> pd.DataFrame:
    """Time series cross-validation for models outside statsforecast.

    df: one series in long format (unique_id, ds, y, plus any predictor columns),
        sorted by ds.
    fit_forecast(train, future) -> DataFrame with the same row count as `future`
        and one column per model (plus optional "<model>-lo-<level>" and
        "<model>-hi-<level>" columns). `future` holds the next h rows with the
        predictor columns, so the caller decides ex post (actual predictors) or
        ex ante (forecast predictors before calling).
    Returns a frame shaped like StatsForecast.cross_validation: unique_id, ds,
    cutoff, y, and the model columns.
    """
    df = df.sort_values("ds").reset_index(drop=True)
    n = len(df)
    out = []
    for w in range(n_windows):
        end = n - h - (n_windows - 1 - w) * step_size      # first index of the test rows
        train, future = df.iloc[:end], df.iloc[end:end + h]
        pred = fit_forecast(train.copy(), future.drop(columns="y").copy())
        block = future[["unique_id", "ds", "y"]].reset_index(drop=True)
        block.insert(2, "cutoff", train["ds"].iloc[-1])
        out.append(pd.concat([block, pred.reset_index(drop=True)], axis=1))
    return pd.concat(out, ignore_index=True)
