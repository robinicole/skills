"""Practical issues template: weekly data, intermittent counts, bounded forecasts,
forecast combinations, prediction intervals for aggregates, backcasting, missing
values and outliers.

Book: FPP3 chapter 13 (R: https://otexts.com/fpp3/practical.html [unverified URL];
Python edition chapter 13 [unverified URL]).
Python: statsforecast (Croston family, MSTL, ETS, ARIMA), statsmodels (ETSModel
simulation, SARIMAX for gaps, STL for outliers).
Run: python practical.py   (needs fpp_data.py and fc_checks.py in the same folder)
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
from statsforecast.models import (MSTL, TSB, AutoARIMA, AutoETS, CrostonClassic,
                                  CrostonSBA, HistoricAverage, Naive, RandomWalkWithDrift,
                                  SeasonalNaive)

from fc_checks import out_dir, score_cv
from fpp_data import load, to_long

OUT = out_dir()
LEVELS = [80, 95]

# %% 1 Data
pbs = load("PBS")
v07 = pbs[(pbs["Concession"] == "General") & (pbs["Type"] == "Co-payments") & (pbs["ATC2"] == "V07")]
v07 = to_long(v07, y="Scripts", time="Month", keys=[]).assign(unique_id="V07")
eggs = to_long(load("prices").dropna(subset=["eggs"]), y="eggs", name="prices")
retail = load("aus_retail")
cafe = to_long(retail[(retail["State"] == "Victoria") &
                      (retail["Industry"] == "Cafes, restaurants and takeaway food services")],
               y="Turnover", name="aus_retail")
cafe_log = cafe.assign(y=np.log(cafe["y"]))

# %% 2 Exploration needed for this method
print(f"V07: {len(v07)} months, share of zero months {(v07['y'] == 0).mean():.2f}, "
      f"mean {v07['y'].mean():.2f}. Small counts with many zeros: intermittent demand.")

# %% 3 Baselines
# Intermittent demand: Croston variants against naive and mean. Score with MAE or
# RMSE; MAPE is undefined at zero.
sf_int = StatsForecast(models=[CrostonClassic(), CrostonSBA(), TSB(alpha_d=0.2, alpha_p=0.2),
                               Naive(), HistoricAverage()], freq="MS")

# %% 4 Model fit
cv_int = sf_int.cross_validation(df=v07, h=6, n_windows=12, step_size=3)
from utilsforecast.evaluation import evaluate
from utilsforecast.losses import mae, rmse
res_int = evaluate(cv_int, metrics=[mae, rmse]).groupby("metric").mean(numeric_only=True)
print("Intermittent demand, cross-validated:\n", res_int.round(3))
print("Croston forecasts are a demand rate per month, not a count to expect in any month.")

# Bounded forecasts: egg prices kept between a = 50 and b = 400 with a scaled logit.
a, b = 50.0, 400.0
z = eggs.assign(y=np.log((eggs["y"] - a) / (b - eggs["y"])))
fz = StatsForecast(models=[RandomWalkWithDrift()], freq="YS").forecast(df=z, h=50, level=LEVELS)


def from_logit(v):
    return (b - a) * np.exp(v) / (1 + np.exp(v)) + a


bounded = fz.copy()
cols = [c for c in fz.columns if c.startswith("RWD")]
bounded[cols] = from_logit(fz[cols].to_numpy())
print("Eggs, bounded drift forecast, last step:",
      bounded[["RWD", "RWD-lo-95", "RWD-hi-95"]].iloc[-1].round(1).to_dict(),
      "(point is a median; every value stays inside 50 to 400)")

# Combinations: equal-weight mean of ETS, ARIMA and STL+ETS on log cafe turnover.
sf_comb = StatsForecast(models=[AutoETS(season_length=12, alias="ETS"),
                                AutoARIMA(season_length=12, alias="ARIMA"),
                                MSTL(season_length=12, trend_forecaster=AutoETS(model="ZZN"), alias="STL_ETS"),
                                SeasonalNaive(season_length=12)], freq="MS", n_jobs=-1)

# %% 5 Diagnostics
# Outliers: robust STL remainder beyond 3 IQR. Replace only values you believe are
# errors or will not recur; otherwise keep them (or add a dummy in a regression).
from statsmodels.tsa.seasonal import STL
stl = STL(cafe_log["y"].to_numpy(), period=12, seasonal=13, robust=True).fit()
q1, q3 = np.percentile(stl.resid, [25, 75])
flag = (stl.resid < q1 - 3 * (q3 - q1)) | (stl.resid > q3 + 3 * (q3 - q1))
print("Outlier candidates:", cafe.loc[flag, "ds"].dt.strftime("%Y-%m").tolist())

# Missing values: ask first whether a gap carries information. If it is random,
# a state space model handles it. SARIMAX accepts NaN and the Kalman smoother fills it.
from statsmodels.tsa.statespace.sarimax import SARIMAX
gappy = cafe_log["y"].to_numpy().copy()
gappy[[200, 201, 350]] = np.nan                  # gaps made for the demonstration
sar = SARIMAX(gappy, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
print("Interpolated values at the gaps:", np.exp(sar.predict()[[200, 201, 350]]).round(1),
      "true:", np.exp(cafe_log["y"].to_numpy()[[200, 201, 350]]).round(1))

# %% 6 Evaluation with time series cross-validation
cv = sf_comb.cross_validation(df=cafe_log, h=12, n_windows=6, step_size=6)
cv["Combination"] = cv[["ETS", "ARIMA", "STL_ETS"]].mean(axis=1)
pt = cv[["unique_id", "ds", "cutoff", "y", "ETS", "ARIMA", "STL_ETS", "SeasonalNaive", "Combination"]]
print("Combination versus members (log scale, pooled):\n",
      evaluate(pt, metrics=[mae, rmse]).groupby("metric").mean(numeric_only=True).round(4))

# %% 7 Forecast with prediction intervals and a plot
# Interval for an aggregate: the total of the next 12 months. Point forecasts add;
# intervals do not. Simulate sample paths, sum within each path, take quantiles.
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
y_log = pd.Series(cafe_log["y"].to_numpy(), index=pd.DatetimeIndex(cafe_log["ds"], freq="MS"))
ets = ETSModel(y_log, error="add", trend="add", damped_trend=True, seasonal="add",
               seasonal_periods=12).fit(disp=False)
paths = np.exp(ets.simulate(nsimulations=12, repetitions=2000, anchor="end", rng=np.random.default_rng(1)))
totals = paths.sum(axis=0)
print(f"Total of next 12 months: mean {totals.mean():.0f}, "
      f"80% interval [{np.quantile(totals, 0.1):.0f}, {np.quantile(totals, 0.9):.0f}]")

# Backcasting: reverse time, forecast, reverse back.
rev = cafe_log.iloc[::-1].reset_index(drop=True)
rev["ds"] = pd.date_range("2000-01-01", periods=len(rev), freq="MS")   # placeholder dates
back = StatsForecast(models=[AutoETS(season_length=12)], freq="MS").forecast(df=rev, h=12)
back_vals = np.exp(back["AutoETS"].to_numpy()[::-1])
print("Backcast of the 12 months before", cafe["ds"].iloc[0].strftime("%Y-%m"), ":", back_vals.round(1))

fig, ax = plt.subplots(2, 1, figsize=(8, 6))
ax[0].plot(eggs["ds"], eggs["y"], color="black")
ax[0].plot(bounded["ds"], bounded["RWD"])
ax[0].fill_between(bounded["ds"], bounded["RWD-lo-95"], bounded["RWD-hi-95"], alpha=0.2)
ax[0].axhline(a, ls=":"); ax[0].axhline(b, ls=":"); ax[0].set_title("Eggs, scaled logit, bounds 50 and 400")
ax[1].hist(totals, bins=40); ax[1].set_title("Simulated total of next 12 months (cafe turnover)")
fig.tight_layout(); fig.savefig(OUT / "practical.png", dpi=120); plt.close(fig)

# %% 8 What to report
# - Which practical issue applied and the fix chosen (and why not the alternatives).
# - Intermittent demand: the rate forecast, the metric used (no MAPE), the variant.
# - Bounded forecasts: the bounds and that the point forecast is a median.
# - Combinations: members, weights (equal), and accuracy against each member.
# - Aggregates: interval from simulated paths, never from summed interval ends.
# - Missing values and outliers: what was done to each and why.
print("Done. Outputs in", OUT)
