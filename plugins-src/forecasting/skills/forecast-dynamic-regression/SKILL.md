---
name: forecast-dynamic-regression
description: Builds regression with ARIMA errors for forecasts with predictors whose errors are autocorrelated, dynamic harmonic regression with Fourier terms for long or non-integer seasonal periods such as weekly data, lagged predictors, and scenario forecasts, with ex-ante evaluation. Use when the user says "regression with ARIMA errors", "ARIMAX", "exogenous variables", "Fourier terms", "lagged predictor", "weekly data", "forecast with temperature" or "scenario forecast". Not for estimating the effect of an intervention.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast dynamic regression

You combine predictors with ARIMA errors, so drivers and autocorrelation are both
modelled and the intervals are honest about the errors.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/dynamic-regression.md`.
3. Read the plan, `explore.md`, `baselines.md` and any `regression.md` or
   `arima.md` in `docs/forecast-plans/*/`.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. For each predictor, record how its future values are obtained: known
   (calendar, Fourier terms), forecast, or scenario. Why: it decides whether
   accuracy and intervals are ex-ante or conditional.
2. Copy `../../templates/dynamic_regression.py` with `fpp_data.py` and
   `fc_checks.py`. Replace the data sections you need.

## Stage 2: Diagnostics

1. Stationarity of every variable (`ndiffs`). Why: regressing non-stationary
   series gives inconsistent coefficients. When the target is differenced, the
   predictors are differenced the same way (statsforecast does this when d > 0).
2. After fitting: residual check on the **innovation** residuals
   (`model.model_["residuals"]`, dof = p + q + P + Q). The regression residuals are
   expected to be autocorrelated; plot them separately.

## Stage 3: Implementation

1. Fit `AutoARIMA().fit(y, X=X)`; the predictor coefficients are `ex_1`, `ex_2`, ...
   in `model.model_["coef"]`. With the `StatsForecast` API, add the predictors as
   columns and pass future values in `X_df`.
2. Dynamic harmonic regression: Fourier terms for each seasonal period
   (`Fourier(period=365.25/7, order=K)` for weekly data) and
   `AutoARIMA(season_length=1)` for the errors. Choose K by AICc **with d fixed**.
   If the best K is the largest tried, extend the range or cap K and say so.
   Why: the seasonal shape is fixed over time; if it drifts, prefer STL or ETS.
3. Lagged predictors: candidate lag counts fitted on the same rows (drop max-lag
   rows for all); choose by AICc; refit on all usable rows.
4. Trend: compare a deterministic trend (time as predictor, d = 0) with a
   stochastic one (d = 1 with drift). Why: the deterministic trend assumes the
   slope never changes and gives intervals that are too narrow beyond a few periods.

## Stage 4: Evaluation and robustness

- Cross-validation with `fc_checks.rolling_origin`, ex-ante (forecast the
  predictors inside each window) as the headline and ex-post labelled as model
  error only, against the benchmark.
- Scenarios: two or more predictor paths; intervals conditional on each.

## Verification gate

Apply `workflow.md`. Quote the coefficients and error order, the innovation
residual check, ex-ante and ex-post accuracy, and how future predictor values
were obtained.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/dynamic-regression.md`. Coefficients are
associations under this error model, not causal effects. Intervals do not include
uncertainty in forecast predictors; say so beside the forecast.

Next: `/forecasting:forecast-auditor`. Several seasonal periods or nonlinear
effects: `/forecasting:forecast-advanced`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Residual check on the regression residuals | They are autocorrelated by design | Check the innovation residuals |
| Non-stationary predictors with d = 0 | Inconsistent coefficients | Difference all variables alike |
| AICc across lag counts on different rows | Not comparable | Same rows, then refit |
| K chosen at the edge of the range | Search stopped early | Extend or cap and report |
| Intervals presented as unconditional | They ignore predictor uncertainty | Label them conditional |
| m = 52 seasonal ARIMA for weekly data | Wrong period; slow and unstable | Fourier terms, period 365.25/7 |
| Deterministic trend for long forecast horizons | Too narrow intervals | Stochastic trend (d = 1 with drift) |
| Reading a coefficient as an effect | Forecasting needs only association | State it as association |

## Book sections

FPP3 chapter 10: 10.1 estimation, 10.2 regression with ARIMA errors, 10.3
forecasting, 10.4 stochastic and deterministic trends, 10.5 dynamic harmonic
regression, 10.6 lagged predictors; 13.1 weekly, daily and sub-daily data. R:
`https://otexts.com/fpp3/dynamic.html`, `estimation.html`, `regarima.html`,
`forecasting.html`, `stochastic-and-deterministic-trends.html`, `dhr.html`,
`lagged-predictors.html`, `weekly.html`. Python edition:
`https://otexts.com/fpppy/` chapter 10. URLs unverified (see `NOTES.md`).
