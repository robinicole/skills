# Chapter 10: Dynamic regression models

## Section URLs

R edition [unverified]: `dynamic.html`, `estimation.html`, `regarima.html`,
`forecasting.html`, `stochastic-and-deterministic-trends.html`, `dhr.html`,
`lagged-predictors.html`, `dynamic-exercises.html`.
Python edition [unverified]: same topics, slugs not confirmed.

## Key concepts and decision rules

- Regression with ARIMA errors: the regression captures the predictors; the error
  term follows an ARIMA process instead of white noise. Only the innovation
  residuals (the ARIMA's own errors) should be white noise; the regression
  residuals are expected to be autocorrelated.
- Estimation: all variables must be stationary, otherwise the coefficients are not
  consistent (unless the series are cointegrated). If the target needs
  differencing, difference every predictor the same way; the automatic function
  does this.
- The coefficient of a predictor is read as its effect on the target after
  accounting for the error dynamics.
- Forecasting needs future values of the predictors: forecast them, use known
  future values (calendar terms), or set scenarios. The resulting intervals
  ignore the uncertainty in the predictors; say so.
- Stochastic versus deterministic trend: a deterministic trend (regression on time
  with ARMA errors) assumes the slope never changes and gives narrow intervals; a
  stochastic trend (ARIMA with d=1 and drift) allows the slope to change and gives
  wider, more honest intervals for longer horizons. The book prefers the stochastic
  trend for anything beyond short horizons.
- Dynamic harmonic regression: Fourier terms as predictors with ARIMA errors. The
  standard approach for long seasonal periods (weekly, daily, hourly) and for
  non-integer periods. Choose the number of Fourier pairs K by AICc. Cost: the
  seasonal pattern is fixed over time; when seasonality drifts, prefer STL or ETS.
- Lagged predictors: include the predictor at several lags; choose the lag count by
  AICc, but every candidate must be fitted on the same rows (drop the first k
  observations for all) for the AICc values to be comparable. Refit the chosen
  model on all data.
- Intervention and calendar predictors (holidays, promotions, trading days) fit
  naturally here.

## Model diagnostics the book recommends

ACF and Ljung-Box on the innovation residuals; check the estimated ARIMA error
order is sensible; plot regression residuals separately to see the dynamics the
ARIMA error absorbed.

## Evaluation guidance

AICc within the same differencing and the same rows; cross-validation for final
selection; ex-ante accuracy with forecast predictors as the honest number.

## R functions and Python equivalents

| R (fable) | Python [unverified] |
|---|---|
| `ARIMA(y ~ x1 + x2)` | `statsforecast.models.AutoARIMA` with exogenous columns in the training frame and `X_df=` in `forecast()` |
| `ARIMA(y ~ fourier(K=) + PDQ(0,0,0))` | `Fourier` terms from statsmodels as exogenous columns; `AutoARIMA(season_length=1)` |
| `ARIMA(y ~ x + lag(x, 1) + lag(x, 2))` | shifted columns built with `pandas.shift` |
| `forecast(new_data=)`, `scenarios()` | `forecast(h=, X_df=future_exog)` |
| `statsmodels SARIMAX(exog=)` | alternative with full summary |

## Common mistakes the book warns about

- Fitting regression with ARIMA errors on non-stationary predictors.
- Checking the regression residuals instead of the innovation residuals.
- Comparing AICc of lagged-predictor models fitted on different row counts.
- Reporting intervals as if the predictors were known.
- Using a deterministic trend for long horizons.
