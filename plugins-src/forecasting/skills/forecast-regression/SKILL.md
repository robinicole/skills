---
name: forecast-regression
description: Builds regression forecasts with predictors, from linear regression with trend, season dummies, Fourier terms and intervention dummies to regression with ARIMA errors when the residuals are autocorrelated, plus dynamic harmonic regression for weekly or other long seasonal periods, lagged predictors and scenario forecasts, keeping ex-ante and ex-post accuracy apart. Use when the user says "regression forecast", "TSLM", "forecast with predictors", "season dummies", "piecewise trend", "regression with ARIMA errors", "ARIMAX", "exogenous variables", "Fourier terms", "lagged predictor", "weekly data", "forecast with temperature" or "scenario forecast". Also use it for questions about choosing predictors for a forecast model. Not for estimating causal effects or the effect of an intervention.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast regression

You build time series regressions that forecast, not only fit. Start with a linear
regression; when its residuals are autocorrelated, keep the predictors and model
the errors as ARIMA. Book chapters 7 and 10.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/regression.md` and
   `../../references/diagnostics/dynamic-regression.md`.
3. Read the plan, `explore.md`, `baselines.md` and any `arima.md` in
   `docs/forecast-plans/*/` if present.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. List candidate predictors and, for each, how its **future** values will be known:
   calendar or Fourier terms (known), set in advance (known), forecast (uncertain),
   scenario. Why: a predictor you cannot forecast better than the target adds
   nothing, and the source decides whether accuracy and intervals are ex-ante or
   conditional.
2. Copy `../../templates/regression.py` (linear regression) and, for ARIMA errors,
   `../../templates/dynamic_regression.py`, with `fpp_data.py` and `fc_checks.py`.
   Replace the data sections you need.

## Stage 2: Diagnostics

1. Scatter the target against each predictor. Why: shows nonlinear shapes before
   fitting.
2. After the linear fit: residual time plot, ACF, Ljung-Box (dof = number of
   coefficients), Breusch-Godfrey; residuals against each predictor and the fitted
   values. Why: a pattern means a missing or nonlinear term; autocorrelation means
   the standard errors and intervals are wrong.
3. Spurious regression check: high R squared plus autocorrelated residuals is a
   FATAL verdict until fixed.
4. Autocorrelated residuals: move to ARIMA errors (Stage 3, step 5). Check the
   stationarity of every variable first (`ndiffs`). Why: regressing non-stationary
   series gives inconsistent coefficients. When the target is differenced, the
   predictors are differenced the same way (statsforecast does this when d > 0).
5. With ARIMA errors, check the **innovation** residuals
   (`model.model_["residuals"]`, dof = p + q + P + Q). The regression residuals are
   expected to be autocorrelated; plot them separately.

## Stage 3: Implementation

1. Deterministic terms: `DeterministicProcess(index, constant=True, order=1,
   seasonal=True, drop=True)` for trend and m - 1 dummies, or `Fourier(period,
   order=K)` for long periods. K = m/2 reproduces the dummies.
2. Event terms: spike dummy for a one-off, step dummy for a permanent change, a
   piecewise trend with knots at known breaks. Do not forecast with cubic splines.
3. Select predictors by AICc (or leave-one-out CV, or BIC) over all subsets when
   feasible, backward otherwise. Never by p-value or R squared. Why: AICc penalises
   parameters, so it tracks out-of-sample accuracy better than R squared, which
   always rises with more predictors.
4. Forecast: known future terms, forecast predictors, or explicit scenarios.
5. ARIMA errors: `AutoARIMA().fit(y, X=X)`; the predictor coefficients are `ex_1`,
   `ex_2`, ... in `model.model_["coef"]`. With the `StatsForecast` API, add the
   predictors as columns and pass future values in `X_df`.
6. Weekly data and other long or non-integer periods (dynamic harmonic
   regression): Fourier terms for each seasonal period
   (`Fourier(period=365.25/7, order=K)` for weekly data) and
   `AutoARIMA(season_length=1)` for the errors. Choose K by AICc **with d fixed**.
   If the best K is the largest tried, extend the range or cap K and say so.
   Why: the seasonal shape is fixed over time; if it drifts, prefer STL or ETS.
   Several seasonal periods (daily, sub-daily): `forecast-advanced`.
7. Lagged predictors: candidate lag counts fitted on the same rows (drop max-lag
   rows for all); choose by AICc; refit on all usable rows.
8. Trend: compare a deterministic trend (time as predictor, d = 0) with a
   stochastic one (d = 1 with drift). Why: the deterministic trend assumes the
   slope never changes and gives intervals that are too narrow beyond a few periods.

## Stage 4: Evaluation and robustness

- Time series cross-validation with `fc_checks.rolling_origin` against the
  benchmarks from `baselines.md`, same forecast origins. Compare the linear and the
  ARIMA-error model on those origins when both were fitted.
- Report ex-ante accuracy (predictors forecast inside each window) as the
  headline. Ex-post accuracy (actual predictors) isolates model error and must be
  labelled.
- Scenarios: two or more predictor paths; intervals conditional on each.

## Verification gate

Apply `workflow.md`. Quote the selected predictors and their selection table, the
error model, the residual checks (innovation residuals for ARIMA errors), ex-ante
and ex-post accuracy against the benchmark, and how future predictor values were
obtained.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/regression.md`. Explain coefficients as
associations: "a quarter with 1 point higher income growth had on average 0.74
points higher consumption growth, holding the other predictors fixed". Say that
this is not a causal effect. Intervals do not include uncertainty in forecast
predictors, and scenario intervals are conditional on the scenario; say so beside
the forecast.

Next: `/forecasting:forecast-auditor`. Several seasonal periods or nonlinear
effects: `/forecasting:forecast-advanced`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Selecting predictors by p-value | p-values do not measure forecast value | AICc, BIC or leave-one-out CV |
| Reporting R squared as accuracy | Rises with every predictor; in-sample | Cross-validated accuracy |
| m season dummies plus an intercept | Perfect collinearity | m - 1 dummies (`drop=True`) |
| Ignoring autocorrelated residuals | Intervals too narrow; possible spurious fit | ARIMA errors |
| Residual check on the regression residuals of an ARIMA-error model | They are autocorrelated by design | Check the innovation residuals |
| Non-stationary predictors with d = 0 | Inconsistent coefficients | Difference all variables alike |
| AICc across lag counts on different rows | Not comparable | Same rows, then refit |
| K chosen at the edge of the range | Search stopped early | Extend or cap and report |
| m = 52 seasonal ARIMA for weekly data | Wrong period; slow and unstable | Fourier terms, period 365.25/7 |
| Deterministic trend for long forecast horizons | Too narrow intervals | Stochastic trend (d = 1 with drift) |
| Ex-post accuracy as the headline | Uses future values no one has | Ex-ante accuracy |
| Intervals presented as unconditional | They ignore predictor uncertainty | Label them conditional |
| Reading coefficients as causal effects | Confounders and reverse links | State them as associations |
| Cubic spline trend for forecasting | Extrapolates a cubic | Piecewise linear trend |

## Book sections

FPP3 chapter 7: 7.1 the linear model, 7.2 least squares, 7.3 evaluating the model,
7.4 useful predictors, 7.5 selecting predictors, 7.6 forecasting with regression,
7.7 nonlinear regression, 7.8 correlation, causation and forecasting. Chapter 10:
10.1 estimation, 10.2 regression with ARIMA errors, 10.3 forecasting, 10.4
stochastic and deterministic trends, 10.5 dynamic harmonic regression, 10.6 lagged
predictors; 13.1 weekly, daily and sub-daily data. R:
`https://otexts.com/fpp3/regression.html`, `dynamic-regression.html`,
`practical.html#sec-weekly`. Python edition: `https://otexts.com/fpppy/` chapters
7 and 10. URLs checked 2026-10-22.
