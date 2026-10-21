"""Regression template: linear regression with trend, season dummies, Fourier terms
and predictors; predictor selection by AICc and leave-one-out CV; residual checks;
ex-ante versus ex-post forecasts; scenario forecasts.

Book: FPP3 chapter 7 (R: https://otexts.com/fpp3/regression.html [unverified URL];
Python edition chapter 7 [unverified URL]).
Python: statsmodels OLS. Its prediction intervals include parameter uncertainty, as
the book's TSLM intervals do.
Run: python regression.py   (needs fpp_data.py and fc_checks.py in the same folder)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib",
                     "statsmodels": "statsmodels", "statsforecast": "statsforecast",
                     "utilsforecast": "utilsforecast", "pyreadr": "pyreadr"})
if missing:
    raise SystemExit("Install the missing packages, then run again.")

import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.deterministic import DeterministicProcess, Fourier

from fc_checks import out_dir, residual_check, rolling_origin, score_cv
from fpp_data import load, to_long

OUT = out_dir()
LEVELS = [80, 95]


def aicc(res) -> float:
    """AICc for an OLS fit, with k = coefficients + 1 (the error variance)."""
    n, k = res.nobs, res.df_model + res.k_constant + 1
    return res.aic + 2 * k * (k + 1) / (n - k - 1)


def loo_cv(res) -> float:
    """Leave-one-out CV statistic from the hat matrix: mean of (e_i / (1 - h_ii))^2."""
    h = res.get_influence().hat_matrix_diag
    return float(np.mean((res.resid / (1 - h)) ** 2))


def predict_with_intervals(res, X_new, name: str) -> pd.DataFrame:
    """Point forecasts and prediction intervals as <name>, <name>-lo-<lv>, <name>-hi-<lv>."""
    out = {}
    for lv in LEVELS:
        f = res.get_prediction(X_new).summary_frame(alpha=1 - lv / 100)
        out[name] = f["mean"].to_numpy()
        out[f"{name}-lo-{lv}"] = f["obs_ci_lower"].to_numpy()
        out[f"{name}-hi-{lv}"] = f["obs_ci_upper"].to_numpy()
    return pd.DataFrame(out)


# %% 1 Data
# Quarterly US percentage changes: consumption and four candidate predictors.
uc = load("us_change").rename(columns={"Quarter": "ds"})
PREDICTORS = ["Income", "Production", "Savings", "Unemployment"]

# %% 2 Exploration needed for this method
# Scatter the target against each predictor. Correlation is enough to forecast;
# it says nothing about cause.
fig, axes = plt.subplots(1, 4, figsize=(14, 3))
for ax, p in zip(axes, PREDICTORS):
    ax.scatter(uc[p], uc["Consumption"], s=8)
    ax.set_xlabel(p)
axes[0].set_ylabel("Consumption")
fig.tight_layout()
fig.savefig(OUT / "regression_scatter.png", dpi=120)
plt.close(fig)
print("Correlations with Consumption:\n", uc[PREDICTORS + ["Consumption"]].corr()["Consumption"].round(2))

# %% 3 Baselines
# Mean and naive on the target. A regression that cannot beat them adds nothing.
from statsforecast import StatsForecast
from statsforecast.models import HistoricAverage, Naive
cons = to_long(load("us_change"), y="Consumption", name="us_change")
sf_base = StatsForecast(models=[HistoricAverage(), Naive()], freq="QS")

# %% 4 Model fit
# Predictor selection: fit every subset, rank by AICc (CV and BIC shown too).
# Do not select by p-value or R squared; R squared always rises with more predictors.
rows = []
for k in range(len(PREDICTORS) + 1):
    for subset in itertools.combinations(PREDICTORS, k):
        X = sm.add_constant(uc[list(subset)]) if subset else np.ones((len(uc), 1))
        res = sm.OLS(uc["Consumption"], X).fit()
        rows.append({"predictors": "+".join(subset) or "(intercept)", "adj_r2": res.rsquared_adj,
                     "CV": loo_cv(res), "AIC": res.aic, "AICc": aicc(res), "BIC": res.bic})
selection = pd.DataFrame(rows).sort_values("AICc")
print("All-subsets selection (lowest AICc first):\n", selection.head(6).round(3))
best = selection.iloc[0]["predictors"].split("+")
fit = sm.OLS(uc["Consumption"], sm.add_constant(uc[best])).fit()
print(fit.summary().tables[1])

# %% 5 Diagnostics
# Residuals should be uncorrelated with mean zero; check against time, each
# predictor and the fitted values. A pattern means a missing or nonlinear term.
k = len(best) + 1
diag = residual_check(fit.resid, m=4, dof=k, name="regression")
bg = acorr_breusch_godfrey(fit, nlags=8)
print("Residual check:", diag)
print(f"Breusch-Godfrey (8 lags) p = {bg[1]:.3f}; Durbin-Watson = {durbin_watson(fit.resid):.2f}")
fig, axes = plt.subplots(1, len(best) + 1, figsize=(4 * (len(best) + 1), 3))
for ax, p in zip(axes, best):
    ax.scatter(uc[p], fit.resid, s=8)
    ax.set_xlabel(p)
axes[-1].scatter(fit.fittedvalues, fit.resid, s=8)
axes[-1].set_xlabel("fitted")
axes[0].set_ylabel("residual")
fig.tight_layout()
fig.savefig(OUT / "regression_residual_scatter.png", dpi=120)
plt.close(fig)

# %% 6 Evaluation with time series cross-validation
# Ex-post: actual future predictor values. This isolates model error only; it is
# not the accuracy a user will get. Ex-ante needs forecasts of the predictors
# (see dynamic_regression.py for that case).
data = cons.assign(**{p: uc[p].to_numpy() for p in best})


def fit_forecast(train, future):
    r = sm.OLS(train["y"], sm.add_constant(train[best])).fit()
    Xf = sm.add_constant(future[best], has_constant="add")
    return predict_with_intervals(r, Xf, "Regression")


h, nw = 4, 20
cv_reg = rolling_origin(data, h=h, n_windows=nw, step_size=1, fit_forecast=fit_forecast)
cv_base = sf_base.cross_validation(df=cons, h=h, n_windows=nw, step_size=1, level=LEVELS)
cv = cv_reg.merge(cv_base.drop(columns="y"), on=["unique_id", "ds", "cutoff"])
scores = score_cv(cv, train_df=cons, m=1, levels=LEVELS, by_h=False)
print("Ex-post cross-validated accuracy (regression uses actual predictors):\n",
      scores.set_index("metric").round(3))

# Trend and season model with dummies, then Fourier terms (beer production).
beer = to_long(load("aus_production"), y="Beer", name="aus_production")
beer = beer[beer["ds"] >= "1992-01-01"].reset_index(drop=True)
idx = pd.DatetimeIndex(beer["ds"], freq="QS-OCT")
dp_dummy = DeterministicProcess(index=idx, constant=True, order=1, seasonal=True, drop=True)
dp_fourier = DeterministicProcess(index=idx, constant=True, order=1,
                                  additional_terms=[Fourier(period=4, order=2)], drop=True)
for label, dp in [("season dummies", dp_dummy), ("Fourier K=2", dp_fourier)]:
    r = sm.OLS(beer["y"].to_numpy(), dp.in_sample()).fit()
    print(f"Beer, trend + {label}: AICc {aicc(r):.1f}, columns {list(dp.in_sample().columns)}")
# K = m/2 Fourier pairs give the same fit as m-1 season dummies.

# %% 7 Forecast with prediction intervals and a plot
# Scenario forecasts: the predictors are set to chosen paths, so the intervals are
# conditional on those paths and ignore predictor uncertainty.
H = 4
last = uc["ds"].iloc[-1]
future_ds = pd.date_range(last, periods=H + 1, freq="QS")[1:]
scenarios = {"Increase": {p: 0.0 for p in best}, "Decrease": {p: 0.0 for p in best}}
if "Income" in best:
    scenarios["Increase"]["Income"], scenarios["Decrease"]["Income"] = 1.0, -1.0
if "Savings" in best:
    scenarios["Increase"]["Savings"], scenarios["Decrease"]["Savings"] = 0.5, -0.5
if "Unemployment" in best:
    scenarios["Increase"]["Unemployment"], scenarios["Decrease"]["Unemployment"] = 0.0, 0.0
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(uc["ds"].iloc[-40:], uc["Consumption"].iloc[-40:], color="black")
for name, vals in scenarios.items():
    Xf = sm.add_constant(pd.DataFrame({p: [v] * H for p, v in vals.items()})[best], has_constant="add")
    f = predict_with_intervals(fit, Xf, name)
    ax.plot(future_ds, f[name], label=name)
    ax.fill_between(future_ds, f[f"{name}-lo-80"], f[f"{name}-hi-80"], alpha=0.2)
    print(name, f.round(2).to_dict("list"))
ax.legend()
ax.set_title("Consumption under two scenarios (80% intervals)")
fig.savefig(OUT / "regression_scenarios.png", dpi=120)
plt.close(fig)

# %% 8 What to report
# - The selected predictors and the selection table (AICc, CV, BIC), not p-values.
# - Residual checks: Ljung-Box with dof = number of coefficients, Breusch-Godfrey,
#   residuals against predictors and fitted values.
# - Ex-post accuracy labelled as ex-post; ex-ante accuracy if predictors must be forecast.
# - Scenario forecasts with their assumed predictor paths and intervals, stated as conditional.
# - That coefficients describe association, not cause.
print("Done. Outputs in", OUT)
