"""Dynamic regression template: regression with ARIMA errors, ex-ante versus ex-post
evaluation, stochastic versus deterministic trend, dynamic harmonic regression
(Fourier terms) and lagged predictors.

Book: FPP3 chapter 10 (R: https://otexts.com/fpp3/dynamic.html [unverified URL];
Python edition chapter 10 [unverified URL]).
Python: statsforecast AutoARIMA / ARIMA with predictors passed as X.
Run: python dynamic_regression.py   (needs fpp_data.py and fc_checks.py)
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
from statsforecast.arima import arima_string
from statsforecast.models import ARIMA, AutoARIMA, Naive
from statsmodels.tsa.deterministic import DeterministicProcess, Fourier

from fc_checks import out_dir, residual_check, rolling_origin, score_cv
from fpp_data import load, to_long

OUT = out_dir()
LEVELS = [80, 95]


def as_frame(pred: dict, name: str) -> pd.DataFrame:
    """Turn a statsforecast model .predict() dict into named columns."""
    return pd.DataFrame({(name if k == "mean" else f"{name}-{k}"): np.asarray(v) for k, v in pred.items()})


def describe(model) -> str:
    md = model.model_
    coef = {k: round(float(v), 3) for k, v in md["coef"].items()}
    return f"{arima_string(md).strip()} AICc={md['aicc']:.1f} coef={coef}"


# %% 1 Data
uc = load("us_change")
y, x = uc["Consumption"].to_numpy(), uc[["Income"]].to_numpy()
cons = to_long(uc, y="Consumption", name="us_change").assign(Income=uc["Income"].to_numpy())

# %% 2 Exploration needed for this method
# Every variable must be stationary, or be differenced the same way as the target.
from statsforecast.arima import ndiffs
print("Differences needed: Consumption", ndiffs(y, test="kpss"), "Income", ndiffs(x[:, 0], test="kpss"))

# %% 3 Baselines
naive = Naive()

# %% 4 Model fit
# Regression with ARIMA errors: the error term is ARIMA, not white noise.
fit = AutoARIMA().fit(y, X=x)
print("Consumption ~ Income with ARIMA errors:", describe(fit))
coef = fit.model_["coef"]
reg_resid = y - coef.get("intercept", 0.0) - coef["ex_1"] * x[:, 0]   # regression residuals
innov = fit.model_["residuals"]                                         # innovation residuals

# %% 5 Diagnostics
# Only the innovation residuals should be white noise. The regression residuals keep
# the autocorrelation that the ARIMA error absorbs.
p, q, P, Q, *_ = fit.model_["arma"]
print("Innovation residuals:", residual_check(innov, m=4, dof=p + q + P + Q, name="dynreg_innov"))
fig, ax = plt.subplots(2, 1, figsize=(8, 4))
ax[0].plot(reg_resid); ax[0].set_title("Regression residuals (autocorrelated)")
ax[1].plot(innov); ax[1].set_title("ARIMA (innovation) residuals (should be white noise)")
fig.tight_layout(); fig.savefig(OUT / "dynreg_residuals.png", dpi=120); plt.close(fig)

# %% 6 Evaluation with time series cross-validation
# Ex-post uses the actual future Income: model error only. Ex-ante forecasts Income
# first, as a real forecast must. Report ex-ante as the honest accuracy.
def ex_post(train, future):
    m = AutoARIMA().fit(train["y"].to_numpy(), X=train[["Income"]].to_numpy())
    return as_frame(m.predict(h=len(future), X=future[["Income"]].to_numpy(), level=LEVELS), "ExPost")


def ex_ante(train, future):
    inc = AutoARIMA().fit(train["Income"].to_numpy()).predict(h=len(future))["mean"]
    m = AutoARIMA().fit(train["y"].to_numpy(), X=train[["Income"]].to_numpy())
    out = as_frame(m.predict(h=len(future), X=inc.reshape(-1, 1), level=LEVELS), "ExAnte")
    nv = Naive().fit(train["y"].to_numpy()).predict(h=len(future), level=LEVELS)
    return pd.concat([out, as_frame(nv, "Naive")], axis=1)


cv_post = rolling_origin(cons, h=4, n_windows=20, step_size=1, fit_forecast=ex_post)
cv_ante = rolling_origin(cons, h=4, n_windows=20, step_size=1, fit_forecast=ex_ante)
cv = cv_ante.merge(cv_post.drop(columns="y"), on=["unique_id", "ds", "cutoff"])
print("Ex-ante versus ex-post accuracy:\n",
      score_cv(cv, train_df=cons[["unique_id", "ds", "y"]], m=1, levels=LEVELS, by_h=False)
      .set_index("metric").round(3))
print("Ex-ante intervals ignore the error in the Income forecast, so their coverage reads too well.")

# Stochastic versus deterministic trend (Australian air passengers, yearly).
air = load("aus_airpassengers")
ya = air["Passengers"].to_numpy()
t = np.arange(1, len(ya) + 1, dtype=float).reshape(-1, 1)
det = AutoARIMA(d=0, max_p=1).fit(ya, X=t)  # max_p=1 as in the Python edition: avoids a non-invertible ARIMA(2,0,1)
sto = AutoARIMA(d=1).fit(ya)
H = 20
t_f = np.arange(len(ya) + 1, len(ya) + H + 1, dtype=float).reshape(-1, 1)
f_det = det.predict(h=H, X=t_f, level=[95]); f_sto = sto.predict(h=H, level=[95])
print("Deterministic trend:", describe(det))
print("Stochastic trend:   ", describe(sto))
print(f"95% interval width at h={H}: deterministic {np.asarray(f_det['hi-95'])[-1] - np.asarray(f_det['lo-95'])[-1]:.1f}, "
      f"stochastic {np.asarray(f_sto['hi-95'])[-1] - np.asarray(f_sto['lo-95'])[-1]:.1f}. "
      "The stochastic trend admits that the slope can change.")

# Dynamic harmonic regression: weekly US gasoline, period 52.18, Fourier terms
# with ARIMA errors. Choose K by AICc with the differencing order held fixed.
gas = to_long(load("us_gasoline"), y="Barrels", name="us_gasoline")
gas = gas[gas["ds"] <= "2004-12-31"].reset_index(drop=True)      # the book uses 1991-2004
idx = pd.DatetimeIndex(gas["ds"], freq="W-MON")
yg = gas["y"].to_numpy()


def fourier_dp(K):
    return DeterministicProcess(index=idx, constant=False,
                                additional_terms=[Fourier(period=365.25 / 7, order=K)])


d_fixed = AutoARIMA(season_length=1).fit(yg, X=fourier_dp(1).in_sample().to_numpy()).model_["arma"][5]
dhr = {}
for K in range(1, 9):
    dhr[K] = AutoARIMA(season_length=1, d=d_fixed).fit(yg, X=fourier_dp(K).in_sample().to_numpy())
best_K = min(dhr, key=lambda k: dhr[k].model_["aicc"])
print("DHR AICc by K:", {k: round(float(v.model_["aicc"]), 1) for k, v in dhr.items()}, "best K =", best_K)
if best_K == max(dhr):
    print("Best K is at the edge of the range searched. Extend the range, or cap K by hand:"
          " each pair adds two parameters, and a seasonal shape needs few pairs to look smooth.")
print("Chosen:", arima_string(dhr[best_K].model_).strip())

# Lagged predictors: insurance quotes on TV advertising at lags 0..3. Drop the first
# 3 rows for every candidate so AICc values use the same data.
ins = load("insurance")
for k in range(1, 4):
    ins[f"TV_lag{k}"] = ins["TVadverts"].shift(k)
ins_fit = ins.iloc[3:].reset_index(drop=True)
lag_sets = {0: ["TVadverts"], 1: ["TVadverts", "TV_lag1"],
            2: ["TVadverts", "TV_lag1", "TV_lag2"], 3: ["TVadverts", "TV_lag1", "TV_lag2", "TV_lag3"]}
lag_fits = {k: AutoARIMA(d=0).fit(ins_fit["Quotes"].to_numpy(), X=ins_fit[c].to_numpy())
            for k, c in lag_sets.items()}
best_lag = min(lag_fits, key=lambda k: lag_fits[k].model_["aicc"])
print("Lagged predictors AICc:", {k: round(float(v.model_["aicc"]), 2) for k, v in lag_fits.items()},
      "best number of lags =", best_lag)
# Refit the chosen form on all usable rows (only the first `best_lag` rows are lost).
ins_all = ins.iloc[best_lag:].reset_index(drop=True)
lag_model = AutoARIMA(d=0).fit(ins_all["Quotes"].to_numpy(), X=ins_all[lag_sets[best_lag]].to_numpy())
print("Refit on all rows:", describe(lag_model))

# %% 7 Forecast with prediction intervals and a plot
# Consumption, 8 quarters ahead, with Income set to its historical mean (a scenario).
H = 8
x_future = np.full((H, 1), uc["Income"].mean())
f = as_frame(fit.predict(h=H, X=x_future, level=LEVELS), "DynReg")
f_ds = pd.date_range(uc["Quarter"].iloc[-1], periods=H + 1, freq="QS")[1:]
fig, ax = plt.subplots(2, 1, figsize=(8, 6))
ax[0].plot(uc["Quarter"].iloc[-40:], y[-40:], color="black")
ax[0].plot(f_ds, f["DynReg"]); ax[0].fill_between(f_ds, f["DynReg-lo-95"], f["DynReg-hi-95"], alpha=0.2)
ax[0].set_title("Consumption, Income at its mean (intervals conditional on that path)")
Xf = fourier_dp(best_K).out_of_sample(steps=52).to_numpy()
fg = as_frame(dhr[best_K].predict(h=52, X=Xf, level=LEVELS), "DHR")
gds = pd.date_range(gas["ds"].iloc[-1], periods=53, freq="W-MON")[1:]
ax[1].plot(gas["ds"].iloc[-260:], yg[-260:], color="black")
ax[1].plot(gds, fg["DHR"]); ax[1].fill_between(gds, fg["DHR-lo-95"], fg["DHR-hi-95"], alpha=0.2)
ax[1].set_title(f"US gasoline, dynamic harmonic regression K={best_K}")
fig.tight_layout(); fig.savefig(OUT / "dynreg_forecasts.png", dpi=120); plt.close(fig)

# %% 8 What to report
# - The regression coefficients and the ARIMA error order.
# - Innovation residual check (Ljung-Box, dof = ARMA coefficients); regression residuals shown separately.
# - Ex-ante accuracy as the headline; ex-post labelled as model error only.
# - How future predictor values were obtained (forecast, known calendar terms, scenario),
#   and that intervals ignore predictor uncertainty.
# - For DHR: K chosen by AICc with d fixed; for lags: AICc on identical rows.
print("Done. Outputs in", OUT)
