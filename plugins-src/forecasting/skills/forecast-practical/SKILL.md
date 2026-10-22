---
name: forecast-practical
description: Handles the data problems that break standard forecasting workflows, namely intermittent demand and small counts (Croston family), forecasts that must stay positive or inside bounds, forecast combinations, prediction intervals for totals over several periods, backcasting, very short or very long series, missing values and outliers. Use when the user says "intermittent demand", "Croston", "lots of zeros", "forecast must stay positive", "combine forecasts", "interval for the annual total", "missing values in my series", "outliers in my series" or "backcast". Not for choosing the main model family.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast practical

You fix the data problem first, then hand back to the method skill.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/practical.md`.
3. Read the plan and `explore.md` in `docs/forecast-plans/*/`.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

Name the problem from the table, then copy `../../templates/practical.py` with
`fpp_data.py` and `fc_checks.py` and keep the matching section.

| Problem | Fix |
|---|---|
| Small counts, many zeros | Croston family: `CrostonClassic`, `CrostonSBA`, `TSB` |
| Must stay positive | Model the log; back-transform |
| Must stay in [a, b] | Scaled logit: log((y - a)/(b - y)); back-transform |
| Several close models | Equal-weight mean of point forecasts |
| Interval for a total over periods | Simulate sample paths, sum per path, quantiles |
| History before the first observation | Reverse, forecast, reverse back |
| Very short series | Simple models; AICc chooses; no seasonal model under two seasons |
| Very long series | Train on the recent part, or a model whose parameters evolve |
| Missing values | Ask why first; dummies if informative, state-space interpolation if random |
| Outliers | Robust STL remainder beyond 3 IQR; keep with a dummy unless an error |
| Weekly data | Fourier terms with period 365.25/7: `forecast-regression` |

## Stage 2: Diagnostics

- Intermittent: share of zeros overall and in the last two seasons. Zeros at the
  end may mean the item has stopped; ask the data owner.
- Bounds: are any forecast or interval values outside them?
- Missing values: why are they missing? A closed shop is information, not noise.

## Stage 3: Implementation

Run only the sections you need. Croston forecasts are a **rate** per period.
Scaled-logit and log back-transforms give medians. Combinations: average the
point forecasts; intervals need pooled simulated paths. Aggregates: never add
interval ends. Why: errors at different forecast horizons are correlated, so the sum's
spread is not the sum of spreads.

## Stage 4: Evaluation and robustness

- Intermittent: MAE or MASE across origins; no MAPE.
- Combinations: the combination against each member on the same origins.
- Interpolated gaps: compare with a model fitted only after the last gap.

## Verification gate

Apply `workflow.md`. Quote the problem found, the fix, and its effect on
cross-validated accuracy or on the bounds.

## Stage 5: Interpretation and handoff

Add a "Practical issues" section to the method file in
`docs/forecast-plans/<project>/`. Say what was changed and why. Hand back to the
method skill, then `/forecasting:forecast-auditor`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| MAPE on intermittent data | Undefined at zero | MAE or MASE |
| Reading a Croston forecast as a count | It is an average rate | Say "average per period" |
| Adding interval ends for a total | Ignores correlation across forecast horizons | Simulate paths |
| Averaging interval ends of a combination | No valid distribution | Pool paths, or report points only |
| Interpolating informative gaps | Removes real information | Dummies for the gap and after |
| Deleting outliers | They may recur | Keep with a dummy; replace only errors |
| Refusing short series | No minimum length exists | Simple models, AICc |
| m = 52 for weekly data | Wrong in 53-week years | Fourier terms |

## Book sections

FPP3 chapter 13: 13.1 weekly, daily and sub-daily data, 13.2 time series of
counts, 13.3 ensuring forecasts stay within limits, 13.4 forecast combinations,
13.5 prediction intervals for aggregates, 13.6 backcasting, 13.7 very long and very
short series, 13.8 forecasting on training and test sets, 13.9 missing values and
outliers. R: `https://otexts.com/fpp3/practical.html`, `weekly.html`, `counts.html`,
`practical.html#sec-limits`, `combinations.html`, `aggregates.html`, `backcasting.html`,
`long-short-ts.html`, `training-test.html`, `missing-outliers.html`. Python
edition: `https://otexts.com/fpppy/` chapter 13, which has no sections on aggregate intervals or training and test sets. URLs checked 2026-10-22.
