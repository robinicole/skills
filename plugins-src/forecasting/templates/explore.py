"""Explore template: time plot, seasonal and subseries plots, lag plot, ACF, white
noise test, Box-Cox lambda, STL and classical decomposition, and features to triage
many series.

Book: FPP3 chapters 2, 3, 4 (R: https://otexts.com/fpp3/graphics.html,
decomposition.html, features.html [unverified URLs]; Python edition chapters 2-4
[unverified URLs]).
Python: matplotlib, statsmodels (acf, STL, seasonal_decompose), coreforecast.
Run: python explore.py   (needs fpp_data.py and fc_checks.py in the same folder)
"""
# %% 0 Prerequisites
from fc_checks import preflight

missing = preflight({"pandas": "pandas", "numpy": "numpy", "matplotlib": "matplotlib",
                     "statsmodels": "statsmodels", "coreforecast": "coreforecast",
                     "pyreadr": "pyreadr"})
if missing:
    raise SystemExit("Install the missing packages, then run again.")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from coreforecast.scalers import boxcox, boxcox_lambda
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.seasonal import STL, seasonal_decompose

from fc_checks import ljung_box_lag, out_dir
from fpp_data import load, to_long

OUT = out_dir()


def strengths(y: np.ndarray, m: int) -> dict:
    """Trend and seasonal strength from a robust STL fit (0 = absent, 1 = dominant)."""
    res = STL(y, period=m, robust=True).fit()
    r = res.resid
    return {"trend_strength": float(max(0.0, 1 - np.var(r) / np.var(r + res.trend))),
            "seasonal_strength": float(max(0.0, 1 - np.var(r) / np.var(r + res.seasonal)))}


# %% 1 Data
retail = load("aus_retail")
cafe = retail[(retail["State"] == "Victoria") &
              (retail["Industry"] == "Cafes, restaurants and takeaway food services")]
cafe = to_long(cafe, y="Turnover", name="aus_retail")
m = 12

# %% 2 Exploration needed for this method
# Time plot: level, trend, breaks, outliers, and whether the seasonal swing grows with the level.
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(cafe["ds"], cafe["y"]); ax.set_title("Victoria cafe turnover ($m)")
fig.savefig(OUT / "explore_timeplot.png", dpi=120); plt.close(fig)

# Seasonal plot: one line per year. Subseries plot: one panel per month.
s = cafe.assign(year=cafe["ds"].dt.year, month=cafe["ds"].dt.month)
wide = s.pivot(index="month", columns="year", values="y")
fig, ax = plt.subplots(figsize=(8, 4))
for i, yr in enumerate(wide.columns):
    ax.plot(wide.index, wide[yr], color=plt.cm.viridis(i / len(wide.columns)), lw=0.8)
ax.set_title("Seasonal plot (darker = earlier year)")
fig.savefig(OUT / "explore_seasonal.png", dpi=120); plt.close(fig)
fig, axes = plt.subplots(1, 12, figsize=(14, 3), sharey=True)
for mo, a in zip(range(1, 13), axes):
    v = s[s["month"] == mo]
    a.plot(v["year"], v["y"], lw=0.8); a.axhline(v["y"].mean(), color="red", lw=0.8)
    a.set_title(str(mo)); a.set_xticks([])
fig.suptitle("Subseries plot (red line = mean of that month)")
fig.savefig(OUT / "explore_subseries.png", dpi=120); plt.close(fig)

# Lag plots and ACF: which lags carry signal; trend shows as slow decay, seasonality
# as spikes at multiples of m.
fig, axes = plt.subplots(1, 4, figsize=(12, 3))
for k, a in zip([1, 3, 6, 12], axes):
    a.scatter(cafe["y"].shift(k), cafe["y"], s=4); a.set_title(f"lag {k}")
fig.tight_layout(); fig.savefig(OUT / "explore_lags.png", dpi=120); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 3))
plot_acf(cafe["y"], lags=48, ax=ax, zero=False)
fig.savefig(OUT / "explore_acf.png", dpi=120); plt.close(fig)

# White noise test on the series (Ljung-Box). Small p = autocorrelation present.
from statsmodels.stats.diagnostic import acorr_ljungbox
lag = ljung_box_lag(m, len(cafe))
print("Ljung-Box on the series:", acorr_ljungbox(cafe["y"], lags=[lag]).round(4).to_dict("records"))

# %% 3 Baselines
# Exploration chooses the benchmark: seasonal naive when seasonality is present.
print("Seasonal and trend strength:", {k: round(v, 2) for k, v in strengths(cafe["y"].to_numpy(), m).items()})

# %% 4 Model fit
# Transformation: choose lambda so the seasonal swing looks constant. Guerrero method.
lam = boxcox_lambda(cafe["y"].to_numpy(), method="guerrero", season_length=m)
print(f"Guerrero lambda: {lam:.2f}; round to a readable value (0 = log, 0.5 = square root)")
y_t = boxcox(cafe["y"].to_numpy(), lam)
# STL on the transformed series. seasonal window: larger = slower-changing seasonality.
stl = STL(pd.Series(y_t, index=pd.DatetimeIndex(cafe["ds"], freq="MS")),
          period=m, seasonal=13, robust=True).fit()
fig = stl.plot(); fig.set_size_inches(8, 7)
fig.savefig(OUT / "explore_stl.png", dpi=120); plt.close(fig)
# Classical decomposition, for comparison only: fixed seasonal pattern, no trend at the ends.
cls = seasonal_decompose(pd.Series(y_t, index=pd.DatetimeIndex(cafe["ds"], freq="MS")),
                         model="additive", period=m)
print("Classical decomposition loses", int(cls.trend.isna().sum()), "trend values at the ends")

# %% 5 Diagnostics
# The STL remainder should look like noise. Outliers: remainder beyond 3 IQR.
r = stl.resid
q1, q3 = np.percentile(r, [25, 75])
outliers = cafe.loc[(r.to_numpy() < q1 - 3 * (q3 - q1)) | (r.to_numpy() > q3 + 3 * (q3 - q1)), "ds"]
print("Possible outliers (robust STL remainder beyond 3 IQR):", list(outliers.dt.strftime("%Y-%m")))

# %% 6 Evaluation with time series cross-validation
# Not used here: exploration does not score forecasts. It sets the inputs that
# forecast-baselines and the method skills evaluate.

# %% 7 Forecast with prediction intervals and a plot
# Not used here. Features for many series instead: triage all 304 tourism series.
tour = load("tourism")
feats = []
for (reg, st, pur), g in tour.groupby(["Region", "State", "Purpose"]):
    feats.append({"series": f"{reg}/{pur}", "Purpose": pur, **strengths(g["Trips"].to_numpy(), 4)})
feats = pd.DataFrame(feats)
fig, ax = plt.subplots(figsize=(6, 5))
for pur, g in feats.groupby("Purpose"):
    ax.scatter(g["trend_strength"], g["seasonal_strength"], s=10, label=pur)
ax.set_xlabel("trend strength"); ax.set_ylabel("seasonal strength"); ax.legend()
fig.savefig(OUT / "explore_features.png", dpi=120); plt.close(fig)
print("Median strengths by purpose:\n", feats.groupby("Purpose")[["trend_strength", "seasonal_strength"]].median().round(2))
print("Most seasonal series:", feats.nlargest(3, "seasonal_strength")["series"].tolist())

# %% 8 What to report
# - For each series or group: seasonal period m, trend yes/no, seasonality additive or
#   multiplicative, transformation and lambda, breaks and outliers with dates.
# - The plots that support each statement.
# - For many series: the feature table and the groups it suggests.
print("Done. Outputs in", OUT)
