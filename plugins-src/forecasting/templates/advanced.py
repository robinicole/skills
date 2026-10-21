"""Advanced methods template: complex seasonality (MSTL, dynamic harmonic regression),
Prophet, vector autoregression, neural network autoregression, and bagged ETS.
Use each only as far as the book recommends: keep ETS or ARIMA in every comparison.

Book: FPP3 chapter 12 (R: https://otexts.com/fpp3/advanced-methods.html [unverified URL];
Python edition chapter 12 [unverified URL]).
Python: statsforecast (MSTL, AutoARIMA), prophet, statsmodels VAR, mlforecast with
scikit-learn MLPRegressor (Not from the book: NNAR has no direct Python equivalent).
Run: python advanced.py   (needs fpp_data.py and fc_checks.py in the same folder)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib",
                     "statsforecast": "statsforecast", "utilsforecast": "utilsforecast",
                     "statsmodels": "statsmodels", "pyreadr": "pyreadr",
                     "mlforecast": "mlforecast", "sklearn": "scikit-learn",
                     "coreforecast": "coreforecast"})
optional_missing = preflight({"prophet": "prophet"}, label="optional")   # Prophet is skipped if missing
if missing:
    raise SystemExit("Install the missing packages, then run again.")

import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import MSTL, AutoARIMA, AutoETS, SeasonalNaive
from statsmodels.tsa.deterministic import DeterministicProcess, Fourier
from utilsforecast.evaluation import evaluate
from utilsforecast.losses import mae, rmse

from fc_checks import out_dir, residual_check
from fpp_data import load, to_long

OUT = out_dir()
LEVELS = [80, 95]
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)


def test_scores(test: pd.DataFrame, fc: pd.DataFrame) -> pd.DataFrame:
    return evaluate(test[["unique_id", "ds", "y"]].merge(fc, on=["unique_id", "ds"]),
                    metrics=[mae, rmse])


# %% 1 Data
ve = load("vic_elec")
# Half-hourly demand, last 10 weeks of 2014: daily (48) and weekly (336) seasonality.
hh = to_long(ve[ve["Time"] >= "2014-10-23"], y="Demand", time="Time", keys=[])
hh = hh.assign(unique_id="Demand", y=hh["y"] / 1e3)        # GW
# Daily demand with daily maximum temperature, for Prophet.
daily = (ve.assign(ds=ve["Time"].dt.floor("D"))
         .groupby("ds").agg(y=("Demand", "sum"), temp=("Temperature", "max")).reset_index())
daily = daily.assign(unique_id="Demand", y=daily["y"] / 1e3)

# %% 2 Exploration needed for this method
fig, ax = plt.subplots(2, 1, figsize=(9, 5))
ax[0].plot(hh["ds"].iloc[-336 * 2:], hh["y"].iloc[-336 * 2:]); ax[0].set_title("Two weeks, half-hourly: daily and weekly cycles")
ax[1].scatter(daily["temp"], daily["y"], s=4); ax[1].set_title("Daily demand against max temperature: nonlinear")
fig.tight_layout(); fig.savefig(OUT / "advanced_explore.png", dpi=120); plt.close(fig)

# %% 3 Baselines
H_HH = 48 * 7
hh_train, hh_test = hh.iloc[:-H_HH], hh.iloc[-H_HH:]

# %% 4 Model fit
# Complex seasonality, option 1: MSTL with both periods, non-seasonal ARIMA on the
# seasonally adjusted series, seasonal parts forecast by seasonal naive.
sf = StatsForecast(models=[MSTL(season_length=[48, 336], trend_forecaster=AutoARIMA(), alias="MSTL_ARIMA"),
                           SeasonalNaive(season_length=336, alias="SNaive_week")], freq="30min")
fc_mstl = sf.forecast(df=hh_train, h=H_HH)
# Option 2: dynamic harmonic regression, one Fourier set per period, ARIMA errors.
idx = pd.DatetimeIndex(hh["ds"], freq="30min")
dp = DeterministicProcess(index=idx, constant=False,
                          additional_terms=[Fourier(period=48, order=10), Fourier(period=336, order=5)])
X = dp.in_sample().to_numpy()
dhr = AutoARIMA(season_length=1).fit(hh_train["y"].to_numpy(), X=X[:-H_HH])
fc_dhr = hh_test[["unique_id", "ds"]].assign(DHR=np.asarray(dhr.predict(h=H_HH, X=X[-H_HH:])["mean"]))
print("Half-hourly, last week held out:\n",
      test_scores(hh_test, fc_mstl.merge(fc_dhr, on=["unique_id", "ds"])).round(3))

# Prophet (daily demand with temperature and its square, weekly and yearly seasonality).
H_D = 28
d_train, d_test = daily.iloc[:-H_D], daily.iloc[-H_D:]
if not optional_missing:
    from prophet import Prophet
    pm = Prophet(weekly_seasonality=True, yearly_seasonality=True, daily_seasonality=False,
                 interval_width=0.8)
    pm.add_regressor("temp"); pm.add_regressor("temp2")
    pm.fit(d_train.assign(temp2=d_train["temp"] ** 2)[["ds", "y", "temp", "temp2"]])
    pf = pm.predict(d_test.assign(temp2=d_test["temp"] ** 2)[["ds", "temp", "temp2"]])
    fc_prophet = d_test[["unique_id", "ds"]].assign(Prophet=pf["yhat"].to_numpy())
    resid_p = d_train["y"].to_numpy() - pm.predict(d_train.assign(temp2=d_train["temp"] ** 2))["yhat"].to_numpy()
    print("Prophet residuals:", residual_check(resid_p, m=7, name="prophet"))
    # Comparison model: dynamic regression with Fourier terms and the same predictors.
    didx = pd.DatetimeIndex(daily["ds"], freq="D")
    ddp = DeterministicProcess(index=didx, constant=False,
                               additional_terms=[Fourier(period=7, order=3), Fourier(period=365.25, order=6)])
    DX = np.column_stack([ddp.in_sample().to_numpy(), daily["temp"], daily["temp"] ** 2])
    dyn = AutoARIMA(season_length=1).fit(d_train["y"].to_numpy(), X=DX[:-H_D])
    fc_dyn = d_test[["unique_id", "ds"]].assign(DynReg=np.asarray(dyn.predict(h=H_D, X=DX[-H_D:])["mean"]))
    print("Daily, last 28 days held out (actual temperatures, so ex-post):\n",
          test_scores(d_test, fc_prophet.merge(fc_dyn, on=["unique_id", "ds"])).round(3))

# Vector autoregression: consumption and income, lag order by BIC.
from statsmodels.tsa.api import VAR
uc = load("us_change").set_index("Quarter")[["Consumption", "Income"]]
uc.index = pd.DatetimeIndex(uc.index, freq="QS-OCT")
var_sel = VAR(uc).select_order(maxlags=8)
p_bic = max(1, int(var_sel.selected_orders["bic"]))
print("VAR lag order by information criterion:", var_sel.selected_orders, "using BIC:", p_bic)
var = VAR(uc).fit(p_bic)
for i, col in enumerate(uc.columns):
    print(f"VAR({p_bic}) residuals, {col}:", residual_check(var.resid.iloc[:, i], m=4, dof=0,
                                                           name=f"var_{col}", plot=False))

# Neural network autoregression, approximated (Not from the book in Python):
# p lags from the best linear AR by AIC, one hidden layer of k = (p + 1) / 2 units
# (non-seasonal data, so P = 0), 20 networks from random starts averaged.
from mlforecast import MLForecast
from mlforecast.target_transforms import LocalStandardScaler
from sklearn.neural_network import MLPRegressor
from statsmodels.tsa.ar_model import ar_select_order
lynx = to_long(load("pelt"), y="Lynx", name="pelt")
p_ar = max(ar_select_order(lynx["y"].to_numpy(), maxlag=12, ic="aic").ar_lags or [1])
k = int(np.ceil((p_ar + 1) / 2))
nets = {f"nn{s}": MLPRegressor(hidden_layer_sizes=(k,), max_iter=5000, random_state=s) for s in range(20)}
H_L = 10
l_train, l_test = lynx.iloc[:-H_L], lynx.iloc[-H_L:]
mlf = MLForecast(models=nets, freq="YS", lags=list(range(1, p_ar + 1)),
                 target_transforms=[LocalStandardScaler()])
mlf.fit(l_train)
nn = mlf.predict(h=H_L)
nn["NNAR"] = nn[list(nets)].mean(axis=1)
ets_l = StatsForecast(models=[AutoETS(), AutoARIMA()], freq="YS").forecast(df=l_train, h=H_L)
print(f"NNAR({p_ar},{k}) approximation on lynx, last {H_L} years held out:\n",
      test_scores(l_test, nn[["unique_id", "ds", "NNAR"]].merge(ets_l, on=["unique_id", "ds"])).round(1))
print("NNAR prediction intervals need simulated paths with resampled errors; none are produced here.")

# Bagged ETS: Box-Cox, STL, moving-block bootstrap of the remainder, back-transform,
# fit ETS to each synthetic series, average the point forecasts.
from coreforecast.scalers import boxcox, boxcox_lambda, inv_boxcox
from statsmodels.tsa.seasonal import STL
cement = to_long(load("aus_production"), y="Cement", name="aus_production")
cement = cement[cement["ds"] >= "1988-01-01"].reset_index(drop=True)
H_C, B, block = 8, 30, 8
c_train, c_test = cement.iloc[:-H_C], cement.iloc[-H_C:]
lam = boxcox_lambda(c_train["y"].to_numpy(), method="guerrero", season_length=4)
yt = boxcox(c_train["y"].to_numpy(), lam)
dec = STL(yt, period=4, robust=True).fit()
rng = np.random.default_rng(0)
boot = []
for b in range(B):
    starts = rng.integers(0, len(yt) - block, size=len(yt) // block + 2)
    rem = np.concatenate([dec.resid[s:s + block] for s in starts])[: len(yt)]
    boot.append(c_train.assign(unique_id=f"b{b}", y=inv_boxcox(dec.trend + dec.seasonal + rem, lam)))
boot = pd.concat(boot, ignore_index=True)
fb = StatsForecast(models=[AutoETS(season_length=4)], freq="QS").forecast(df=boot, h=H_C)
bagged = fb.groupby("ds", as_index=False)["AutoETS"].mean().rename(columns={"AutoETS": "BaggedETS"})
plain = StatsForecast(models=[AutoETS(season_length=4)], freq="QS").forecast(df=c_train, h=H_C)
print(f"Cement, bagged ETS from {B} bootstrapped series versus ETS:\n",
      test_scores(c_test, plain.merge(bagged.assign(unique_id="Cement"), on=["unique_id", "ds"])).round(1))

# %% 5 Diagnostics
# Covered above per model: Prophet residuals, VAR residuals per equation. Prophet's
# residuals usually stay autocorrelated, so its intervals are not trustworthy.

# %% 6 Evaluation with time series cross-validation
# Each comparison above uses one held-out block to keep the run short. Before a
# decision, repeat over several forecast origins (StatsForecast.cross_validation or
# fc_checks.rolling_origin) as in baselines.py.

# %% 7 Forecast with prediction intervals and a plot
var_fc = var.forecast_interval(uc.values[-p_bic:], steps=8, alpha=0.2)
f_ds = pd.date_range(uc.index[-1], periods=9, freq="QS")[1:]
fig, ax = plt.subplots(2, 1, figsize=(8, 6))
ax[0].plot(hh_test["ds"], hh_test["y"], color="black", lw=0.8)
ax[0].plot(fc_mstl["ds"], fc_mstl["MSTL_ARIMA"], label="MSTL"); ax[0].plot(fc_dhr["ds"], fc_dhr["DHR"], label="DHR")
ax[0].legend(); ax[0].set_title("Half-hourly demand, held-out week")
ax[1].plot(uc.index[-40:], uc["Consumption"].iloc[-40:], color="black")
ax[1].plot(f_ds, var_fc[0][:, 0], label="VAR")
ax[1].fill_between(f_ds, var_fc[1][:, 0], var_fc[2][:, 0], alpha=0.2, label="80%")
ax[1].legend(); ax[1].set_title("Consumption, VAR forecast")
fig.tight_layout(); fig.savefig(OUT / "advanced_forecasts.png", dpi=120); plt.close(fig)

# %% 8 What to report
# - Why a standard ETS or ARIMA was not enough (the specific feature it missed).
# - The advanced model against ETS/ARIMA and a benchmark on held-out data.
# - Residual checks; for Prophet, say if residuals stay autocorrelated.
# - For VAR: the lag order and the criterion; for NNAR: p, k and how intervals were made.
# - For bagging: number of bootstrap series and block size.
print("Done. Outputs in", OUT)
