---
name: forecast-arima
description: Fits ARIMA and seasonal ARIMA models, deciding stationarity and differencing with KPSS and seasonal strength tests, reading ACF and PACF, running the automatic order search, checking residuals, and comparing ARIMA with ETS by cross-validation. Use when the user says "ARIMA model", "seasonal ARIMA", "SARIMA", "auto ARIMA", "stationarity", "unit root test", "differencing" or "PACF". Also use it for questions about differencing and reading ACF or PACF plots. Not for regression with ARIMA errors (use forecast-dynamic-regression).
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast ARIMA

You fit ARIMA models with the differencing decided by tests, not by habit.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/arima.md`.
3. Read the plan, `explore.md` and `baselines.md` in `docs/forecast-plans/*/` if present.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. Copy `../../templates/arima.py` with `fpp_data.py` and `fc_checks.py`. Replace
   the data section.
2. Stabilise the variance first: log or Box-Cox when the swing grows with the level.
   Why: differencing removes trend and season, not changing variance.

## Stage 2: Diagnostics

1. Seasonal differencing D from `nsdiffs(y, period=m)`; then d from
   `ndiffs(..., test="kpss")` on the seasonally differenced series. Why: a seasonal
   difference often removes the trend as well, so take it first.
2. Never more than two differences in total. A lag-1 autocorrelation near -0.5
   after differencing means one difference too many.
3. ACF and PACF of the differenced series. AR(p): PACF cuts off after p, ACF
   decays. MA(q): the reverse. Spikes at multiples of m: seasonal P (PACF) or Q (ACF).
   When both decay, let the search decide.

## Stage 3: Implementation

1. Automatic search: `AutoARIMA(season_length=m)`; wider search with
   `stepwise=False, approximation=False`.
2. A hand-picked candidate from the plots: `ARIMA(order=(p, d, q),
   seasonal_order=(P, D, Q), season_length=m)`.
3. Rank by AICc **inside each (d, D) group only**. Why: differencing changes the
   data the likelihood is computed on.
4. Residual check with dof = p + q + P + Q (`model.model_["arma"]` gives
   `(p, q, P, Q, m, d, D)`). Failing: another order, or a wider search.
5. Constant: d = 0 with a constant gives a non-zero mean; d = 1 with a constant
   gives a drift; d = 2 with a constant gives a quadratic trend, which is rarely
   sensible.

## Stage 4: Evaluation and robustness

- Cross-validation against ETS and the benchmark on the origins in
  `baselines.md`. Why: ARIMA and ETS overlap only partly; the data decide.
- After a log, back-transform forecasts and intervals (`np.exp`); the point is a
  median unless bias-adjusted.
- Robustness: does the choice survive a shorter training window?

## Verification gate

Apply `workflow.md`. Quote D and d with their tests, the chosen ARIMA, its
coefficients, the residual check with dof, and cross-validated skill.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/arima.md`. Explain the long-run behaviour of
the chosen model (reverts to a mean, follows a drift, or stays flat) and that the
intervals keep widening when d is 1 or more.

Next: `/forecasting:forecast-auditor`. If drivers matter:
`/forecasting:forecast-dynamic-regression`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Comparing AICc across d or D | Different data in the likelihood | AICc within one (d, D); CV across |
| Comparing ARIMA with ETS by AICc | Different likelihoods | Cross-validation |
| Over-differencing | Adds MA structure, widens intervals | Test-based d and D, at most 2 in total |
| Differencing to fix variance | Variance growth remains | Log or Box-Cox first |
| d = 2 with a constant | Quadratic trend forecasts | Drop the constant or use damped ETS |
| Trusting the search without a residual check | Stepwise search can stop early | Ljung-Box with dof; wider search |
| Ljung-Box with dof = 0 for ARIMA | Too lenient | dof = p + q + P + Q |

## Book sections

FPP3 chapter 9: 9.1 stationarity and differencing, 9.2 backshift notation, 9.3
autoregressive models, 9.4 moving average models, 9.5 non-seasonal ARIMA, 9.6
estimation and order selection, 9.7 ARIMA modelling in practice, 9.8 forecasting,
9.9 seasonal ARIMA, 9.10 ARIMA versus ETS. R: `https://otexts.com/fpp3/arima.html`,
`stationarity.html`, `AR.html`, `MA.html`, `non-seasonal-arima.html`,
`arima-estimation.html`, `arima-r.html`, `arima-forecasting.html`,
`seasonal-arima.html`, `arima-ets.html`. Python edition:
`https://otexts.com/fpppy/` chapter 9. URLs unverified (see `NOTES.md`).
