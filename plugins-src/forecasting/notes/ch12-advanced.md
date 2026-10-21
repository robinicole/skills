# Chapter 12: Advanced forecasting methods

## Section URLs

R edition [unverified]: `advanced-methods.html`, `complexseasonality.html`,
`prophet.html`, `VAR.html`, `nnetar.html`, `bootstrap.html`,
`advanced-exercises.html`.
Python edition [unverified]: same topics, slugs not confirmed; the neural
section may use `neuralforecast` or `mlforecast`.

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
  fitted many times from random starts and averaged. Default p from the best
  linear AR model by AICc, P = 1, k = (p + P + 1)/2 rounded up. Forecasts are
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

| R (fable, fable.prophet) | Python [unverified] |
|---|---|
| `STL(y ~ season(period=7) + season(period=365))` then `decomposition_model` | `statsforecast.models.MSTL(season_length=[7, 365], trend_forecaster=AutoARIMA())` |
| `ARIMA(y ~ fourier(period=, K=) + fourier(period=, K=) + PDQ(0,0,0))` | two `Fourier` term sets as exogenous columns |
| `prophet(y ~ season(period=, order=))` | `prophet.Prophet` (separate package) |
| `VAR(vars(y1, y2))`, `VAR(..., ic="bic")` | `statsmodels.tsa.api.VAR`, `select_order(ic="bic")` |
| `NNETAR(y)` | `neuralforecast.models.MLP` with `input_size=p` or `mlforecast` with lag features; no exact NNAR equivalent [unverified which the Python edition uses] |
| `generate(..., bootstrap_block_size=)` | manual block bootstrap of STL remainder |
| `AutoTBATS` (not in the book, statsforecast) | alternative for several periods |

## Common mistakes the book warns about

- Fitting seasonal ARIMA or ETS to periods in the hundreds.
- Trusting Prophet's intervals.
- Fitting a VAR to non-stationary series or to series with no feedback.
- Reading NNAR intervals from a normal formula.
