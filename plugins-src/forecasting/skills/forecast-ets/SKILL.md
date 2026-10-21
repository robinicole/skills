---
name: forecast-ets
description: Fits exponential smoothing (ETS) state space models, from simple exponential smoothing and Holt to damped trend and Holt-Winters, selects the form by AICc, reads the smoothing parameters, and produces prediction intervals. Use when the user says "exponential smoothing", "ETS model", "Holt-Winters", "damped trend", "AutoETS" or "simple exponential smoothing". Also use it for questions about which smoothing method or trend type to use. Not for comparing ETS with ARIMA by AICc, and not for series with predictors.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast ETS

You fit exponential smoothing models and check that they beat the benchmark.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/ets.md`.
3. Read the plan, `explore.md` and `baselines.md` in `docs/forecast-plans/*/` if present.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. From `explore.md`: m, trend, season type, positivity. Why: these limit the ETS
   forms worth fitting.
2. Copy `../../templates/ets.py` with `fpp_data.py` and `fc_checks.py`. Replace the
   data section.

## Stage 2: Diagnostics

1. Positivity before any multiplicative component: `(y > 0).all()`. Zeros or
   negatives with an M component is FATAL.
2. Never request additive error with multiplicative season (A,N,M; A,A,M; A,Ad,M).
   Why: these forms are numerically unstable and the automatic search excludes them.
3. After fitting: innovation residuals with `residual_check(model.model_["residuals"],
   m, dof=0)`. Read the parameters from `model.model_["par"][:4]` (alpha, beta,
   gamma, phi) and the form from `model.model_["method"]`.

## Stage 3: Implementation

1. Fit `AutoETS(season_length=m)` (search by AICc) and the forms the plots suggest,
   for example `model="MAM", damped=True`.
2. Compare them by AICc. Valid here: same data, same family.
3. Read the parameters in words: alpha near 1 = the level follows the latest
   value; beta near 0 = a slope that barely changes; gamma near 0 = a fixed
   seasonal pattern; phi below 1 = the trend flattens out.
4. Long forecast horizon with a trend: fit the damped version too. Why: an
   undamped trend extrapolates a straight line and over-forecasts far ahead.

## Stage 4: Evaluation and robustness

- Time series cross-validation with the origins in `baselines.md`, against the
  benchmark, per forecast horizon (`score_cv`, `skill`).
- Compare with ARIMA only by cross-validation (`forecast-arima`). Never by AICc.
- Coverage of the intervals against nominal. Under-coverage: switch to conformal
  intervals (`ConformalIntervals(h=h, n_windows=5)`) and score again.
- Many series: share of series where ETS beats the benchmark.

## Verification gate

Apply `workflow.md`. Quote the ETS form, the parameters, the residual check and
the skill against the benchmark per forecast horizon.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/ets.md`: candidates and AICc, the chosen
form and its parameters in words, residual check, cross-validated accuracy, the
forecast with intervals and the plot.

If residuals fail: try ARIMA (`/forecasting:forecast-arima`). If drivers matter:
`/forecasting:forecast-dynamic-regression`. Then `/forecasting:forecast-auditor`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| AICc to choose between ETS and ARIMA | Likelihoods are not comparable | Cross-validation |
| Multiplicative components on data with zeros | Undefined | Additive, or transform |
| Requesting A error with M season | Unstable | Use M error, or a log and A season |
| Holt's trend for long forecast horizons | Over-forecasts | Damped trend, chosen by cross-validation |
| Reading AICc as accuracy | It is in-sample | Cross-validated scores per forecast horizon |
| Same intervals for A and M error | Point forecasts match; intervals differ | Choose the error type on residuals and coverage |

## Book sections

FPP3 chapter 8: 8.1 simple exponential smoothing, 8.2 methods with trend, 8.3
methods with seasonality, 8.4 a taxonomy, 8.5 innovations state space models, 8.6
estimation and model selection, 8.7 forecasting with ETS. R:
`https://otexts.com/fpp3/expsmooth.html`, `ses.html`, `holt.html`,
`holt-winters.html`, `taxonomy.html`, `ets.html`, `estimation-and-model-selection.html`,
`ets-forecasting.html`. Python edition: `https://otexts.com/fpppy/` chapter 8.
URLs unverified (see `NOTES.md`).
