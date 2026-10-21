---
name: forecast-regression
description: Builds linear regression forecasts with trend, season dummies, Fourier terms, intervention dummies and predictors, selects predictors by AICc or cross-validation, and keeps ex-ante and ex-post forecasts apart. Use when the user asks for a "regression forecast", "TSLM", "forecast with predictors", "season dummies", "trend regression" or "piecewise trend", and the residuals are not autocorrelated. Also use it for questions about choosing predictors for a linear forecast model. Not for predictors with autocorrelated errors (use forecast-dynamic-regression), and not for estimating causal effects.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast regression

You build time series regressions and make sure they forecast, not only fit.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/regression.md`.
3. Read the plan, `explore.md` and `baselines.md` in `docs/forecast-plans/*/` if present.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. List candidate predictors and, for each, how its **future** values will be known:
   calendar (known), set in advance (known), forecast (uncertain), scenario.
   Why: a predictor you cannot forecast better than the target adds nothing.
2. Copy `../../templates/regression.py` with `fpp_data.py` and `fc_checks.py`.
   Replace the data section.

## Stage 2: Diagnostics

1. Scatter the target against each predictor. Why: shows nonlinear shapes before
   fitting.
2. After fitting: residual time plot, ACF, Ljung-Box (dof = number of
   coefficients), Breusch-Godfrey; residuals against each predictor and the fitted
   values. Why: a pattern means a missing or nonlinear term; autocorrelation means
   the standard errors and intervals are wrong.
3. Spurious regression check: high R squared plus autocorrelated residuals is a
   FATAL verdict until fixed.

## Stage 3: Implementation

1. Deterministic terms: `DeterministicProcess(index, constant=True, order=1,
   seasonal=True, drop=True)` for trend and m - 1 dummies, or `Fourier(period,
   order=K)` for long periods. K = m/2 reproduces the dummies.
2. Event terms: spike dummy for a one-off, step dummy for a permanent change, a
   piecewise trend with knots at known breaks. Do not forecast with cubic splines.
3. Select predictors by AICc (or leave-one-out CV, or BIC) over all subsets when
   feasible, backward otherwise. Never by p-value or R squared.
4. Forecast: known future terms, forecast predictors, or explicit scenarios.

Why AICc: it penalises parameters, so it tracks out-of-sample accuracy better than
R squared, which always rises with more predictors.

## Stage 4: Evaluation and robustness

- Time series cross-validation with `fc_checks.rolling_origin` against the
  benchmarks from `baselines.md`, same forecast origins.
- Report ex-ante accuracy (predictors forecast) as the headline. Ex-post accuracy
  (actual predictors) isolates model error and must be labelled.
- If residuals are autocorrelated, switch to `forecast-dynamic-regression` and
  compare.

## Verification gate

Apply `workflow.md`. Quote the selected predictors and their selection table, the
residual checks, and ex-ante cross-validated accuracy against the benchmark.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/regression.md`. Explain coefficients as
associations: "a quarter with 1 point higher income growth had on average 0.74
points higher consumption growth, holding the other predictors fixed". Say that
this is not a causal effect. State that scenario intervals are conditional on the
scenario.

Next: `/forecasting:forecast-auditor`, or `/forecasting:forecast-dynamic-regression`
if residuals failed.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Selecting predictors by p-value | p-values do not measure forecast value | AICc, BIC or leave-one-out CV |
| Reporting R squared as accuracy | Rises with every predictor; in-sample | Cross-validated accuracy |
| m season dummies plus an intercept | Perfect collinearity | m - 1 dummies (`drop=True`) |
| Ignoring autocorrelated residuals | Intervals too narrow; possible spurious fit | Dynamic regression |
| Ex-post accuracy as the headline | Uses future values no one has | Ex-ante accuracy |
| Reading coefficients as causal effects | Confounders and reverse links | State them as associations |
| Cubic spline trend for forecasting | Extrapolates a cubic | Piecewise linear trend |

## Book sections

FPP3 chapter 7: 7.1 the linear model, 7.2 least squares, 7.3 evaluating the model,
7.4 useful predictors, 7.5 selecting predictors, 7.6 forecasting with regression,
7.7 nonlinear regression, 7.8 correlation, causation and forecasting. R:
`https://otexts.com/fpp3/regression.html`, `least-squares.html`,
`useful-predictors.html`, `selecting-predictors.html`,
`forecasting-regression.html`, `nonlinear-regression.html`,
`correlation-causation.html`. Python edition: `https://otexts.com/fpppy/` chapter 7. URLs
unverified (see `NOTES.md`).
