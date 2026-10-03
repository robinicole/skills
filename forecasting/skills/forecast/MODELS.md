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

Fitted values are one-step-ahead predictions on training data. Use them for the residual check and for nothing else: they say nothing about accuracy at longer horizons.

Residual check, after any transform test the residuals on the transformed scale:

- Ljung-Box p > 0.05 at 10 lags (non-seasonal) or 2m (seasonal).
- Mean within ±2 standard errors of zero.
- Variance flat on a time plot.

A model that fails is misspecified. Add the missing structure (a seasonal term, a transform, a regressor) and recheck.

Intervals widen with horizon for every method except the mean: naive with √h, drift faster, ETS and ARIMA by their own formulas. When residuals are not normal, use conformal intervals:

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

Weighted averages with geometrically decaying weights. Named by three letters, Error (A, M), Trend (N, A, Ad), Season (N, A, M). ETS(A,N,N) is simple smoothing. ETS(M,Ad,M) is damped trend with multiplicative season, a strong retail default. A damped trend beats a straight trend beyond a few periods almost every time. Multiplicative components need strictly positive data.

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

Stationary means no trend, no seasonality, constant variance. Stabilise variance with a log or Box-Cox, remove trend with one difference (rarely two), remove seasonality with a seasonal difference at lag m. KPSS decides how many:

```python
from statsforecast.arima import ndiffs, nsdiffs

d = ndiffs(y, test="kpss")
D = nsdiffs(y, period=m)
```

Reading orders by hand from the differenced series: AR(p) has a PACF that cuts off after p and a decaying ACF; MA(q) is the reverse. Seasonal spikes in the ACF suggest Q, in the PACF suggest P. When both decay, let the search decide.

Let the automatic search run, then sanity check it. AICc compares models only when they share the same d and D.

```python
from statsforecast.models import AutoARIMA, ARIMA

AutoARIMA(season_length=m)
AutoARIMA(season_length=m, stepwise=False, approximation=False)        # fuller search
ARIMA(order=(0, 1, 1), seasonal_order=(0, 1, 1), season_length=m)       # airline model
```

Long-run behaviour: d = 0 reverts to the mean; d = 1 without constant goes flat, with constant follows a drift; d = 2 extrapolates a line, usually too aggressive. Intervals keep growing for d ≥ 1.

ETS or ARIMA: linear ETS models are special ARIMAs, neither contains the other. ETS handles multiplicative structure and damping natively; ARIMA handles cycles, long autocorrelation and regressors. Backtest decides.

## Dynamic regression

For drivers (price, weather, promotions): y = β·x + η, where η is ARIMA. Plain regression leaves autocorrelated errors and intervals that are too narrow.

Predictors that need no outside data: linear or piecewise trend (knots at known breaks), seasonal dummies, Fourier terms, holiday dummies, intervention dummies (spike for one-off, step for permanent), lagged drivers. K Fourier pairs cost 2K parameters against m-1 dummies; pick K by AICc.

Select predictors by AICc or backtest error. Prefer the lowest AICc unless a simpler model is within about 2.

Forecasting needs the predictors' future values. A driver you cannot forecast better than the target adds nothing. Backtest with actual future predictor values (ex post) only to isolate model error, and report ex-ante accuracy as the real number.

Correlation is enough for forecasting and says nothing causal; a price coefficient here is not a price elasticity.

Trend choice: regression on time assumes the trend never changes and gives narrow intervals. A differenced ARIMA with drift admits it might change. Beyond a few periods, the second is the honest default.

Dynamic harmonic regression (Fourier terms as x) is the standard answer for weekly or daily data, and the only route for non-integer periods like 52.18:

```python
import pandas as pd
from statsmodels.tsa.deterministic import DeterministicProcess, Fourier
from statsforecast.models import AutoARIMA

# one weekly series in df (unique_id, ds, y)
dp = DeterministicProcess(index=pd.DatetimeIndex(df["ds"], freq="W-MON"), constant=False,
                          additional_terms=[Fourier(period=52.18, order=3)])
df_x = pd.concat([df.reset_index(drop=True), dp.in_sample().reset_index(drop=True)], axis=1)
X_future = (dp.out_of_sample(steps=13).rename_axis("ds").reset_index()
              .assign(unique_id=df["unique_id"].iloc[0]))

sf = StatsForecast(models=[AutoARIMA(season_length=1)], freq="W-MON")
fc = sf.forecast(df=df_x, h=13, X_df=X_future, level=[80, 95])
```

## Complex seasonality

Daily data with weekly and yearly cycles, or hourly with daily and weekly. Seasonal ETS and ARIMA get slow and weak once m passes roughly 24. Three answers:

- MSTL with several periods, forecasting the adjusted series: `MSTL(season_length=[7, 365], trend_forecaster=AutoARIMA())`.
- Dynamic harmonic regression with one Fourier set per period.
- TBATS (`statsforecast.models.AutoTBATS`): trigonometric seasonality plus Box-Cox, slow but self-contained.

## Other models

Reach for these when a standard model fails on a specific feature, and keep ETS or ARIMA in the comparison so you can see what the extra machinery bought.

- **Prophet**: piecewise trend, Fourier seasonality and holidays. Easy to explain, handles gaps and outliers. Usually loses to ETS and ARIMA on accuracy and its intervals run narrow. Use it when its changepoint and holiday handling fits the problem.
- **VAR**: several series modelled jointly. Worth it only with real feedback between series (competitor prices); otherwise parameters explode and per-series dynamic regression wins.
- **Neural or boosted models**: lags and Fourier features into a network (`neuralforecast`) or gradient boosting (`mlforecast`). Captures nonlinearity; boosting is usually the better engineering choice at scale.
- **Bagging**: STL, block-bootstrap the remainder, refit on many synthetic series, average. A few percent over ETS for about 100 times the compute; worth it on the series that matter most.

## Combining

A simple mean of ETS, ARIMA and a regression beats most of its members most of the time. Fitted weights rarely help.
