"""ETS template: exponential smoothing state space models, selection by AICc,
damped trend, components, prediction intervals, cross-validation against benchmarks.

Book: FPP3 chapter 8 (R: https://otexts.com/fpp3/expsmooth.html [unverified URL];
Python edition chapter 8 [unverified URL]).
Python: statsforecast AutoETS (model string Error, Trend, Season; "Z" = choose).
Run: python ets.py   (needs fpp_data.py and fc_checks.py in the same folder)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib",
                     "statsforecast": "statsforecast", "utilsforecast": "utilsforecast",
                     "statsmodels": "statsmodels", "pyreadr": "pyreadr"})
if missing:
    raise SystemExit("Install the missing packages, then run again.")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoETS, Naive, SeasonalNaive

from fc_checks import out_dir, residual_check, score_cv, skill
from fpp_data import freq, load, to_long

OUT = out_dir()
LEVELS = [80, 95]
PAR_NAMES = ["alpha", "beta", "gamma", "phi"]


def ets_report(model) -> dict:
    """Method, smoothing parameters and AICc of a fitted statsforecast ETS model."""
    md = model.model_
    par = dict(zip(PAR_NAMES, md["par"][:4]))
    return {"method": md["method"], "aicc": round(float(md["aicc"]), 2),
            **{k: round(float(v), 4) for k, v in par.items() if not np.isnan(v)}}


# %% 1 Data
# Non-seasonal: Algerian exports (% of GDP), yearly.
ge = load("global_economy")
alg = to_long(ge[ge["Country"] == "Algeria"], y="Exports", name="global_economy")
# Seasonal: Australian gas production, quarterly; seasonal swings grow with the level.
gas = to_long(load("aus_production"), y="Gas", name="aus_production")

# %% 2 Exploration needed for this method
# Trend? Seasonality? Additive or multiplicative (does the swing grow with the level)?
# Multiplicative components need strictly positive data.
fig, ax = plt.subplots(2, 1, figsize=(8, 5))
ax[0].plot(alg["ds"], alg["y"]); ax[0].set_title("Algeria exports: no trend, no season")
ax[1].plot(gas["ds"], gas["y"]); ax[1].set_title("Gas: trend, season growing with level")
fig.tight_layout(); fig.savefig(OUT / "ets_timeplots.png", dpi=120); plt.close(fig)
print("Gas strictly positive:", bool((gas["y"] > 0).all()))

# %% 3 Baselines
alg_base = [Naive()]
gas_base = [SeasonalNaive(season_length=4)]

# %% 4 Model fit
# Simple exponential smoothing, ETS(A,N,N), on the non-seasonal series.
ses = AutoETS(model="ANN").fit(alg["y"].to_numpy())
print("Algeria:", ets_report(ses))
# Candidate ETS models on gas, compared by AICc (valid inside the ETS family only).
# Additive error with multiplicative season (A,N,M / A,A,M / A,Ad,M) is unstable: never request it.
candidates = {"ETS(A,A,A)": dict(model="AAA", damped=False),
              "ETS(M,A,M)": dict(model="MAM", damped=False),
              "ETS(M,Ad,M)": dict(model="MAM", damped=True),
              "ETS auto": dict(model="ZZZ")}
gas_y = gas["y"].to_numpy()
for name, kw in candidates.items():
    print(f"Gas {name}:", ets_report(AutoETS(season_length=4, **kw).fit(gas_y)))
auto = AutoETS(season_length=4).fit(gas_y)

# %% 5 Diagnostics
# Innovation residuals (relative errors for multiplicative error models) should be
# white noise. ETS has no ARMA coefficients, so dof = 0.
diag = residual_check(auto.model_["residuals"], m=4, dof=0, name="ETS_gas")
print("Residual check:", diag)
# Components: level, slope and season states over time. Check that they make sense.
states = np.asarray(auto.model_["states"])
fig, axes = plt.subplots(states.shape[1] if states.shape[1] < 4 else 3, 1, figsize=(8, 6))
for i, ax in enumerate(np.atleast_1d(axes)):
    ax.plot(states[:, i]); ax.set_title(["level", "slope", "first seasonal state"][i])
fig.tight_layout(); fig.savefig(OUT / "ets_components.png", dpi=120); plt.close(fig)

# %% 6 Evaluation with time series cross-validation
# AICc cannot compare ETS with ARIMA or with benchmarks: cross-validation decides.
sf = StatsForecast(models=[AutoETS(season_length=4, alias="ETS_auto"),
                           AutoETS(season_length=4, model="MAM", damped=True, alias="ETS_MAdM"),
                           *gas_base], freq=freq("aus_production"))
cv = sf.cross_validation(df=gas, h=8, n_windows=10, step_size=2, level=LEVELS)
scores = score_cv(cv, train_df=gas, m=4, levels=LEVELS)
print("Gas, pooled CV accuracy:\n",
      score_cv(cv, train_df=gas, m=4, levels=LEVELS, by_h=False).set_index("metric").round(3))
print("MASE skill against seasonal naive, per forecast horizon:\n",
      skill(scores, "mase", "SeasonalNaive")[["h", "ETS_auto", "ETS_MAdM"]].round(3))

sf_alg = StatsForecast(models=[AutoETS(model="ANN", alias="SES"), *alg_base], freq=freq("global_economy"))
cv_alg = sf_alg.cross_validation(df=alg, h=5, n_windows=10, step_size=1, level=LEVELS)
print("Algeria, pooled CV accuracy:\n",
      score_cv(cv_alg, train_df=alg, m=1, levels=LEVELS, by_h=False).set_index("metric").round(3))

# %% 7 Forecast with prediction intervals and a plot
fc = sf.forecast(df=gas, h=12, level=LEVELS)
fig, ax = plt.subplots(figsize=(8, 3))
recent = gas[gas["ds"] >= "1995-01-01"]
ax.plot(recent["ds"], recent["y"], color="black")
ax.plot(fc["ds"], fc["ETS_auto"], label="ETS auto")
ax.fill_between(fc["ds"], fc["ETS_auto-lo-95"], fc["ETS_auto-hi-95"], alpha=0.2, label="95%")
ax.fill_between(fc["ds"], fc["ETS_auto-lo-80"], fc["ETS_auto-hi-80"], alpha=0.3, label="80%")
ax.legend(); ax.set_title("Gas production forecast")
fig.savefig(OUT / "ets_forecast.png", dpi=120); plt.close(fig)
fc.to_csv(OUT / "ets_forecast.csv", index=False)

# %% 8 What to report
# - The ETS form chosen (for example ETS(M,Ad,M)) and its parameters, read in words:
#   alpha near 1 = level follows recent data; gamma near 0 = stable seasonal pattern.
# - Why the form fits: error, trend and season choices tied to the time plot.
# - Residual check results (Ljung-Box lag and p-value, mean).
# - Cross-validated accuracy per forecast horizon against seasonal naive.
# - The forecast with 80% and 95% prediction intervals.
print("Done. Outputs in", OUT)
