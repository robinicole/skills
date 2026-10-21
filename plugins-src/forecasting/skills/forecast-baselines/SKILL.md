---
name: forecast-baselines
description: Fits the four benchmark forecasts (mean, naive, seasonal naive, drift), checks residuals, handles transformations and bias adjustment, and designs forecast evaluation with train/test splits, time series cross-validation and accuracy measures (MAE, RMSE, MASE, RMSSE, CRPS, Winkler, coverage). Use when the user says "baseline forecast", "naive forecast", "seasonal naive", "time series cross-validation", "backtest", "forecast accuracy" or "which accuracy metric". Also use it for questions about how to evaluate, test or compare forecasts. Not for reviewing a finished forecast (use forecast-auditor).
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast baselines

You set the bar and the scoring rules. Every other method skill is judged against
what you produce here.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/baselines.md` and `../../references/evaluation.md`.
3. Read the plan and `explore.md` in `docs/forecast-plans/*/` if they exist.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. Copy `../../templates/baselines.py`, `fpp_data.py` and `fc_checks.py` into
   `analysis/`. Replace section 1 with the user's data. Keep the rest as it is.
2. Fix the evaluation design **before** any model is scored: forecast horizon h,
   number of forecast origins, step between them, interval levels, primary point
   measure and distribution measure (matching table in `evaluation.md`).
   Why: choosing the measure after seeing results lets the choice favour a model.

## Stage 2: Diagnostics

1. Fit the four benchmarks: mean, naive, seasonal naive (seasonal data), drift.
   Why: they are cheap, hard to beat at short forecast horizons, and expose models that add
   nothing.
2. Residual check on each benchmark you might ship (`residual_check`, dof = 0).
   Why: it shows which structure is left for a real model to capture.
3. Transformation: if `explore.md` chose one, fit on the transformed scale and
   decide whether the user needs medians or means. Bias-adjust when forecasts are
   summed. Why: back-transformed points are medians, and medians do not add.

Emit verdicts from `diagnostics/baselines.md` when a check fails.

## Stage 3: Implementation

Run the template. Keep:

- The test-set scores (one split, at least h long).
- The cross-validation frame from `sf.cross_validation(...)`, scored with
  `score_cv(cv, train_df, m, levels, crps_levels)` per forecast horizon and pooled.
- The skill table against the benchmark (`skill(scores, "mase", "SeasonalNaive")`).

Why per forecast horizon: a model can win at h = 1 and lose at h = 12; the decision may need
only one of them.

## Stage 4: Evaluation and robustness

- Check the design with `audit_checks.check_cv_design` and `check_horizon`.
- Repeat the scoring with a sliding window (`input_size=`) if old data may describe
  a different process; report both.
- Many series: mean and median of the scaled measure, share of series where each
  model beats the benchmark.
- Coverage of each interval level against nominal (`check_calibration`).

## Verification gate

Apply `workflow.md`. Quote the benchmark scores per forecast horizon and the
design (h, origins, step, measures) from actual output.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/baselines.md`: the design, the benchmark
table, which benchmark is the bar and why, residual findings, transformation and
mean/median decision.

Hand off to the method skill in the plan. Tell it: "the bar is <benchmark> with
<measure> = <value> per forecast horizon; use the same origins".

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| Accuracy from fitted values | One-step, in-sample, rewards every parameter | Test set or cross-validation |
| One short test set | Accuracy rests on a few points | Cross-validation over many forecast origins |
| MAE or RMSE averaged across series | Large series dominate | MASE or RMSSE |
| MAPE on data with zeros | Undefined, and it favours under-forecasts | MASE; MAPE only as a secondary figure on positive data |
| Averaging per-origin RMSE | With one error per origin it equals MAE | Average squared errors, then root (`score_cv`) |
| Lambda or scaling fitted on all data | Leaks the test period into training | Fit them inside each training window |
| Choosing the measure after the results | Biases the comparison | Fix it in Stage 1 |
| Summing back-transformed medians | The sum is biased low | Bias-adjust to means first |

## Book sections

FPP3 chapter 5: 5.2 simple methods, 5.3 fitted values and residuals, 5.4 residual
diagnostics, 5.5 distributional forecasts and prediction intervals, 5.6
forecasting using transformations, 5.7 forecasting with decomposition, 5.8
evaluating point accuracy, 5.9 distributional accuracy, 5.10 time series
cross-validation. R: `https://otexts.com/fpp3/toolbox.html`, `simple-methods.html`,
`residuals.html`, `prediction-intervals.html`, `ftransformations.html`,
`accuracy.html`, `distaccuracy.html`, `tscv.html`. Python edition:
`https://otexts.com/fpppy/` chapter 5. URLs unverified (see `NOTES.md`).
