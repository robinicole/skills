# Explore, transform, decompose

Reference for step 3 of [SKILL.md](SKILL.md).

## Plots

| Plot | Shows | Decides |
| --- | --- | --- |
| Time plot | Level, trend, variance growth, breaks, outliers | Transform? Stable enough to model? |
| Seasonal plot (one line per year) | Seasonal shape and drift | Fixed or evolving seasonality |
| Subseries plot (one panel per month or weekday) | Change in each season's mean | Additive or multiplicative |
| Lag plot | y(t) against y(t-k) | Which lags carry signal |
| ACF | Correlation at every lag | Period, trend, white noise |

Reading an ACF: slow decay from lag 1 is trend, spikes at multiples of m are seasonality, both together give a decaying scalloped shape. White noise stays inside about ±2/√T.

## White noise test

Ljung-Box, on the series or on residuals, with the lag rule from the residual check in [MODELS.md](MODELS.md#residuals-and-intervals). A small p-value means autocorrelation remains.

```python
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf

acf_vals = acf(y, nlags=3 * m)
acorr_ljungbox(y, lags=[2 * m], return_df=True)
```

## Features for many series

With more series than you can plot, compute trend strength and seasonal strength from STL and scatter one against the other. Near 1 the component dominates, near 0 it is barely there. This sorts series into those needing seasonal models and those that are mostly noise.

```python
from statsmodels.tsa.seasonal import STL

res = STL(y, period=m, robust=True).fit()
r = res.resid
seas_strength = max(0, 1 - r.var() / (r + res.seasonal).var())
trend_strength = max(0, 1 - r.var() / (r + res.trend).var())
```

The `tsfeatures` package computes these and more at scale.

## Box-Cox

Use it when seasonal swings grow with the level. Lambda 0 is a log, 1 is no change. The goal is a lambda that makes seasonal amplitude constant across the plot, rounded to something readable (0, 0.5). scipy picks lambda by likelihood, which targets normality; treat it as a starting value and check it on the plot (FPP3 uses the Guerrero method).

Back-transforming a forecast gives the median. When forecasts will be summed or a mean is needed, apply the bias adjustment.

```python
from scipy.stats import boxcox
from scipy.special import inv_boxcox

y_t, lam = boxcox(y)                 # starting lambda, check on the plot
fc = inv_boxcox(fc_t, lam)           # median, original scale
fc_mean = fc * (1 + sigma2_h * (1 - lam) / (2 * fc ** (2 * lam)))
```

## Decomposition

y = T + S + R (additive) or y = T × S × R (multiplicative). Use multiplicative, or a log then additive, when seasonal size scales with level.

STL handles any period, lets the seasonal component evolve and can be robust to outliers. Two knobs:

- `trend`: window for trend smoothness.
- `seasonal`: how fast the seasonal pattern may change. A large odd number such as 13 allows slow drift; smaller lets it move faster.

```python
from statsmodels.tsa.seasonal import STL

res = STL(y, period=12, seasonal=13, trend=23, robust=True).fit()
seasadj = y - res.seasonal
```

Seasonally adjusted data is for spotting turning points and for forecasting with a non-seasonal model before adding seasonality back (see decomposition forecasting in [MODELS.md](MODELS.md)). When the seasonal pattern is the thing being forecast, model the raw series.

X-13/SEATS is what statistical agencies use for monthly and quarterly official data. Classical decomposition is outdated; use STL.
