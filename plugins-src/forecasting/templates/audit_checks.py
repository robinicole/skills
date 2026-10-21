"""Audit checks for a finished forecast: the checks that code can run. The
forecast-auditor skill adds the checks that need judgment (leakage by design,
decision fit). Each check returns findings with a category and a severity.

Severities: fatal (the forecast should not be used), serious (use only with the
caveat stated), minor (note it).
Categories: 1 Problem fit, 2 Data, 3 Model, 4 Evaluation, 5 Uncertainty.
Run: python audit_checks.py   (demo on an ETS analysis; needs fpp_data.py, fc_checks.py)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "statsforecast": "statsforecast",
                     "statsmodels": "statsmodels", "utilsforecast": "utilsforecast",
                     "pyreadr": "pyreadr"})
if missing:
    raise SystemExit("Install the missing packages, then run again.")

import numpy as np
import pandas as pd

from fc_checks import add_horizon, model_names, residual_check, score_cv

BENCHMARKS = {"Naive", "SeasonalNaive", "HistoricAverage", "RWD"}


def finding(category, check, severity, text):
    return {"category": category, "check": check, "severity": severity, "finding": text}


def check_horizon(decision_h: int, evaluated_h: int, forecast_h: int) -> list[dict]:
    out = []
    if evaluated_h < decision_h:
        out.append(finding("4 Evaluation", "horizon", "serious",
                           f"Cross-validation scored h<= {evaluated_h}, the decision needs h={decision_h}."))
    if forecast_h < decision_h:
        out.append(finding("1 Problem fit", "horizon", "fatal",
                           f"Forecast covers {forecast_h} periods; the decision needs {decision_h}."))
    return out


def check_baseline(cv: pd.DataFrame) -> list[dict]:
    if not BENCHMARKS & set(model_names(cv)):
        return [finding("4 Evaluation", "baseline", "fatal",
                        "No benchmark (naive, seasonal naive, mean, drift) in the comparison.")]
    return []


def check_cv_design(cv: pd.DataFrame, train_df: pd.DataFrame, m: int) -> list[dict]:
    out = []
    n_origins = cv["cutoff"].nunique()
    if n_origins < 5:
        out.append(finding("4 Evaluation", "cv origins", "serious",
                           f"Only {n_origins} forecast origins; accuracy rests on very few windows."))
    first_cut = cv["cutoff"].min()
    n_first = (train_df["ds"] <= first_cut).groupby(train_df["unique_id"]).sum().min()
    if m > 1 and n_first < 2 * m:
        out.append(finding("4 Evaluation", "cv first window", "serious",
                           f"First training window has {n_first} points, under two seasons ({2 * m})."))
    leak = cv.merge(train_df[["unique_id", "ds"]], on=["unique_id", "ds"])
    if (leak["ds"] <= leak["cutoff"]).any():
        out.append(finding("2 Data", "leakage", "fatal", "Some test rows are at or before their cutoff."))
    return out


def check_skill(scores: pd.DataFrame, metric: str = "mase") -> list[dict]:
    t = scores[scores["metric"] == metric].drop(columns=["metric", "h"], errors="ignore").mean()
    bench = [c for c in t.index if c in BENCHMARKS]
    others = [c for c in t.index if c not in BENCHMARKS]
    if not bench or not others:
        return []
    best_bench, best_model = t[bench].min(), t[others].min()
    if best_model >= best_bench:
        return [finding("4 Evaluation", "skill", "serious",
                        f"No model beats the best benchmark on {metric} "
                        f"({best_model:.3f} against {best_bench:.3f}). Ship the benchmark or rework.")]
    return []


def check_metric_scale(metric: str, n_series: int) -> list[dict]:
    if n_series > 1 and metric.lower() in {"mae", "rmse", "mse"}:
        return [finding("4 Evaluation", "metric scale", "serious",
                        f"{metric} averaged over {n_series} series of different scales; use MASE or RMSSE.")]
    if metric.lower() in {"mape", "smape"}:
        return [finding("4 Evaluation", "metric", "minor",
                        f"{metric} is undefined at zero and needs a true zero; report a scaled measure too.")]
    return []


def check_calibration(cv: pd.DataFrame, levels: list[int]) -> list[dict]:
    """Coverage against nominal, with a binomial standard error over the scored rows.
    Rows from one origin are correlated, so this test is lenient: treat a pass as weak evidence."""
    out = []
    for mdl in model_names(cv):
        for lv in levels:
            lo, hi = f"{mdl}-lo-{lv}", f"{mdl}-hi-{lv}"
            if lo not in cv:
                continue
            inside = ((cv["y"] >= cv[lo]) & (cv["y"] <= cv[hi])).to_numpy()
            p, n = lv / 100, len(inside)
            se = np.sqrt(p * (1 - p) / n)
            cov = inside.mean()
            if cov < p - 2 * se:
                out.append(finding("5 Uncertainty", "calibration", "serious",
                                   f"{mdl} {lv}% interval covers {cov:.0%} (n={n}): too narrow."))
            elif cov > p + 2 * se:
                out.append(finding("5 Uncertainty", "calibration", "minor",
                                   f"{mdl} {lv}% interval covers {cov:.0%} (n={n}): wider than needed."))
    return out


def check_residuals(resid, m: int, dof: int, name: str) -> list[dict]:
    r = residual_check(resid, m=m, dof=dof, name=name, plot=False)
    out = []
    if not r["white_noise"]:
        out.append(finding("3 Model", "residual autocorrelation", "serious",
                           f"{name}: Ljung-Box p={r['lb_pvalue']:.3g} at lag {r['lb_lag']}. "
                           "The model misses structure and its intervals are too narrow."))
    if not r["mean_within_2se"]:
        out.append(finding("3 Model", "residual mean", "minor", f"{name}: residual mean {r['mean']:.3g} is not zero."))
    return out


def check_break(y, alpha: float = 0.05) -> list[dict]:
    """CUSUM test on residuals from a linear trend fit. A rejection flags a level or
    slope change, and also any curved trend, so it is only a prompt to look at the
    time plot. Not from the book: the book finds breaks by plotting."""
    import statsmodels.api as sm
    from statsmodels.stats.diagnostic import breaks_cusumolsresid
    y = np.asarray(y, dtype=float)
    X = sm.add_constant(np.arange(len(y)))
    res = sm.OLS(y, X).fit()
    stat, p, _ = breaks_cusumolsresid(res.resid, ddof=2)
    if p < alpha:
        return [finding("2 Data", "structural break", "minor",
                        f"CUSUM test rejects a stable linear trend (p={p:.3g}). Look at the time plot: "
                        "if there is a break, start the training window after it or model it.")]
    return []


def report(findings: list[dict]) -> pd.DataFrame:
    order = {"fatal": 0, "serious": 1, "minor": 2}
    t = pd.DataFrame(findings, columns=["category", "check", "severity", "finding"])
    return t.sort_values("severity", key=lambda s: s.map(order)).reset_index(drop=True)


if __name__ == "__main__":
    # %% 1 Data
    from statsforecast import StatsForecast
    from statsforecast.models import AutoETS, SeasonalNaive
    from fpp_data import load, to_long
    gas = to_long(load("aus_production"), y="Gas", name="aus_production")
    # %% 2 Exploration needed for this method
    # The audit needs: the cv frame, the training data, m, the forecast horizon the decision needs, levels.
    m, decision_h, levels = 4, 8, [80, 95]
    # %% 3 Baselines
    sf = StatsForecast(models=[AutoETS(season_length=m), SeasonalNaive(season_length=m)], freq="QS")
    # %% 4 Model fit
    cv = sf.cross_validation(df=gas, h=4, n_windows=4, step_size=4, level=levels)   # deliberately short
    fitted = AutoETS(season_length=m).fit(gas["y"].to_numpy())
    # %% 5 Diagnostics
    scores = score_cv(cv, train_df=gas, m=m, levels=levels)
    # %% 6 Evaluation with time series cross-validation
    f = []
    f += check_horizon(decision_h, evaluated_h=int(add_horizon(cv)["h"].max()), forecast_h=8)
    f += check_baseline(cv)
    f += check_cv_design(cv, gas, m)
    f += check_skill(scores)
    f += check_metric_scale("mase", n_series=1)
    f += check_calibration(cv, levels)
    f += check_residuals(fitted.model_["residuals"], m=m, dof=0, name="AutoETS")
    f += check_break(np.log(gas["y"]))
    # %% 7 Forecast with prediction intervals and a plot
    # The auditor does not forecast. It reports and hands off.
    # %% 8 What to report
    # - Every finding with its category and severity, fatal first.
    print(report(f).to_string(index=False))
