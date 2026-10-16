# Models

Reference for step 4 of [SKILL.md](SKILL.md). Every section ends with the statsforecast call.

## Benchmarks

| Benchmark | Forecast | Right for |
| --- | --- | --- |
| Mean | Average of history | Flat noise |
| Naive | Last value | Random walks, prices |
| Seasonal naive | Value one season ago | Any seasonal series; this is the bar |
| Drift | Last value plus average historical change | Trending series |

```python
from statsforecast import StatsForecast
from statsforecast.models import HistoricAverage, Naive, SeasonalNaive, RandomWalkWithDrift

sf = StatsForecast(
    models=[HistoricAverage(), Naive(), SeasonalNaive(season_length=m), RandomWalkWithDrift()],
    freq="MS",
)
```

## Residuals and intervals

Fitted values are one-step-ahead predictions on training data, so they serve the residual check and say nothing about accuracy at longer horizons.

Residual check, for every candidate except the benchmarks (they are the yardstick). After a transform, test the residuals on the transformed scale.

- Ljung-Box p > 0.05 at 10 lags (non-seasonal) or 2m (seasonal), capped at T/5. For ARIMA and regression models pass the number of estimated parameters as `model_df` so the degrees of freedom are reduced; otherwise p-values are too lenient.
- Mean within ±2 standard errors of zero.
- Variance flat on a time plot.
- For regression candidates, residuals plotted against each predictor and against the fitted values show no pattern. A pattern means a missing or nonlinear term. A high R² with autocorrelated residuals is a spurious regression, not a fit.

A model that fails is misspecified. Add the missing structure (a seasonal term, a transform, a regressor) and recheck.

Intervals widen with horizon for every method except the mean: naive with √h, drift faster, seasonal naive in steps once per season (flat within a season, so the bar's band looks constant for m steps), ETS and ARIMA by their own formulas. Conformal intervals drop the normality assumption:

```python
from statsforecast.utils import ConformalIntervals

fc = sf.forecast(df=df, h=12, level=[80, 95],
                 prediction_intervals=ConformalIntervals(h=12, n_windows=5))
```

## Decomposition forecasting

Forecast the seasonally adjusted series with a non-seasonal model, forecast the seasonal part as seasonal naive, add them. Cheap and strong.

```python
from statsforecast.models import MSTL, AutoARIMA

MSTL(season_length=m, trend_forecaster=AutoARIMA())
```

## ETS (exponential smoothing)

The default first real model: fast, robust, close to the best most of the time, with proper intervals.

Weighted averages with geometrically decaying weights. Named by three letters, Error (A, M), Trend (N, A, Ad), Season (N, A, M). ETS(A,N,N) is simple smoothing. ETS(M,Ad,M) is damped trend with multiplicative season, a strong retail default. Holt's linear trend over-forecasts at long horizons; damping (phi between 0.8 and 0.98 in practice) is the usual fix and the most popular choice for automatic forecasting of many series, but let AICc decide. Multiplicative components need strictly positive data, and the A,N,M / A,A,M / A,Ad,M combinations are numerically unstable and excluded from the search, so do not request them with `model=`.

Pick by AICc on training data, then confirm in backtest.

```python
from statsforecast.models import AutoETS

AutoETS(season_length=m)                           # AICc search over the taxonomy
AutoETS(season_length=m, model="ZZN")              # no seasonality
AutoETS(season_length=m, model="MAM", damped=True)
```

Parameters carry meaning: alpha near 1 means the level chases the latest value; near 0 means long memory. Gamma near 0 means a fixed seasonal pattern.

ETS takes no regressors. When drivers matter, use dynamic regression and keep ETS as a candidate.

## ARIMA

Difference until stationary, then fit AR and MA terms to what is left.

Stationary means no trend, no seasonality, constant variance. Stabilise variance with a log or Box-Cox, then difference seasonally first at lag m (that alone is often enough), then at lag 1 if still needed, never beyond second order. A seasonal-strength test (the `nsdiffs` default, F_S > 0.64) decides D; KPSS on the seasonally differenced series decides d:

```python
import numpy as np
from statsforecast.arima import ndiffs, nsdiffs

ya = np.asarray(y)
D = nsdiffs(ya, period=m)
d = ndiffs(ya[m:] - ya[:-m] if D else ya, test="kpss")
```

Reading orders by hand from the differenced series: AR(p) has a PACF that cuts off after p and a decaying ACF; MA(q) is the reverse. Seasonal spikes in the ACF suggest Q, in the PACF suggest P. When both decay, let the search decide.

Let the automatic search run, then sanity check it. AICc compares models only when they share the same d and D.

```python
from statsforecast.models import AutoARIMA, ARIMA

AutoARIMA(season_length=m)
AutoARIMA(season_length=m, stepwise=False, approximation=False)        # fuller search
ARIMA(order=(0, 1, 1), seasonal_order=(0, 1, 1), season_length=m)       # airline model
```

Long-run behaviour: d = 0 with constant reverts to the mean, without constant to zero; d = 1 without constant goes flat, with constant follows a drift; d = 2 extrapolates a line (a quadratic with constant, which the search refuses), usually too aggressive. Intervals keep growing for d ≥ 1.

ETS or ARIMA: linear ETS models are special ARIMAs, neither contains the other. ETS handles multiplicative structure and damping natively; ARIMA handles cycles, long autocorrelation and regressors. Their likelihoods are computed differently, so AICc cannot compare them; backtest decides.

## Dynamic regression

For drivers (price, weather, promotions): y = β·x + η, where η is ARIMA. Plain regression leaves autocorrelated errors and intervals that are too narrow. Every variable must be stationary: when y needs differencing, difference each predictor the same way (statsforecast does this when d > 0 with `X_df`).

Predictors that need no outside data: linear or piecewise trend (knots at known breaks), seasonal dummies, Fourier terms, holiday dummies, intervention dummies (spike for one-off, step for permanent), lagged drivers. K Fourier pairs cost 2K parameters against m-1 dummies; pick K by AICc.

Select predictors by AICc or leave-one-out CV, never by p-values or R². Fit all subsets when feasible, backward stepwise otherwise. Lagged predictors: every candidate lag count must be fitted on the same rows (drop the first k for all of them) or the AICc values are not comparable.

Forecasting needs the predictors' future values. A driver you cannot forecast better than the target adds nothing. Backtest with actual future predictor values (ex post) only to isolate model error, and report ex-ante accuracy as the real number. Intervals ignore the uncertainty in the predictors' future values, so read them as conditional on the assumed path.

Correlation is enough for forecasting and says nothing causal; a price coefficient here is not a price elasticity.

Trend choice: regression on time assumes the trend never changes and gives narrow intervals. A differenced ARIMA with drift admits it might change. Beyond a few periods, the second is the honest default.

Dynamic harmonic regression (Fourier terms as x) is the standard answer for weekly or daily data, and the standard route for non-integer periods like 52.18 (TBATS is the other). Pick K by AICc over 1..m/2, but for long periods AICc overestimates K, so cap it by hand (the book uses about 5 for weekly, 10 for daily within a year). Its cost: the seasonal pattern cannot change over time; when seasonality drifts, prefer STL or ETS.

```python
import pandas as pd
from statsmodels.tsa.deterministic import DeterministicProcess, Fourier
from statsforecast.models import AutoARIMA

# one weekly series in df (unique_id, ds, y)
dp = DeterministicProcess(index=pd.DatetimeIndex(df["ds"], freq="W-MON"), constant=False,
                          additional_terms=[Fourier(period=52.18, order=3)])   # K=3; compare K by AICc
df_x = pd.concat([df.reset_index(drop=True), dp.in_sample().reset_index(drop=True)], axis=1)
X_future = (dp.out_of_sample(steps=13).rename_axis("ds").reset_index()
              .assign(unique_id=df["unique_id"].iloc[0]))

sf = StatsForecast(models=[AutoARIMA(season_length=1)], freq="W-MON")
fc = sf.forecast(df=df_x, h=13, X_df=X_future, level=[80, 95])
```

## Complex seasonality

Daily data with weekly and yearly cycles, or hourly with daily and weekly. Seasonal ARIMA becomes impractical once a period runs into the hundreds (seasonal differencing gets unreliable, memory blows up) and seasonal ETS stops much earlier. Three answers, the book's preference first:

- Dynamic harmonic regression with one Fourier set per period.
- MSTL with several periods, forecasting the adjusted series: `MSTL(season_length=[7, 365], trend_forecaster=AutoARIMA())`.
- TBATS (`statsforecast.models.AutoTBATS`): trigonometric seasonality plus Box-Cox, slow but self-contained.

## Other models

Reach for these when a standard model fails on a specific feature, and keep ETS or ARIMA in the comparison so you can see what the extra machinery bought.

- **Prophet**: piecewise trend, Fourier seasonality and holidays, fully automatic. Rarely beats ETS or ARIMA on accuracy, and it ignores residual autocorrelation, so its residuals usually fail Ljung-Box and its intervals are wrong (too wide in the book's example). Use it when its changepoint and holiday handling fits the problem.
- **VAR**: several series modelled jointly, all stationary (levels or differences). Worth it only with real feedback between series (competitor prices); otherwise parameters explode and per-series dynamic regression wins. Choose the lag order by BIC; AICc picks too many lags.
- **Neural or boosted models**: lags and Fourier features into a network (`neuralforecast`) or gradient boosting (`mlforecast`). Captures nonlinearity; boosting is usually the better engineering choice at scale. The book's NNAR(p,P,k) sets p from the best linear AR by AICc, P = 1, k = (p+P+1)/2, forecasts by iterating one step at a time, and gets intervals only by simulating paths with bootstrapped residuals.
- **Bagging**: Box-Cox, STL, block-bootstrap the remainder, recombine and back-transform into many synthetic series, fit ETS to each, average the forecasts. Beats plain ETS on average at the cost of one fit per bootstrap series; worth it on the series that matter most.

## Combining

A simple mean of ETS, STL+ETS and ARIMA beats most of its members most of the time. Fitted weights rarely help. Averaging the point forecasts gives no valid interval; pool simulated sample paths from the members and take quantiles.
