# Chapter 12: Advanced forecasting methods

## Section URLs

R edition (checked 2026-10-22; old section slugs redirect to chapter anchors): `advanced.html`, `complexseasonality.html`,
`prophet.html`, `VAR.html`, `nnetar.html`, `bootstrap.html`,
`advanced-exercises.html`.
Python edition (checked 2026-10-22): one page per chapter, `12-advanced.html`, same section anchors. NNAR is not here: neural networks are chapter 14 (`14-neural-networks.html`, neuralforecast), so 12.4 is bagging.

## Key concepts and decision rules

- Complex seasonality: daily data with weekly and annual cycles, half-hourly data
  with daily, weekly and annual cycles. Options the book shows: STL with several
  seasonal periods then a non-seasonal model on the adjusted series (the seasonal
  components forecast by seasonal naive); dynamic harmonic regression with one set
  of Fourier terms per period and ARIMA errors (preferred when predictors such as
  temperature matter, and the standard route for non-integer periods); the number
  of Fourier pairs per period is chosen by AICc. Seasonal ARIMA and ETS are not
  practical for long periods.
- Prophet: piecewise linear trend with automatic change points, Fourier
  seasonality, holiday effects, fitted as a regression (Bayesian). In the book's
  examples it does not beat ETS or ARIMA, its residuals are autocorrelated, and
  its intervals are poorly calibrated; it is worth considering when strong
  holiday effects and several seasonal periods are present and the user wants
  something automatic.
- Vector autoregression (VAR): several series modelled jointly, each as a function
  of the lags of all. Every series must be stationary (difference if needed).
  Choose the lag order by BIC (AICc picks too many lags in the book's view, or at
  least select carefully), check the residual autocorrelation of each equation.
  Useful only when there is genuine feedback between series; otherwise dynamic
  regression is simpler. Used for impulse response analysis and forecasting.
- Neural network autoregression NNAR(p, P, k): lagged values (p non-seasonal
  lags, P seasonal lags) feed a single hidden layer with k neurons; the model is
  fitted several times from random starts and averaged. Default p from the best
  linear AR model by AIC (seasonal series: P = 1, and p from an AR fitted to the
  seasonally adjusted data), k = (p + P + 1)/2 rounded to the nearest integer. Forecasts are
  produced by iterating one step at a time. Prediction intervals only by
  simulating future paths with bootstrapped or normal residuals. It can capture
  nonlinear dynamics but has no interpretable structure.
- Bootstrapping and bagging: Box-Cox transform, STL decompose, block-bootstrap the
  remainder to make many synthetic series, back-transform; fit ETS to each and
  average the forecasts. Bagged ETS usually beats plain ETS slightly, at a cost of
  one fit per bootstrap series. The same simulated series give bootstrap
  prediction intervals.

## Model diagnostics the book recommends

Residual checks per model; for VAR, Ljung-Box per equation; for Prophet, notice
the autocorrelated residuals.

## Evaluation guidance

Held-out comparison against ETS and ARIMA so the extra machinery proves its worth.

## R functions and Python equivalents

| R (fable, fable.prophet) | Python (checked against the Python edition 2026-10-22) |
|---|---|
| `STL(y ~ season(period=7) + season(period=365))` then `decomposition_model` | `statsforecast.models.MSTL(season_length=[m1, m2])` with the default trend forecaster; also: `trend_forecaster=AutoARIMA()` |
| `ARIMA(y ~ fourier(period=, K=) + fourier(period=, K=) + PDQ(0,0,0))` | one `utilsforecast.feature_engineering.fourier(season_length=, k=)` per period via `pipeline`, then `AutoARIMA(seasonal=False)` with `X_df=`; also: statsmodels `Fourier` sets |
| `prophet(y ~ season(period=, order=))` | `prophet.Prophet` (separate package) with `add_seasonality(name=, period=, fourier_order=)`; also: `statsforecast.adapters.prophet.AutoARIMAProphet` |
| `VAR(vars(y1, y2))`, `VAR(..., ic="bic")` | `statsmodels.tsa.api.VAR(df).fit(ic="aic"/"bic")`; also: `select_order()` |
| `NNETAR(y)` | not in Python edition chapter 12; chapter 14 uses `neuralforecast.models.MLP(h=, input_size=)` in `NeuralForecast`; no exact NNAR equivalent; also: `mlforecast` with lag features |
| `generate(..., bootstrap_block_size=)` | `MSTL` components from `sf.fitted_[0, 0].model_`, block bootstrap of the remainder in a hand-written function, `AutoETS` on each series, forecasts averaged |
| `AutoTBATS` (not in the book, statsforecast) | alternative for several periods (not in the Python edition) |

## Common mistakes the book warns about

- Fitting seasonal ARIMA or ETS to periods in the hundreds.
- Trusting Prophet's intervals.
- Fitting a VAR to non-stationary series or to series with no feedback.
- Reading NNAR intervals from a normal formula.
