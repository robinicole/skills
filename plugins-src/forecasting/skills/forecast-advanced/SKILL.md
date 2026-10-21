---
name: forecast-advanced
description: Applies the book's advanced methods when standard models miss a feature, namely multiple seasonal periods with MSTL or Fourier terms, Prophet, vector autoregression, neural network autoregression and bagged ETS, always compared with ETS or ARIMA. Use when the user says "Prophet", "VAR model", "multiple seasonality", "half-hourly", "hourly data", "neural network forecast", "NNAR" or "bagging". Also use it for questions about data with two or more seasonal cycles, or about nonlinear models. Not for a first model on an ordinary monthly or quarterly series.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md. Prophet optional.
---

# Forecast advanced

You use more complex machinery only when a simpler model has a specific gap, and
you show what the extra machinery bought.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/advanced.md`.
3. Read the plan and the method files in `docs/forecast-plans/*/`.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. Name the gap: several seasonal periods, nonlinear effects, feedback between
   series, or unstable ETS forecasts. No named gap: go back to `forecast-ets` or
   `forecast-arima`. Why: the book keeps these methods as specialised tools.
2. Copy `../../templates/advanced.py` with `fpp_data.py` and `fc_checks.py`. Keep
   only the sections for the gap.

## Stage 2: Diagnostics

Per method, from `diagnostics/advanced.md`:

- Multiple seasonality: each period visible in the ACF; none left in the
  residual ACF after the fit.
- Prophet: residual check; residuals usually stay autocorrelated, so treat its
  intervals as unreliable.
- VAR: every series stationary; lag order by BIC; residual check per equation.
- NNAR: number of networks averaged; intervals only from simulation.

## Stage 3: Implementation

- **Several seasonal periods**: `MSTL(season_length=[m1, m2],
  trend_forecaster=AutoARIMA())`, or dynamic harmonic regression with one Fourier
  set per period and `AutoARIMA(season_length=1)` errors. Use the second when
  predictors such as temperature matter.
- **Prophet**: `Prophet(...)` with `add_regressor` for known drivers. Use it when
  its automatic change points and holiday effects fit the problem.
- **VAR**: `VAR(df).select_order(maxlags)`, fit with the BIC order. Only when the
  series affect each other; otherwise dynamic regression is simpler.
- **NNAR** (Not from the book in Python): `MLForecast` with lags 1..p, p from the
  best AR by AIC, one hidden layer of k = (p + P + 1)/2 units, 20 or more networks
  averaged. No interval without simulation.
- **Bagged ETS**: Box-Cox, STL, moving-block bootstrap of the remainder (block at
  least 2m), back-transform, ETS on each series, average.

## Stage 4: Evaluation and robustness

- Score each advanced model against ETS or ARIMA and a benchmark on the same
  held-out data, then over several forecast origins before deciding.
- Ex-post if actual future predictors were used; label it.

## Verification gate

Apply `workflow.md`. Quote the gap, the advanced model's accuracy next to the
standard model and the benchmark, and the residual checks.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/advanced.md`: the gap, the method, what it
gained over the standard model, and its limits (Prophet intervals, NNAR intervals,
VAR parameter count). If it did not beat the standard model, recommend the
standard model.

Next: `/forecasting:forecast-auditor`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Prophet as the default | Rarely beats ETS or ARIMA in the book's examples | Use it for a named gap, compared with them |
| Trusting Prophet intervals | Residual autocorrelation ignored | Check coverage; report points only if poor |
| Seasonal ARIMA with m = 336 | Impractical and unstable | MSTL or Fourier terms |
| VAR without feedback between series | Many parameters for nothing | Dynamic regression |
| VAR on non-stationary series | Spurious dynamics | Difference first |
| One neural network | Unstable from one random start | Average many |
| Normal-formula intervals for NNAR | No such formula | Simulate paths or give none |

## Book sections

FPP3 chapter 12: 12.1 complex seasonality, 12.2 Prophet, 12.3 vector
autoregressions, 12.4 neural network models, 12.5 bootstrapping and bagging. R:
`https://otexts.com/fpp3/advanced-methods.html`, `complexseasonality.html`,
`prophet.html`, `VAR.html`, `nnetar.html`, `bootstrap.html`. Python edition:
`https://otexts.com/fpppy/` chapter 12. URLs unverified (see `NOTES.md`).
