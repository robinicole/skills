---
name: forecast-hierarchical
description: Forecasts hierarchical and grouped time series so every level adds up, comparing bottom-up, top-down, middle-out and MinT reconciliation, checking coherence and scoring accuracy at each level. Use when the user says "hierarchical forecast", "reconcile forecasts", "MinT", "forecasts don't add up", "store and region totals" or "grouped time series". Not for a single series.
metadata:
  author: Robin Nicole
  compatibility: Python 3.10 or later. Packages listed in references/preflight.md.
---

# Forecast hierarchical

You make forecasts coherent across levels and show what that does to accuracy at
each level.

## Before you begin

1. Read `../../references/lessons.md` and `docs/forecast-plans/lessons.md` if present.
2. Read `../../references/diagnostics/hierarchical.md`.
3. Read the plan, `explore.md` and `baselines.md` in `docs/forecast-plans/*/`.
4. Read `../../references/workflow.md`.

## Stage 1: Setup

1. Write down the structure: levels, attributes, nesting. Strict nesting (store in
   region) is a hierarchy; crossed attributes (product by region) are grouped.
   Why: top-down and middle-out need a strict hierarchy.
2. Copy `../../templates/hierarchical.py` with `fpp_data.py` and `fc_checks.py`.
3. Add a constant `total` column, then `Y, S, tags = aggregate(df, spec)`. Each
   spec entry lists the columns that define one level, starting with `["total"]`.

## Stage 2: Diagnostics

1. Check `tags`: every level present; the bottom count equals the raw series count.
   A wrong structure is FATAL.
2. Look at a series from each level. Why: the top is smooth and seasonal, the
   bottom noisy and often intermittent. The base model may need to differ by level.
3. Residual check on the base models, at least for every series at the levels the
   decision uses: loop `residual_check(resid, m, dof, name, plot=False)` and report
   the share that pass per level. Why: MinT weights series by their errors; a base
   model that misses structure passes its error into the reconciled forecasts.

## Stage 3: Implementation

1. Base forecasts for every series at every level with `fitted=True` (MinT needs
   in-sample errors): `sf.forecast(df=Y_train, h=h, level=levels, fitted=True)` and
   `sf.forecast_fitted_values()`.
2. Reconcile with several methods side by side: `BottomUp()`,
   `TopDown(method="forecast_proportions")` and `MiddleOut(...)` for hierarchies,
   `MinTrace(method="ols" | "wls_struct" | "mint_shrink")` for both.
   Why: MinT uses every level's information and the error covariance; shrinkage
   keeps the covariance estimate stable with many series.
3. Intervals: `level=` and `intervals_method="normality"` or `"bootstrap"` in
   `reconcile`.
4. Coherence check (`hierarchical.py` section 5). A gap above rounding is FATAL.

## Stage 4: Evaluation and robustness

- Scale-free accuracy (MASE, RMSSE) per level with
  `hierarchicalforecast.evaluation.evaluate(..., tags=tags)`, base against each
  reconciled version. Why: reconciliation can help most levels and lose at some.
- Repeat over several forecast origins before deciding. The template's section 6
  runs four origins (cutoff = last training date); widen it for a decision, and
  count the origins where each method beats the base forecasts per level.
- Interval coverage per level against nominal. Why: reconciled intervals at the
  top are often too narrow.
- Negative reconciled values on non-negative data: `MinTrace(..., nonnegative=True)`,
  and score that setting on the same origins before shipping it.

## Verification gate

Apply `workflow.md`. Quote the structure (series per level), the base residual
pass rate per level, the coherence gap, accuracy per level over several forecast
origins, and coverage per level.

## Stage 5: Interpretation and handoff

Write `docs/forecast-plans/<project>/hierarchical.md`: structure, base model,
methods compared, per-level table, the recommended method for the levels the
decision uses, and where reconciliation lost accuracy.

Next: `/forecasting:forecast-auditor`, then `/forecasting:forecast-report`.

## Common mistakes

| Mistake | Why it is wrong | Instead |
|---|---|---|
| One overall accuracy number | Hides losses at some levels | A row per level |
| RMSE pooled across levels | The top level dominates | MASE or RMSSE per level |
| Top-down on grouped data | No single nesting to split along | Bottom-up or MinT |
| MinT with sample covariance and many series | Covariance estimate fails | `mint_shrink` |
| Forgetting `fitted=True` | MinT has no residuals to use | Forecast with fitted values |
| No total column in `aggregate` | The top level is missing | Add a constant `total` column |
| Assuming reconciliation always improves accuracy | It often does, not always | Measure it |

## Book sections

FPP3 chapter 11: 11.1 hierarchical and grouped time series, 11.2 single level
approaches, 11.3 forecast reconciliation, 11.4 tourism example, 11.5 grouped
example, 11.6 reconciled distributional forecasts. R:
`https://otexts.com/fpp3/hierarchical.html`, `hts.html`, `single-level.html`,
`reconciliation.html`, `tourism.html`, `rec-prob.html`. Python edition:
`https://otexts.com/fpppy/` chapter 11. URLs unverified (see `NOTES.md`).
