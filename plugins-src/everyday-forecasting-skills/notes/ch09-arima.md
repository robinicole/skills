# Chapter 9: ARIMA models

## Section URLs

R edition [unverified]: `arima.html`, `stationarity.html`, `backshift.html`,
`AR.html`, `MA.html`, `non-seasonal-arima.html`, `arima-estimation.html`,
`arima-r.html`, `arima-forecasting.html`, `seasonal-arima.html`, `arima-ets.html`,
`arima-exercises.html`.
Python edition [unverified]: same topics, slugs not confirmed.

## Key concepts and decision rules

- Stationarity: properties do not depend on the time of observation; no trend, no
  seasonality, constant variance; cycles are allowed. A random walk is not
  stationary; its differences are.
- Differencing: first differences remove a trend; seasonal differences (lag m)
  remove seasonality. Rule: when both are needed, take the seasonal difference
  first and check whether a first difference is still needed; never difference
  more than twice; over-differencing shows as a large negative lag-1 autocorrelation.
- Unit root tests to decide d: KPSS (null is stationarity; a small p-value means
  difference), used by the automatic order functions. Seasonal strength from an
  STL decomposition decides D (difference when the seasonal strength exceeds a
  threshold near 0.64).
- Stabilise the variance (log or Box-Cox) before differencing.
- AR(p): the series regressed on its own past values; MA(q): on past errors.
  ARIMA(p,d,q) combines them on the differenced series; the constant decides the
  long-run behaviour: d=0 with constant reverts to a non-zero mean; d=1 with constant
  follows a drift line; d=2 with constant is a quadratic trend, which the book calls
  dangerous and the automatic search refuses.
- Reading orders by hand after differencing: an AR(p) series has a PACF that cuts
  off after lag p and a decaying ACF; an MA(q) series has an ACF that cuts off after
  lag q and a decaying PACF. When both decay, use the automatic search.
- Automatic ARIMA: Hyndman and Khandakar algorithm; selects d and D by tests,
  then p, q, P, Q by AICc with a stepwise search. AICc comparisons only hold for
  the same d and D (differencing changes the data the likelihood is computed on).
  A non-stepwise, non-approximated search is slower but wider.
- Modelling procedure: plot, transform if needed, difference until stationary,
  read ACF and PACF, try candidate models, check residuals with Ljung-Box, pick by
  AICc, forecast.
- Seasonal ARIMA(p,d,q)(P,D,Q)m: seasonal AR and MA terms at multiples of m.
  Seasonal spikes in the ACF suggest Q, in the PACF suggest P.
- Forecasting: point forecasts by recursion; intervals grow with h and keep growing
  for d of 1 or more. Intervals assume uncorrelated residuals; they are too narrow
  when that fails and when parameter uncertainty is ignored.
- ARIMA versus ETS: linear ETS models are special cases of ARIMA; the other ETS
  models are not. Neither family contains the other. Compare them by held-out
  accuracy or cross-validation, never by AICc.

## Model diagnostics the book recommends

ACF and PACF of the differenced series; KPSS; Ljung-Box on residuals with degrees
of freedom equal to the number of ARMA coefficients; residual time plot and
histogram; check that the automatic choice is sensible.

## Evaluation guidance

AICc within one differencing order; cross-validation across families.

## R functions and Python equivalents

| R (fable, feasts) | Python [unverified] |
|---|---|
| `features(y, unitroot_kpss)` | `statsmodels.tsa.stattools.kpss` |
| `features(y, unitroot_ndiffs/nsdiffs)` | `statsforecast.arima.ndiffs(x, test="kpss")`, `nsdiffs(x, period=)` |
| `difference(y, lag=)` | `pandas.Series.diff(periods=)` |
| `gg_tsdisplay(plot_type="partial")` | `plot_acf`, `plot_pacf` |
| `ARIMA(y)` automatic | `statsforecast.models.AutoARIMA(season_length=)` |
| `ARIMA(y ~ pdq(0,1,1) + PDQ(0,1,1))` | `statsforecast.models.ARIMA(order=, seasonal_order=, season_length=)` |
| `ARIMA(y, stepwise=FALSE, approx=FALSE)` | `AutoARIMA(stepwise=False, approximation=False)` |
| `report()`, `glance()` | `sf.fitted_[i, j].model_` dict (`arma`, `coef`, `aicc`) [check] |
| `statsmodels.tsa.arima.model.ARIMA` / `SARIMAX` | alternative with full summary |

## Common mistakes the book warns about

- Differencing more than needed.
- Comparing AICc across different d or D.
- Comparing ARIMA and ETS by AICc.
- Trusting the automatic search without checking residuals.
- Using d=2 with a constant.
