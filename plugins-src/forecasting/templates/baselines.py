"""Baselines template: the four benchmark methods, residual checks, transformation
with bias adjustment, train/test split, time series cross-validation and accuracy.

Book: FPP3 chapter 5 (R: https://otexts.com/fpp3/toolbox.html [unverified URL];
Python: https://otexts.com/fpppy/ chapter 5 [unverified URL]).
Run: python baselines.py   (needs fpp_data.py and fc_checks.py in the same folder)
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
from statsforecast import StatsForecast
from statsforecast.models import HistoricAverage, Naive, RandomWalkWithDrift, SeasonalNaive

from fc_checks import out_dir, residual_check, score_cv, skill
from fpp_data import freq, load, to_long

OUT = out_dir()

# %% 1 Data
# Quarterly Australian beer production from 1992, as in the book's toolbox chapter.
df = to_long(load("aus_production"), y="Beer", name="aus_production")
df = df[df["ds"] >= "1992-01-01"].reset_index(drop=True)
m, h, FREQ = 4, 8, freq("aus_production")     # seasonal period, forecast horizon
LEVELS = [80, 95]

# %% 2 Exploration needed for this method
# Look at the series first: the benchmark that fits depends on trend and seasonality.
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(df["ds"], df["y"])
ax.set_title("Beer production (megalitres): seasonal, no clear trend")
fig.savefig(OUT / "baselines_timeplot.png", dpi=120)
plt.close(fig)

# %% 3 Baselines
# Mean, naive, seasonal naive and drift. Every later model must beat the best of these.
benchmarks = [HistoricAverage(), Naive(), SeasonalNaive(season_length=m), RandomWalkWithDrift()]
sf = StatsForecast(models=benchmarks, freq=FREQ)

# %% 4 Model fit
# Train/test split: hold out the last h observations (at least the forecast horizon).
train, test = df.iloc[:-h], df.iloc[-h:]
fc_test = sf.forecast(df=train, h=h, level=LEVELS, fitted=True)
fitted = sf.forecast_fitted_values()

# %% 5 Diagnostics
# Residuals of a benchmark that captures the data should look like white noise.
# Seasonal naive is the natural benchmark here; check its residuals.
res = fitted["y"] - fitted["SeasonalNaive"]
diag = residual_check(res, m=m, dof=0, name="SeasonalNaive")
print("Residual check:", diag)

# Transformation and bias adjustment. Gas production has seasonal swings that grow
# with the level, so it needs a transformation; beer does not. Lambda by Guerrero.
from coreforecast.scalers import boxcox, boxcox_lambda, inv_boxcox
gas = to_long(load("aus_production"), y="Gas", name="aus_production")
lam = boxcox_lambda(gas["y"].to_numpy(), method="guerrero", season_length=m)
print(f"Guerrero lambda for gas: {lam:.2f} (0 is a log, 1 is no transformation)")
gas_t = gas.assign(y=boxcox(gas["y"].to_numpy(), lam))
fc_t = StatsForecast(models=[SeasonalNaive(season_length=m)], freq=FREQ).forecast(
    df=gas_t, h=h, level=[95])
# Forecast standard deviation on the transformed scale, read off the 95% interval.
sigma_h = ((fc_t["SeasonalNaive-hi-95"] - fc_t["SeasonalNaive"]) / 1.96).to_numpy()
median = inv_boxcox(fc_t["SeasonalNaive"].to_numpy(), lam)   # back-transformed point
mean = median * (1 + sigma_h ** 2 * (1 - lam) / (2 * median ** (2 * lam)))  # bias-adjusted
lo95 = inv_boxcox(fc_t["SeasonalNaive-lo-95"].to_numpy(), lam)  # interval ends need no adjustment
hi95 = inv_boxcox(fc_t["SeasonalNaive-hi-95"].to_numpy(), lam)
print(pd.DataFrame({"ds": fc_t["ds"], "median": median, "mean": mean,
                    "lo95": lo95, "hi95": hi95}).round(1).head(4))

# %% 6 Evaluation with time series cross-validation
# Test-set accuracy from one split, then cross-validation over many forecast origins.
from utilsforecast.evaluation import evaluate
from utilsforecast.losses import mae, mase, rmse
from functools import partial
test_scores = evaluate(test.merge(fc_test, on=["unique_id", "ds"]),
                       metrics=[mae, rmse, partial(mase, seasonality=m)], train_df=train)
print("Test set accuracy:\n", test_scores)

cv = sf.cross_validation(df=df, h=h, step_size=1, n_windows=12, level=[10, 20, 30, 40, 50, 60, 70, 80, 90, 95])
CRPS_LEVELS = [10, 20, 30, 40, 50, 60, 70, 80, 90]
scores = score_cv(cv, train_df=df, m=m, levels=LEVELS, crps_levels=CRPS_LEVELS)
overall = score_cv(cv, train_df=df, m=m, levels=LEVELS, crps_levels=CRPS_LEVELS, by_h=False)
print("Cross-validated accuracy, all horizons pooled:\n", overall.set_index("metric").round(3))
print("MASE skill against seasonal naive, per horizon:\n",
      skill(scores, "mase", "SeasonalNaive").round(3))
scores.to_csv(OUT / "baselines_cv_scores.csv", index=False)

# %% 7 Forecast with prediction intervals and a plot
fc = sf.forecast(df=df, h=h, level=LEVELS)
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(df["ds"], df["y"], color="black", label="data")
ax.plot(fc["ds"], fc["SeasonalNaive"], label="seasonal naive")
ax.fill_between(fc["ds"], fc["SeasonalNaive-lo-95"], fc["SeasonalNaive-hi-95"], alpha=0.2, label="95%")
ax.fill_between(fc["ds"], fc["SeasonalNaive-lo-80"], fc["SeasonalNaive-hi-80"], alpha=0.3, label="80%")
ax.legend()
fig.savefig(OUT / "baselines_forecast.png", dpi=120)
plt.close(fig)
fc.to_csv(OUT / "baselines_forecast.csv", index=False)

# %% 8 What to report
# - The benchmark used as the bar and why (seasonal naive for seasonal data).
# - Residual check of each candidate: Ljung-Box lag, p-value, mean.
# - Cross-validated accuracy per forecast horizon: MASE or RMSSE, coverage, Winkler, CRPS.
# - Whether a transformation was used, its lambda, and whether forecasts are medians or bias-adjusted means.
# - The forecast with 80% and 95% prediction intervals, and the plot.
print("Done. Outputs in", OUT)
