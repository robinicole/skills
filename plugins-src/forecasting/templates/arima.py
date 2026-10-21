"""ARIMA template: stationarity, differencing, unit root tests, ACF/PACF reading,
automatic and seasonal ARIMA, residual checks, ARIMA versus ETS by cross-validation.

Book: FPP3 chapter 9 (R: https://otexts.com/fpp3/arima.html [unverified URL];
Python edition chapter 9 [unverified URL]).
Python: statsforecast AutoARIMA / ARIMA, statsmodels KPSS and ACF/PACF.
Run: python arima.py   (needs fpp_data.py and fc_checks.py in the same folder)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib",
                     "statsforecast": "statsforecast", "utilsforecast": "utilsforecast",
                     "statsmodels": "statsmodels", "pyreadr": "pyreadr",
                     "coreforecast": "coreforecast"})
if missing:
    raise SystemExit("Install the missing packages, then run again.")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from coreforecast.scalers import boxcox, boxcox_lambda
from statsforecast import StatsForecast
from statsforecast.arima import arima_string, ndiffs, nsdiffs
from statsforecast.models import ARIMA, AutoARIMA, AutoETS, Naive, SeasonalNaive
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import kpss

from fc_checks import out_dir, residual_check, score_cv, skill
from fpp_data import freq, load, to_long

OUT = out_dir()
LEVELS = [80, 95]


def arima_report(model) -> dict:
    md = model.model_
    p, q, P, Q, m, d, D = md["arma"]
    return {"model": arima_string(md).strip(), "aicc": round(float(md["aicc"]), 2),
            "coef": {k: round(float(v), 3) for k, v in md["coef"].items()},
            "dof": p + q + P + Q, "d": d, "D": D}


def tsdisplay(y, title, fname, lags=36):
    fig, ax = plt.subplots(3, 1, figsize=(8, 8))
    ax[0].plot(y); ax[0].set_title(title)
    plot_acf(y, ax=ax[1], lags=lags, zero=False)
    plot_pacf(y, ax=ax[2], lags=lags, zero=False, method="ywm")
    fig.tight_layout(); fig.savefig(OUT / fname, dpi=120); plt.close(fig)


# %% 1 Data
# Non-seasonal: Egyptian exports (% of GDP), yearly.
ge = load("global_economy")
egy = to_long(ge[ge["Country"] == "Egypt, Arab Rep."], y="Exports", name="global_economy")
# Seasonal: monthly cost of corticosteroid drug scripts (ATC2 = H02), summed, in $ millions.
pbs = load("PBS")
h02 = (pbs[pbs["ATC2"] == "H02"].groupby("Month", as_index=False)["Cost"].sum()
       .assign(Cost=lambda d: d["Cost"] / 1e6))
h02 = to_long(h02, y="Cost", time="Month", keys=[]).assign(unique_id="H02")

# %% 2 Exploration needed for this method
# Stabilise the variance first (log or Box-Cox), then difference until stationary:
# seasonal difference first, then a first difference only if still needed.
lam = boxcox_lambda(h02["y"].to_numpy(), method="guerrero", season_length=12)
print(f"H02 Guerrero lambda {lam:.2f}; the book-style choice is a log (lambda 0) when it is near 0.")
y_log = np.log(h02["y"].to_numpy())
D = nsdiffs(y_log, period=12)
y_sd = y_log[12:] - y_log[:-12] if D else y_log
d = ndiffs(y_sd, test="kpss")
print(f"H02 log scale: seasonal differences D = {D}, then first differences d = {d}")
stat, p, *_ = kpss(y_sd, regression="c", nlags="auto")
print(f"KPSS on the seasonally differenced log series: stat {stat:.3f}, p {p:.3f} "
      "(small p means not stationary; statsmodels caps p between 0.01 and 0.1)")
tsdisplay(y_sd, "log H02, seasonally differenced", "arima_h02_tsdisplay.png")
print(f"Egypt exports: d = {ndiffs(egy['y'].to_numpy(), test='kpss')}")
tsdisplay(egy["y"].to_numpy(), "Egypt exports", "arima_egypt_tsdisplay.png", lags=20)
# Reading the plots: an AR(p) has a PACF that cuts off after lag p and a decaying ACF;
# an MA(q) is the reverse; spikes at lag 12, 24 point to seasonal P (PACF) or Q (ACF).

# %% 3 Baselines
base_egy = [Naive()]
base_h02 = [SeasonalNaive(season_length=12)]

# %% 4 Model fit
# Automatic search (stepwise), a wider search, and a hand-picked model from the plots.
y_egy = egy["y"].to_numpy()
for label, mdl in [("auto stepwise", AutoARIMA()),
                   ("auto full search", AutoARIMA(stepwise=False, approximation=False)),
                   ("by hand AR(4)", ARIMA(order=(4, 0, 0), include_mean=True))]:
    print("Egypt", label, arima_report(mdl.fit(y_egy)))
# H02 on the log scale. AICc compares models only when d and D are the same.
h02_log = h02.assign(y=np.log(h02["y"]))
cands = {"auto": AutoARIMA(season_length=12),
         "full search": AutoARIMA(season_length=12, stepwise=False, approximation=False),
         "(3,0,1)(0,1,2)": ARIMA(order=(3, 0, 1), seasonal_order=(0, 1, 2), season_length=12)}
fits = {k: v.fit(h02_log["y"].to_numpy()) for k, v in cands.items()}
for k, f in fits.items():
    print("H02", k, arima_report(f))

# %% 5 Diagnostics
# Ljung-Box on the residuals with dof = p + q + P + Q. Failing means the model
# missed structure: try another order or let a wider search run.
# AICc ranks models only inside one (d, D) group; across groups, cross-validation decides.
groups = {}
for k, f in fits.items():
    r = arima_report(f)
    groups.setdefault((r["d"], r["D"]), []).append(k)
for (dd, DD), names in groups.items():
    best_name = min(names, key=lambda k: fits[k].model_["aicc"])
    rep = arima_report(fits[best_name])
    diag = residual_check(fits[best_name].model_["residuals"], m=12, dof=rep["dof"],
                          name=f"ARIMA_h02_d{dd}D{DD}")
    print(f"d={dd}, D={DD}: best by AICc is {rep['model']}; residual check:", diag)

# %% 6 Evaluation with time series cross-validation
# ARIMA against ETS and seasonal naive. Information criteria cannot compare
# ARIMA and ETS: their likelihoods differ. Cross-validation decides.
# Fit on the log scale, then back-transform (exp gives the median).
sf = StatsForecast(models=[AutoARIMA(season_length=12, alias="ARIMA"),
                           AutoETS(season_length=12, alias="ETS"), *base_h02],
                   freq=freq("PBS"))
cv_log = sf.cross_validation(df=h02_log, h=12, n_windows=12, step_size=1, level=LEVELS)
cv = cv_log.copy()
value_cols = [c for c in cv.columns if c not in ("unique_id", "ds", "cutoff")]
cv[value_cols] = np.exp(cv[value_cols])
scores = score_cv(cv, train_df=h02, m=12, levels=LEVELS)
print("H02 pooled CV accuracy (original scale):\n",
      score_cv(cv, train_df=h02, m=12, levels=LEVELS, by_h=False).set_index("metric").round(3))
print("RMSSE skill against seasonal naive, per forecast horizon:\n",
      skill(scores, "rmsse", "SeasonalNaive")[["h", "ARIMA", "ETS"]].round(3))

# %% 7 Forecast with prediction intervals and a plot
fc = sf.forecast(df=h02_log, h=24, level=LEVELS)
cols = [c for c in fc.columns if c not in ("unique_id", "ds")]
fc[cols] = np.exp(fc[cols])        # back-transform: point = median, intervals exact
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(h02["ds"], h02["y"], color="black")
ax.plot(fc["ds"], fc["ARIMA"], label="ARIMA")
ax.fill_between(fc["ds"], fc["ARIMA-lo-95"], fc["ARIMA-hi-95"], alpha=0.2, label="95%")
ax.fill_between(fc["ds"], fc["ARIMA-lo-80"], fc["ARIMA-hi-80"], alpha=0.3, label="80%")
ax.legend(); ax.set_title("H02 cost ($m), ARIMA on log scale")
fig.savefig(OUT / "arima_forecast.png", dpi=120); plt.close(fig)
fc.to_csv(OUT / "arima_forecast.csv", index=False)

# %% 8 What to report
# - The transformation, D and d with the tests that chose them (seasonal strength, KPSS).
# - The selected ARIMA(p,d,q)(P,D,Q)m, its coefficients and AICc, and the
#   candidates compared (same d and D only).
# - Ljung-Box with dof = p + q + P + Q.
# - ARIMA versus ETS versus seasonal naive by cross-validation, per forecast horizon.
# - Forecast with intervals; after a log, the point is a median unless bias-adjusted.
print("Done. Outputs in", OUT)
